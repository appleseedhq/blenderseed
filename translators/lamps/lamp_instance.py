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

        self.__as_lamp = None

        self._lamp_name = inst_name

        self.__as_area_lamp_mesh = None
        self.__as_area_lamp_mesh_inst = None

    def create_entities(self, bl_scene):
        lamp_model = self._get_lamp_model()

        if self.bl_lamp.data.type != 'AREA':
            if lamp_model == 'point_light':
                as_lamp_params = self._get_point_lamp_params()
            if lamp_model == 'spot_light':
                as_lamp_params = self._get_spot_lamp_params()
            if lamp_model == 'directional_light':
                as_lamp_params = self._get_directional_lamp_params()
            if lamp_model == 'sun_light':
                as_lamp_params = self._get_sun_lamp_params()

            self.__as_lamp = asr.Light(lamp_model, self._lamp_name, as_lamp_params)

        else:
            shape_params = self._get_area_mesh_params()
            mesh_name = f"{self.__inst_name}_mesh"

            self.__as_area_lamp_mesh = asr.create_primitive_mesh(mesh_name, shape_params)

    def set_xform_step(self, time, bl_matrix):
        pass

    def flush_entities(self, as_assembly):
        if self.bl_lamp.data.type != 'AREA':
            self.__as_lamp.set_transform(self._convert_matrix(self.__bl_matrix))
            as_assembly.lights().insert(self.__as_lamp)

        else:
            mesh_name = f"{self.__inst_name}_mesh"
            inst_name = f"{self.__inst_name}_inst"
            mat_name = f"{self.appleseed_name}_mat"
            instance_params = self._get_area_mesh_instance_params()

            self.__as_area_lamp_mesh_inst = asr.ObjectInstance(inst_name,
                                                              instance_params,
                                                              mesh_name,
                                                              self._convert_area_matrix(self.__bl_matrix),
                                                              {"default": mat_name}, {"default": "__null_material"})


            as_assembly.objects().insert(self.__as_area_lamp_mesh)
            self.__as_area_lamp_mesh = as_assembly.objects().get_by_name(mesh_name)

            as_assembly.object_instances().insert(self.__as_area_lamp_mesh_inst)
            self.__as_area_lamp_mesh_inst = as_assembly.object_instances().get_by_name(inst_name)
