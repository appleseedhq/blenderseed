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

import math

import appleseed as asr

from .translator import Translator


class LampTranslator(Translator):

    def __init__(self, scene, lamp):
        self.__bl_lamp = lamp

    def create_entities(self):
        lamp = self.__bl_lamp
        as_lamp_data = lamp.data.appleseed

        type_mapping = {'POINT': 'point_light',
                        'SPOT': 'spot_light',
                        'HEMI': 'directional_light',
                        'SUN': 'sun_light'}

        self.model = type_mapping[lamp.data.type]
        self.__as_light = asr.Light(self.model, self.__bl_lamp.name, {})
        radiance = self._convert_color(as_lamp_data.radiance)
        lamp_radiance_name = "{0}_radiance".format(self.__bl_lamp.name)
        self.__as_light_radiance = asr.ColorEntity(lamp_radiance_name, {'color_space': 'linear_rgb'}, radiance)

        self.set_parameters()
        self.set_transform()

    def set_parameters(self):
        lamp = self.__bl_lamp.data
        as_lamp_data = lamp.appleseed
        light_params = {'intensity': "{0}_radiance".format(self.__bl_lamp.name),
                        'intensity_multiplier': as_lamp_data.radiance_multiplier,
                        'exposure': as_lamp_data.exposure,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier}

        if self.model == 'spot_light':
            if as_lamp_data.radiance_use_tex and as_lamp_data.radiance_tex != '':
                light_params['intensity'] = as_lamp_data.radiance_tex + "_inst"
            if as_lamp_data.radiance_multiplier_use_tex and as_lamp_data.radiance_multiplier_tex != '':
                light_params['intensity_multiplier'] = as_lamp_data.radiance_multiplier_tex + "_ins"
            outer_angle = math.degrees(lamp.spot_size)
            inner_angle = (1.0 - lamp.spot_blend) * outer_angle
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

        self.__as_light.set_parameters(light_params)

    def set_transform(self):
        self.__as_light.set_transform(self._convert_matrix(self.__bl_lamp.matrix_world))

    def flush_entities(self, project):

        scene = project.get_scene()
        scene.colors().insert(self.__as_light_radiance)
        assembly = scene.assemblies()['assembly']
        assembly.lights().insert(self.__as_light)


class AreaLampTranslator(Translator):

    def __init__(self, scene, lamp):
        self.__bl_lamp = lamp
        self.__lamp_radiance_color = None

    def create_entities(self):
        lamp_data = self.__bl_lamp.data
        as_lamp_data = lamp_data.appleseed

        shape_params = {'primitive': 'grid',
                        'width': self.__bl_lamp.data.size,
                        'height': self.__bl_lamp.data.size}

        if lamp_data.shape == 'RECTANGLE':
            shape_params['height'] = self.__bl_lamp.data.size_y

        self.__as_area_mesh = self.__as_obj = asr.MeshObject(self.__bl_lamp.name + "_mesh", shape_params)

        self.__as_area_mesh_inst = asr.ObjectInstance('area_inst', {}, self.__bl_lamp.name + "_mesh",
                                                      self._convert_matrix(self.__bl_lamp.matrix_world, area=True),
                                                      {"default": "emissive"})

        lamp_params = {'radiance_multiplier': as_lamp_data.radiance_multiplier,
                       'exposure': as_lamp_data.exposure,
                       'angle': as_lamp_data.light_cone_edf_angle,
                       'cast_indirect_light': as_lamp_data.cast_indirect,
                       'importance_multiplier': as_lamp_data.importance_multiplier,
                       'light_near_start': as_lamp_data.light_near_start}

        if as_lamp_data.radiance_use_tex and as_lamp_data.radiance_tex != '':
            lamp_params['radiance'] = as_lamp_data.radiance_tex + "_inst"
        else:
            self.__lamp_radiance_color = asr.ColorEntity("{0}_radiance_color".format(self.__bl_lamp.name),
                                                         {'color_space': 'linear_rgb'},
                                                         self._convert_color(as_lamp_data.radiance))
            lamp_params['radiance'] = "{0}_radiance_color".format(self.__bl_lamp.name)

        if as_lamp_data.radiance_multiplier_use_tex and as_lamp_data.radiance_multiplier_tex != '':
            lamp_params['radiance_multiplier'] = as_lamp_data.radiance_multiplier_tex + "_inst"

        if as_lamp_data.light_emission_profile != 'diffuse_edf':
            del lamp_params['angle']

        self.__edf = asr.EDF(as_lamp_data.light_emission_profile, 'edf_item', lamp_params)

        self.__edf_mat = asr.Material('generic_material', 'emissive', {'surface_shader': 'edf_surface_shader',
                                                                       'edf': 'edf_item'})

        self.__as_shader = asr.SurfaceShader("physical_surface_shader", "edf_surface_shader",
                                             {})

    def set_parameters(self):
        pass

    def set_transform(self):
        pass

    def flush_entities(self, project):

        scene = project.get_scene()
        assembly = scene.assemblies()['assembly']
        if self.__lamp_radiance_color is not None:
            scene.colors().insert(self.__lamp_radiance_color)
        assembly.objects().insert(self.__as_area_mesh)
        assembly.object_instances().insert(self.__as_area_mesh_inst)
        assembly.edfs().insert(self.__edf)
        assembly.surface_shaders().insert(self.__as_shader)
        assembly.materials().insert(self.__edf_mat)
