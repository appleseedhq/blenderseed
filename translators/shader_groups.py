
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

from .translator import Translator

import appleseed as asr
import bpy

from ..util import image_extensions


class ShaderGroupTranslator(Translator):

    def __init__(self, scene, node_group):
        self.__node_group = node_group
        self.__shaders = node_group.nodes
        self.__shader_list = None
        self.__scene = scene

    def create_entities(self):

        self.__shader_group = asr.ShaderGroup(self.__node_group.name)

        self.set_parameters()

    def set_parameters(self):
        surface_shader = None
        for shader in self.__shaders:
            if shader.node_type == 'osl_surface':
                surface_shader = shader
                self.__shader_list = surface_shader.traverse_tree()

        self.__shader_group.clear()

        for shader in self.__shader_list:
            parameters = {}
            parameter_types = shader.parameter_types
            shader_keys = dir(shader)
            for key in parameter_types.keys():
                if key in shader_keys:
                    parameter_value = parameter_types[key]
                    parameter = getattr(shader, key)
                    if key in shader.filepaths:
                        parameter = bpy.path.abspath(parameter)
                        if self.__scene.appleseed.sub_textures is True:
                            if parameter.endswith(image_extensions):
                                base_filename = parameter.split('.')
                                parameter = "{0}.tx".format(base_filename[0])

                    if parameter_value == "int checkbox":
                        parameter_value = "int"
                        parameter = int(parameter)
                    if parameter_value in ('color', 'vector', 'normal', 'float[2]'):
                        parameter = " ".join(map(str, parameter))
                    parameters[key] = parameter_value + " " + str(parameter)

            for socket in shader.inputs:
                if not socket.is_linked:
                    if socket.socket_value != "":
                        parameter_value = parameter_types[socket.socket_osl_id]
                        parameter = socket.get_socket_value(True)
                        if parameter_value in ('color', 'vector', 'normal', 'float[2]'):
                            parameter = " ".join(map(str, parameter))
                            if parameter_value == 'float[2]':
                                parameter_value = 'float[]'
                        parameters[socket.socket_osl_id] = parameter_value + " " + str(parameter)

            self.__shader_group.add_shader("shader", shader.file_name, shader.name, parameters)

            self.__shader_group.add_shader("surface", surface_shader.file_name, surface_shader.name, {})

            for output in shader.outputs:
                if output.is_linked:
                    for link in output.links:
                        self.__shader_group.add_connection(shader.name, output.socket_osl_id, link.to_node.name, link.to_socket.socket_osl_id)

    def flush_entities(self, project):
        scene = project.get_scene()
        assembly = scene.assemblies()['assembly']
        assembly.shader_groups().insert(self.__shader_group)
