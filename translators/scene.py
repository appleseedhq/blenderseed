#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 The appleseedhq Organization
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

import appleseed as asr
import bpy

from .assethandlers import AssetHandler, CopyAssetsAssetHandler
from .cameras import RenderCameraTranslator
from .lamps import LampInstanceTranslator, LampTranslator
from .material import MaterialTranslator
from .nodetree import NodeTreeTranslator
from .objects import ArchiveAssemblyTranslator, MeshInstanceTranslator, MeshTranslator
from .textures import TextureTranslator
from .utilites import ProjectExportMode
from .world import WorldTranslator
from ..logger import get_logger
from ..utils.util import Timer

logger = get_logger()

objects_to_ignore = ('ARMATURE', 'CURVE', 'CAMERA')


class SceneTranslator(object):
    """
    Translates a Blender scene into an appleseed project.
    """

    # Constructors.
    @classmethod
    def create_project_export_translator(cls, engine, depsgraph):
        """
        Create a scene translator to export the scene to an appleseed project on disk.
        """

        project_dir = os.path.dirname(depsgraph.scene.appleseed.export_path)

        logger.debug("Creating texture and geometry directories in %s", project_dir)

        geometry_dir = os.path.join(project_dir, "_geometry")
        textures_dir = os.path.join(project_dir, "_textures")

        if not os.path.exists(geometry_dir):
            os.makedirs(geometry_dir)

        if not os.path.exists(textures_dir):
            os.makedirs(textures_dir)

        logger.debug("Creating project export scene translator, filename: %s", depsgraph.scene.appleseed.export_path)

        asset_handler = CopyAssetsAssetHandler(project_dir, geometry_dir, textures_dir)

        return cls(engine=engine,
                   depsgraph=depsgraph,
                   export_mode=ProjectExportMode.PROJECT_EXPORT,
                   selected_only=depsgraph.scene.appleseed.export_selected,
                   context=None,
                   asset_handler=asset_handler)

    @classmethod
    def create_final_render_translator(cls, engine, depsgraph):
        """
        Create a scene translator to export the scene to an in memory appleseed project.
        """

        logger.debug("Creating final render scene translator")

        asset_handler = AssetHandler()

        return cls(engine=engine,
                   depsgraph=depsgraph,
                   export_mode=ProjectExportMode.FINAL_RENDER,
                   selected_only=False,
                   context=None,
                   asset_handler=asset_handler)

    @classmethod
    def create_interactive_render_translator(cls, engine, context):
        """
        Create a scene translator to export the scene to an in memory appleseed project
        optimized for quick interactive edits.
        """

        logger.debug("Creating interactive render scene translator")

        asset_handler = AssetHandler()

        return cls(engine=engine,
                   depsgraph=context.depsgraph,
                   export_mode=ProjectExportMode.INTERACTIVE_RENDER,
                   selected_only=False,
                   context=context,
                   asset_handler=asset_handler)

    def __init__(self, engine, depsgraph, export_mode, selected_only, context, asset_handler):
        """
        Constructor. Do not use it to create instances of this class.
        Use the @classmethods instead.
        """

        self.__engine = engine
        self.__depsgraph = depsgraph
        self.__asset_handler = asset_handler
        self.__export_mode = export_mode
        self.__selected_only = selected_only
        self.__context = context

        # Blender datablock lists.
        self.__bl_obeject_datablocks = []
        self.__bl_material_datablocks = []
        self.__bl_nodetree_datablocks = []

        # Translators.
        self.__world_translator = None
        self.__camera_translator = None
        self.__lamp_translators = {}
        self.__object_translators = {}
        self.__instance_translators = {}
        self.__instance_sources = {}
        self.__material_translators = {}
        self.__nodetree_translators = {}
        self.__texture_translators = {}

        self.__project = None
        self.__frame = None

    # Properties.
    @property
    def bl_engine(self):
        return self.__engine

    @property
    def bl_depsgraph(self):
        return self.__depsgraph

    @property
    def bl_scene(self):
        return self.__depsgraph.scene

    @property
    def as_project(self):
        return self.__project

    @property
    def as_scene(self):
        return self.__project.get_scene()

    @property
    def main_assembly(self):
        return self.__main_assembly

    @property
    def asset_handler(self):
        return self.__asset_handler

    @property
    def selected_only(self):
        return self.__selected_only

    @property
    def export_mode(self):
        return self.__export_mode

    @property
    def all_translators(self):
        return[self.__lamp_translators,
               self.__object_translators,
               self.__instance_translators,
               self.__instance_sources,
               self.__material_translators,
               self.__nodetree_translators,
               self.__texture_translators]

    def translate_scene(self):
        """
        Translate the Blender scene to an appleseed project.
        """

        logger.debug("Translating scene %s", self.bl_scene.name)

        prof_timer = Timer()
        prof_timer.start()

        self.__create_project()

        self.__translate_render_settings()
        self.__translate_frame()

        self.__create_world_translator()

        self.__create_camera_translator()

        self.__bl_material_datablocks = self.__parse_material_datablocks()

        self.__bl_nodetree_datablocks = self.__parse_nodetree_datablocks()

        self.__bl_obeject_datablocks = self.__parse_object_datablocks()

        self.__create_translators()

        if self.export_mode == ProjectExportMode.FINAL_RENDER:
            self.__create_final_render_instancers()

        if self.__world_translator is not None:
            self.__world_translator.create_entities(self.bl_scene)

        self.__camera_translator.create_entities(self.bl_scene)

        for translators in self.all_translators:
            for translator in translators.values():
                translator.create_entities(self.bl_scene)

        self.__calc_motion()

        for translators in self.all_translators:
            for translator in translators.values():
                translator.flush_entities(self.main_assembly, self.as_project)

        if self.__world_translator != None:
            self.__world_translator.flush_entities(self.as_scene, self.main_assembly, self.as_project)

        self.__camera_translator.flush_entities(self.as_scene, self.main_assembly, self.as_project)

        self.__load_searchpaths()

        prof_timer.stop()
        logger.debug("Scene translated in %f seconds.", prof_timer.elapsed())

    def write_project(self, filename):
        """
        Write the appleseed project out to disk.
        """

        asr.ProjectFileWriter().write(
            self.as_project,
            filename,
            asr.ProjectFileWriterOptions.OmitWritingGeometryFiles | asr.ProjectFileWriterOptions.OmitHandlingAssetFiles)

    # Internal methods.
    def __create_project(self):
        """
        Creates the base project.
        """

        logger.debug("Creating appleseed project")

        self.__project = asr.Project(self.bl_scene.name)

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
        logger.debug("Creating default material")

        surface_shader = asr.SurfaceShader("diagnostic_surface_shader", "__default_surface_shader", {'mode': 'facing_ratio'})
        material = asr.Material('generic_material', "__default_material", {'surface_shader': '__default_surface_shader'})

        self.__main_assembly.surface_shaders().insert(surface_shader)
        self.__main_assembly.materials().insert(material)

    def __create_null_material(self):
        logger.debug("Creating null material")

        material = asr.Material('generic_material', "__null_material", {})
        self.__main_assembly.materials().insert(material)

    def __translate_render_settings(self):
        """
        Convert render settings (AA samples, lighting engine, ...) to appleseed properties.
        """

        logger.debug("Translating render settings")

        scene = self.bl_scene
        asr_scene_props = scene.appleseed

        conf_final = self.as_project.configurations()['final']
        conf_interactive = self.as_project.configurations()['interactive']

        lighting_engine = asr_scene_props.lighting_engine if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER else 'pt'

        if self.__context:
            number_of_pixels = int(self.__context.region.width) * int(self.__context.region.height) * asr_scene_props.interactive_max_samples
        else:
            number_of_pixels = -1

        tile_renderer = 'adaptive' if asr_scene_props.pixel_sampler == 'adaptive' else 'generic'
        pixel_renderer = '' if asr_scene_props.pixel_sampler == 'adaptive' else 'uniform'

        parameters = {'uniform_pixel_renderer': {'decorrelate_pixels': True if asr_scene_props.decorrelate_pixels else False,
                                                 'force_antialiasing': True if asr_scene_props.force_aa else False,
                                                 'samples': asr_scene_props.samples},
                      'adaptive_tile_renderer': {'min_samples': asr_scene_props.adaptive_min_samples,
                                                 'noise_threshold': asr_scene_props.adaptive_noise_threshold,
                                                 'batch_size': asr_scene_props.adaptive_batch_size,
                                                 'max_samples': asr_scene_props.adaptive_max_samples},
                      'use_embree': asr_scene_props.use_embree,
                      'pixel_renderer': pixel_renderer,
                      'lighting_engine': lighting_engine,
                      'tile_renderer': tile_renderer,
                      'passes': asr_scene_props.renderer_passes,
                      'generic_frame_renderer': {'tile_ordering': asr_scene_props.tile_ordering},
                      'progressive_frame_renderer': {'max_samples': number_of_pixels,
                                                     'max_fps': asr_scene_props.interactive_max_fps},
                      'light_sampler': {'algorithm': asr_scene_props.light_sampler,
                                        'enable_light_importance_sampling': asr_scene_props.enable_light_importance_sampling},
                      'shading_result_framebuffer': "permanent" if asr_scene_props.renderer_passes > 1 else "ephemeral"}

        if self.export_mode != ProjectExportMode.PROJECT_EXPORT:
            if self.export_mode == ProjectExportMode.INTERACTIVE_RENDER:
                render_threads = -2
            else:
                render_threads = asr_scene_props.threads if not asr_scene_props.threads_auto else 'auto'
            parameters['rendering_threads'] = render_threads
            parameters['texture_store'] = {'max_size': asr_scene_props.tex_cache * 1024 * 1024}

        if lighting_engine == 'pt':
            parameters['pt'] = {'enable_ibl': True if asr_scene_props.enable_ibl else False,
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
            parameters['sppm'] = {'alpha': asr_scene_props.sppm_alpha,
                                  'dl_mode': asr_scene_props.sppm_dl_mode,
                                  'enable_caustics': "true" if asr_scene_props.enable_caustics else "false",
                                  'env_photons_per_pass': asr_scene_props.sppm_env_photons,
                                  'initial_radius': asr_scene_props.sppm_initial_radius,
                                  'light_photons_per_pass': asr_scene_props.sppm_light_photons,

                                  # Leave at 0 for now - not in appleseed.studio GUI
                                  'max_path_length': 0,
                                  'max_photons_per_estimate': asr_scene_props.sppm_max_per_estimate,
                                  'path_tracing_max_path_length': asr_scene_props.sppm_pt_max_length,
                                  'path_tracing_max_ray_intensity': asr_scene_props.sppm_pt_max_ray_intensity,
                                  'path_tracing_rr_min_path_length': asr_scene_props.sppm_pt_rr_start,
                                  'photon_tracing_max_path_length': asr_scene_props.sppm_photon_max_length,
                                  'photon_tracing_rr_min_path_length': asr_scene_props.sppm_photon_rr_start}

        if asr_scene_props.shading_override:
            parameters['shading_engine'] = {'override_shading': {'mode': asr_scene_props.override_mode}}

        conf_final.set_parameters(parameters)

        parameters['lighting_engine'] = 'pt'
        conf_interactive.set_parameters(parameters)

    def __translate_frame(self):
        """
        Convert image related settings (resolution, crop windows, AOVs, ...) to appleseed.
        """

        logger.debug("Translating frame")

        asr_scene_props = self.bl_scene.appleseed
        scale = self.bl_scene.render.resolution_percentage / 100.0
        if self.__context:
            width = int(self.__context.region.width)
            height = int(self.__context.region.height)
            self.__viewport_resolution = [width, height]
        else:
            width = int(self.bl_scene.render.resolution_x * scale)
            height = int(self.bl_scene.render.resolution_y * scale)

        noise_seed = (asr_scene_props.noise_seed + self.bl_scene.frame_current) if asr_scene_props.per_frame_noise else asr_scene_props.noise_seed

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

        if self.bl_scene.render.use_border and self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            min_x = int(self.bl_scene.render.border_min_x * width)
            max_x = int(self.bl_scene.render.border_max_x * width) - 1
            min_y = height - int(self.bl_scene.render.border_max_y * height)
            max_y = height - int(self.bl_scene.render.border_min_y * height) - 1
            self.__frame.set_crop_window([min_x, min_y, max_x, max_y])

        elif self.export_mode == ProjectExportMode.INTERACTIVE_RENDER and self.__context.space_data.use_render_border \
                and self.__context.region_data.view_perspective in ('ORTHO', 'PERSP'):
            min_x = int(self.__context.space_data.render_border_min_x * width)
            max_x = int(self.__context.space_data.render_border_max_x * width) - 1
            min_y = height - int(self.__context.space_data.render_border_max_y * height)
            max_y = height - int(self.__context.space_data.render_border_min_y * height) - 1
            self.__frame.set_crop_window([min_x, min_y, max_x, max_y])

        if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            aovs = self.__set_aovs()

        # Create and set the frame in the project.
        self.__frame = asr.Frame("beauty",
                                 frame_params,
                                 aovs)

        self.__project.set_frame(self.__frame)
        self.__frame = self.as_project.get_frame()

        if len(asr_scene_props.post_processing_stages) > 0 and self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            self.__set_post_process()

    def __set_aovs(self):
        aovs = asr.AOVContainer()

        if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            asr_scene_props = self.bl_scene.appleseed

            if asr_scene_props.diffuse_aov:
                aovs.insert(asr.AOV('diffuse_aov', {}))
            if asr_scene_props.direct_diffuse_aov:
                aovs.insert(asr.AOV('direct_diffuse_aov', {}))
            if asr_scene_props.indirect_diffuse_aov:
                aovs.insert(asr.AOV('indirect_diffuse_aov', {}))
            if asr_scene_props.glossy_aov:
                aovs.insert(asr.AOV('glossy_aov', {}))
            if asr_scene_props.direct_glossy_aov:
                aovs.insert(asr.AOV('direct_glossy_aov', {}))
            if asr_scene_props.indirect_glossy_aov:
                aovs.insert(asr.AOV('indirect_glossy_aov', {}))
            if asr_scene_props.normal_aov:
                aovs.insert(asr.AOV('normal_aov', {}))
            if asr_scene_props.position_aov:
                aovs.insert(asr.AOV('position_aov', {}))
            if asr_scene_props.uv_aov:
                aovs.insert(asr.AOV('uv_aov', {}))
            if asr_scene_props.depth_aov:
                aovs.insert(asr.AOV('depth_aov', {}))
            if asr_scene_props.pixel_time_aov:
                aovs.insert(asr.AOV('pixel_time_aov', {}))
            if asr_scene_props.invalid_samples_aov:
                aovs.insert(asr.AOV('invalid_samples_aov', {}))
            if asr_scene_props.pixel_sample_count_aov:
                aovs.insert(asr.AOV('pixel_sample_count_aov', {}))
            if asr_scene_props.pixel_variation_aov:
                aovs.insert(asr.AOV('pixel_variation_aov', {}))
            if asr_scene_props.albedo_aov:
                aovs.insert(asr.AOV('albedo_aov', {}))
            if asr_scene_props.emission_aov:
                aovs.insert(asr.AOV('emission_aov', {}))
            if asr_scene_props.npr_shading_aov:
                aovs.insert(asr.AOV('npr_shading_aov', {}))
            if asr_scene_props.npr_contour_aov:
                aovs.insert(asr.AOV('npr_contour_aov', {}))

        return aovs

    def __set_post_process(self):
        asr_scene_props = self.bl_scene.appleseed

        for index, stage in enumerate(asr_scene_props.post_processing_stages):
            if stage.model == 'render_stamp_post_processing_stage':
                params = {'order': index,
                          'format_string': stage.render_stamp}
            else:
                params = {'order': index,
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

            post_process = asr.PostProcessingStage(stage.model,
                                                   stage.name,
                                                   params)

            self.__frame.post_processing_stages().insert(post_process)

    def __create_world_translator(self):
        if self.bl_scene.world.appleseed_sky.env_type != 'none':
            self.__world_translator = WorldTranslator(self.bl_scene.world,
                                                      self.asset_handler)

            if self.bl_scene.world.appleseed_sky.env_type in ('latlong_map', 'mirrorball_map'):
                tex_key = self.bl_scene.world.appleseed_sky.env_tex.name_full
                if tex_key not in self.__texture_translators:
                    self.__texture_translators[tex_key] = TextureTranslator(self.bl_scene.world.appleseed_sky.env_tex,
                                                                            self.bl_scene.world.appleseed_sky.env_tex_colorspace,
                                                                            self.asset_handler)

    def __create_camera_translator(self):
        if self.bl_scene.camera is not None:
            camera = self.bl_depsgraph.objects[self.bl_scene.camera.name_full]
            logger.debug("Creating camera translator for active camera")
            if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
                self.__camera_translator = RenderCameraTranslator(camera,
                                                                  self.asset_handler)
            else:
                raise NotImplementedError()

            if camera.data.appleseed.diaphragm_map is not None:
                tex_key = camera.data.appleseed.diaphragm_map.name_full
                if tex_key not in self.__texture_translators:
                    self.__texture_translators[tex_key] = TextureTranslator(camera.data.appleseed.diaphragm_map,
                                                                            camera.data.appleseed.diaphragm_map_colorspace,
                                                                            self.asset_handler)

    def __calc_motion(self):
        """Calculates subframes for motion blur.  Each blur type can have its own segment count, so the final list
        created has every transform time needed.  This way we only have to move the frame set point (with the associated
        depsgraph recalculation) one time.
        """
        cam_times = {0.0}
        xform_times = {0.0}
        deform_times = {0.0}

        if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            shutter_length = self.bl_scene.appleseed.shutter_close - self.bl_scene.appleseed.shutter_open

            if self.bl_scene.appleseed.enable_camera_blur:
                self.__get_subframes(shutter_length, self.bl_scene.appleseed.camera_blur_samples, cam_times)

            if self.bl_scene.appleseed.enable_object_blur:
                self.__get_subframes(shutter_length, self.bl_scene.appleseed.object_blur_samples, xform_times)

            if self.bl_scene.appleseed.enable_deformation_blur:
                self.__get_subframes(shutter_length, self.__round_up_pow2(self.bl_scene.appleseed.deformation_blur_samples), deform_times)

        # Merge all subframe times
        all_times = set()
        all_times.update(cam_times)
        all_times.update(xform_times)
        all_times.update(deform_times)
        all_times = sorted(list(all_times))
        current_frame = self.bl_scene.frame_current

        for time in all_times:
            new_frame = current_frame + time
            int_frame = math.floor(new_frame)
            subframe = new_frame - int_frame

            self.bl_engine.frame_set(int_frame, subframe=subframe)

            logger.debug("Processing transforms for frame %s", self.bl_scene.frame_current)

            if time in cam_times:
                self.__camera_translator.set_xform_step(time)

            if time in xform_times:
                for inst in self.bl_depsgraph.object_instances:
                    if inst.is_instance:
                        source_key = inst.instance_object.name_full
                        parent_key = inst.parent.name_full
                        inst_key = f"{source_key}|{parent_key}|{inst.persistent_id[0]}"
                        try:
                            self.__instance_translators[inst_key].set_xform_step(time, inst.matrix_world)
                        except Exception as e:
                            print(str(e))
                    else:
                        if inst.show_self:
                            obj = inst.object
                            if obj.type == 'MESH' or (obj.type == 'EMPTY' and obj.appleseed.object_export == "archive_assembly"):
                                try:
                                    self.__object_translators[obj.name_full].set_xform_step(time)
                                except Exception as e:
                                    print(str(e))

            if time in deform_times:
                logger.debug("Processing deformations for frame %s", self.bl_scene.frame_current)

                for translator in self.__object_translators.values():
                    translator.set_deform_key(time, self.bl_depsgraph, all_times)
                for translator in self.__instance_sources.values():
                    translator.set_deform_key(time, self.bl_depsgraph, all_times)

        self.bl_engine.frame_set(current_frame, subframe=0.0)

    def __get_subframes(self, shutter_length, samples, times):
        assert samples > 1

        segment_size = shutter_length / (samples - 1)

        for seg in range(0, samples):
            times.update({self.bl_scene.appleseed.shutter_open + (seg * segment_size)})

    def __parse_material_datablocks(self):
        """
        Parses the material blocks present in the evaluated depsgraph and returns them in a list
        :return: List of Blender material data blocks
        """
        logger.debug("Parsing Material Datablocks")

        mat_blocks = []

        for block in self.bl_depsgraph.ids:
            if isinstance(block, bpy.types.Material):
                mat_blocks.append(block)

        return mat_blocks

    def __parse_nodetree_datablocks(self):
        """
        Parses the node group blocks present in the evaluated depsgraph and returns them in a list
        :return: List of Blender node group data blocks
        """
        logger.debug("Parsing Nodetree Datablocks")

        nodetree_blocks = []

        for block in self.bl_depsgraph.ids:
            if isinstance(block, bpy.types.Material):
                if block.appleseed.osl_node_tree is not None and block.appleseed.mode == 'surface':
                    nodetree_blocks.append(block.appleseed.osl_node_tree)
            if isinstance(block, bpy.types.Light):
                if block.appleseed.osl_node_tree is not None:
                    nodetree_blocks.append(block.appleseed.osl_node_tree)

        return nodetree_blocks

    def __parse_object_datablocks(self):
        object_blocks = []

        for inst in self.bl_depsgraph.object_instances:
            if inst.show_self and not inst.is_instance:
                obj = inst.object
                if obj.type not in objects_to_ignore and len(obj.data.polygons) > 0:
                    object_blocks.append(obj)

        return object_blocks

    def __create_translators(self):
        """
        Creates appleseed translators for all the 'real' object, lamps and materials in the scene
        :return: None
        """
        for mat in self.__bl_material_datablocks:
            mat_key = mat.name_full
            self.__material_translators[mat_key] = MaterialTranslator(mat)

        for tree in self.__bl_nodetree_datablocks:
            tree_key = tree.name_full
            self.__nodetree_translators[tree_key] = NodeTreeTranslator(tree, self.asset_handler)

        for obj in self.__bl_obeject_datablocks:
            obj_key = obj.name_full
            if obj.appleseed.object_export == "archive_assembly":
                self.__object_translators[obj_key] = ArchiveAssemblyTranslator(obj, self.asset_handler)
            elif obj.type == 'MESH':
                self.__object_translators[obj_key] = MeshTranslator(obj, self.export_mode, self.asset_handler)
                if obj.appleseed.object_alpha_texture is not None:
                    tex_key = obj.appleseed.object_alpha_texture.name_full
                    if tex_key not in self.__texture_translators:
                        self.__texture_translators[tex_key] = TextureTranslator(obj.appleseed.object_alpha_texture,
                                                                                obj.appleseed.object_alpha_texture_colorspace,
                                                                                self.asset_handler)

            elif obj.type == 'LIGHT':
                self.__lamp_translators[obj_key] = LampTranslator(obj, self.asset_handler)
                if obj.data.appleseed.radiance_use_tex and obj.data.appleseed.radiance_tex is not None:
                    tex_key = obj.data.appleseed.radiance_tex.name_full
                    if tex_key not in self.__texture_translators:
                        self.__texture_translators[tex_key] = TextureTranslator(obj.data.appleseed.radiance_tex,
                                                                                obj.data.appleseed.radiance_tex_color_space,
                                                                                self.asset_handler)

                if obj.data.appleseed.radiance_multiplier_use_tex and obj.data.appleseed.radiance_multiplier_tex is not None:
                    tex_key = obj.data.appleseed.radiance_multiplier_tex.name_full
                    if tex_key not in self.__texture_translators:
                        self.__texture_translators[tex_key] = TextureTranslator(obj.data.appleseed.radiance_multiplier_tex,
                                                                                obj.data.appleseed.radiance_multiplier_tex_color_space,
                                                                                self.asset_handler)

    def __create_final_render_instancers(self):
        """
        Creates translators for each mesh/lamp and instance of a lamp/object that was created via a particle system
        or dupli item.  For final rendering all instances are placed in a single level dictionary in order to make
        it easier to assign xform blur steps later on.
        :return: None
        """
        for inst in self.bl_depsgraph.object_instances:
            if inst.is_instance:
                source_key = inst.instance_object.name_full
                parent_key = inst.parent.name_full
                inst_key = f"{source_key}|{parent_key}|{inst.persistent_id[0]}"
                if inst.instance_object.type == 'MESH':
                    self.__instance_translators[inst_key] = MeshInstanceTranslator(inst_key,
                                                                                   source_key)

                    if source_key not in self.__object_translators:
                        self.__instance_sources[source_key] = MeshTranslator(inst.instance_object,
                                                                             self.export_mode,
                                                                             self.asset_handler,
                                                                             is_inst_source=True)
                    else:
                        self.__object_translators[source_key].add_instance()

                elif inst.instance_object.type == 'LIGHT':
                    self.__instance_translators[inst_key] = LampInstanceTranslator(inst.instance_object,
                                                                                   self.asset_handler,
                                                                                   inst_key,
                                                                                   inst.matrix_world.copy())

    def __load_searchpaths(self):
        paths = self.as_project.get_search_paths()

        paths.extend(path for path in self.asset_handler.searchpaths if path not in paths)

        self.as_project.set_search_paths(paths)

    @staticmethod
    def __round_up_pow2(x):
        assert (x >= 2)
        return 1 << (x - 1).bit_length()
