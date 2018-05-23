
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
import math


class ObjectTranslator(Translator):

    def __init__(self, scene, obj):
        self.__obj = obj
        self.__scene = scene

    def create_entities(self):
        mat_name = self.__obj.material_slots[0].name + "_mat"
        self.__as_obj = asr.MeshObject('mesh', {'primitive': 'sphere',
                                                'radius': 1.0})

        self.__as_obj_instance = asr.ObjectInstance('mesh_inst', {}, 'mesh', self._convert_matrix(self.__obj.matrix_world), {"default": mat_name})

    def set_parameters(self):
        pass

    def set_transform(self):
        pass

    def flush_entities(self, project):

        scene = project.get_scene()
        assembly = scene.assemblies()['assembly']

        assembly.objects().insert(self.__as_obj)
        assembly.object_instances().insert(self.__as_obj_instance)
