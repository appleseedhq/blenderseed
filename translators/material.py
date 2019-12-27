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

import appleseed as asr

from .nodetree import NodeTreeTranslator
from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class MaterialTranslator(Translator):

    def __init__(self, mat, asset_handler):
        super().__init__(mat, asset_handler)

        self.__mat_name = str()

        self.__as_mat_params = dict()
        self.__as_mat = None
        self.__as_shader_params = dict()
        self.__as_shader = None

        self.__as_nodetree = None

    @property
    def bl_mat(self):
        return self._bl_obj

    @property
    def bl_node_tree(self):
        return self._bl_obj.node_tree

    def create_entities(self, bl_scene):
        # Store the name of the material in case it changes later.
        self.bl_mat.appleseed.mat_name = self.obj_name

        mat_name = f"{self.bl_mat.appleseed.mat_name}_mat"
        surface_name = f"{self.bl_mat.appleseed.mat_name}_surface"

        if self.bl_mat.node_tree is not None:
            self.__as_nodetree = NodeTreeTranslator(self.bl_node_tree, self._asset_handler, self.bl_mat.appleseed.mat_name)
            self.__as_nodetree.create_entities(bl_scene)

        self.__as_shader_params = self.__get_shader_params()
        self.__as_mat_params = self.__get_mat_params()

        self.__as_shader = asr.SurfaceShader("physical_surface_shader", surface_name, {})

        self.__as_mat = asr.Material('osl_material', mat_name, {})

        self.__as_mat.set_parameters(self.__as_mat_params)
        self.__as_shader.set_parameters(self.__as_shader_params)

    def flush_entities(self, as_scene, as_assembly, as_project):
        if self.__as_nodetree is not None:
            self.__as_nodetree.flush_entities(as_scene, as_assembly, as_project)

        shader_name = self.__as_shader.get_name()
        as_assembly.surface_shaders().insert(self.__as_shader)
        self.__as_shader = as_assembly.surface_shaders().get_by_name(shader_name)

        mat_name = self.__as_mat.get_name()
        as_assembly.materials().insert(self.__as_mat)
        self.__as_mat = as_assembly.materials().get_by_name(mat_name)

    def update_material(self, bl_scene):
        pass

    def __get_shader_params(self):
        as_mat_data = self.bl_mat.appleseed
        shader_params = {'lighting_samples': as_mat_data.shader_lighting_samples}

        return shader_params

    def __get_mat_params(self):
        mat_params = {'surface_shader': f"{self.bl_mat.appleseed.mat_name}_surface"}

        if self.bl_node_tree is not None:
            mat_params['osl_surface'] = f"{self.bl_mat.appleseed.mat_name}_tree"

        return mat_params