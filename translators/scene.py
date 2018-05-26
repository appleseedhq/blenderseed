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
import bpy

from .camera import CameraTranslator
from .lamps import LampTranslator, AreaLampTranslator
from .materials import MaterialTranslator
from .objects import ObjectTranslator
from .shader_groups import ShaderGroupTranslator
from .translator import ProjectExportMode
from .world import WorldTranslator
from ..util import get_osl_search_paths


class SceneTranslator(object):
    """
    Class that translates a Blender scene to an appleseed project.
    """

    #
    # Constants and settings.
    #

    OBJECT_TYPES_TO_IGNORE = {'ARMATURE'}

    #
    # Object Creation.
    #

    @classmethod
    def create_project_export_translator(cls, scene, filename):
        """
        Create a scene translator to export the scene to an appleseed project on disk.
        """

        translator = cls(scene, ProjectExportMode.PROJECT_EXPORT)

        # Create directories to store geometry and textures in the same
        # directory as the project.

        project_dir = os.path.dirname(filename)

        geometry_dir = os.path.join(project_dir, "_geometry")
        textures_dir = os.path.join(project_dir, "_textures")

        if not os.path.exists(geometry_dir):
            os.makedirs(geometry_dir)

        if not os.path.exists(textures_dir):
            os.makedirs(textures_dir)

        return translator

    @classmethod
    def create_final_render_translator(cls, scene):
        """
        Create a scene translator to export the scene to an in memory appleseed project.
        """

        raise NotImplementedError()

    @classmethod
    def create_interactive_render_translator(cls, scene):
        """
        Create a scene translator to export the scene to an in memory appleseed project
        optimized for quick interactive edits.
        """

        raise NotImplementedError()

    def __init__(self, scene, export_mode):
        """
        Constructor. Do not use it to create instances of this class.
        Use instead SceneTranslator.create_project_export_translator() or
        The other @classmethods.
        """

        self.__scene = scene
        self.__export_mode = export_mode

        # Translators.
        self.__world_translator = None
        self.__camera_translators = {}
        self.__material_translators = {}
        self.__lamp_translators = {}
        self.__object_translators = {}
        self.__osl_translators = {}
        self.__texture_translators = {}

    #
    # Getters & Setters.
    #

    def get_project(self):
        """
        Return the appleseed project.
        """
        return self.__project

    #
    # Scene Translation.
    #

    def translate_scene(self):
        """
        Translate the Blenderscene to an appleseed project.
        """

        self.__create_project()

        self.__translate_render_settings()
        self.__translate_frame()

        self.__create_translators()

        # Create appleseed entities.

        if self.__world_translator:
            self.__world_translator.create_entities()

        for t in self.__camera_translators.values():
            t.create_entities()

        for t in self.__object_translators.values():
            t.create_entities()

        for t in self.__lamp_translators.values():
            t.create_entities()

        for t in self.__osl_translators.values():
            t.create_entities()

        for t in self.__material_translators.values():
            t.create_entities()

        for t in self.__texture_translators.values():
            t.create_entities()

        # todo: repeat for other translators.

        # Insert appleseed entities into the project.

        if self.__world_translator:
            self.__world_translator.flush_entities(self.__project)

        for t in self.__camera_translators.values():
            t.flush_entities(self.__project)

        for t in self.__object_translators.values():
            t.flush_entities(self.__project)

        for t in self.__lamp_translators.values():
            t.flush_entities(self.__project)

        for t in self.__material_translators.values():
            t.flush_entities(self.__project)

        for t in self.__osl_translators.values():
            t.flush_entities(self.__project)

        for t in self.__texture_translators.values():
            t.flush_entities(self.__project)

        # todo: repeat for other translators.

    def write_project(self, filename):
        """Write the appleseed project."""

        asr.ProjectFileWriter().write(
            self.__project,
            filename,
            asr.ProjectFileWriterOptions.OmitWritingGeometryFiles | asr.ProjectFileWriterOptions.OmitHandlingAssetFiles)

    #
    # Internal methods.
    #

    def __create_project(self):
        """Create a default empty project."""

        self.__project = asr.Project(self.__scene.name)

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

    def __translate_render_settings(self):
        """
        Convert render settings (AA samples, lighting engine, ...) to appleseed properties.
        """
        project = self.__project
        scene = self.__scene
        asr_scene_props = scene.appleseed

        conf_final = project.configurations()['final']
        conf_interactive = project.configurations()['interactive']

        parameters = {
            'uniform_pixel_sampler': {'decorrelate_pixels': True if asr_scene_props.decorrelate_pixels else False,
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

        conf_final.set_parameters(parameters)
        conf_interactive.set_parameters(parameters)

    def __translate_frame(self):
        """
        Convert image related settings (resolution, crop windows, AOVs, ...) to appleseed.
        """

        asr_scene_props = self.__scene.appleseed
        scale = self.__scene.render.resolution_percentage / 100.0
        width = int(self.__scene.render.resolution_x * scale)
        height = int(self.__scene.render.resolution_y * scale)

        frame_params = {
            'resolution': asr.Vector2i(width, height),
            'camera': self.__scene.camera.name,
            'tile_size': asr.Vector2i(asr_scene_props.tile_width, asr_scene_props.tile_width),
            'filter': asr_scene_props.pixel_filter,
            'filter_size': asr_scene_props.pixel_filter_size}

        # AOVs.
        aovs = asr.AOVContainer()

        if self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER:
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

        if self.__scene.render.use_border:
            min_x = int(self.__scene.render.border_min_x * width)
            max_x = int(self.__scene.render.border_max_x * width)
            min_y = height - int(self.__scene.render.border_max_y * height) - 1
            max_y = height - int(self.__scene.render.border_min_y * height) - 1
            frame.set_crop_window([min_x, min_y, max_x, max_y])

        self.__project.set_frame(frame)

    def __create_translators(self):
        """
        Create translators for each Blender object.  These translators contain all the functions and information
        necessary to convert Blender objects, lights, cameras and materials into equivalent appleseed items.
        """

        print("[appleseed] Creating translators")
        materials = []

        # Create world translator

        self.__world_translator = WorldTranslator(self.__scene)
        print("[appleseed] Creating world translator for {0}".format(self.__scene.world.name))

        # Create translators for all objects in the scene.

        for obj in self.__scene.objects:

            # Skip object types we don't support
            if obj.type in SceneTranslator.OBJECT_TYPES_TO_IGNORE:
                continue

            if obj.type in 'CAMERA':
                self.__camera_translators[obj.name] = CameraTranslator(self.__scene, obj)
                print("[appleseed] Creating camera translator for {0}".format(obj.name))

            if obj.type in 'LAMP':
                if obj.data.type == 'AREA':
                    print("[appleseed] Creating area lamp translator for {0}".format(obj.name))
                    self.__lamp_translators[obj.name] = AreaLampTranslator(self.__scene, obj)
                    if obj.data.appleseed.area_node_tree is not None:
                        print("[appleseed] Creating shader group translator for {0}".format(obj.name))
                        self.__osl_translators[obj.data.appleseed.area_node_tree.name] = ShaderGroupTranslator(self.__scene, obj.data.appleseed.area_node_tree)
                else:
                    print("[appleseed] Creating lamp translator for {0}".format(obj.name))
                    self.__lamp_translators[obj.name] = LampTranslator(self.__scene, obj)

            if obj.type in 'MESH':
                print("[appleseed] Creating object translator for {0}".format(obj.name))
                self.__object_translators[obj.name] = ObjectTranslator(self.__scene, obj)

                for mat in obj.material_slots:
                    if mat.material not in materials:
                        materials.append(mat.material)

        for mat in materials:
            print("[appleseed] Creating material translator for {0}".format(mat.name))
            self.__material_translators[mat.name] = MaterialTranslator(self.__scene, mat)

            print("[appleseed] Creating shader group translator for {0}".format(mat.name))
            self.__osl_translators[mat.appleseed.osl_node_tree.name] = ShaderGroupTranslator(self.__scene, mat.appleseed.osl_node_tree)

            # Todo: create other translators here...
