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

from .assethandlers import AssetHandler
from .materials import MaterialTranslator
from ..utils import util


class PreviewRenderer(object):

    def __init__(self):
        self.__project = None

        self.__asset_handler = AssetHandler()

    @property
    def as_project(self):
        return self.__project

    @property
    def asset_handler(self):
        return self.__asset_handler

    def translate_preview(self, scene):
        self.__create_preview_scene(scene)

        self.__generate_material(scene)

        self.__create_material(scene)

        self.__create_config()

        self.__set_searchpaths()

        self.__set_frame(scene)

    def update_preview(self, scene):
        likely_material = self.__get_preview_material(scene)
        self.__mat_translator.update(likely_material, self.__main_assembly, scene)

        as_scene = self.__project.get_scene()
        camera = as_scene.cameras().get_by_name("preview_camera")
        as_scene.cameras().remove(camera)

        self.__create_config()
        self.__create_camera(scene)
        self.__set_frame(scene)
        self.__set_searchpaths()

    def __create_preview_scene(self, scene):
        """This function creates the scene that is used to render material previews.  It consists of:
        A background plane
        A single mesh lamp
        A sphere with the material being previewed
        """

        # Create the project
        self.__project = asr.Project("preview_render")

        # Render settings.
        self.__project.add_default_configurations()

        # Create the scene.
        self.__project.set_scene(asr.Scene())

        preview_template_dir = self.__create_project()

        self.__create_camera(scene)

        plane, plane_bsdf, plane_inst, plane_mat, plane_tex, plane_tex_inst = self.__create_backdrop(preview_template_dir)

        sphere, sphere_inst = self.__create_sphere(preview_template_dir)

        lamp, lamp_edf, lamp_inst, lamp_mat = self.__create_lamp(preview_template_dir)

        # Create the base shader used for all preview set items
        shader = asr.SurfaceShader("physical_surface_shader", "base_shader", {})

        # Insert all objects into the scene
        for obj in lamp:
            self.__main_assembly.objects().insert(obj)
        self.__main_assembly.object_instances().insert(lamp_inst)
        self.__main_assembly.materials().insert(lamp_mat)
        self.__main_assembly.edfs().insert(lamp_edf)
        self.__main_assembly.surface_shaders().insert(shader)
        for obj in sphere:
            self.__main_assembly.objects().insert(obj)
        self.__main_assembly.object_instances().insert(sphere_inst)
        for obj in plane:
            self.__main_assembly.objects().insert(obj)
        self.__main_assembly.object_instances().insert(plane_inst)
        self.__main_assembly.materials().insert(plane_mat)
        self.__main_assembly.bsdfs().insert(plane_bsdf)
        self.__main_assembly.textures().insert(plane_tex)
        self.__main_assembly.texture_instances().insert(plane_tex_inst)

    def __create_project(self):
        # Create the environment.
        self.__project.get_scene().set_environment(asr.Environment("environment", {}))
        # Create the main assembly.
        self.__project.get_scene().assemblies().insert(asr.Assembly("assembly", {}))
        self.__main_assembly = self.__project.get_scene().assemblies()["assembly"]
        # Instance the main assembly.
        assembly_inst = asr.AssemblyInstance("assembly_inst", {}, "assembly")
        assembly_inst.transform_sequence().set_transform(0.0, asr.Transformd(asr.Matrix4d.identity()))
        self.__project.get_scene().assembly_instances().insert(assembly_inst)
        # Path to the .binarymesh models needed for the preview render
        preview_template_dir = os.path.join(os.path.dirname(os.path.dirname(util.realpath(__file__))), "mat_preview")
        return preview_template_dir

    def __create_lamp(self, preview_template_dir):
        # Define the single area lamp used for illumination
        lamp = asr.MeshObjectReader.read(self.__project.get_search_paths(), "lamp_obj",
                                         {'filename': os.path.join(preview_template_dir, 'material_preview_lamp.binarymesh')})
        lamp_matrix = asr.Matrix4d([0.8611875772476196, 0.508287250995636, 0.0, 0.0,
                                    -0.508287250995636, 0.8611875772476196, 0.0, 0.0,
                                    0.0, 0.0, 1.0, 0.0,
                                    0.0, 0.0, 0.0, 1.0])
        lamp_inst = asr.ObjectInstance("lamp", {}, "lamp_obj.part_0", asr.Transformd(lamp_matrix),
                                       {'default': "lamp_mat"}, {'default': "lamp_mat"})
        lamp_mat = asr.Material("generic_material", "lamp_mat", {'edf': "lamp_edf", 'surface_shader': "base_shader"})
        lamp_edf = asr.EDF("diffuse_edf", "lamp_edf", {'radiance': 7})
        return lamp, lamp_edf, lamp_inst, lamp_mat

    def __create_sphere(self, preview_template_dir):
        # Define the sphere preview object.
        sphere = asr.MeshObjectReader.read(self.__project.get_search_paths(), "sphere_obj",
                                           {'filename': os.path.join(preview_template_dir, 'material_preview_sphere.binarymesh')})
        sphere_inst = asr.ObjectInstance("sphere", {}, "sphere_obj.part_0", asr.Transformd(asr.Matrix4d.identity()),
                                         {'default': "preview_mat"}, {'default': "preview_mat"})
        return sphere, sphere_inst

    def __create_backdrop(self, preview_template_dir):
        # Define the background plane
        plane = asr.MeshObjectReader.read([], "plane_obj", {'filename': os.path.join(preview_template_dir,
                                                                                     'material_preview_ground.binarymesh')})
        plane_inst = asr.ObjectInstance("plane", {}, "plane_obj.part_0", asr.Transformd(asr.Matrix4d.identity()),
                                        {'default': "plane_mat"})
        plane_mat = asr.Material("generic_material", "plane_mat", {'bsdf': "plane_bsdf", 'surface_shader': "base_shader"})
        plane_bsdf = asr.BSDF("lambertian_brdf", "plane_bsdf", {'reflectance': "plane_tex"})
        plane_tex = asr.Texture("disk_texture_2d", "plane_tex_tex", {'filename': os.path.join(preview_template_dir,
                                                                                              "checker_texture.png"),
                                                                     'color_space': 'srgb'}, [])
        plane_tex_inst = asr.TextureInstance("plane_tex", {}, "plane_tex_tex", asr.Transformf(asr.Matrix4f.identity()))
        return plane, plane_bsdf, plane_inst, plane_mat, plane_tex, plane_tex_inst

    def __create_camera(self, scene):
        # Define the render camera
        camera = asr.Camera('pinhole_camera', "preview_camera", {"film_width": 0.032,
                                                                 "focal_length": 0.035,
                                                                 "aspect_ratio": util.get_frame_aspect_ratio(scene)})
        camera_matrix = asr.Matrix4d([1.0, 0.0, 0.0, -0.03582507744431496,
                                      0.0, -4.371138828673793e-08, -1.0, -2.135615587234497,
                                      0.0, 1.0, -4.371138828673793e-08, 0.5015512704849243,
                                      0.0, 0.0, 0.0, 1.0])
        camera.transform_sequence().set_transform(0.0, asr.Transformd(camera_matrix))
        self.__project.get_scene().cameras().insert(camera)

    def __create_material(self, scene):
        self.__mat_translator.create_entities(scene)
        self.__mat_translator.flush_entities(self.__main_assembly)

    def __generate_material(self, scene):
        # Collect objects and their materials in a object -> [materials] dictionary.
        likely_material = self.__get_preview_material(scene)

        self.__mat_translator = MaterialTranslator(likely_material, self.asset_handler, preview=True)

    def __get_preview_material(self, scene):
        objects_materials = {}
        for obj in (obj for obj in scene.objects if obj.is_visible(scene) and not obj.hide_render):
            for mat in util.get_instance_materials(obj):
                if mat is not None:
                    if obj.name not in objects_materials.keys():
                        objects_materials[obj] = []
                    objects_materials[obj].append(mat)

        # Find objects that are likely to be the preview objects.
        preview_objects = [o for o in objects_materials.keys() if o.name.startswith('preview')]
        if not preview_objects:
            return

        # Find the materials attached to the likely preview object.
        likely_material = objects_materials[preview_objects[0]]
        if not likely_material:
            return

        return likely_material[0]

    def __create_config(self):
        conf_final = self.as_project.configurations()['final']
        conf_interactive = self.as_project.configurations()['interactive']

        parameters = {"lighting_engine": "pt",
                      'rendering_threads': -1,
                      "pt": {"dl_light_samples": 4,
                             "decorrelate_pixels": True,
                             "enable_ibl": True,
                             "ibl_env_samples": 1,
                             "clamp_roughness": True,
                             "rr_min_path_length": 3,
                             "max_diffuse_bounces": 2,
                             "max_glossy_bounces": 2,
                             "max_specular_bounces": 2,
                             "max_volume_bounces": 2},
                      "pixel_renderer": "uniform",
                      "uniform_pixel_renderer": {"decorrelate_pixels": False,
                                                 "samples": self.__mat_translator.bl_mat.appleseed.preview_quality},
                      "generic_tile_renderer": {"min_samples": self.__mat_translator.bl_mat.appleseed.preview_quality,
                                                "max_samples": self.__mat_translator.bl_mat.appleseed.preview_quality}}

        conf_final.set_parameters(parameters)
        conf_interactive.set_parameters(parameters)

    def __set_searchpaths(self):
        # Add OSL shader directories to search paths.
        paths = self.__project.get_search_paths()

        paths.extend(x for x in self.asset_handler.searchpaths if x not in paths)

        self.__project.set_search_paths(paths)

    def __set_frame(self, scene):
        width, height = util.get_render_resolution(scene)

        frame_params = {
            'resolution': asr.Vector2i(width, height),
            'camera': "preview_camera"}

        frame = asr.Frame("beauty", frame_params)

        self.__project.set_frame(frame)
