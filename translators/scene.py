#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2014-2018 The appleseedhq Organization
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
from .camera import CameraTranslator, InteractiveCameraTranslator
from .group import GroupTranslator
from .assethandlers import AssetHandler, CopyAssetsAssetHandler
from .object import InstanceTranslator
from .translator import ObjectKey, ProjectExportMode
from .world import WorldTranslator
from ..logger import get_logger
from ..util import Timer, inscenelayer

logger = get_logger()


class SceneTranslator(GroupTranslator):
    """
    Class that translates a Blender scene to an appleseed project.
    """

    #
    # Constants and settings.
    #

    OBJECT_TYPES_TO_IGNORE = {'ARMATURE'}

    #
    # Constructors.
    #

    @classmethod
    def create_project_export_translator(cls, scene, filename):
        """
        Create a scene translator to export the scene to an appleseed project on disk.
        """

        project_dir = os.path.dirname(filename)

        logger.debug("Creating texture and geometry directories in %s", project_dir)

        geometry_dir = os.path.join(project_dir, "_geometry")
        textures_dir = os.path.join(project_dir, "_textures")
        shaders_dir = os.path.join(project_dir, "_shaders")
        archives_dir = os.path.join(project_dir, "_archives")

        if not os.path.exists(geometry_dir):
            os.makedirs(geometry_dir)

        if not os.path.exists(textures_dir):
            os.makedirs(textures_dir)

        if not os.path.exists(shaders_dir):
            os.makedirs(shaders_dir)

        if not os.path.exists(archives_dir):
            os.makedirs(archives_dir)

        logger.debug("Creating project export scene translator, filename: %s", filename)

        asset_handler = CopyAssetsAssetHandler(project_dir, geometry_dir, textures_dir, shaders_dir, archives_dir)

        return cls(
            scene,
            export_mode=ProjectExportMode.PROJECT_EXPORT,
            selected_only=scene.appleseed.export_selected,
            context=None,
            asset_handler=asset_handler)

    @classmethod
    def create_final_render_translator(cls, scene):
        """
        Create a scene translator to export the scene to an in memory appleseed project.
        """

        logger.debug("Creating final render scene translator")

        asset_handler = AssetHandler()

        return cls(
            scene,
            export_mode=ProjectExportMode.FINAL_RENDER,
            selected_only=False,
            context=None,
            asset_handler=asset_handler)

    @classmethod
    def create_interactive_render_translator(cls, context):
        """
        Create a scene translator to export the scene to an in memory appleseed project
        optimized for quick interactive edits.
        """

        logger.debug("Creating interactive render scene translator")

        asset_handler = AssetHandler()

        return cls(
            scene=context.scene,
            export_mode=ProjectExportMode.INTERACTIVE_RENDER,
            selected_only=False,
            context=context,
            asset_handler=asset_handler)

    def __init__(self, scene, export_mode, selected_only, context, asset_handler):
        """
        Constructor. Do not use it to create instances of this class.
        Use the @classmethods instead.
        """

        super(SceneTranslator, self).__init__(scene, export_mode, selected_only, asset_handler)

        self.__selected_only = selected_only

        self.__context = context

        self.__viewport_resolution = None

        # Translators.
        self.__world_translator = None
        self.__camera_translator = None
        self.__group_translators = {}

        self.__project = None

    #
    # Properties.
    #

    @property
    def bl_scene(self):
        """
        Return the Blender scene.
        """
        return self._bl_obj

    @property
    def as_project(self):
        """
        Return the appleseed project.
        """
        return self.__project

    @property
    def as_scene(self):
        """
        Return the appleseed scene.
        """
        return self.__project.get_scene()

    @property
    def selected_only(self):
        return self.__selected_only

    @property
    def camera_translator(self):
        return self.__camera_translator

    #
    # Scene Translation.
    #

    def translate_scene(self):
        """
        Translate the Blender scene to an appleseed project.
        """

        logger.debug("Translating scene %s", self.bl_scene.name)

        prof_timer = Timer()
        prof_timer.start()

        self.__create_project()

        self.__create_translators()

        # Create appleseed entities for world and camera
        if self.__world_translator:
            self.__world_translator.create_entities(self.bl_scene)
        self.__camera_translator.create_entities(self.bl_scene)

        # Create entities for all mesh objects and lights in scene
        self._do_create_entities(self.bl_scene)

        # Create entities for any linked groups (libraries) in the scene
        for x in self.__group_translators.values():
            x.create_entities(self.bl_scene)

        self.__calc_motion_subframes()

        # Insert appleseed entities into the project.
        if self.__world_translator:
            self.__world_translator.flush_entities(self.as_scene)

        self.__camera_translator.flush_entities(self.as_scene)

        self._do_flush_entities(self.__main_assembly)

        for x in self.__group_translators.values():
            x.flush_entities(self.__main_assembly)

        self.__translate_render_settings()
        self.__translate_frame()

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

    # Interactive rendering update functions
    def update_scene(self, scene, context):
        """
        Update the scene during interactive rendering.
        Scene updates are called whenever a parameter changes.
        """

        # Set internal scene reference to current state of Blender scene
        logger.debug("Start scene update")
        self._bl_obj = scene
        self.__context = context

        # Update materials.
        for mat in self._material_translators:
            # Get Blender material
            try:
                bl_mat = bpy.data.materials[str(mat)]
            except:
                logger.debug("Material not found for %s", mat)
                continue

            # Check if base material is updated
            if bl_mat.is_updated or bl_mat.is_updated_data:
                logger.debug("Updating material %s", mat)
                self._material_translators[mat].update(bl_mat, self.__main_assembly, scene)

            # Check if material node tree has been updated
            if bl_mat.appleseed.osl_node_tree is not None:
                if bl_mat.appleseed.osl_node_tree.is_updated:
                    logger.debug("Updating material tree for %s", mat)
                    self._material_translators[mat].update(bl_mat, self.__main_assembly, scene)

        # Update lamp materials
        for mat in self._lamp_material_translators:
            # Get Blender lamp
            try:
                bl_lamp = bpy.data.lamps[str(mat)]
            except:
                logger.debug("Material not found for %s", mat)
                continue
            if bl_lamp.appleseed.osl_node_tree.is_updated or bl_lamp.is_updated:
                logger.debug("Updating material tree for %s", mat)
                self._lamp_material_translators[mat].update(bl_lamp, self.__main_assembly, scene)

        # Update objects
        for translator in self._object_translators:
            try:
                bl_obj = bpy.data.objects[str(translator)]

                if bl_obj.is_updated or bl_obj.is_updated_data:
                    logger.debug("Updating object %s", translator)
                    self._object_translators[translator].update(bl_obj)
            except:
                logger.debug("Object not found for %s", translator)

        for translator in self._dupli_translators:
            try:
                bl_obj = bpy.data.objects[str(translator)]

                if bl_obj.is_updated or bl_obj.is_updated_data:
                    logger.debug("Updating dupli object %s", translator)

                    self._dupli_translators[translator].update(bl_obj, self.bl_scene)
            except Exception as e:
                logger.debug("Dupli object not found for %s, exception: %s", translator, e)

        for translator in self._lamp_translators:
            try:
                bl_lamp = bpy.data.objects[str(translator)]

                if bl_lamp.is_updated or bl_lamp.is_updated_data:
                    logger.debug("Updating lamp %s", translator)
                    self._lamp_translators[translator].update(bl_lamp, self.__main_assembly, scene)
            except:
                logger.debug("Lamp not found for %s", translator)

        if self.bl_scene.is_updated or self.bl_scene.is_updated_data:
            self.__world_translator.update(self.bl_scene, self.as_scene)

        if self.bl_scene.camera.is_updated or self.bl_scene.camera.is_updated_data:
            self.__camera_translator.update(self.as_scene, camera=self.bl_scene.camera, context=self.__context)

        self.__camera_translator.set_transform(0.0)

    def check_view(self, context):
        """
        Check the viewport to see if it has changed camera position or window size.
        For whatever reason, these changes do not trigger an update request so we must check things manually.
        """

        view_update = False
        self.__context = context

        # Check if the camera needs to be updated
        cam_param_update, cam_translate_update = self.__camera_translator.check_for_camera_update(self.bl_scene.camera, self.__context)

        # Check if the frame needs to be updated
        width = int(self.__context.region.width)
        height = int(self.__context.region.height)
        new_viewport_resolution = [width, height]
        if new_viewport_resolution != self.__viewport_resolution:
            view_update = True
            cam_param_update = True

        return view_update, cam_param_update, cam_translate_update

    def update_view(self, view_update, cam_param_update):
        """
        Update the viewport window during interactive rendering.  The viewport update is triggered
        automatically following a scene update, or when the check view function returns true on any of its checks.
        """

        logger.debug("Begin view update")

        if cam_param_update:
            self.__camera_translator.update(self.as_scene)

        if view_update:
            self.__translate_frame()

        self.__camera_translator.set_transform(0.0)

    #
    # Internal methods.
    #

    def __create_project(self):
        """
        Create a default empty project.
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

    def __create_world_translator(self):
        logger.debug("Creating world translator")

        self.__world_translator = WorldTranslator(self.bl_scene, self.asset_handler)

    def __create_translators(self):
        """
        Create translators for each Blender object.  These translators contain all the functions and information
        necessary to convert Blender objects, lights, cameras and materials into equivalent appleseed entities.
        """

        if self.bl_scene.appleseed_sky.env_type != 'none':
            self.__create_world_translator()

        # Create translators for all objects in the scene.
        super(SceneTranslator, self)._create_translators(self.bl_scene)

        # Always create a translator for the active camera even if it is not visible or renderable.
        obj_key = ObjectKey(self.bl_scene.camera)
        logger.debug("Creating camera translator for active camera  %s", obj_key)
        if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            self.__camera_translator = CameraTranslator(self.bl_scene.camera, self.asset_handler)
        else:
            self.__camera_translator = InteractiveCameraTranslator(self.bl_scene.camera, self.__context, self.asset_handler)

        for obj in self.bl_scene.objects:

            # Skip object types that are not renderable.
            if obj.type in SceneTranslator.OBJECT_TYPES_TO_IGNORE:
                logger.debug("Ignoring object %s of type %s", obj.name, obj.type)
                continue

            if obj.hide_render:
                continue

            if self.export_mode == ProjectExportMode.INTERACTIVE_RENDER and obj.hide:
                continue

            if not inscenelayer(obj, self.bl_scene):
                logger.debug("skipping invisible object %s", obj.name)
                continue

            if self.selected_only and not obj.select:
                continue

            obj_key = ObjectKey(obj)

            if obj.type == 'EMPTY':
                if obj.is_duplicator and obj.dupli_type == 'GROUP':
                    group = obj.dupli_group

                    group_key = ObjectKey(group)

                    # Create a translator for the group if needed.
                    if not group_key in self.__group_translators:
                        logger.debug("Creating group translator for group %s", group_key)
                        self.__group_translators[group_key] = GroupTranslator(group, self.export_mode, False, self.asset_handler)

                    # Instance the group into the scene.
                    logger.debug("Creating group instance translator for object %s", obj.name)
                    self._object_translators[obj_key] = InstanceTranslator(obj, self.__group_translators[group_key], self.asset_handler)

    def __calc_motion_subframes(self):
        """Calculates subframes for motion blur.  Each blur type can have it's own segment count, so the final list
        created has every transform time needed.  This way we only have to move the frame set point one time, instead of the dozens
        and dozens of times the old exporter did (yay for progress).
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

            self.bl_scene.frame_set(int_frame, subframe=subframe)

            if time in cam_times:
                self.__camera_translator.set_transform_key(self.bl_scene, time, cam_times)

            if time in xform_times:
                self.set_transform_key(self.bl_scene, time, xform_times)

                for x in self.__group_translators.values():
                    x.set_transform_key(self.bl_scene, time, xform_times)

            if time in deform_times:
                self.set_deform_key(self.bl_scene, time, deform_times)

                for x in self.__group_translators.values():
                    x.set_deform_key(self.bl_scene, time, deform_times)

        self.bl_scene.frame_set(current_frame)

    def __get_subframes(self, shutter_length, samples, times):
        assert samples > 1

        segment_size = shutter_length / (samples - 1)

        for seg in range(0, samples):
            times.update({self.bl_scene.appleseed.shutter_open + (seg * segment_size)})

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

        if self.export_mode == ProjectExportMode.INTERACTIVE_RENDER:
            render_threads = -2
        else:
            render_threads = asr_scene_props.threads if not asr_scene_props.threads_auto else 'auto'

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
                      'rendering_threads': render_threads,
                      'generic_frame_renderer': {'tile_ordering': asr_scene_props.tile_ordering},
                      'progressive_frame_renderer': {'max_samples': number_of_pixels,
                                                     'max_fps': asr_scene_props.interactive_max_fps},
                      'texture_store': {'max_size': asr_scene_props.tex_cache * 1024 * 1024},
                      'light_sampler': {'algorithm': asr_scene_props.light_sampler},
                      'shading_result_framebuffer': "permanent" if asr_scene_props.renderer_passes > 1 else "ephemeral"}

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
                                'dl_low_light_threshold': asr_scene_props.dl_low_light_threshold}
            if not asr_scene_props.max_ray_intensity_unlimited:
                parameters['pt']['max_ray_intensity'] = asr_scene_props.max_ray_intensity
            parameters['pt']['max_diffuse_bounces'] = asr_scene_props.max_diffuse_bounces if not asr_scene_props.max_diffuse_bounces_unlimited else -1
            parameters['pt']['max_glossy_bounces'] = asr_scene_props.max_glossy_brdf_bounces if not asr_scene_props.max_glossy_brdf_bounces_unlimited else -1
            parameters['pt']['max_specular_bounces'] = asr_scene_props.max_specular_bounces if not asr_scene_props.max_specular_bounces_unlimited else -1
            parameters['pt']['max_volume_bounces'] = asr_scene_props.max_volume_bounces if not asr_scene_props.max_volume_bounces_unlimited else -1
            parameters['pt']['max_bounces'] = asr_scene_props.max_bounces if not asr_scene_props.max_bounces_unlimited else -1
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
                                  'path_tracing_rr_min_path_length': asr_scene_props.sppm_pt_rr_start,
                                  'photon_tracing_max_path_length': asr_scene_props.sppm_photon_max_length,
                                  'photon_tracing_rr_min_path_length': asr_scene_props.sppm_photon_rr_start}

        if asr_scene_props.shading_override:
            parameters['shading_engine'] = {'override_shading': {'mode': asr_scene_props.override_mode}}
        conf_final.set_parameters(parameters)
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

        frame_params = {
            'resolution': asr.Vector2i(width, height),
            'camera': self.bl_scene.camera.name,
            'tile_size': asr.Vector2i(asr_scene_props.tile_size, asr_scene_props.tile_size),
            'filter': asr_scene_props.pixel_filter,
            'filter_size': asr_scene_props.pixel_filter_size,
            'denoiser': asr_scene_props.denoise_mode,
            'skip_denoised': asr_scene_props.skip_denoised,
            'random_pixel_order': asr_scene_props.random_pixel_order,
            'prefilter_spikes': asr_scene_props.prefilter_spikes,
            'spike_threshold': asr_scene_props.spike_threshold,
            'patch_distance_threshold': asr_scene_props.patch_distance_threshold,
            'denoise_scales': asr_scene_props.denoise_scales,
            'mark_invalid_pixels': asr_scene_props.mark_invalid_pixels}

        # AOVs
        aovs = asr.AOVContainer()
        if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
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

        # Create and set the frame in the project.
        frame = asr.Frame("beauty", frame_params, aovs)

        if len(asr_scene_props.post_processing_stages) > 0 and self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
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

                frame.post_processing_stages().insert(post_process)

        if self.bl_scene.render.use_border and self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            min_x = int(self.bl_scene.render.border_min_x * width)
            max_x = int(self.bl_scene.render.border_max_x * width) - 1
            min_y = height - int(self.bl_scene.render.border_max_y * height)
            max_y = height - int(self.bl_scene.render.border_min_y * height) - 1
            frame.set_crop_window([min_x, min_y, max_x, max_y])

        elif self.export_mode == ProjectExportMode.INTERACTIVE_RENDER and self.__context.space_data.use_render_border \
                and self.__context.region_data.view_perspective in ('ORTHO', 'PERSP'):
            min_x = int(self.__context.space_data.render_border_min_x * width)
            max_x = int(self.__context.space_data.render_border_max_x * width) - 1
            min_y = height - int(self.__context.space_data.render_border_max_y * height)
            max_y = height - int(self.__context.space_data.render_border_min_y * height) - 1
            frame.set_crop_window([min_x, min_y, max_x, max_y])

        self.__project.set_frame(frame)

    def __load_searchpaths(self):
        paths = self.__project.get_search_paths()

        # Load any search paths from asset handler
        paths.extend(x for x in self.asset_handler.searchpaths if x not in paths)

        self.__project.set_search_paths(paths)

    @staticmethod
    def __round_up_pow2(x):
        assert (x >= 2)
        return 1 << (x - 1).bit_length()
