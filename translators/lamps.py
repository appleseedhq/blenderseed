
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
import mathutils

from .translator import Translator

import math

from ..logger import get_logger
logger = get_logger()


class LampTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, lamp):
        super(LampTranslator, self).__init__(lamp)

    #
    # Properties.
    #

    @property
    def bl_lamp(self):
        return self._bl_obj

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        lamp = self.bl_lamp
        as_lamp_data = lamp.data.appleseed

        type_mapping = {'POINT': 'point_light',
                        'SPOT': 'spot_light',
                        'HEMI': 'directional_light',
                        'SUN': 'sun_light'}

        self.model = type_mapping[lamp.data.type]

        light_params = {'intensity': "{0}_radiance".format(self.bl_lamp.name),
                        'intensity_multiplier': as_lamp_data.radiance_multiplier,
                        'exposure': as_lamp_data.exposure,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier}

        # TODO: Textures for spot lamp
        if self.model == 'spot_light':
            outer_angle = math.degrees(lamp.data.spot_size)
            inner_angle = (1.0 - lamp.data.spot_blend) * outer_angle
            light_params['exposure_multiplier'] = as_lamp_data.exposure_multiplier
            light_params['tilt_angle'] = as_lamp_data.tilt_angle
            light_params['inner_angle'] = inner_angle
            light_params['outer_angle'] = outer_angle
        if self.model == 'directional_light':
            light_params['irradiance'] = light_params.pop('intensity')
            light_params['irradiance_multiplier'] = light_params.pop('intensity_multiplier')
        if self.model == 'sun_light':
            del_list = ['intensity', 'exposure', 'exposure_multiplier']
            for x in del_list:
                try:
                    del light_params[x]
                except:
                    pass
            light_params['radiance_multiplier'] = light_params.pop('intensity_multiplier')
            light_params['size_multiplier'] = as_lamp_data.size_multiplier
            light_params['distance'] = as_lamp_data.distance
            light_params['turbidity'] = as_lamp_data.turbidity
            if as_lamp_data.use_edf:
                light_params['environment_edf'] = 'sky_edf'

        self.__as_light = asr.Light(self.model, self.bl_lamp.name, light_params)
        self.__as_light.set_transform(self._convert_matrix(self.bl_lamp.matrix_world))

        radiance = self._convert_color(as_lamp_data.radiance)
        lamp_radiance_name = "{0}_radiance".format(self.bl_lamp.name)
        self.__as_light_radiance = asr.ColorEntity(lamp_radiance_name, {'color_space': 'linear_rgb'}, radiance)

    def flush_entities(self, assembly):

        assembly.colors().insert(self.__as_light_radiance)
        assembly.lights().insert(self.__as_light)


class AreaLampTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, lamp):
        super(LampTranslator, self).__init__(lamp)
        self.__lamp_shader_group = None

    #
    # Properties.
    #

    @property
    def bl_lamp(self):
        return self._bl_obj

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        lamp_data = self.bl_lamp.data
        as_lamp_data = lamp_data.appleseed

        # Create area light mesh shape
        shape_params = {'primitive': as_lamp_data.area_shape}

        if as_lamp_data.area_shape == 'grid':
            shape_params['width'] = self.bl_lamp.data.size
            shape_params['height'] = self.bl_lamp.data.size

            if lamp_data.shape == 'RECTANGLE':
                shape_params['height'] = self.bl_lamp.data.size_y

        elif as_lamp_data.area_shape == 'disk':
            shape_params['radius'] = self.bl_lamp.data.size / 2

        else:
            shape_params['radius'] = self.bl_lamp.data.size / 2
            shape_params['resolution_u'] = 12
            shape_params['resolution_v'] = 12

        self.__as_area_mesh = asr.MeshObject(self.bl_lamp.name + "_mesh", shape_params)

        # Create area light object instance, set visibility flags
        lamp_inst_params = {'visibility': {'camera': False}} if not as_lamp_data.area_visibility else {}

        self.__as_area_mesh_inst = asr.ObjectInstance('area_inst', lamp_inst_params, self.bl_lamp.name + "_mesh",
                                                      self._convert_matrix(self.bl_lamp.matrix_world),
                                                      {"default": self.bl_lamp.name + "_mat"})

        # Emit basic lamp shader group
        if lamp_data.appleseed.area_node_tree is None:
            shader_name = self.bl_lamp.name + "_tree"
            self.__lamp_shader_group = asr.ShaderGroup(shader_name)

            lamp_params = {'in_color': "color {0}".format(" ".join(map(str, as_lamp_data.area_color))),
                           'in_intensity': "float {0}".format(as_lamp_data.area_intensity),
                           'in_intensity_scale': "float {0}".format(as_lamp_data.area_intensity_scale),
                           'in_exposure': "float {0}".format(as_lamp_data.area_exposure),
                           'in_normalize': "int {0}".format(as_lamp_data.area_normalize)}

            self.__lamp_shader_group.add_shader("shader", "as_blender_areaLight", "asAreaLight", lamp_params)
            self.__lamp_shader_group.add_shader("surface", "as_closure2surface", "asClosure2Surface", {})
            self.__lamp_shader_group.add_connection("asAreaLight", "out_output", "asClosure2Surface", "in_input")
            osl_params = {'osl_surface': shader_name,
                          'surface_shader': "{0}_surface_shader".format(self.bl_lamp.name)}
        else:
            osl_params = {'osl_surface': as_lamp_data.area_node_tree.name,
                          'surface_shader': "{0}_surface_shader".format(self.bl_lamp.name)}

        # Emit are lamp material and surface shader.
        self.__edf_mat = asr.Material('osl_material', self.bl_lamp.name + "_mat", osl_params)

        self.__as_shader = asr.SurfaceShader("physical_surface_shader",
                                             "{0}_surface_shader".format(self.bl_lamp.name), {})

    def flush_entities(self, assembly):
        assembly.objects().insert(self.__as_area_mesh)
        assembly.object_instances().insert(self.__as_area_mesh_inst)
        assembly.surface_shaders().insert(self.__as_shader)
        assembly.materials().insert(self.__edf_mat)
        if self.__lamp_shader_group is not None:
            assembly.shader_groups().insert(self.__lamp_shader_group)

    #
    # Internal methods.
    #

    def _convert_matrix(self, m):
        rot = mathutils.Matrix.Rotation(math.radians(-90), 4, 'X')
        m = rot * m * rot

        return super(AreaLampTranslator, self)._convert_matrix(m)
