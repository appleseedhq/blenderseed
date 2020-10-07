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
from .material import MaterialTranslator
from .objects import ArchiveAssemblyTranslator, MeshTranslator, LampTranslator
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
        self.__as_object_translators = dict()
        self.__as_material_translators = dict()
        self.__as_texture_translators = dict()

        # Motion Steps.
        self.__all_times = {0.0}
        self.__cam_times = {0.0}
        self.__xform_times = {0.0}
        self.__deform_times = {0.0}

        # Interactive tools.
        self.__viewport_resolution = None
        self.__current_frame = None

        # Render crop window.
        self.__crop_window = None

        self.__project = None
        self.__frame = None

    @property
    def as_project(self):
        return self.__project

    @property
    def as_scene(self):
        return self.__project.get_scene()

    @property
    def as_main_assembly(self):
        return self.__main_assembly

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

        self.__calc_crop_window(depsgraph, context)

        if self.__crop_window is not None:
            self.__frame.set_crop_window(self.__crop_window)

        if len(depsgraph.scene_eval.appleseed.post_processing_stages) > 0 and self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            self.__set_post_process(depsgraph)

        self.__project.set_frame(self.__frame)
        self.__frame = self.__project.get_frame()

        # Create camera
        if depsgraph.scene_eval.camera is not None:
            # Create interactive or final render camera
            if self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER:
                self.__as_camera_translator = InteractiveCameraTranslator(depsgraph.scene_eval.camera, self.__asset_handler)
            else:
                self.__as_camera_translator = RenderCameraTranslator(depsgraph.scene_eval.camera, self.__asset_handler)
        else:
            engine.error_set("appleseed: No camera in scene!")

        # Create world
        if depsgraph.scene_eval.world is not None:
            self.__as_world_translator = WorldTranslator(depsgraph.scene_eval.world, self.__asset_handler)

        # Blender scene processing
        objects_to_add = dict()
        materials_to_add = dict()
        textures_to_add = dict()

        for obj in bpy.data.objects:
            if obj.type == 'LIGHT':
                objects_to_add[obj] = LampTranslator(obj, self.__export_mode, self.__asset_handler)
            elif obj.type == 'MESH' and len(obj.data.loops) > 0:
                objects_to_add[obj] = MeshTranslator(obj, self.__export_mode, self.__asset_handler)
            elif obj.type == 'EMPTY' and obj.appleseed.object_export == "archive_assembly":
                objects_to_add[obj] = ArchiveAssemblyTranslator(obj, self.__asset_handler)

        for mat in bpy.data.materials:
            materials_to_add[mat] = MaterialTranslator(mat, self.__asset_handler)

        for tex in bpy.data.images:
            if tex.users > 0 and tex.name not in ("Render Result", "Viewer Node"):
                textures_to_add[tex] = TextureTranslator(tex, self.__asset_handler)

        # Create camera, world, material and texture entities
        self.__as_camera_translator.create_entities(depsgraph, context, engine)

        if self.__as_world_translator is not None:
            self.__as_world_translator.create_entities(depsgraph)

        for obj, trans in materials_to_add.items():
            trans.create_entities(depsgraph, engine)
        for obj, trans in textures_to_add.items():
            trans.create_entities(depsgraph)

        # Set initial position of all objects and lamps
        self.__calc_initial_positions(depsgraph, engine, objects_to_add)

        # Remove unused translators
        for translator in list(objects_to_add.keys()):
            if objects_to_add[translator].instances_size == 0:
                del objects_to_add[translator]

        # Create 3D entities
        for obj, trans in objects_to_add.items():
            trans.create_entities(depsgraph, len(self.__deform_times))

        # Calculate additional steps for motion blur
        if self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            self.__calc_motion_steps(depsgraph, engine, objects_to_add)

        self.__as_camera_translator.flush_entities(self.as_scene, self.as_main_assembly, self.as_project)
        if self.__as_world_translator is not None:
            self.__as_world_translator.flush_entities(self.as_scene, self.as_main_assembly, self.as_project)

        for obj, trans in objects_to_add.items():
            trans.flush_entities(self.as_scene, self.as_main_assembly, self.as_project)
        for obj, trans in materials_to_add.items():
            trans.flush_entities(self.as_scene, self.as_main_assembly, self.as_project)
        for obj, trans in textures_to_add.items():
            trans.flush_entities(self.as_scene, self.as_main_assembly, self.as_project)

        # Transfer temp translators to main list
        for bl_obj, translator in objects_to_add.items():
            self.__as_object_translators[bl_obj] = translator
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

    def update_scene(self, depsgraph, engine):
        objects_to_add = dict()
        materials_to_add = dict()

        object_updates = list()

        check_for_deletions = False

        recreate_instances = list()

        # Check for updated datablocks.
        for update in depsgraph.updates:
            # This one is easy.
            if isinstance(update.id, bpy.types.Material):
                if update.id.original in self.__as_material_translators.keys():
                    self.__as_material_translators[update.id.original].update_material(depsgraph, engine)
                else:
                    materials_to_add[update.id.original] = MaterialTranslator(update.id.original,
                                                                              self.__asset_handler)
            # Now comes agony and mental anguish.
            elif isinstance(update.id, bpy.types.Object):
                if update.id.type == 'MESH':
                    if update.id.original in self.__as_object_translators.keys():
                        if update.is_updated_geometry:
                            self.__as_object_translators[update.id.original].update_obj_instance()
                            object_updates.append(update.id.original)
                        if update.is_updated_transform:
                            recreate_instances.append(update.id.original)
                    else:
                        objects_to_add[update.id.original] = MeshTranslator(update.id.original,
                                                                            self.__export_mode,
                                                                            self.__asset_handler)
                elif update.id.type == 'LIGHT':
                    if update.id.original in self.__as_object_translators.keys():
                        if update.is_updated_geometry:
                            self.__as_object_translators[update.id.original].update_lamp(depsgraph,
                                                                                         self.as_main_assembly,
                                                                                         self.as_scene,
                                                                                         self.__project)
                            object_updates.append(update.id.original)
                            recreate_instances.append(update.id.original)
                        if update.is_updated_transform:
                            recreate_instances.append(update.id.original)
                    else:
                        objects_to_add[update.id.original] = LampTranslator(update.id.original,
                                                                            self.__export_mode,
                                                                            self.__asset_handler)

                elif update.id.type == 'EMPTY' and update.id.appleseed.object_export == "archive_assembly":
                    if update.id.original in self.__as_object_translators.keys():
                        if update.is_updated_geometry:
                            self.__as_object_translators[update.id.original].update_archive_ass(depsgraph)
                            object_updates.append(update.id.original)
                        if update.is_updated_transform:
                            recreate_instances.append(update.id.original)
            elif isinstance(update.id, bpy.types.World):
                self.__as_world_translator.update_world(self.as_scene, depsgraph)
            elif isinstance(update.id, bpy.types.Scene):
                # Check if world was added or deleted.
                # Delete existing world.
                if depsgraph.scene_eval.world is None and self.__as_world_translator is not None:
                    self.__as_world_translator.delete_world(self.as_scene)
                    self.__as_world_translator = None
                # Create new world.
                elif depsgraph.scene_eval.world is not None and self.__as_world_translator is None:
                    self.__as_world_translator = WorldTranslator(depsgraph.scene_eval.world, self.__asset_handler)
                    self.__as_world_translator.create_entities(depsgraph)
                    self.__as_world_translator.flush_entities(self.as_scene,
                                                              self.as_main_assembly,
                                                              self.as_project)
            elif isinstance(update.id, bpy.types.Collection):
                check_for_deletions = True

        # Now we figure out which objects have particle systems that need to have their instances recreated.
        for obj in object_updates:
            if len(obj.particle_systems) > 0:
                for system in obj.particle_systems:
                    if system.settings.render_type == 'OBJECT':
                        recreate_instances.append(system.settings.instance_object.original)
                    elif system.settings.render_type == 'COLLECTION':
                        for other_obj in system.settings.instance_collection.objects:
                            if other_obj.type in ('MESH', 'LIGHT') and other_obj.original not in recreate_instances:
                                recreate_instances.append(other_obj.original)

        for obj in recreate_instances:
            self.__as_object_translators[obj].clear_instances(self.as_main_assembly)

        for inst in depsgraph.object_instances:
            if inst.show_self:
                obj, inst_id = self.__get_instance_data(inst)
                if obj in recreate_instances:
                    self.__as_object_translators[obj].add_instance_step(0.0, inst_id, inst.matrix_world)
                elif obj in objects_to_add.keys():
                    objects_to_add[obj].add_instance_step(0.0, inst_id, inst.matrix_world)

        # Create new materials.
        for mat in materials_to_add.values():
            mat.create_entities(depsgraph, engine)

        # Create new objects.
        for trans in objects_to_add.values():
            trans.create_entities(depsgraph, 0)

        for obj in recreate_instances:
            self.__as_object_translators[obj].flush_instances(self.as_main_assembly)

        for mat_obj, trans in materials_to_add.items():
            trans.flush_entities(self.as_scene, self.as_main_assembly, self.as_project)
            self.__as_material_translators[mat_obj] = trans

        for bl_obj, trans in objects_to_add.items():
            trans.flush_entities(self.as_scene, self.as_main_assembly, self.as_project)
            self.__as_object_translators[bl_obj] = trans

        # Check if any objects were deleted.
        if check_for_deletions:
            obj_list = list(self.__as_object_translators.keys())

            for obj in obj_list:
                try:
                    if obj.name_full in bpy.data.objects or obj.name_full in bpy.data.lights:
                        continue
                except:
                    self.__as_object_translators[obj].delete_object(self.as_main_assembly)
                    del self.__as_object_translators[obj]

    def check_view_window(self, depsgraph, context):
        # Check if any camera parameters have changed (location, model, etc...)
        updates = self.__as_camera_translator.check_for_updates(context, depsgraph.scene_eval)

        # Check if frame size has changed.
        current_resolution = self.__viewport_resolution
        self.__calc_viewport_resolution(depsgraph, context)
        updates['frame_size'] = current_resolution != self.__viewport_resolution

        # Check if crop window has changed.
        current_crop_window = self.__crop_window
        self.__calc_crop_window(depsgraph, context)
        updates['crop_window'] = current_crop_window != self.__crop_window

        return updates

    def update_view_window(self, updates):
        if updates['cam_model']:
            self.__as_camera_translator.update_cam_model(self.as_scene)
            self.__as_camera_translator.add_cam_xform(0.0)
        else:
            if updates['cam_params']:
                self.__as_camera_translator.update_cam_params()
            if updates['cam_xform']:
                self.__as_camera_translator.add_cam_xform(0.0)

        if updates['frame_size']:
            self.__update_frame_size()

        if updates['crop_window']:
            self.__frame.reset_crop_window()
            if self.__crop_window is not None:
                self.__frame.set_crop_window(self.__crop_window)

    # Interactive update functions.
    def write_project(self, export_path):
        # Export project files.
        filename = os.path.abspath(bpy.path.ensure_ext(bpy.path.abspath(export_path), '.appleseed'))

        asr.ProjectFileWriter().write(self.__project,
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
        self.as_scene.set_environment(asr.Environment("environment", {}))

        # Create the main assembly.
        self.as_scene.assemblies().insert(asr.Assembly("assembly", {}))
        self.__main_assembly = self.as_scene.assemblies()["assembly"]

        # Instance the main assembly.
        assembly_inst = asr.AssemblyInstance("assembly_inst", {}, "assembly")

        assembly_inst.transform_sequence().set_transform(0.0, asr.Transformd(asr.Matrix4d.identity()))
        self.as_scene.assembly_instances().insert(assembly_inst)

        # Create default materials.
        self.__create_default_material()
        self.__create_null_material()

    def __create_default_material(self):
        logger.debug("appleseed: Creating default material")

        surface_shader = asr.SurfaceShader("diagnostic_surface_shader", "__default_surface_shader", {'mode': 'facing_ratio'})

        material = asr.Material('generic_material', "__default_material", {'surface_shader': '__default_surface_shader'})

        self.as_main_assembly.surface_shaders().insert(surface_shader)
        self.as_main_assembly.materials().insert(material)

    def __create_null_material(self):
        logger.debug("appleseed: Creating null material")

        material = asr.Material('generic_material', "__null_material", {})

        self.as_main_assembly.materials().insert(material)

    def __calc_shutter_times(self, depsgraph):
        scene = depsgraph.scene_eval

        shutter_length = scene.appleseed.shutter_close - scene.appleseed.shutter_open

        if scene.appleseed.enable_camera_blur:
            self.__get_sub_frames(
                scene, shutter_length, scene.appleseed.camera_blur_samples, self.__cam_times)

        if scene.appleseed.enable_object_blur:
            self.__get_sub_frames(scene, shutter_length, scene.appleseed.object_blur_samples, self.__xform_times)

        if scene.appleseed.enable_deformation_blur:
            self.__get_sub_frames(scene,
                                  shutter_length,
                                  self.__round_up_pow2(scene.appleseed.deformation_blur_samples),
                                  self.__deform_times)

        # Merge all subframe times
        all_times = set()
        all_times.update(self.__cam_times)
        all_times.update(self.__xform_times)
        all_times.update(self.__deform_times)
        self.__all_times = sorted(list(all_times))

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

        parameters = {'uniform_pixel_renderer': {'force_antialiasing': True if asr_scene_props.force_aa else False,
                                                 'samples': asr_scene_props.samples},
                      'adaptive_tile_renderer': {'min_samples': asr_scene_props.adaptive_min_samples,
                                                 'noise_threshold': asr_scene_props.adaptive_noise_threshold,
                                                 'batch_size': asr_scene_props.adaptive_batch_size,
                                                 'max_samples': asr_scene_props.adaptive_max_samples},
                      'texture_controlled_pixel_renderer': {'min_samples': asr_scene_props.adaptive_min_samples,
                                                            'max_samples': asr_scene_props.adaptive_max_samples,
                                                            'file_path': realpath(asr_scene_props.texture_sampler_filepath)},
                      'use_embree': asr_scene_props.use_embree,
                      'pixel_renderer': pixel_renderer,
                      'lighting_engine': lighting_engine,
                      'tile_renderer': tile_renderer,
                      'passes': asr_scene_props.renderer_passes,
                      'generic_frame_renderer': {'tile_ordering': asr_scene_props.tile_ordering},
                      'progressive_frame_renderer': {'max_average_spp': asr_scene_props.interactive_max_samples,
                                                     'max_fps': asr_scene_props.interactive_max_fps,
                                                     'time_limit': asr_scene_props.interactive_max_time},
                      'light_sampler': {'algorithm': asr_scene_props.light_sampler,
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
                                  'enable_importons': asr_scene_props.sppm_enable_importons,
                                  'importon_lookup_radius': asr_scene_props.sppm_importon_lookup_radius,
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

    def __translate_frame(self, depsgraph):
        logger.debug("appleseed: Translating frame")

        scene = depsgraph.scene_eval

        asr_scene_props = scene.appleseed

        noise_seed = (asr_scene_props.noise_seed + scene.frame_current) if asr_scene_props.per_frame_noise else asr_scene_props.noise_seed

        width, height = self.__viewport_resolution

        frame_params = {'resolution': asr.Vector2i(width, height),
                        'camera': "Camera",
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

        if self.__export_mode != ProjectExportMode.PROJECT_EXPORT:
            frame_params['tile_size'] = asr.Vector2i(asr_scene_props.tile_size, asr_scene_props.tile_size)

        return frame_params

    def __calc_crop_window(self, depsgraph, context=None):
        width, height = self.__viewport_resolution

        self.__crop_window = None

        if depsgraph.scene_eval.render.use_border and self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
            min_x = int(depsgraph.scene_eval.render.border_min_x * width)
            min_y = height - int(depsgraph.scene_eval.render.border_max_y * height)
            max_x = int(depsgraph.scene_eval.render.border_max_x * width) - 1
            max_y = height - int(depsgraph.scene_eval.render.border_min_y * height) - 1
            self.__crop_window = [min_x,
                                  min_y,
                                  max_x,
                                  max_y]

        else:
            # Interactive render borders
            if context is not None and context.space_data.use_render_border and context.region_data.view_perspective in ('ORTHO', 'PERSP'):
                min_x = int(context.space_data.render_border_min_x * width)
                min_y = height - int(context.space_data.render_border_max_y * height)
                max_x = int(context.space_data.render_border_max_x * width) - 1
                max_y = height - int(context.space_data.render_border_min_y * height) - 1

                self.__crop_window = [min_x,
                                      min_y,
                                      max_x,
                                      max_y]

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
                min_y = clamp_value(window_y_min, 0, height - 1)
                max_x = clamp_value(window_x_max, 0, width - 1)
                max_y = clamp_value(window_y_max, 0, height - 1)

                self.__crop_window = [min_x,
                                      min_y,
                                      max_x,
                                      max_y]

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

    def __get_post_processing_stage_params(self, stage, order):
        params = {'order': order}

        if stage.model == 'bloom_post_processing_stage':
            params.update({'iterations': stage.iterations,
                           'intensity': stage.intensity,
                           'threshold': stage.threshold,
                           'soft_knee': stage.soft_knee,
                           'debug_blur': stage.debug_blur})

        elif stage.model == 'chromatic_aberration_post_processing_stage':
            params.update({'strength': stage.strength,
                           'fringe_smoothness': stage.fringe_smoothness})

        elif stage.model == 'color_map_post_processing_stage':
            params.update({'color_map': stage.color_map,
                           'auto_range': stage.auto_range,
                           'range_min': stage.range_min,
                           'range_max': stage.range_max,
                           'add_legend_bar': stage.add_legend_bar,
                           'legend_bar_ticks': stage.legend_bar_ticks,
                           'render_isolines': stage.render_isolines,
                           'line_thickness': stage.line_thickness})

            if stage.color_map == 'custom':
                params.update({'color_map_file_path': stage.color_map_file_path})

        elif stage.model == 'render_stamp_post_processing_stage':
            params.update({'format_string': stage.render_stamp,  # FIXME shouldn't this be `stage.format_string`?
                           'scale_factor': stage.scale_factor})

        elif stage.model == 'tone_map_post_processing_stage':
            params.update({'tone_map_operator': stage.tone_map_operator,
                           'clamp_colors': stage.clamp_colors})

            # Add tone map operator-specific parameters.
            operator_params = {'linear': {},
                               'aces_narkowicz': {'aces_narkowicz_exposure_bias': stage.aces_narkowicz_exposure_bias},
                               'aces_unreal': {},
                               'filmic_hejl': {},
                               'filmic_piecewise': {'filmic_piecewise_toe_strength': stage.filmic_piecewise_toe_strength,
                                                    'filmic_piecewise_toe_length': stage.filmic_piecewise_toe_length,
                                                    'filmic_piecewise_shoulder_strength': stage.filmic_piecewise_shoulder_strength,
                                                    'filmic_piecewise_shoulder_length': stage.filmic_piecewise_shoulder_length,
                                                    'filmic_piecewise_shoulder_angle': stage.filmic_piecewise_shoulder_angle},
                               'filmic_uncharted': {'filmic_uncharted_A': stage.filmic_uncharted_A,
                                                    'filmic_uncharted_B': stage.filmic_uncharted_B,
                                                    'filmic_uncharted_C': stage.filmic_uncharted_C,
                                                    'filmic_uncharted_D': stage.filmic_uncharted_D,
                                                    'filmic_uncharted_E': stage.filmic_uncharted_E,
                                                    'filmic_uncharted_F': stage.filmic_uncharted_F,
                                                    'filmic_uncharted_W': stage.filmic_uncharted_W,
                                                    'filmic_uncharted_exposure_bias': stage.filmic_uncharted_exposure_bias},
                               'reinhard': {'reinhard_use_luminance': stage.reinhard_use_luminance},
                               'reinhard_extended': {'reinhard_extended_max_white': stage.reinhard_extended_max_white,
                                                     'reinhard_extended_use_luminance': stage.reinhard_extended_use_luminance}}

            params.update(operator_params[stage.tone_map_operator])

        else:
            assert stage.model == 'vignette_post_processing_stage', stage.model
            params.update({'intensity': stage.intensity,
                           'anisotropy': stage.anisotropy})

        return params

    def __set_post_process(self, depsgraph):
        asr_scene_props = depsgraph.scene_eval.appleseed

        for index, stage in enumerate(asr_scene_props.post_processing_stages):
            params = self.__get_post_processing_stage_params(stage, index)

            post_process = asr.PostProcessingStage(stage.model, stage.name, params)

            logger.debug("Adding Post Process: %s", stage.name)

            self.__frame.post_processing_stages().insert(post_process)

    def __calc_initial_positions(self, depsgraph, engine, objects_to_add):
        logger.debug("appleseed: Setting intial object positions for frame %s", depsgraph.scene_eval.frame_current)

        self.__as_camera_translator.add_cam_xform(0.0, engine)

        for inst in depsgraph.object_instances:
            if inst.show_self:
                obj, inst_id = self.__get_instance_data(inst)
                if obj in objects_to_add.keys():
                    objects_to_add[obj].add_instance_step(0.0, inst_id, inst.matrix_world)

    def __calc_motion_steps(self, depsgraph, engine, objects_to_add):
        self.__current_frame = depsgraph.scene_eval.frame_current

        logger.debug("appleseed: Processing motion steps for frame %s", self.__current_frame)

        for index, time in enumerate(self.__all_times[1:]):
            new_frame = self.__current_frame + time
            int_frame = math.floor(new_frame)
            subframe = new_frame - int_frame

            engine.frame_set(int_frame, subframe=subframe)

            if time in self.__cam_times:
                self.__as_camera_translator.add_cam_xform(time, engine)

            if time in self.__xform_times:
                for inst in depsgraph.object_instances:
                    if inst.show_self:
                        obj, inst_id = self.__get_instance_data(inst)
                        if obj in objects_to_add.keys():
                            objects_to_add[obj].add_instance_step(time, inst_id, inst.matrix_world)

            if time in self.__deform_times:
                for translator in objects_to_add.values():
                    translator.set_deform_key(time, depsgraph, index)

        engine.frame_set(self.__current_frame, subframe=0.0)

    def __load_searchpaths(self):
        logger.debug("appleseed: Loading searchpaths")
        paths = self.__project.get_search_paths()

        paths.extend(path for path in self.__asset_handler.searchpaths if path not in paths)

        self.__project.set_search_paths(paths)

    def __update_frame_size(self):
        params = self.__frame.get_parameters()

        width, height = self.__viewport_resolution

        params['resolution'] = asr.Vector2i(width, height)

        self.__frame.set_parameters(params)

    # Static utility methods
    @staticmethod
    def __get_sub_frames(scene, shutter_length, samples, times):
        assert samples > 1

        segment_size = shutter_length / (samples - 1)

        for seg in range(0, samples):
            times.update({scene.appleseed.shutter_open + (seg * segment_size)})

    @staticmethod
    def __get_instance_data(instance):
        if instance.is_instance:  # Instance was generated by a particle system or dupli object.
            obj = instance.instance_object.original
            inst_id = f"{obj.appleseed.obj_name}|{instance.parent.original.name_full}|{instance.persistent_id[0]}"
        else:  # Instance is a discreet object in the scene.
            obj = instance.object.original
            inst_id = f"{obj.appleseed.obj_name}|{instance.persistent_id[0]}"

        return obj, inst_id

    @staticmethod
    def __round_up_pow2(deformation_blur_samples):
        assert (deformation_blur_samples >= 2)
        return 1 << (deformation_blur_samples - 1).bit_length()
