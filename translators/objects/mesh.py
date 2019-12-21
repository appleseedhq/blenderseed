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

import appleseed as asr
from ..translator import Translator
from ..utilites import ProjectExportMode
from ...logger import get_logger
from ...utils.util import is_object_deforming, Timer

logger = get_logger()


class MeshTranslator(Translator):
    def __init__(self, bl_obj, export_mode, asset_handler, xform_times):
        super().__init__(bl_obj, asset_handler, xform_times)

        self.__export_mode = export_mode

    def add_instance_step(self, instance_id, bl_matrix):
        inst_id = f"{self.bl_obj_name}|{instance_id}"
        self._instance_lib.add_xform_step(inst_id, self._convert_matrix(bl_matrix))

    def create_entities(self, bl_scene, context=None):
        pass

    def flush_entities(self, as_main_assembly, as_project):
        pass

    def set_deform_key(self, time, depsgraph, index):
        pass
