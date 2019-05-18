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

import appleseed as asr

from .nodetree import NodeTreeTranslator
from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class MaterialTranslator(Translator):
    """
    This class translates a Blender material data block into its associated appleseed entities (Material and Surface shader)
    """

    def __init__(self, mat, asset_handler):
        logger.debug("Creating translator for %s", mat.name_full)
        super().__init__(mat, asset_handler)

        self.__as_nodetree = None
        self.__as_mat_params = {}
        self.__as_mat = None
        self.__as_shader_params = {}
        self.__as_shader = None
        self.__as_volume_params = {}
        self.__as_volume = None
        self.__as_colors = []

    @property
    def bl_mat(self):
        return self._bl_obj

    @property
    def bl_node_tree(self):
        return self._bl_obj.node_tree

    def create_entities(self, bl_scene):
        logger.debug("Creating entity for %s", self.appleseed_name)
        as_mat_data = self.bl_mat.appleseed

        if self.bl_mat.node_tree is not None:
            self.__as_nodetree = NodeTreeTranslator(self.bl_mat.node_tree,
                                                    self.asset_handler,
                                                    self.appleseed_name)
            self.__as_nodetree.create_entities(bl_scene)

        mat_name = f"{self.appleseed_name}_mat"
        surface_name = f"{self.appleseed_name}_surface"

        self.__as_shader_params = self.__get_shader_params()

        self.__as_shader = asr.SurfaceShader("physical_surface_shader",
                                             surface_name, {})

        self.__as_mat_params = self.__get_mat_params()

        if as_mat_data.mode == 'surface':
            self.__as_mat = asr.Material('osl_material', mat_name, {})
        else:
            vol_name = f"{self.appleseed_name}_volume"

            self.__as_volume_params = self.__get_vol_params()

            self.__as_colors.append(asr.ColorEntity(f"{vol_name}_absorption_color",
                                                    {'color_space': 'linear_rgb'},
                                                    self._convert_color(as_mat_data.volume_absorption)))

            self.__as_colors.append(asr.ColorEntity(f"{vol_name}_scattering_color",
                                                    {'color_space': 'linear_rgb'},
                                                    self._convert_color(as_mat_data.volume_scattering)))

            self.__as_mat = asr.Material('generic_material',
                                         mat_name,
                                         {})
            self.__as_volume = asr.Volume('generic_volume',
                                          vol_name,
                                          {})
            self.__as_volume.set_parameters(self.__as_volume_params)

        self.__as_mat.set_parameters(self.__as_mat_params)
        self.__as_shader.set_parameters(self.__as_shader_params)

    def flush_entities(self, as_assembly, as_project):
        logger.debug("Flushing entity for %s", self.appleseed_name)

        if self.__as_nodetree is not None:
            self.__as_nodetree.flush_entities(as_assembly, as_project)

        shader_name = self.__as_shader.get_name()
        as_assembly.surface_shaders().insert(self.__as_shader)
        self.__as_shader = as_assembly.surface_shaders().get_by_name(shader_name)

        mat_name = self.__as_mat.get_name()
        as_assembly.materials().insert(self.__as_mat)
        self.__as_mat = as_assembly.materials().get_by_name(mat_name)

        for index, color in enumerate(self.__as_colors):
            col_name = color.get_name()
            as_assembly.colors().insert(color)
            self.__as_colors[index] = as_assembly.colors().get_by_name(col_name)

        if self.__as_volume is not None:
            vol_name = self.__as_volume.get_name()
            as_assembly.volumes().insert(self.__as_volume)
            self.__as_volume = as_assembly.volumes().get_by_name(vol_name)

    def update_material(self, context, depsgraph, as_assembly):
        logger.debug("Updating translator for %s", self.appleseed_name)

        if self.__as_nodetree is not None:
            self.__as_nodetree.delete(as_assembly)

        as_assembly.surface_shaders().remove(self.__as_shader)
        as_assembly.materials().remove(self.__as_mat)

        for color in self.__as_colors:
            as_assembly.colors().remove(color)

        self.__as_colors = []

        self.create_entities(depsgraph.scene_eval)
        self.flush_entities(as_assembly, None)

    def __get_shader_params(self):
        as_mat_data = self.bl_mat.appleseed
        shader_params = {'lighting_samples': as_mat_data.shader_lighting_samples}

        return shader_params

    def __get_mat_params(self):
        mat_params = {'surface_shader': f"{self.appleseed_name}_surface"}

        if self.bl_mat.appleseed.mode == 'volume':
            mat_params['volume'] = f"{self.appleseed_name}_volume"

        if self.bl_node_tree is not None and self.bl_mat.appleseed.mode == 'surface':
            nodetree_name = self.bl_node_tree.name_full
            mat_params['osl_surface'] = f"{self.appleseed_name}_tree"

        return mat_params

    def __get_vol_params(self):
        as_mat_data = self.bl_mat.appleseed
        vol_name = f"{self.appleseed_name}_volume"

        vol_params = {'absorption': vol_name + "_absorption_color",
                      'scattering': vol_name + "_scattering_color",
                      'absorption_multiplier': as_mat_data.volume_absorption_multiplier,
                      'scattering_multiplier': as_mat_data.volume_scattering_multiplier,
                      'phase_function_model': as_mat_data.volume_phase_function_model,
                      'average_cosine': as_mat_data.volume_average_cosine}

        return vol_params
