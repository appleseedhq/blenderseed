
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

import bpy
import appleseed as asr
from .materials import MaterialTranslator
import os
from .. import util


class PreviewRenderer(object):

    def __init__(self, scene):
        self.__scene = scene
        self.__project = None

    @property
    def as_project(self):
        return self.__project

    def translate_preview(self):
        (width, height) = util.get_render_resolution(self.__scene)
        if width <= 96:
            return

        self.__project = asr.Project("preview")

        # Render settings.
        self.__project.add_default_configurations()

        # Create the scene.
        self.__project.set_scene(asr.Scene())

        # Add OSL shader directories to search paths.
        tool_dir, shader_directories = util.get_osl_search_paths()
        paths = self.__project.get_search_paths()
        paths.extend(x for x in shader_directories)
        self.__project.set_search_paths(paths)

        # Create the environment.
        self.__project.get_scene().set_environment(asr.Environment("environment", {}))

        # Create the main assembly.
        self.__project.get_scene().assemblies().insert(asr.Assembly("assembly", {}))
        self.__main_assembly = self.__project.get_scene().assemblies()["assembly"]

        # Instance the main assembly.
        assembly_inst = asr.AssemblyInstance("assembly_inst", {}, "assembly")
        assembly_inst.transform_sequence().set_transform(0.0, asr.Transformd(asr.Matrix4d.identity()))
        self.__project.get_scene().assembly_instances().insert(assembly_inst)

        obj = bpy.context.active_object
        mat = obj.active_material

        self.__create_preview_scene()

        self.__mat_translator = MaterialTranslator(mat)

        self.__mat_translator.create_entities(self.__scene)
        self.__mat_translator.flush_entities(self.__main_assembly)

    def __create_preview_scene(self):
        preview_template_dir = os.path.join(os.path.dirname(os.path.dirname(util.realpath(__file__))), "mat_preview")

        plane = asr.MeshObjectReader.read({}, "plane_obj", {'filename': os.path.join(preview_template_dir, 'material_preview_ground.obj')})

        plane_inst = asr.ObjectInstance("plane", {}, "plane_obj", asr.Matrix4d.identity(), {'default': "plane_mat"}, {})

        sphere = asr.MeshObject("sphere_obj", {'primitive': 'sphere',
                                               'radius': 1,
                                               'resolution_u': 12,
                                               'resolution_v': 12})

        sphere_inst = asr.ObjectInstance("sphere", {}, "sphere_obj", asr.Matrix4d.identity(), {}, {})

        lamp = asr.MeshObjectReader.read({}, "lamp_obj", {'filename': os.path.join(preview_template_dir, 'material_preview_lamp.obj')})

        lamp_inst = asr.ObjectInstance("lamp", {}, "lamp_obj", asr.Matrix4d.identity(), {'default': "lamp_mat"}, {'default': "lamp_mat"})

        lamp_mat = asr.Material("generic_material", "lamp_mat", {'edf': "lamp_edf"})

        lamp_edf = asr.EDF("diffuse_edf", "lamp_edf", {'radiance': 5})

        shader = asr.SurfaceShader("physical_surface_shader", "base_shader", {})
