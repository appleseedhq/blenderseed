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


class MaterialTranslator(Translator):

    def __init__(self, scene, mat):
        self.__material = mat

    def create_entities(self):
        as_mat_data = self.__material.appleseed
        self.__as_shader = asr.SurfaceShader("physical_surface_shader",
                                             "{0}_surface_shader".format(self.__material.name),
                                             {'lighting_samples': as_mat_data.shader_lighting_samples})

        osl_params = {'osl_surface': as_mat_data.osl_node_tree.name,
                      'surface_shader': "{0}_surface_shader".format(self.__material.name)}

        self.__as_mat = asr.Material('osl_material', self.__material.name + "_mat", osl_params)

    def flush_entities(self, project):

        scene = project.get_scene()
        assembly = scene.assemblies()['assembly']
        assembly.surface_shaders().insert(self.__as_shader)
        assembly.materials().insert(self.__as_mat)
