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
        self.__bl_lamp_type = self.bl_lamp.data.type

        self.__as_lamp_model = self.__get_lamp_model()

        if self.__bl_lamp_type != 'AREA':
            if self.__as_lamp_model == 'point_light':
                as_lamp_params = self.__get_point_lamp_params()
            if self.__as_lamp_model == 'spot_light':
                as_lamp_params = self.__get_spot_lamp_params()
            if self.__as_lamp_model == 'directional_light':
                as_lamp_params = self.__get_directional_lamp_params()
            if self.__as_lamp_model == 'sun_light':
                as_lamp_params = self.__get_sun_lamp_params()

            self.__as_lamp = asr.Light(self.__as_lamp_model, self.__inst_name, as_lamp_params)
            self.__as_lamp.set_transform(self._convert_matrix(self.__bl_matrix))

        else:
            pass

    def set_xform_step(self, time, bl_matrix):
        pass
