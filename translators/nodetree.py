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

import os

import bpy
import appleseed as asr

from .assethandlers import AssetType
from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class NodeTreeTranslator(Translator):
    """
    This class translates a Blender node tree into an appleseed OSL shader group
    """

    def __init__(self, node_tree, asset_handler):
        super().__init__(node_tree, asset_handler=asset_handler)

        self.__as_shader_group = None

    @property
    def bl_nodes(self):
        return self._bl_obj.nodes

    def create_entities(self, bl_scene):
        tree_name = f"{self.appleseed_name}_tree"

        self.__as_shader_group = asr.ShaderGroup(tree_name)

        self.__create_shadergroup(bl_scene)

    def flush_entities(self, as_assembly, as_project):
        shader_groupname = self.__as_shader_group.get_name()
        as_assembly.shader_groups().insert(self.__as_shader_group)
        self.__as_shader_group = as_assembly.shader_groups().get_by_name(shader_groupname)

    def __create_shadergroup(self, bl_scene):
        surface_shader = None
        for node in self.bl_nodes:
            if node.node_type == 'osl_surface':
                surface_shader = node
                self.__shader_list = surface_shader.traverse_tree()

        if surface_shader is None:
            logger.debug("No surface shader for %s", self.__as_shader_group.get_name())
            return

        self.__as_shader_group.clear()

        for node in self.__shader_list:
            parameters = {}
            parameter_types = node.parameter_types

            for key, parameter in node.items():
                if key in parameter_types:
                    parameter_value = parameter_types[key]

                    if key in node.filepaths:
                        sub_texture = bl_scene.appleseed.sub_textures
                        parameter = self.asset_handler.process_path(parameter.filepath,
                                                                    AssetType.TEXTURE_ASSET, sub_texture)

                    if parameter_value == "int checkbox":
                        parameter_value = "int"
                        parameter = int(parameter)
                    if parameter_value in ('color', 'vector', 'normal'):
                        parameter = " ".join(map(str, parameter))
                    if parameter_value == 'float[2]':
                        parameter_value = 'float[]'
                    parameters[key] = parameter_value + " " + str(parameter)

            if node.node_type == 'osl':
                shader_file_name = self.asset_handler.process_path(node.file_name,
                                                                   AssetType.SHADER_ASSET)
                self.__as_shader_group.add_shader("shader",
                                                  shader_file_name,
                                                  node.name,
                                                  parameters)
            elif node.node_type == 'osl_script':
                script = node.script
                osl_path = bpy.path.abspath(script.filepath, library=script.library)
                if script.is_in_memory or script.is_dirty or script.is_modified or not os.path.exists(osl_path):
                    source_code = script.as_string()
                else:
                    code = open(osl_path, 'r')
                    source_code = code.read()
                    code.close()

                self.__as_shader_group.add_source_shader("shader",
                                                         node.bl_idname,
                                                         node.name,
                                                         source_code,
                                                         parameters)

            for output in node.outputs:
                if output.is_linked:
                    for link in output.links:
                        if link.to_node in self.__shader_list or link.to_node.node_type == 'osl_surface':
                            self.__as_shader_group.add_connection(node.name,
                                                                  output.socket_osl_id,
                                                                  link.to_node.name,
                                                                  link.to_socket.socket_osl_id)

        surface_shader_file = self.asset_handler.process_path(surface_shader.file_name,
                                                              AssetType.SHADER_ASSET)

        self.__as_shader_group.add_shader("surface",
                                          surface_shader_file,
                                          surface_shader.name, {})
