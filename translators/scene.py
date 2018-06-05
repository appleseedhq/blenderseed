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

import os

import appleseed as asr

from .camera import CameraTranslator
from .group import GroupTranslator
from .object import InstanceTranslator
from .translator import ObjectKey, ProjectExportMode
from .world import WorldTranslator
from ..util import get_osl_search_paths, Timer, inscenelayer

from ..logger import get_logger

logger = get_logger()


class SceneTranslator(GroupTranslator):
    '''
    Class that translates a Blender scene to an appleseed project.
    '''

    #
    # Constants and settings.
    #

    OBJECT_TYPES_TO_IGNORE = {'ARMATURE'}

    #
    # Constructors.
    #

    @classmethod
    def create_project_export_translator(cls, scene, filename):
        '''
        Create a scene translator to export the scene to an appleseed project on disk.
        '''

        project_dir = os.path.dirname(filename)

        logger.debug("Creating texture and geometry directories in %s", project_dir)

        geometry_dir = os.path.join(project_dir, "_geometry")
        textures_dir = os.path.join(project_dir, "_textures")

        if not os.path.exists(geometry_dir):
            os.makedirs(geometry_dir)

        if not os.path.exists(textures_dir):
            os.makedirs(textures_dir)

        logger.debug("Creating project export scene translator, filename: %s", filename)

        return cls(
            scene,
            export_mode=ProjectExportMode.PROJECT_EXPORT,
            selected_only=False,
            geometry_dir=geometry_dir,
            textures_dir=textures_dir)

    @classmethod
    def create_final_render_translator(cls, scene):
        '''
        Create a scene translator to export the scene to an in memory appleseed project.
        '''

        logger.debug("Creating final render scene translator")

        return cls(
            scene,
            export_mode=ProjectExportMode.FINAL_RENDER,
            selected_only=False,
            geometry_dir=None,
            textures_dir=None)

    @classmethod
    def create_interactive_render_translator(cls, scene):
        '''
        Create a scene translator to export the scene to an in memory appleseed project
        optimized for quick interactive edits.
        '''

        logger.debug("Creating final render scene translator")

        return cls(
            scene,
            export_mode=ProjectExportMode.INTERACTIVE_RENDER,
            selected_only=False,
            geometry_dir=None,
            textures_dir=None)

    def __init__(self, scene, export_mode, selected_only, geometry_dir, textures_dir):
        '''
        Constructor. Do not use it to create instances of this class.
        Use instead SceneTranslator.create_project_export_translator() or
        The other @classmethods.
        '''

        super(SceneTranslator, self).__init__(scene, export_mode, geometry_dir, textures_dir)

        self.__selected_only = selected_only

        # Translators.
        self.__world_translator = None
        self.__camera_translators = {}
        self.__group_translators = {}

        self.__project = None

    #
    # Properties.
    #

    @property
    def bl_scene(self):
        return self._bl_obj

    @property
    def as_project(self):
        '''
        Return the appleseed project.
        '''
        return self.__project

    @property
    def as_scene(self):
        '''
        Return the appleseed scene.
        '''
        return self.__project.get_scene()

    @property
    def selected_only(self):
        return self.__selected_only

    #
    # Scene Translation.
    #

    def translate_scene(self):
        '''
        Translate the Blender scene to an appleseed project.
        '''

        logger.debug("Translating scene %s", self.bl_scene.name)

        prof_timer = Timer()
        prof_timer.start()

        self.__create_project()

        self.__translate_render_settings()
        self.__translate_frame()

        self.__create_translators()

        # Create appleseed entities.
        if self.__world_translator:
            self.__world_translator.create_entities(self.bl_scene)

        for x in self.__camera_translators.values():
            x.create_entities(self.bl_scene)

        self._do_create_entities(self.bl_scene)

        for x in self.__group_translators.values():
            x.create_entities(self.bl_scene)

        # Insert appleseed entities into the project.
        if self.__world_translator:
            self.__world_translator.flush_entities(self.as_scene)

        for x in self.__camera_translators.values():
            x.flush_entities(self.as_scene)

        self._do_flush_entities(self.__main_assembly)

        for x in self.__group_translators.values():
            x.flush_entities(self.__main_assembly)

        prof_timer.stop()
        logger.debug("Scene translated in %f seconds.", prof_timer.elapsed())

    def write_project(self, filename):
        '''Write the appleseed project.'''

        asr.ProjectFileWriter().write(
            self.as_project,
            filename,
            asr.ProjectFileWriterOptions.OmitWritingGeometryFiles | asr.ProjectFileWriterOptions.OmitHandlingAssetFiles)

    #
    # Internal methods.
    #

    def __create_translators(self):
        """
        Create translators for each Blender object.  These translators contain all the functions and information
        necessary to convert Blender objects, lights, cameras and materials into equivalent appleseed entities.
        """
        if self.bl_scene.appleseed_sky.env_type != 'none':
            self.__create_world_translator()

        # Create translators for all objects in the scene.

        super(SceneTranslator, self)._create_translators()

        # Always create a translator for the active camera even if it is not visible or renderable.

        obj_key = ObjectKey(self.bl_scene.camera)
        logger.debug("Creating camera translator for active camera  %s", obj_key)
        self.__camera_translators[obj_key] = CameraTranslator(self.bl_scene.camera)

        for obj in self.bl_scene.objects:

            # Skip object types that are not renderable.
            if obj.type in SceneTranslator.OBJECT_TYPES_TO_IGNORE:
                logger.debug("Ignoring object %s of type %s", obj.name, obj.type)
                continue

            if obj.hide_render:
                continue

            if not inscenelayer(obj, self.bl_scene):
                logger.debug("skipping invisible object %s", obj.name)
                continue

            if self.selected_only and not obj.select:
                continue

            obj_key = ObjectKey(obj)

            if obj.type == 'CAMERA':
                if not obj_key in self.__camera_translators:
                    logger.debug("Creating camera translator for camera %s", obj_key)
                    self.__camera_translators[obj_key] = CameraTranslator(obj)

            elif obj.type == 'EMPTY':
                if obj.is_duplicator and obj.dupli_type == 'GROUP':
                    group = obj.dupli_group

                    group_key = ObjectKey(group)

                    # Create a translator for the group if needed.
                    if not group_key in self.__group_translators:
                        logger.debug("Creating group translator for group %s", group_key)
                        self.__group_translators[group_key] = GroupTranslator(group, self.export_mode, self.geometry_dir, self.textures_dir)

                    # Instance the group into the scene.
                    logger.debug("Creating group instance translator for object %s", obj.name)
                    self._object_translators[obj_key] = InstanceTranslator(obj, self.__group_translators[group_key])

    def __create_world_translator(self):
        logger.debug("Creating world translator")

        self.__world_translator = WorldTranslator(self.bl_scene)

    def __create_project(self):
        '''Create a default empty project.'''

        logger.debug("Creating appleseed project")

        self.__project = asr.Project(self.bl_scene.name)

        # Render settings.
        self.__project.add_default_configurations()

        # Create the scene.
        self.__project.set_scene(asr.Scene())

        # Add OSL shader directories to search paths.
        tool_dir, shader_directories = get_osl_search_paths()
        paths = self.__project.get_search_paths()
        paths.extend(x for x in shader_directories)
        self.__project.set_search_paths(paths)

        # Create the main assembly.
        self.__project.get_scene().assemblies().insert(asr.Assembly("assembly", {}))
        self.__main_assembly = self.__project.get_scene().assemblies()["assembly"]

        # Instance the main assembly.
        assembly_inst = asr.AssemblyInstance("assembly_inst", {}, "assembly")
        assembly_inst.transform_sequence().set_transform(0.0, asr.Transformd(asr.Matrix4d.identity()))
        self.__project.get_scene().assembly_instances().insert(assembly_inst)

        # Export default material for objects without a node tree
        self.__create_default_material()

    def __create_default_material(self):
        logger.debug("Creating default material")

        surface_shader = asr.SurfaceShader("diagnostic_surface_shader", "default_surface_shader", {'mode': 'facing_ratio'})
        material = asr.Material('generic_material', "default_material", {'surface_shader': 'default_surface_shader'})

        self.__main_assembly.surface_shaders().insert(surface_shader)
        self.__main_assembly.materials().insert(material)

    def __translate_render_settings(self):
        '''
        Convert render settings (AA samples, lighting engine, ...) to appleseed properties.
        '''

        logger.debug("Translating render settings")

        scene = self.bl_scene
        asr_scene_props = scene.appleseed

        conf_final = self.as_project.configurations()['final']
        conf_interactive = self.as_project.configurations()['interactive']

        parameters = {'uniform_pixel_sampler': {'decorrelate_pixels': True if asr_scene_props.decorrelate_pixels else False,
                                                'force_antialiasing': True if asr_scene_props.force_aa else False,
                                                'samples': asr_scene_props.sampler_max_samples},
                      'pixel_renderer': asr_scene_props.pixel_sampler,
                      'lighting_engine': asr_scene_props.lighting_engine,
                      'generic_frame_renderer': {'passes': asr_scene_props.renderer_passes,
                                                 'tile_ordering': asr_scene_props.tile_ordering},
                      'texture_store': {'max_size': asr_scene_props.tex_cache * 1024 * 1024},
                      'light_sampler': {'algorithm': asr_scene_props.light_sampler},
                      'shading_result_framebuffer': "permanent" if asr_scene_props.renderer_passes > 1 else "ephemeral"}

        if asr_scene_props.lighting_engine == 'pt':
            parameters['pt'] = {'enable_ibl': True if asr_scene_props.enable_ibl else False,
                                'enable_dl': True if asr_scene_props.enable_dl else False,
                                'clamp_roughness': True,
                                'enable_caustics': True if scene.appleseed.enable_caustics else False,
                                'record_light_paths': True if scene.appleseed.record_light_paths else False,
                                'next_event_estimation': True if scene.appleseed.next_event_estimation else False,
                                'rr_min_path_length': asr_scene_props.rr_start,
                                'optimize_for_lights_outside_volumes': asr_scene_props.optimize_for_lights_outside_volumes,
                                'volume_distance_samples': asr_scene_props.volume_distance_samples,
                                'dl_light_samples': asr_scene_props.dl_light_samples,
                                'ibl_env_samples': asr_scene_props.ibl_env_samples}
            if not asr_scene_props.max_ray_intensity_unlimited:
                parameters['pt']['max_ray_intensity'] = asr_scene_props.max_ray_intensity
            if asr_scene_props.dl_low_light_threshold > 0.0:
                parameters['pt']['dl_low_light_threshold'] = asr_scene_props.dl_low_light_threshold
            if not asr_scene_props.max_diffuse_bounces_unlimited:
                parameters['pt']['max_diffuse_bounces'] = asr_scene_props.max_diffuse_bounces
            if not asr_scene_props.max_glossy_brdf_bounces_unlimited:
                parameters['pt']['max_glossy_brdf_bounces'] = asr_scene_props.max_glossy_brdf_bounces
            if not asr_scene_props.max_specular_bounces_unlimited:
                parameters['pt']['max_specular_bounces'] = asr_scene_props.max_specular_bounces
            if not asr_scene_props.max_volume_bounces_unlimited:
                parameters['pt']['max_volume_bounces'] = asr_scene_props.max_volume_bounces
            if not asr_scene_props.max_bounces_unlimited:
                parameters['pt']['max_bounces'] = asr_scene_props.max_bounces
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
        '''
        Convert image related settings (resolution, crop windows, AOVs, ...) to appleseed.
        '''

        logger.debug("Translating frame")

        asr_scene_props = self.bl_scene.appleseed
        scale = self.bl_scene.render.resolution_percentage / 100.0
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

        # AOVs.
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
            if asr_scene_props.uv_aov:
                aovs.insert(asr.AOV('uv_aov', {}))
            if asr_scene_props.depth_aov:
                aovs.insert(asr.AOV('depth_aov', {}))
            if asr_scene_props.pixel_time_aov:
                aovs.insert(asr.AOV('pixel_time_aov', {}))

        # Create and set the frame in the project.
        frame = asr.Frame("beauty", frame_params, aovs)

        if self.bl_scene.render.use_border:
            min_x = int(self.bl_scene.render.border_min_x * width)
            max_x = int(self.bl_scene.render.border_max_x * width)
            min_y = height - int(self.bl_scene.render.border_max_y * height) - 1
            max_y = height - int(self.bl_scene.render.border_min_y * height) - 1
            frame.set_crop_window([min_x, min_y, max_x, max_y])

        self.__project.set_frame(frame)
