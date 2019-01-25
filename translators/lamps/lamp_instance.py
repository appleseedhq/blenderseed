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
from .lamp import LampTranslator


class LampInstanceTranslator(LampTranslator):
    def __init__(self, bl_lamp, asset_handler, inst_name, bl_matrix):
        super().__init__(bl_lamp, asset_handler=asset_handler)

        self.__inst_name = inst_name
        self.__bl_matrix = bl_matrix

    def create_entities(self, bl_scene):
        super().create_entities(bl_scene)

    def set_xform_step(self, time, bl_matrix):
        pass

    def flush_entities(self, as_assembly):
        super().flush_entities(as_assembly)

        if self.bl_lamp.data.type != 'AREA':
            self.__as_lamp.set_transform(self._convert_matrix(self.__bl_matrix))
        else:
            self.__as_area_lamp_mesh_inst.transform_sequence().set_transform(0.0, self.__convert_area_matrix(self.__bl_matrix))
