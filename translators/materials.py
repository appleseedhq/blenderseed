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

import appleseed as asr

from .translator import Translator

from ..logger import get_logger
logger = get_logger()

class MaterialTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, mat):
        super(MaterialTranslator, self).__init__(mat)

        if self.bl_node_tree:
            self.__shaders = self.bl_node_tree.nodes
            self.__shader_list = None

    #
    # Properties.
    #

    @property
    def bl_mat(self):
        return self._bl_obj

    @property
    def bl_node_tree(self):
        return self.bl_mat.appleseed.osl_node_tree

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        as_mat_data = self.bl_mat.appleseed
        self.__as_shader = asr.SurfaceShader("physical_surface_shader",
                                             "{0}_surface_shader".format(self.bl_mat.name),
                                             {'lighting_samples': as_mat_data.shader_lighting_samples})

        osl_params = {'surface_shader': "{0}_surface_shader".format(self.bl_mat.name)}

        if self.bl_node_tree:
            self.__shader_group = asr.ShaderGroup(self.bl_node_tree.name)
            self.set_shader_group_parameters()

            osl_params['osl_surface'] = as_mat_data.osl_node_tree.name,

        self.__as_mat = asr.Material('osl_material', self.bl_mat.name + "_mat", osl_params)

    def flush_entities(self, assembly):
        assembly.surface_shaders().insert(self.__as_shader)
        assembly.materials().insert(self.__as_mat)

        if self.bl_node_tree:
            assembly.shader_groups().insert(self.__shader_group)

    #
    # Internal methods.
    #

    def set_shader_group_parameters(self):
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
