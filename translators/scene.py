#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 Jonathan Dent, The appleseedhq Organization
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import math
import os

import bpy

import appleseed as asr
from .assethandlers import AssetHandler, CopyAssetsAssetHandler
from .cameras import InteractiveCameraTranslator, RenderCameraTranslator
from .lamps import LampTranslator
from .material import MaterialTranslator
from .objects import ArchiveAssemblyTranslator, MeshTranslator
from .textures import TextureTranslator
from .utilites import ProjectExportMode
from .world import WorldTranslator
from ..logger import get_logger
from ..utils.util import Timer, calc_film_aspect_ratio, clamp_value, realpath

logger = get_logger()


class SceneTranslator(object):
    """
    Translates a Blender scene into an appleseed project.
    """

    # Constructors.
    @classmethod
    def create_project_export_translator(cls, depsgraph):
        project_dir = os.path.dirname(depsgraph.scene_eval.appleseed.export_path)

        logger.debug("Creating texture and geometry directories in %s", project_dir)

        geometry_dir = os.path.join(project_dir, "_geometry")
        textures_dir = os.path.join(project_dir, "_textures")

        if not os.path.exists(geometry_dir):
            os.makedirs(geometry_dir)

        if not os.path.exists(textures_dir):
            os.makedirs(textures_dir)

        logger.debug("Creating project export scene translator, filename: %s", depsgraph.scene_eval.appleseed.export_path)

        asset_handler = CopyAssetsAssetHandler(project_dir, geometry_dir, textures_dir, depsgraph)

        return cls(export_mode=ProjectExportMode.PROJECT_EXPORT,
                   selected_only=depsgraph.scene.appleseed.export_selected,
                   asset_handler=asset_handler)

    @classmethod
    def create_final_render_translator(cls, depsgraph):
        """
        Create a scene translator to export the scene to an in memory appleseed project.
        :param depsgraph:
        :return:
        """

        logger.debug("Creating final render scene translator")

        asset_handler = AssetHandler(depsgraph)

        return cls(export_mode=ProjectExportMode.FINAL_RENDER,
                   selected_only=False,
                   asset_handler=asset_handler)

    @classmethod
    def create_interactive_render_translator(cls, depsgraph):
        """
        Create a scene translator to export the scene to an in memory appleseed project
        optimized for quick interactive edits.
        :param depsgraph:
        :return:
        """

        logger.debug("Creating interactive render scene translator")

        asset_handler = AssetHandler(depsgraph)

        return cls(export_mode=ProjectExportMode.INTERACTIVE_RENDER,
                   selected_only=False,
                   asset_handler=asset_handler)

    def __init__(self, export_mode, selected_only, asset_handler):
        """
        Constructor. Do not use it to create instances of this class.
        Use the @classmethods instead.
        """

        self.__asset_handler = asset_handler
        self.__export_mode = export_mode
        self.__selected_only = selected_only

        # Translators.
        self.__as_world_translator = None
        self.__as_camera_translator = None
        self.__as_lamp_translators = dict()
        self.__as_object_translators = dict()
        self.__as_material_translators = dict()
        self.__as_texture_translators = dict()

        # Motion Steps
        self.__all_times = {0.0}
        self.__cam_times = {0.0}
        self.__xform_times = {0.0}
        self.__deform_times = {0.0}

        # Interactive tools
        self.__viewport_resolution = None

        self.__project = None
        self.__frame = None

    @property
    def as_project(self):
        return self.__project

    def translate_scene(self, engine, depsgraph, context=None):
        logger.debug("appleseed: Translating scene %s", depsgraph.scene_eval.name)

        prof_timer = Timer()
        prof_timer.start()

        self.__create_project(depsgraph)

        if self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            self.__calc_shutter_times(depsgraph)

        self.__translate_render_settings(depsgraph)

        self.__calc_viewport_resolution(depsgraph, context)

        aovs = self.__set_aovs(depsgraph)
        frame_params = self.__translate_frame(depsgraph)

        self.__frame = asr.Frame("beauty", frame_params, aovs)

        self.__set_render_border_window(depsgraph, context)

        if len(depsgraph.scene_eval.appleseed.post_processing_stages) > 0 and self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            self.__set_post_process(depsgraph)

        self.__project.set_frame(self.__frame)
        self.__frame = self.__project.get_frame()

        # Create camera
        if depsgraph.scene_eval.camera is not None:
            # Create interactive or final render camera
            if self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER:
                logger.debug("appleseed: Creating interactive render camera translator")
                self.__as_camera_translator = InteractiveCameraTranslator(depsgraph.scene_eval.camera, self.__asset_handler)
            else:
                logger.debug("appleseed: Creating final render camera translator")
                self.__as_camera_translator = RenderCameraTranslator(depsgraph.scene_eval.camera, self.__asset_handler)
        else:
            engine.error_set("appleseed: No camera in scene!")

        # Create world
        if depsgraph.scene_eval.world is not None and depsgraph.scene_eval.world.appleseed_sky.env_type != 'none':
            logger.debug("appleseed: Creating world translator")
            self.__as_world_translator = WorldTranslator(depsgraph.scene_eval.world, self.__asset_handler)

        # Blender scene processing
        objects_to_add = dict()
        lights_to_add = dict()
        materials_to_add = dict()
        textures_to_add = dict()

        for obj in bpy.data.objects:
            if obj.type == 'LIGHT':
                logger.debug("appleseed: Creating light translator for %s", obj.name_full)
                lights_to_add[obj] = LampTranslator(obj, self.__asset_handler)
            elif obj.type == 'MESH':
                logger.debug("appleseed: Creating mesh translator for %s", obj.name_full)
                objects_to_add[obj] = MeshTranslator(obj.evaluated_get(depsgraph), self.__export_mode, self.__asset_handler, list(self.__xform_times))
        #     elif obj.type == 'MESH' and obj.appleseed.object_export == "archive_assembly":
        #         logger.debug("appleseed: Creating archive assembly translator for %s", obj.name_full)
        #         objects_to_add[obj] = ArchiveAssemblyTranslator(obj, self.__asset_handler, self.__xform_times)

        for mat in bpy.data.materials:
            if mat.users > 0:
                logger.debug("appleseed: Creating material translator for %s", mat.name_full)
                materials_to_add[mat] = MaterialTranslator(mat, self.__asset_handler)

        for tex in bpy.data.images:
            if tex.users > 1:
                logger.debug("appleseed: Creating texture translator for %s", tex.name_full)
                textures_to_add[tex] = TextureTranslator(tex, self.__asset_handler)

        # Create camera, world, material and texture entities
        logger.debug("appleseed: Creating camera entity")
        self.__as_camera_translator.create_entities(depsgraph.scene_eval, context, engine)
        if self.__as_world_translator is not None:
            logger.debug("appleseed: Creating world entity")
            self.__as_world_translator.create_entities(depsgraph.scene_eval)

        for obj, trans in materials_to_add.items():
            logger.debug("appleseed: Creating entity for translator %s", obj.name_full)
            trans.create_entities(depsgraph.scene_eval)
        for obj, trans in textures_to_add.items():
            logger.debug("appleseed: Creating entity for translator %s", obj.name_full)
            trans.create_entities(depsgraph.scene_eval)

        # Set initial position of all objects and lamps
        self.__calc_initial_positions(depsgraph, engine, objects_to_add, lights_to_add)

        # Remove unused translators
        for translator in list(objects_to_add.keys()):
            if objects_to_add[translator].instances_size == 0:
                logger.debug("appleseed: Translator %s has no instances, deleting...", translator)
                del objects_to_add[translator]

        for translator in list(lights_to_add.keys()):
            if len(lights_to_add[translator].matrices) == 0:
                logger.debug("appleseed: Translator %s has no instances, deleting...", translator)
                del lights_to_add[translator]

        # Create 3D entities
        for obj, trans in objects_to_add.items():
            logger.debug("appleseed: Creating mesh entity for %s", obj.name_full)
            trans.create_entities(depsgraph.scene_eval, len(self.__deform_times))
        for obj, trans in lights_to_add.items():
            logger.debug("appleseed: Creating light entity for %s", obj.name_full)
            trans.create_entities(depsgraph.scene_eval)

        # Calculate additional steps for motion blur
        if self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            self.__calc_motion_steps(depsgraph, engine, objects_to_add)

        # Flush entities
        as_scene = self.__project.get_scene()

        self.__as_camera_translator.flush_entities(as_scene, self.__main_assembly, self.__project)
        if self.__as_world_translator is not None:
            self.__as_world_translator.flush_entities(as_scene, self.__main_assembly, self.__project)

        for obj, trans in objects_to_add.items():
            logger.debug("appleseed: Flushing entity for %s into project", obj.name_full)
            trans.flush_entities(as_scene, self.__main_assembly, self.__project)
        for obj, trans in lights_to_add.items():
            logger.debug("appleseed: Flushing entity for %s into project", obj.name_full)
            trans.flush_entities(as_scene, self.__main_assembly, self.__project)
        for obj, trans in materials_to_add.items():
            logger.debug("appleseed: Flushing entity for %s into project", obj.name_full)
            trans.flush_entities(as_scene, self.__main_assembly, self.__project)
        for obj, trans in textures_to_add.items():
            logger.debug("appleseed: Flushing entity for %s into project", obj.name_full)
            trans.flush_entities(as_scene, self.__main_assembly, self.__project)

        # Transfer temp translators to main list
        for bl_obj, translator in objects_to_add.items():
            self.__as_object_translators[bl_obj] = translator
        for bl_obj, translator in lights_to_add.items():
            self.__as_lamp_translators[bl_obj] = translator
        for bl_obj, translator in materials_to_add.items():
            self.__as_material_translators[bl_obj] = translator
        for bl_obj, translator in textures_to_add.items():
            self.__as_texture_translators[bl_obj] = translator

        self.__load_searchpaths()

        prof_timer.stop()
        logger.debug("Scene translated in %f seconds.", prof_timer.elapsed())

    def update_multiview_camera(self, engine, depsgraph):
        current_frame = depsgraph.scene_eval.frame_current

        for time in self.__cam_times:
            new_frame = current_frame + time
            int_frame = math.floor(new_frame)
            subframe = new_frame - int_frame

            engine.frame_set(int_frame, subframe=subframe)

            self.__as_camera_translator.update_mult_cam_xform(engine, depsgraph.scene_eval, time)
        
        engine.frame_set(current_frame, subframe=0.0)

    def write_project(self, export_path):
        filename = bpy.path.ensure_ext(bpy.path.abspath(export_path), '.appleseed')

        asr.ProjectFileWriter().write(
            self.__project,
            filename,
            asr.ProjectFileWriterOptions.OmitWritingGeometryFiles | asr.ProjectFileWriterOptions.OmitHandlingAssetFiles)

    # Internal methods.
    def __create_project(self, depsgraph):
        logger.debug("appleseed: Creating appleseed project")

        self.__project = asr.Project(depsgraph.scene_eval.name)

        # Render settings.
        self.__project.add_default_configurations()

        # Create the scene.
        self.__project.set_scene(asr.Scene())

        # Create the environment.
        self.__project.get_scene().set_environment(asr.Environment("environment", {}))

        # Create the main assembly.
        self.__project.get_scene().assemblies().insert(asr.Assembly("assembly", {}))
        self.__main_assembly = self.__project.get_scene().assemblies()["assembly"]

        # Instance the main assembly.
        assembly_inst = asr.AssemblyInstance("assembly_inst", {}, "assembly")

        assembly_inst.transform_sequence().set_transform(0.0, asr.Transformd(asr.Matrix4d.identity()))
        self.__project.get_scene().assembly_instances().insert(assembly_inst)

        # Create default materials.
        self.__create_default_material()
        self.__create_null_material()

    def __create_default_material(self):
        logger.debug("appleseed: Creating default material")

        surface_shader = asr.SurfaceShader("diagnostic_surface_shader", "__default_surface_shader", {'mode': 'facing_ratio'})

        material = asr.Material('generic_material', "__default_material", {'surface_shader': '__default_surface_shader'})

        self.__main_assembly.surface_shaders().insert(surface_shader)
        self.__main_assembly.materials().insert(material)

    def __create_null_material(self):
        logger.debug("appleseed: Creating null material")

        material = asr.Material('generic_material', "__null_material", {})

        self.__main_assembly.materials().insert(material)

    def __calc_shutter_times(self, depsgraph):
        scene = depsgraph.scene_eval

        shutter_length = scene.appleseed.shutter_close - scene.appleseed.shutter_open

        if scene.appleseed.enable_camera_blur:
            self.__get_sub_frames(scene, shutter_length, scene.appleseed.camera_blur_samples, self.__cam_times)

        if scene.appleseed.enable_object_blur:
            self.__get_sub_frames(scene, shutter_length, scene.appleseed.object_blur_samples, self.__xform_times)

        if scene.appleseed.enable_deformation_blur:
            self.__get_sub_frames(scene, shutter_length, self.__round_up_pow2(scene.appleseed.deformation_blur_samples),
                                  self.__deform_times)

        # Merge all subframe times
        all_times = set()
        all_times.update(self.__cam_times)
        all_times.update(self.__xform_times)
        all_times.update(self.__deform_times)
        self.__all_times = sorted(list(all_times))

        # Xform times is converted to a list here so it can be easily passed into the BlTransformLibrary of each translator.
        self.__xform_times = sorted(list(self.__xform_times))

    def __translate_render_settings(self, depsgraph):
        logger.debug("appleseed: Translating render settings")

        scene = depsgraph.scene_eval
        asr_scene_props = scene.appleseed

        conf_final = self.__project.configurations()['final']
        conf_interactive = self.__project.configurations()['interactive']

        lighting_engine = asr_scene_props.lighting_engine if self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER else 'pt'

        tile_renderer = 'adaptive' if asr_scene_props.pixel_sampler == 'adaptive' else 'generic'

        pixel_render_mapping = {'uniform': 'uniform',
                                'adaptive': '',
                                'texture': 'texture'}
        pixel_renderer = pixel_render_mapping[asr_scene_props.pixel_sampler]

        parameters = {
            'uniform_pixel_renderer': {
                'force_antialiasing': True if asr_scene_props.force_aa else False,
                'samples': asr_scene_props.samples},
            'adaptive_tile_renderer': {
                'min_samples': asr_scene_props.adaptive_min_samples,
                'noise_threshold': asr_scene_props.adaptive_noise_threshold,
                'batch_size': asr_scene_props.adaptive_batch_size,
                'max_samples': asr_scene_props.adaptive_max_samples},
            'texture_controlled_pixel_renderer': {
                'min_samples': asr_scene_props.adaptive_min_samples,
                'max_samples': asr_scene_props.adaptive_max_samples,
                'file_path': realpath(asr_scene_props.texture_sampler_filepath)},
            'use_embree': asr_scene_props.use_embree,
            'pixel_renderer': pixel_renderer,
            'lighting_engine': lighting_engine,
            'tile_renderer': tile_renderer,
            'passes': asr_scene_props.renderer_passes,
            'generic_frame_renderer': {'tile_ordering': asr_scene_props.tile_ordering},
            'progressive_frame_renderer': {
                'max_average_spp': asr_scene_props.interactive_max_samples,
                'max_fps': asr_scene_props.interactive_max_fps,
                'time_limit': asr_scene_props.interactive_max_time},
            'light_sampler': {
                'algorithm': asr_scene_props.light_sampler,
                'enable_light_importance_sampling': asr_scene_props.enable_light_importance_sampling},
            'shading_result_framebuffer': "permanent" if asr_scene_props.renderer_passes > 1 else "ephemeral"}

        if self.__export_mode != ProjectExportMode.PROJECT_EXPORT:
            if self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER:
                render_threads = -1
            else:
                render_threads = asr_scene_props.threads if not asr_scene_props.threads_auto else 'auto'
            parameters['rendering_threads'] = render_threads
            parameters['texture_store'] = {'max_size': asr_scene_props.tex_cache * 1024 * 1024}

        if lighting_engine == 'pt':
            parameters['pt'] = {
                'enable_ibl': True if asr_scene_props.enable_ibl else False,
                'enable_dl': True if asr_scene_props.enable_dl else False,
                'enable_caustics': True if scene.appleseed.enable_caustics else False,
                'clamp_roughness': True if scene.appleseed.enable_clamp_roughness else False,
                'record_light_paths': True if scene.appleseed.record_light_paths else False,
                'next_event_estimation': True,
                'rr_min_path_length': asr_scene_props.rr_start,
                'optimize_for_lights_outside_volumes': asr_scene_props.optimize_for_lights_outside_volumes,
                'volume_distance_samples': asr_scene_props.volume_distance_samples,
                'dl_light_samples': asr_scene_props.dl_light_samples,
                'ibl_env_samples': asr_scene_props.ibl_env_samples,
                'dl_low_light_threshold': asr_scene_props.dl_low_light_threshold,
                'max_diffuse_bounces': asr_scene_props.max_diffuse_bounces if not asr_scene_props.max_diffuse_bounces_unlimited else -1,
                'max_glossy_bounces': asr_scene_props.max_glossy_brdf_bounces if not asr_scene_props.max_glossy_brdf_bounces_unlimited else -1,
                'max_specular_bounces': asr_scene_props.max_specular_bounces if not asr_scene_props.max_specular_bounces_unlimited else -1,
                'max_volume_bounces': asr_scene_props.max_volume_bounces if not asr_scene_props.max_volume_bounces_unlimited else -1,
                'max_bounces': asr_scene_props.max_bounces if not asr_scene_props.max_bounces_unlimited else -1}
            if not asr_scene_props.max_ray_intensity_unlimited:
                parameters['pt']['max_ray_intensity'] = asr_scene_props.max_ray_intensity
        else:
            parameters['sppm'] = {
                'alpha': asr_scene_props.sppm_alpha,
                'dl_mode': asr_scene_props.sppm_dl_mode,
                'enable_caustics': "true" if asr_scene_props.enable_caustics else "false",
                'env_photons_per_pass': asr_scene_props.sppm_env_photons,
                'initial_radius': asr_scene_props.sppm_initial_radius,
                'light_photons_per_pass': asr_scene_props.sppm_light_photons,

                # Leave at 0 for now - not in appleseed.studio GUI
                'max_path_length': 0,
                'max_photons_per_estimate': asr_scene_props.sppm_max_per_estimate,
                'path_tracing_max_path_length': asr_scene_props.sppm_pt_max_length,
                'path_tracing_rr_min_path_length': asr_scene_props.sppm_pt_rr_start,
                'photon_tracing_max_path_length': asr_scene_props.sppm_photon_max_length,
                'photon_tracing_rr_min_path_length': asr_scene_props.sppm_photon_rr_start}

            if not asr_scene_props.sppm_pt_max_ray_intensity_unlimited:
                parameters['sppm']['path_tracing_max_ray_intensity'] = asr_scene_props.sppm_pt_max_ray_intensity

        if asr_scene_props.shading_override:
            parameters['shading_engine'] = {'override_shading': {'mode': asr_scene_props.override_mode}}

        conf_final.set_parameters(parameters)

        parameters['lighting_engine'] = 'pt'
        conf_interactive.set_parameters(parameters)

    def __translate_frame(self, depsgraph):
        logger.debug("appleseed: Translating frame")

        scene = depsgraph.scene_eval

        asr_scene_props = scene.appleseed

        noise_seed = (asr_scene_props.noise_seed + scene.frame_current) if asr_scene_props.per_frame_noise else asr_scene_props.noise_seed

        width, height = self.__viewport_resolution

        frame_params = {
            'resolution': asr.Vector2i(width, height),
            'camera': "Camera",
            'tile_size': asr.Vector2i(asr_scene_props.tile_size, asr_scene_props.tile_size),
            'filter': asr_scene_props.pixel_filter,
            'filter_size': asr_scene_props.pixel_filter_size,
            'denoiser': asr_scene_props.denoise_mode,
            'noise_seed': noise_seed,
            'skip_denoised': asr_scene_props.skip_denoised,
            'random_pixel_order': asr_scene_props.random_pixel_order,
            'prefilter_spikes': asr_scene_props.prefilter_spikes,
            'spike_threshold': asr_scene_props.spike_threshold,
            'patch_distance_threshold': asr_scene_props.patch_distance_threshold,
            'denoise_scales': asr_scene_props.denoise_scales,
            'mark_invalid_pixels': asr_scene_props.mark_invalid_pixels}

        return frame_params

    def __calc_viewport_resolution(self, depsgraph, context):
        scene = depsgraph.scene_eval
        scale = scene.render.resolution_percentage / 100.0

        if context is not None:
            width = int(context.region.width)
            height = int(context.region.height)
        else:
            width = int(scene.render.resolution_x * scale)
            height = int(scene.render.resolution_y * scale)

        self.__viewport_resolution = [width, height]

    def __set_aovs(self, depsgraph):
        logger.debug("appleseed: Translating AOVs")

        asr_scene_props = depsgraph.scene_eval.appleseed

        aovs = asr.AOVContainer()

        if self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            if asr_scene_props.albedo_aov:
                aovs.insert(asr.AOV('albedo_aov', {}))
            if asr_scene_props.diffuse_aov:
                aovs.insert(asr.AOV('diffuse_aov', {}))
            if asr_scene_props.direct_diffuse_aov:
                aovs.insert(asr.AOV('direct_diffuse_aov', {}))
            if asr_scene_props.direct_glossy_aov:
                aovs.insert(asr.AOV('direct_glossy_aov', {}))
            if asr_scene_props.emission_aov:
                aovs.insert(asr.AOV('emission_aov', {}))
            if asr_scene_props.glossy_aov:
                aovs.insert(asr.AOV('glossy_aov', {}))
            if asr_scene_props.indirect_diffuse_aov:
                aovs.insert(asr.AOV('indirect_diffuse_aov', {}))
            if asr_scene_props.indirect_glossy_aov:
                aovs.insert(asr.AOV('indirect_glossy_aov', {}))
            if asr_scene_props.invalid_samples_aov:
                aovs.insert(asr.AOV('invalid_samples_aov', {}))
            if asr_scene_props.normal_aov:
                aovs.insert(asr.AOV('normal_aov', {}))
            if asr_scene_props.npr_contour_aov:
                aovs.insert(asr.AOV('npr_contour_aov', {}))
            if asr_scene_props.npr_shading_aov:
                aovs.insert(asr.AOV('npr_shading_aov', {}))
            if asr_scene_props.pixel_sample_count_aov:
                aovs.insert(asr.AOV('pixel_sample_count_aov', {}))
            if asr_scene_props.pixel_time_aov:
                aovs.insert(asr.AOV('pixel_time_aov', {}))
            if asr_scene_props.pixel_variation_aov:
                aovs.insert(asr.AOV('pixel_variation_aov', {}))
            if asr_scene_props.position_aov:
                aovs.insert(asr.AOV('position_aov', {}))
            if asr_scene_props.screen_space_velocity_aov:
                aovs.insert(asr.AOV('screen_space_velocity_aov', {}))
            if asr_scene_props.uv_aov:
                aovs.insert(asr.AOV('uv_aov', {}))
            if asr_scene_props.cryptomatte_material_aov:
                aovs.insert(asr.AOV('cryptomatte_material_aov', {}))
            if asr_scene_props.cryptomatte_object_aov:
                aovs.insert(asr.AOV('cryptomatte_object_aov', {}))

        return aovs

    def __set_post_process(self, depsgraph):
        asr_scene_props = depsgraph.scene_eval.appleseed

        for index, stage in enumerate(asr_scene_props.post_processing_stages):
            if stage.model == 'render_stamp_post_processing_stage':
                params = {'order': index, 'format_string': stage.render_stamp}
            else:
                params = {
                    'order': index,
                    'color_map': stage.color_map,
                    'auto_range': stage.auto_range,
                    'range_min': stage.range_min,
                    'range_max': stage.range_max,
                    'add_legend_bar': stage.add_legend_bar,
                    'legend_bar_ticks': stage.legend_bar_ticks,
                    'render_isolines': stage.render_isolines,
                    'line_thickness': stage.line_thickness}

                if stage.color_map == 'custom':
                    params['color_map_file_path'] = stage.color_map_file_path

            post_process = asr.PostProcessingStage(stage.model, stage.name, params)

            logger.debug("Adding Post Process: %s", stage.name)

            self.__frame.post_processing_stages().insert(post_process)

    def __set_render_border_window(self, depsgraph, context=None):
        width, height = self.__viewport_resolution

        if depsgraph.scene_eval.render.use_border and self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            min_x = int(depsgraph.scene_eval.render.border_min_x * width)
            max_x = int(depsgraph.scene_eval.render.border_max_x * width) - 1
            min_y = height - int(depsgraph.scene_eval.render.border_max_y * height)
            max_y = height - int(depsgraph.scene_eval.render.border_min_y * height) - 1

            self.__frame.set_crop_window([min_x, min_y, max_x, max_y])

        else:
            # Interactive render borders
            if context is not None and context.space_data.use_render_border and context.region_data.view_perspective in ('ORTHO', 'PERSP'):
                min_x = int(context.space_data.render_border_min_x * width)
                max_x = int(context.space_data.render_border_max_x * width) - 1
                min_y = height - int(context.space_data.render_border_max_y * height)
                max_y = height - int(context.space_data.render_border_min_y * height) - 1

                self.__frame.set_crop_window([min_x, min_y, max_x, max_y])

            elif depsgraph.scene_eval.render.use_border and context.region_data.view_perspective == 'CAMERA':
                """
                I can't explain how the following code produces the correct render window.
                I basically threw every parameter combination I could think of together 
                until the result looked right.
                """

                zoom = 4 / ((math.sqrt(2) + context.region_data.view_camera_zoom / 50) ** 2)
                frame_aspect_ratio = width / height
                camera_aspect_ratio = calc_film_aspect_ratio(depsgraph.scene_eval)

                if frame_aspect_ratio > 1:
                    camera_width = width / zoom
                    camera_height = camera_width / camera_aspect_ratio
                else:
                    camera_height = height / (zoom * camera_aspect_ratio)
                    camera_width = camera_height * camera_aspect_ratio

                view_offset_x, view_offset_y = context.region_data.view_camera_offset
                view_shift_x = ((view_offset_x * 2) / zoom) * width
                view_shift_y = ((view_offset_y * 2) / zoom) * height
                window_shift_x = (width - camera_width) / 2
                window_shift_y = (height - camera_height) / 2

                window_x_min = int(camera_width * depsgraph.scene_eval.render.border_min_x + window_shift_x - view_shift_x)
                window_x_max = int(camera_width * depsgraph.scene_eval.render.border_max_x + window_shift_x - view_shift_x)
                window_y_min = height - int(camera_height * depsgraph.scene_eval.render.border_max_y + window_shift_y - view_shift_y)
                window_y_max = height - int(camera_height * depsgraph.scene_eval.render.border_min_y + window_shift_y - view_shift_y)

                # Check for coordinates outside the render window.
                min_x = clamp_value(window_x_min, 0, width - 1)
                max_x = clamp_value(window_x_max, 0, width - 1)
                min_y = clamp_value(window_y_min, 0, height - 1)
                max_y = clamp_value(window_y_max, 0, height - 1)

                self.__frame.set_crop_window([min_x, min_y, max_x, max_y])

    def __load_searchpaths(self):
        logger.debug("appleseed: Loading searchpaths")
        paths = self.__project.get_search_paths()

        paths.extend(path for path in self.__asset_handler.searchpaths if path not in paths)

        self.__project.set_search_paths(paths)

    def __calc_initial_positions(self, depsgraph, engine, objects_to_add, lights_to_add):
        logger.debug("appleseed: Setting intial object positions for frame %s", depsgraph.scene_eval.frame_current)

        self.__as_camera_translator.add_cam_xform(engine, 0.0)

        for inst in depsgraph.object_instances:
            if inst.show_self:
                obj = inst.object.original
                if obj.type == 'LIGHT':
                    lights_to_add[obj].add_instance_step(inst.persistent_id[0], inst.matrix_world)
                elif obj.type == 'MESH':
                    objects_to_add[obj].add_instance_step(0.0, inst.persistent_id[0], inst.matrix_world)

    def __calc_motion_steps(self, depsgraph, engine, objects_to_add):
        current_frame = depsgraph.scene_eval.frame_current

        logger.debug("appleseed: Processing motion steps for frame %s", current_frame)

        for index, time in enumerate(self.__all_times[1:]):
            new_frame = current_frame + time
            int_frame = math.floor(new_frame)
            subframe = new_frame - int_frame

            engine.frame_set(int_frame, subframe=subframe)

            if time in self.__cam_times:
                self.__as_camera_translator.add_cam_xform(engine, time)
            
            if time in self.__xform_times:
                for inst in depsgraph.object_instances:
                    if inst.show_self:
                        obj = inst.object.original
                        if obj.type == 'MESH':
                            objects_to_add[obj].add_instance_step(time, inst.persistent_id[0], inst.matrix_world)

            # if time in self.__deform_times:
            #     for translator in objects_to_add.values:
            #         translator.set_deform_key(time, depsgraph, index)
        
        engine.frame_set(current_frame, subframe=0.0)

    # Static utility methods
    @staticmethod
    def __get_sub_frames(scene, shutter_length, samples, times):
        assert samples > 1

        segment_size = shutter_length / (samples - 1)

        for seg in range(0, samples):
            times.update({scene.appleseed.shutter_open + (seg * segment_size)})

    @staticmethod
    def __round_up_pow2(deformation_blur_samples):
        assert (deformation_blur_samples >= 2)
        return 1 << (deformation_blur_samples - 1).bit_length()
