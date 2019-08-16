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
from .utilites import ProjectExportMode
from .world import WorldTranslator
from ..logger import get_logger
from ..utils.util import Timer, calc_film_aspect_ratio

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
        :param engine:
        :param depsgraph:
        :return:
        """

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
        :param engine:
        :param depsgraph:
        :return:
        """

        logger.debug("Creating final render scene translator")

        asset_handler = AssetHandler(depsgraph)

        return cls(engine=engine,
                   depsgraph=depsgraph,
                   export_mode=ProjectExportMode.FINAL_RENDER,
                   selected_only=False,
                   context=None,
                   asset_handler=asset_handler)

    @classmethod
    def create_interactive_render_translator(cls, engine, context, depsgraph):
        """
        Create a scene translator to export the scene to an in memory appleseed project
        optimized for quick interactive edits.
        :param engine:
        :param context:
        :param depsgraph:
        :return:
        """

        logger.debug("Creating interactive render scene translator")

        asset_handler = AssetHandler(depsgraph)

        return cls(engine=engine,
                   depsgraph=depsgraph,
                   export_mode=ProjectExportMode.INTERACTIVE_RENDER,
                   selected_only=False,
                   context=context,
                   asset_handler=asset_handler)

    def __init__(self, engine, depsgraph, export_mode, selected_only, context, asset_handler):
        """
        Constructor. Do not use it to create instances of this class.
        Use the @classmethods instead.
        :param engine:
        :param depsgraph:
        :param export_mode:
        :param selected_only:
        :param context:
        :param asset_handler:
        """

        self.__engine = engine
        self.__depsgraph = depsgraph
        self.__asset_handler = asset_handler
        self.__export_mode = export_mode
        self.__selected_only = selected_only
        self.__context = context

        # Translators.
        self.__world_translator = None
        self.__camera_translator = None
        self.__lamp_translators = dict()
        self.__object_translators = dict()
        self.__material_translators = dict()
        self.__texture_translators = dict()

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
        return self.__depsgraph.scene_eval

    @property
    def camera_translator(self):
        return self.__camera_translator

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
        return [self.__lamp_translators,
                self.__object_translators]

    def translate_scene(self):
        """
        Translate the Blender scene to an appleseed project.
        """

        logger.debug("Translating scene %s", self.bl_scene.name)

        prof_timer = Timer()
        prof_timer.start()

        self.__create_project()

        self.__translate_render_settings()
        self.__translate_frame(self.__context)

        self.__create_world_translator()

        self.__create_camera_translator()

        textures_to_add = {}

        if self.__world_translator is not None:
            self.__world_translator.create_entities(self.bl_scene,
                                                    textures_to_add,
                                                    self.__texture_translators)

        self.__camera_translator.create_entities(self.bl_scene,
                                                 textures_to_add,
                                                 self.__texture_translators)

        bl_material_blocks, bl_object_blocks = self.__parse_datablocks()

        as_object_translators, as_material_translators, as_lamp_translators = self.__create_translators(bl_material_blocks,
                                                                                                        bl_object_blocks)

        self.__create_instancers(as_object_translators,
                                 as_lamp_translators)

        self.__create_entities(as_object_translators,
                               as_material_translators,
                               as_lamp_translators,
                               textures_to_add)

        self.__create_texture_entities(textures_to_add)

        self.__calc_motion(as_object_translators)

        self.__flush_entities(as_object_translators,
                              as_material_translators,
                              as_lamp_translators,
                              textures_to_add)

        if self.__world_translator is not None:
            self.__world_translator.flush_entities(self.as_scene,
                                                   self.main_assembly,
                                                   self.as_project)

        self.__camera_translator.flush_entities(self.as_scene,
                                                self.main_assembly,
                                                self.as_project)

        self.__load_searchpaths()

        prof_timer.stop()
        logger.debug("Scene translated in %f seconds.", prof_timer.elapsed())

    # Multiview functions
    def update_multiview_camera(self):
        self.__calc_multiview_camera()

    # Interactive mode functions
    def check_view(self, context, depsgraph):
        """
        Check the viewport to see if it has changed camera position or window size.
        For whatever reason, these changes do not trigger an update request so we must check things manually.
        :param context:
        :param depsgraph:
        :return:
        """

        view_update = False
        cam_param_update, cam_translate_update, cam_model_update = self.__camera_translator.check_view(context,
                                                                                                       depsgraph)

        # Check if the frame needs to be updated
        width = int(self.__context.region.width)
        height = int(self.__context.region.height)
        new_viewport_resolution = [width, height]
        if new_viewport_resolution != self.__viewport_resolution:
            view_update = True
            cam_param_update = True

        return view_update, cam_param_update, cam_translate_update, cam_model_update

    def update_view(self, context, depsgraph, view_update, cam_param_update, cam_model_update):
        """
        Update the viewport window during interactive rendering.  The viewport update is triggered
        automatically following a scene update, or when the check view function returns true on any of its checks.
        :param context:
        :param depsgraph:
        :param view_update:
        :param cam_param_update:
        :param cam_model_update:
        """

        logger.debug("Begin view update")

        if cam_param_update or cam_model_update:
            self.__camera_translator.update_camera(context,
                                                   depsgraph,
                                                   self.as_scene,
                                                   cam_model_update,
                                                   None,
                                                   None)

        if view_update:
            self.__translate_frame(context)

        self.__camera_translator.set_xform_step(0.0)

    def update_scene(self, context, depsgraph):
        """
        This function checks an *impartial* list of updated datablocks that Blender provides
        whenever some kind of scene update happens.  This list is incomplete (textures aren't flagged)
        and there's no indication of when the number of instances changes or objects become hidden, deleted
        or added.  In order to catch these kinds of events there is really no other choice than to delete and
        recreate all the instances in the scene every time an update happens.  Which is dumb and a waste of
        processing, but what else can you do?
        :param context:
        :param depsgraph:
        :return: None
        """

        logger.debug("Begin Scene Update")

        bl_material_blocks = list()
        bl_object_blocks = list()
        textures_to_add = dict()

        for obj in depsgraph.updates:
            if isinstance(obj.id, bpy.types.World):
                if self.__world_translator is not None:
                    self.__world_translator.update_world(context,
                                                         depsgraph,
                                                         self.as_scene,
                                                         textures_to_add,
                                                         self.__texture_translators)
                else:
                    self.__create_world_translator()
                    if self.__world_translator is not None:
                        self.__world_translator.create_entities(depsgraph.scene_eval,
                                                                textures_to_add,
                                                                self.__texture_translators)
                        self.__world_translator.flush_entities(self.as_scene,
                                                               self.main_assembly,
                                                               self.as_project)
            elif isinstance(obj.id, bpy.types.Camera):
                self.__camera_translator.update_camera(context,
                                                       depsgraph,
                                                       self.as_scene,
                                                       True,
                                                       textures_to_add,
                                                       self.__texture_translators)
            elif isinstance(obj.id, bpy.types.Material):
                mat_key = obj.id.name_full
                if mat_key in self.__material_translators:
                    self.__material_translators[mat_key].update_material(context,
                                                                         depsgraph,
                                                                         self.main_assembly)
                else:
                    bl_material_blocks.append(obj.id)
            elif isinstance(obj.id, bpy.types.Object):
                obj_key = obj.id.name_full
                if obj.id.type == 'MESH':
                    if obj_key not in self.__object_translators:
                        bl_object_blocks.append(obj.id)
                    else:
                        self.__object_translators[obj_key].update_object(context,
                                                                         depsgraph,
                                                                         self.main_assembly,
                                                                         textures_to_add,
                                                                         self.__texture_translators)
                elif obj.id.type == 'LIGHT':
                    if obj_key not in self.__lamp_translators:
                        bl_object_blocks.append(obj.id)
                    else:
                        self.__lamp_translators[obj_key].update_lamp(context,
                                                                     depsgraph,
                                                                     self.main_assembly,
                                                                     textures_to_add,
                                                                     self.__texture_translators)

        # Create any new objects or materials
        if bl_material_blocks == [] or bl_object_blocks == []:
            as_object_translators, as_material_translators, as_lamp_translators = self.__create_translators(bl_material_blocks,
                                                                                                            bl_object_blocks)

            self.__create_entities(as_object_translators,
                                   as_material_translators,
                                   as_lamp_translators,
                                   textures_to_add)
            self.__create_instancers(as_object_translators,
                                     as_lamp_translators)
            self.__create_texture_entities(textures_to_add)
            self.__calc_motion(as_object_translators)
            self.__flush_entities(as_object_translators,
                                  as_material_translators,
                                  as_lamp_translators,
                                  textures_to_add)

        # Re-create instances for existing objects
        logger.debug("Updating instances for existing objects")
        self.__update_instances()

        # Cleanup unused objects and lamps
        used_objects = [x.name_full for x in depsgraph.ids if isinstance(x, bpy.types.Object)]

        for obj_key in list(self.__object_translators.keys()):
            if obj_key not in used_objects:
                self.__object_translators[obj_key].delete_object(self.main_assembly)
                del self.__object_translators[obj_key]

        for lamp_key in list(self.__lamp_translators.keys()):
            if lamp_key not in used_objects:
                self.__lamp_translators[lamp_key].delete_lamp(self.as_scene,
                                                              self.main_assembly)
                del self.__lamp_translators[lamp_key]

    # Project file export functions
    def write_project(self, filename):
        """
        Write the appleseed project out to disk.
        :param filename:
        """

        asr.ProjectFileWriter().write(
            self.as_project,
            bpy.path.abspath(filename),
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
        assembly_inst = asr.AssemblyInstance("assembly_inst",
                                             {},
                                             "assembly")
        assembly_inst.transform_sequence().set_transform(0.0, asr.Transformd(asr.Matrix4d.identity()))
        self.__project.get_scene().assembly_instances().insert(assembly_inst)

        # Create default materials.
        self.__create_default_material()
        self.__create_null_material()

    def __create_default_material(self):
        logger.debug("Creating default material")

        surface_shader = asr.SurfaceShader("diagnostic_surface_shader",
                                           "__default_surface_shader",
                                           {'mode': 'facing_ratio'})
        material = asr.Material('generic_material',
                                "__default_material",
                                {'surface_shader': '__default_surface_shader'})

        self.__main_assembly.surface_shaders().insert(surface_shader)
        self.__main_assembly.materials().insert(material)

    def __create_null_material(self):
        logger.debug("Creating null material")

        material = asr.Material('generic_material',
                                "__null_material",
                                {})
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

        tile_renderer = 'adaptive' if asr_scene_props.pixel_sampler == 'adaptive' else 'generic'
        pixel_renderer = '' if asr_scene_props.pixel_sampler == 'adaptive' else 'uniform'

        parameters = {'uniform_pixel_renderer': {'force_antialiasing': True if asr_scene_props.force_aa else False,
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
                      'progressive_frame_renderer': {'max_average_spp': asr_scene_props.interactive_max_samples,
                                                     'max_fps': asr_scene_props.interactive_max_fps},
                      'light_sampler': {'algorithm': asr_scene_props.light_sampler,
                                        'enable_light_importance_sampling': asr_scene_props.enable_light_importance_sampling},
                      'shading_result_framebuffer': "permanent" if asr_scene_props.renderer_passes > 1 else "ephemeral"}

        if self.export_mode != ProjectExportMode.PROJECT_EXPORT:
            if self.export_mode == ProjectExportMode.INTERACTIVE_RENDER:
                # The thread count is this low due to the possibility of quad view being used,
                # which generates 4 independent render engines (one for each panel)
                render_threads = 2
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

    def __translate_frame(self, context):
        """
        Convert image related settings (resolution, crop windows, AOVs, ...) to appleseed.
        :param context:
        """

        logger.debug("Translating frame")

        asr_scene_props = self.bl_scene.appleseed
        scale = self.bl_scene.render.resolution_percentage / 100.0
        if context is not None:
            width = int(context.region.width)
            height = int(context.region.height)
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

        aovs = asr.AOVContainer()
        if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            aovs = self.__set_aovs(aovs)

        # Create and set the frame in the project.
        self.__frame = asr.Frame("beauty",
                                 frame_params,
                                 aovs)

        if self.bl_scene.render.use_border and self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            min_x = int(self.bl_scene.render.border_min_x * width)
            max_x = int(self.bl_scene.render.border_max_x * width) - 1
            min_y = height - int(self.bl_scene.render.border_max_y * height)
            max_y = height - int(self.bl_scene.render.border_min_y * height) - 1
            self.__frame.set_crop_window([min_x, min_y, max_x, max_y])

        elif self.export_mode == ProjectExportMode.INTERACTIVE_RENDER and context.space_data.use_render_border and context.region_data.view_perspective in ('ORTHO', 'PERSP'):
            min_x = int(context.space_data.render_border_min_x * width)
            max_x = int(context.space_data.render_border_max_x * width) - 1
            min_y = height - int(context.space_data.render_border_max_y * height)
            max_y = height - int(context.space_data.render_border_min_y * height) - 1
            self.__frame.set_crop_window([min_x, min_y, max_x, max_y])

        elif self.export_mode == ProjectExportMode.INTERACTIVE_RENDER and self.bl_scene.render.use_border and context.region_data.view_perspective == 'CAMERA':
            """
            I can't explain how the following code produces the correct render window.
            I basically threw every parameter combination I could think of together 
            until the result looked right.
            """

            zoom = 4 / ((math.sqrt(2) + context.region_data.view_camera_zoom / 50)** 2)
            frame_aspect_ratio = width / height
            camera_aspect_ratio = calc_film_aspect_ratio(self.bl_scene)
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

            window_x_min = int(camera_width * self.bl_scene.render.border_min_x + window_shift_x - view_shift_x)
            window_x_max = int(camera_width * self.bl_scene.render.border_max_x + window_shift_x - view_shift_x)
            window_y_min = height - int(camera_height * self.bl_scene.render.border_max_y + window_shift_y - view_shift_y)
            window_y_max = height - int(camera_height * self.bl_scene.render.border_min_y + window_shift_y - view_shift_y)

            self.__frame.set_crop_window([window_x_min, window_y_min, window_x_max, window_y_max])

        self.__project.set_frame(self.__frame)
        self.__frame = self.as_project.get_frame()

        if len(asr_scene_props.post_processing_stages) > 0 and self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            self.__set_post_process()

    def __set_aovs(self, aovs):
        """
        If an AOV is activated for export, place it inside the provided AOV container.
        :param aovs:
        :return:
        """

        if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            logger.debug("Translating AOVs")
            asr_scene_props = self.bl_scene.appleseed

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

            logger.debug("Adding AOV: %s", stage.name)

            self.__frame.post_processing_stages().insert(post_process)

    def __create_world_translator(self):
        if self.bl_scene.world.appleseed_sky.env_type != 'none':
            self.__world_translator = WorldTranslator(self.bl_scene.world,
                                                      self.asset_handler)

    def __create_camera_translator(self):
        camera = self.bl_scene.camera if self.bl_scene.camera is not None else None

        if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            if camera is None:
                self.bl_engine.report({'ERROR'}, "No camera in scene!")
                raise NotImplementedError
            else:
                self.__camera_translator = RenderCameraTranslator(camera,
                                                                  self.asset_handler,
                                                                  self.bl_engine)
        else:
            self.__camera_translator = InteractiveCameraTranslator(self.asset_handler,
                                                                   self.bl_engine,
                                                                   self.__context,
                                                                   camera)

    def __calc_motion(self, as_object_translators):
        """
        Calculates subframes for motion blur.  Each blur type can have its own segment count, so the final list
        created has every transform time needed.  This way we only have to move the frame set point (with the associated
        depsgraph recalculation) one time.
        :param as_object_translators:
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
                self.__camera_translator.set_xform_step(time, )

            if time in xform_times:
                for inst in self.bl_depsgraph.object_instances:
                    if inst.is_instance:
                        source = inst.instance_object
                        parent_key = inst.parent.name_full
                        inst_key = f"{source.name_full}|{parent_key}|{inst.persistent_id[0]}"
                    else:
                        source = inst.object
                        inst_key = f"{source.name_full}|{inst.persistent_id[0]}"

                    if source.type == 'MESH' or source.appleseed.object_export == "archive_assembly":
                        if source.name_full in as_object_translators:
                            as_object_translators[source.name_full].set_xform_step(time, inst_key, inst.matrix_world)

            logger.debug("Processing deformations for frame %s", self.bl_scene.frame_current)

            if time in deform_times:
                for translator in as_object_translators.values():
                    translator.set_deform_key(time,
                                              self.bl_depsgraph,
                                              all_times)

        self.bl_engine.frame_set(current_frame, subframe=0.0)

    def __calc_multiview_camera(self):
        """
        This function is called only during final rendering of a scene that contains a stereoscopic camera.
        The scene itself remains unchanged.
        :return:
        """

        logger.debug("Updating stereoscopic camera")
        self.__camera_translator.remove_cam(self.as_scene)
        self.__camera_translator.create_entities(self.bl_scene,
                                                 None,
                                                 None)

        cam_times = {0.0}

        if self.bl_scene.appleseed.enable_camera_blur:
            shutter_length = self.bl_scene.appleseed.shutter_close - self.bl_scene.appleseed.shutter_open
            self.__get_subframes(shutter_length,
                                 self.bl_scene.appleseed.camera_blur_samples,
                                 cam_times)

        all_times = sorted(list(cam_times))

        current_frame = self.bl_scene.frame_current

        for time in all_times:
            new_frame = current_frame + time
            int_frame = math.floor(new_frame)
            subframe = new_frame - int_frame

            self.bl_engine.frame_set(int_frame,
                                     subframe=subframe)

            logger.debug("Processing transforms for frame %s", self.bl_scene.frame_current)

            if time in cam_times:
                self.__camera_translator.set_xform_step(time, )

        self.bl_engine.frame_set(current_frame,
                                 subframe=0.0)

        self.__camera_translator.flush_entities(self.as_scene,
                                                self.main_assembly,
                                                self.as_project)

    def __get_subframes(self, shutter_length, samples, times):
        assert samples > 1

        segment_size = shutter_length / (samples - 1)

        for seg in range(0, samples):
            times.update({self.bl_scene.appleseed.shutter_open + (seg * segment_size)})

    def __create_translators(self, material_blocks, object_bocks):
        """
        Creates appleseed translators for all the 'real' object, lamps and materials in the scene
        :param material_blocks:
        :param object_bocks:
        :return: Lists of appleseed translators
        """

        as_object_translators = dict()
        as_material_translators = dict()
        as_lamp_translators = dict()

        logger.debug("Creating material translators")
        for mat in material_blocks:
            mat_key = mat.name_full
            as_material_translators[mat_key] = MaterialTranslator(mat,
                                                                  self.asset_handler)

        logger.debug("Creating object translators")
        for obj in object_bocks:
            obj_key = obj.name_full
            if obj.appleseed.object_export == "archive_assembly":
                as_object_translators[obj_key] = ArchiveAssemblyTranslator(obj,
                                                                           self.asset_handler)
            elif obj.type == 'MESH':
                as_object_translators[obj_key] = MeshTranslator(obj,
                                                                self.export_mode,
                                                                self.asset_handler)

            elif obj.type == 'LIGHT':
                as_lamp_translators[obj_key] = LampTranslator(obj,
                                                              self.asset_handler)

        return as_object_translators, as_material_translators, as_lamp_translators

    def __create_instancers(self, as_object_translators, as_lamp_translators):
        """
        Creates translators for each mesh/lamp and instance of a lamp/object that was created via a particle system
        or dupli item.
        :param as_object_translators:
        :param as_lamp_translators:
        """

        logger.debug("Creating instances")
        for inst in self.bl_depsgraph.object_instances:
            if inst.show_self:
                if inst.is_instance:
                    source = inst.instance_object
                    parent_key = inst.parent.name_full
                    inst_key = f"{source.name_full}|{parent_key}|{inst.persistent_id[0]}"
                else:
                    source = inst.object
                    inst_key = f"{source.name_full}|{inst.persistent_id[0]}"

                if (source.type == 'MESH' or source.appleseed.object_export == "archive_assembly") and source.name_full in as_object_translators:
                    as_object_translators[source.name_full].add_instance(inst_key)
                elif source.type == 'LIGHT' and source.name_full in as_lamp_translators:
                    as_lamp_translators[source.name_full].add_instance(inst_key,
                                                                       inst.matrix_world.copy())

        for key in list(as_object_translators.keys()):
            translator = as_object_translators[key]
            if len(translator.instances) == 0:
                logger.debug("Object %s has no instances, deleting", key)
                del as_object_translators[key]

    def __create_entities(self, as_object_translators, as_material_translators, as_lamp_translators, textures_to_add):
        logger.debug("Creating entities")
        for obj in as_object_translators.values():
            obj.create_entities(self.bl_scene,
                                textures_to_add,
                                self.__texture_translators)

        for light in as_lamp_translators.values():
            light.create_entities(self.bl_scene,
                                  textures_to_add,
                                  self.__texture_translators)

        for mat in as_material_translators.values():
            mat.create_entities(self.bl_scene)

    def __create_texture_entities(self, textures_to_add):
        logger.debug("Creating texture entities")
        for tex in textures_to_add.values():
            tex.create_entities(self.bl_scene)

    def __flush_entities(self, as_object_translators, as_material_translators, as_lamp_translators, textures_to_add):
        logger.debug("Flushing entities")
        for key, obj in as_object_translators.items():
            obj.flush_entities(self.main_assembly,
                               self.as_project)
            self.__object_translators[key] = obj

        for key, light in as_lamp_translators.items():
            light.flush_entities(self.main_assembly,
                                 self.as_project)
            self.__lamp_translators[key] = light

        for key, mat in as_material_translators.items():
            mat.flush_entities(self.main_assembly,
                               self.as_project)
            self.__material_translators[key] = mat

        for key, tex in textures_to_add.items():
            tex.flush_entities(self.main_assembly,
                               self.as_project)
            self.__texture_translators[key] = tex

    def __update_instances(self):
        """
        Updates the list of instances for _existing items_ during interactive rendering.
        """

        logger.debug("Updating instances for existing translators")
        for obj_type in self.all_translators:
            for translator in obj_type.values():
                translator.delete_instances(self.main_assembly,
                                            self.as_scene)

        for inst in self.bl_depsgraph.object_instances:
            if inst.show_self:
                if inst.is_instance:
                    source = inst.instance_object
                    parent_key = inst.parent.name_full
                    inst_key = f"{source.name_full}|{parent_key}|{inst.persistent_id[0]}"
                else:
                    source = inst.object
                    inst_key = f"{source.name_full}|{inst.persistent_id[0]}"

                if (source.type == 'MESH' or source.appleseed.object_export == "archive_assembly") and source.name_full in self.__object_translators.keys():
                    self.__object_translators[source.name_full].xform_update(inst_key,
                                                                             inst.matrix_world.copy(),
                                                                             self.main_assembly,
                                                                             self.as_scene)

                if source.type == 'LIGHT' and source.name_full in self.__lamp_translators.keys():
                    self.__lamp_translators[source.name_full].xform_update(inst_key,
                                                                           inst.matrix_world,
                                                                           self.main_assembly,
                                                                           self.as_scene)

    def __parse_datablocks(self):
        """
        Parses the blocks present in the evaluated depsgraph and returns them in a list
        :return: Lists of Blender data blocks
        """

        logger.debug("Parsing Datablocks")

        mat_blocks = list()
        object_blocks = list()

        for mat in bpy.data.materials:
            mat_blocks.append(mat)

        for obj in bpy.data.objects:
            if obj.type not in objects_to_ignore:
                bl_obj = obj.evaluated_get(self.bl_depsgraph)
                if (bl_obj.type == 'MESH' and len(bl_obj.data.polygons) > 0) or bl_obj.type in ('LIGHT', 'EMPTY'):
                    object_blocks.append(bl_obj)

        return mat_blocks, object_blocks

    def __load_searchpaths(self):
        logger.debug("Loading searchpaths")
        paths = self.as_project.get_search_paths()

        paths.extend(path for path in self.asset_handler.searchpaths if path not in paths)

        self.as_project.set_search_paths(paths)

    @staticmethod
    def __round_up_pow2(x):
        assert (x >= 2)
        return 1 << (x - 1).bit_length()
