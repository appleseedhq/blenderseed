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

import math

import appleseed as asr
from ..logger import get_logger

logger = get_logger()


class Translator(object):

    # Constructor.
    def __init__(self, bl_obj, asset_handler, x_form_times):
        self._asset_handler = asset_handler
        self._bl_obj = bl_obj
        self._instance_lib = asr.BlTransformLibrary(x_form_times)

    @property
    def obj_name(self):
        return self._bl_obj.name_full

    @property
    def instances_size(self):
        return self._instance_lib.get_size()

    def add_instance_step(self, instance_id, bl_matrix):
        raise NotImplementedError   

    def create_entities(self, bl_scene, context=None):
        raise NotImplementedError

    def flush_entities(self, as_scene, as_main_assembly, as_project):
        raise NotImplementedError

    @staticmethod
    def _convert_matrix(m):

        return [m[0][0], m[0][1], m[0][2], m[0][3],
                m[1][0], m[1][1], m[1][2], m[1][3],
                m[2][0], m[2][1], m[2][2], m[2][3],
                m[3][0], m[3][1], m[3][2], m[3][3]]

    @staticmethod
    def _convert_color(color):

        return [color[0], color[1], color[2]]
