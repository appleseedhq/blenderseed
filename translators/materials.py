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

from .assethandlers import AssetType
from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class MaterialTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, mat, asset_handler, preview=False):
        super(MaterialTranslator, self).__init__(mat, asset_handler)

        self.__preview = preview

        self.__shader_group = None

        self.__has_shadergroup = False

        self.__volume = None

        if self.bl_node_tree:
            self.__shaders = self.bl_node_tree.nodes

        self.__colors = []

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
        mat_name = self.appleseed_name + "_mat" if not self.__preview else "preview_mat"
        as_mat_data = self.bl_mat.appleseed

        shader_params = {'lighting_samples': as_mat_data.shader_lighting_samples} if hasattr(as_mat_data, "shader_lighting_samples") else {}
        surface_name = "{0}_surface_shader".format(mat_name)
        self.__as_shader = asr.SurfaceShader("physical_surface_shader",
                                             surface_name, shader_params)

        if hasattr(as_mat_data, "mode") and as_mat_data.mode == 'volume':
            vol_name = mat_name + "_volume"

            self.__colors.append(asr.ColorEntity(vol_name + "_absorption_color", {'color_space': 'linear_rgb'},
                                                 self._convert_color(as_mat_data.volume_absorption)))
            self.__colors.append(asr.ColorEntity(vol_name + "_scattering_color", {'color_space': 'linear_rgb'},
                                                 self._convert_color(as_mat_data.volume_scattering)))

            vol_params = {'absorption': vol_name + "_absorption_color",
                          'scattering': vol_name + "_scattering_color",
                          'absorption_multiplier': as_mat_data.volume_absorption_multiplier,
                          'scattering_multiplier': as_mat_data.volume_scattering_multiplier,
                          'phase_function_model': as_mat_data.volume_phase_function_model,
                          'average_cosine': as_mat_data.volume_average_cosine}

            self.__volume = asr.Volume('generic_volume', vol_name, vol_params)

            mat_params = {'surface_shader': "{0}_surface_shader".format(mat_name),
                          'volume': vol_name}

            self.__as_mat = asr.Material('generic_material', mat_name, mat_params)

        else:
            mat_params = {'surface_shader': "{0}_surface_shader".format(mat_name)}
            if self.bl_node_tree:
                shadergroup_name = self.bl_node_tree.name if not self.__preview else "preview_mat_tree"
                mat_params['osl_surface'] = shadergroup_name

                if self.__shader_group is None:
                    self.__shader_group = asr.ShaderGroup(shadergroup_name)

                self.__set_shader_group_parameters(scene)

            self.__as_mat = asr.Material('osl_material', mat_name, mat_params)


    def flush_entities(self, assembly):

        shader_name = self.__as_shader.get_name()
        assembly.surface_shaders().insert(self.__as_shader)
        self.__as_shader = assembly.surface_shaders().get_by_name(shader_name)

        mat_name = self.__as_mat.get_name()
        assembly.materials().insert(self.__as_mat)
        self.__as_mat = assembly.materials().get_by_name(mat_name)

        for index, color in enumerate(self.__colors):
            col_name = color.get_name()
            assembly.colors().insert(color)
            self.__colors[index] = assembly.colors().get_by_name(col_name)

        if self.__volume is not None:
            vol_name = self.__volume.get_name()
            assembly.volumes().insert(self.__volume)
            self.__volume = assembly.volumes().get_by_name(vol_name)

        # Only insert the shader group if one exists and it has not been inserted yet
        if self.__shader_group is not None and not self.__has_shadergroup:
            shader_groupname = self.__shader_group.get_name()
            assembly.shader_groups().insert(self.__shader_group)
            self.__shader_group = assembly.shader_groups().get_by_name(shader_groupname)
            self.__has_shadergroup = True

    def update(self, material, assembly, scene):
        assembly.materials().remove(self.__as_mat)
        assembly.surface_shaders().remove(self.__as_shader)

        if self.__volume is not None:
            assembly.volumes().remove(self.__volume)

        for color in self.__colors:
            assembly.colors().remove(color)

        self._reset(material)

        self.create_entities(scene)
        self.flush_entities(assembly)

    #
    # Internal methods.
    #

    def _reset(self, mat):
        super(MaterialTranslator, self)._reset(mat)

        if self.bl_node_tree:
            self.__shaders = self.bl_node_tree.nodes

        self.__colors = []

        self.__volume = None

    def __set_shader_group_parameters(self, scene):
        surface_shader = None
        for shader in self.__shaders:
            if not isinstance(shader, bpy.types.NodeInternal):
                if shader.node_type == 'osl_surface':
                    surface_shader = shader
                    self.__shader_list = surface_shader.traverse_tree()
                    break

        if surface_shader is None:
            logger.debug("No surface shader for %s", self.__shader_group.get_name())
            return

        self.__shader_group.clear()

        for shader in self.__shader_list:
            parameters = {}
            parameter_types = shader.parameter_types
            shader_keys = dir(shader)

            self.__parse_parameters(parameter_types, parameters, scene, shader, shader_keys)

            shader_file_name = self.asset_handler.process_path(shader.file_name, AssetType.SHADER_ASSET)
            self.__shader_group.add_shader("shader", shader_file_name, shader.name, parameters)

            self.__create_shader_connections(shader)

        surface_shader_file = self.asset_handler.process_path(surface_shader.file_name, AssetType.SHADER_ASSET)

        self.__shader_group.add_shader("surface", surface_shader_file, surface_shader.name, {})

    def __parse_parameters(self, parameter_types, parameters, scene, shader, shader_keys):
        for key in parameter_types:
            if key in shader_keys:
                parameter_value = parameter_types[key]
                parameter = getattr(shader, key)
                if key in shader.filepaths:
                    sub_texture = scene.appleseed.sub_textures
                    parameter = self.asset_handler.process_path(parameter.filepath, AssetType.TEXTURE_ASSET, sub_texture)

                if parameter_value == "int checkbox":
                    parameter_value = "int"
                    parameter = int(parameter)
                if parameter_value in ('color', 'vector', 'normal', 'float[2]'):
                    parameter = " ".join(map(str, parameter))
                if parameter_value == 'float[2]':
                    parameter_value = 'float[]'
                parameters[key] = parameter_value + " " + str(parameter)

    def __create_shader_connections(self, shader):
        for output in shader.outputs:
            if output.is_linked:
                for link in output.links:
                    if link.to_node in self.__shader_list or link.to_node.node_type == 'osl_surface':
                        self.__shader_group.add_connection(shader.name, output.socket_osl_id, link.to_node.name,
                                                           link.to_socket.socket_osl_id)
                    else:
                        continue
