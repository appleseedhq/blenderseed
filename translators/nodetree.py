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

import os

import bpy

import appleseed as asr
from .assethandlers import AssetType
from .cycles_shaders import cycles_nodes, parse_cycles_shader
from .translator import Translator
from ..properties.nodes import AppleseedOSLNode
from ..logger import get_logger
from ..utils.util import filter_params

logger = get_logger()


class NodeTreeTranslator(Translator):

    def __init__(self, node_tree, asset_handler, mat_name):
        logger.debug(f"appleseed: Creating node tree translator for {mat_name} node tree")

        super().__init__(node_tree, asset_handler)

        self.__mat_name = mat_name

        self.__as_shader_group = None

    @property
    def bl_nodes(self):
        return self._bl_obj.nodes

    def create_entities(self, depsgraph, engine=None):
        logger.debug(f"appleseed: Creating node tree entitiy for {self.__mat_name} node tree")

        tree_name = f"{self.__mat_name}_tree"

        self.__as_shader_group = asr.ShaderGroup(tree_name)

        self.__create_shadergroup(depsgraph.scene_eval, engine)

    def flush_entities(self, as_scene, as_assembly, as_project):
        logger.debug(f"appleseed: Flushing node tree entity {self.__mat_name} to project")
        shader_groupname = self.__as_shader_group.get_name()
        as_assembly.shader_groups().insert(self.__as_shader_group)
        self.__as_shader_group = as_assembly.shader_groups().get_by_name(shader_groupname)

    def update_nodetree(self, bl_scene, engine=None):
        logger.debug(f"appleseed: Updating node tree entity for {self.__mat_name}")
        self.__create_shadergroup(bl_scene, engine)

    def delete_nodetree(self, as_main_assembly):
        logger.debug(f"appleseed: Deleting node tree entity for {self.__mat_name}")
        as_main_assembly.shader_groups().remove(self.__as_shader_group)
        self.__as_shader_group = None

    def __create_shadergroup(self, bl_scene, engine):
        surface_shader = None
        for node in self.bl_nodes:
            if isinstance(node, AppleseedOSLNode):
                if node.node_type == 'osl_surface':
                    logger.debug(f"appleseed: Found surface shader for {self.__mat_name} node tree")
                    surface_shader = node
                    self.__shader_list = filter_params(self.__traverse_tree(surface_shader, list(), engine))
                    break
                
        # Replaces a Cycles material node behind the scenes
        if surface_shader is None:
            for node in self.bl_nodes:
                if node.name in ('Light Output', 'Material Output'):
                    if node.inputs[0].is_linked:
                        node_connection = node.inputs[0].links[0]
                        replacement_node = self.bl_nodes.new('AppleseedasClosure2SurfaceNode')
                        self._bl_obj.links.new(node_connection.from_socket, replacement_node.inputs[0])
                        self._bl_obj.links.remove(node_connection)
                        surface_shader = replacement_node
                        self.__shader_list = filter_params(self.__traverse_tree(surface_shader, list(), engine))
                        break

        if surface_shader is None:
            logger.debug(f"appleseed: No surface shader for {self.__mat_name} node tree")
            return

        self.__as_shader_group.clear()

        for node in self.__shader_list:
            if isinstance(node, AppleseedOSLNode):  # appleseed nodes
                parameters = dict()
                parameter_types = node.parameter_types

                node_items = node.keys()

                for key in node_items:
                    if key in parameter_types:
                        parameter_value = getattr(node, key)
                        parameter_type = parameter_types[key]

                        if key in node.filepaths:
                            sub_texture = bl_scene.appleseed.sub_textures
                            parameter_value = self._asset_handler.process_path(
                                parameter_value.filepath,
                                AssetType.TEXTURE_ASSET, sub_texture)

                        if parameter_type == "int checkbox":
                            parameter_type = "int"
                            parameter_value = int(parameter_value)
                        elif parameter_type in ('color', 'vector', 'normal', 'point', 'float[2]'):
                            parameter_value = " ".join(map(str, parameter_value))
                            if parameter_type == 'float[2]':
                                parameter_type = 'float[]'

                        parameters[key] = parameter_type + " " + str(parameter_value)
                
                if node.node_type == 'osl':
                    shader_file_name = self._asset_handler.process_path(node.file_name, AssetType.SHADER_ASSET)
                    logger.debug(f"appleseed: Adding {node.name} shader to {self.__mat_name} node tree")
                    self.__as_shader_group.add_shader("shader", shader_file_name, node.name, parameters)
                elif node.node_type == 'osl_script':
                    script = node.script
                    osl_path = bpy.path.abspath(script.filepath, library=script.library)
                    if script.is_in_memory or script.is_dirty or script.is_modified or not os.path.exists(osl_path):
                        source_code = script.as_string()
                    else:
                        code = open(osl_path, 'r')
                        source_code = code.read()
                        code.close()
                    logger.debug(f"appleseed: Adding {node.name} source shader to {self.__mat_name} node tree")
                    self.__as_shader_group.add_source_shader("shader", node.bl_idname, node.name, source_code, parameters)
                
                for output in node.outputs:
                    if output.is_linked:
                        for link in output.links:
                            if link.to_node in self.__shader_list:
                                self.__as_shader_group.add_connection(node.name,
                                                                      output.socket_osl_id,
                                                                      link.to_node.name,
                                                                      link.to_socket.socket_osl_id)
            else:  # Cycles nodes
                parameters, outputs = parse_cycles_shader(node)
                shader_path = os.path.join(self._asset_handler.cycles_osl_path, cycles_nodes[node.bl_idname])
                shader_file_name = self._asset_handler.process_path(shader_path, AssetType.SHADER_ASSET)
                logger.debug(f"appleseed: Adding {node.name} Cycles shader to {self.__mat_name} node tree")
                self.__as_shader_group.add_shader("shader", shader_file_name, node.name, parameters)

                for index, output in enumerate(node.outputs):
                    if output.is_linked:
                        for link in output.links:
                            if link.to_node in self.__shader_list:
                                self.__as_shader_group.add_connection(node.name,
                                                                      outputs[index],
                                                                      link.to_node.name,
                                                                      link.to_socket.socket_osl_id)


        surface_shader_file = self._asset_handler.process_path(
            surface_shader.file_name, AssetType.SHADER_ASSET)

        self.__as_shader_group.add_shader("surface", surface_shader_file, surface_shader.name, {})

    def __traverse_tree(self, node, tree_list, engine):
        for socket in node.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                if linked_node.bl_idname in cycles_nodes.keys() or isinstance(node, AppleseedOSLNode):
                    self.__traverse_tree(linked_node, tree_list, engine)
                else:
                    logger.error(f"Node {linked_node.name} is not a node compatible with appleseed, stopping traversal")
                    engine.report({'ERROR'}, f"Node {linked_node.name} is not a node compatible with appleseed, stopping traversal")

        tree_list.append(node)
        
        return tree_list
