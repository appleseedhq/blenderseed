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

import math
import os

import mathutils

import appleseed as asr

from ..assethandlers import AssetType
from ..translator import Translator
from ...utils.path_util import get_osl_search_paths


class LampTranslator(Translator):
    def __init__(self, bl_lamp, asset_handler=None):
        super().__init__(bl_lamp, asset_handler=asset_handler)

        self.__as_lamp_radiance = None
        self.__as_lamp = None

        self.__as_area_lamp_material = None
        self.__as_area_lamp_shadergroup = None
        self.__as_area_lamp_mesh = None
        self.__as_area_lamp_mesh_inst = None

    @property
    def bl_lamp(self):
        return self._bl_obj

    def create_entities(self, bl_scene):
        as_lamp_data = self.bl_lamp.data.appleseed

        lamp_model = self.__get_lamp_model()

        if self.bl_lamp.data.type != 'AREA':
            if lamp_model == 'point_light':
                as_lamp_params = self.__get_point_lamp_params()
            if lamp_model == 'spot_light':
                as_lamp_params = self.__get_spot_lamp_params()
            if lamp_model == 'directional_light':
                as_lamp_params = self.__get_directional_lamp_params()
            if lamp_model == 'sun_light':
                as_lamp_params = self.__get_sun_lamp_params()

            self.__as_lamp = asr.Light(lamp_model, self.appleseed_name, as_lamp_params)

            radiance = self._convert_color(as_lamp_data.radiance)
            lamp_radiance_name = f"{self.appleseed_name}_radiance"
            self.__as_lamp_radiance = asr.ColorEntity(lamp_radiance_name, {'color_space': 'linear_rgb'}, radiance)
            
        else:
            shape_params = self.__get_area_mesh_params()
            mesh_name = f"{self.bl_lamp.name_full}_mesh"

            self.__as_area_lamp_mesh = asr.create_primitive_mesh(mesh_name, shape_params)

            inst_name = f"{self.bl_lamp.name_full}_inst"
            instance_params = self.__get_area_mesh_instance_params()
            mat_name = f"{self.bl_lamp.name_full}_mat"

            self.__as_area_lamp_mesh_inst = asr.ObjectInstance(inst_name,
                                                               instance_params,
                                                               mesh_name,
                                                               asr.TransformSequence(),
                                                               {"default": mat_name}, {"default": "__null_material"})

            shader_name = f"{self.bl_lamp.name_full}_tree"

            if as_lamp_data.osl_node_tree is None:
                self.__as_area_lamp_shadergroup = self.__set_shadergroup()

            self.__as_area_lamp_material = asr.Material('osl_material',
                                                        mat_name,
                                                        {'osl_surface': shader_name})

    def flush_entities(self, as_assembly):
        if self.bl_lamp.data.type != 'AREA':
            self.__as_lamp.set_transform(self._convert_matrix(self.bl_lamp.matrix_world))
            as_assembly.lights().insert(self.__as_lamp)
            self.__as_lamp = as_assembly.lights().get_by_name(self.appleseed_name)

            as_assembly.colors().insert(self.__as_lamp_radiance)
            self.__as_lamp_radiance = as_assembly.colors().get_by_name(f"{self.appleseed_name}_radiance")

        else:
            self.__as_area_lamp_mesh_inst.transform_sequence().set_transform(0.0, self.__convert_area_matrix(self.bl_lamp.matrix_world))
            mesh_name = self.__as_area_lamp_mesh.get_name()
            mesh_inst_name = self.__as_area_lamp_mesh_inst.get_name()
            mat_name = self.__as_area_lamp_material.get_name()

            as_assembly.materials().insert(self.__as_area_lamp_material)
            self.__as_area_lamp_material = as_assembly.materials().get_by_name(mat_name)

            as_assembly.objects().insert(self.__as_area_lamp_mesh)
            self.__as_area_lamp_mesh = as_assembly.objects().get_by_name(mesh_name)

            as_assembly.object_instances().insert(self.__as_area_lamp_mesh_inst)
            self.__as_area_lamp_mesh_inst = as_assembly.object_instances().get_by_name(mesh_inst_name)

            if self.__as_area_lamp_shadergroup is not None:
                shadergroup_name = self.__as_area_lamp_shadergroup.get_name()
                as_assembly.shader_groups().insert(self.__as_area_lamp_shadergroup)
                self.__as_area_lamp_shadergroup = as_assembly.shader_groups().get_by_name(shadergroup_name)

    def set_xform_step(self, time, bl_matrix):
        pass

    def __get_point_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        light_params = {'intensity': f"{self.appleseed_name}_radiance",
                        'intensity_multiplier': as_lamp_data.radiance_multiplier,
                        'exposure': as_lamp_data.exposure,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier}

        return light_params

    def __get_spot_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        outer_angle = math.degrees(self.bl_lamp.data.spot_size)
        inner_angle = (1.0 - self.bl_lamp.data.spot_blend) * outer_angle

        intensity = f"{self.appleseed_name}_radiance"
        intensity_multiplier = as_lamp_data.radiance_multiplier

        if as_lamp_data.radiance_use_tex and as_lamp_data.radiance_tex is not None:
            intensity = f"{as_lamp_data.radiance_tex.name_full}_inst"
        if as_lamp_data.radiance_multiplier_use_tex and as_lamp_data.radiance_multiplier_tex is not None:
            intensity_multiplier = f"{as_lamp_data.radiance_multiplier_tex.name_full}_inst"

        light_params = {'intensity': intensity,
                        'intensity_multiplier': intensity_multiplier,
                        'exposure': as_lamp_data.exposure,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier,
                        'exposure_multiplier': as_lamp_data.exposure_multiplier,
                        'tilt_angle': as_lamp_data.tilt_angle,
                        'inner_angle': inner_angle,
                        'outer_angle': outer_angle}

        return light_params

    def __get_directional_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        light_params = {'irradiance': f"{self.appleseed_name}_radiance",
                        'irradiance_multiplier': as_lamp_data.radiance_multiplier,
                        'exposure': as_lamp_data.exposure,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier}

        return light_params

    def __get_sun_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        light_params = {'radiance_multiplier': as_lamp_data.radiance_multiplier,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier,
                        'size_multiplier': as_lamp_data.size_multiplier,
                        'distance': as_lamp_data.distance,
                        'turbidity': as_lamp_data.turbidity}

        if as_lamp_data.use_edf:
            light_params['environment_edf'] = 'sky_edf'

        return light_params

    def __get_lamp_model(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        lamp_type = self.bl_lamp.data.type

        if lamp_type == 'POINT':
            return 'point_light'
        if lamp_type == 'SPOT':
            return 'spot_light'
        if lamp_type == 'SUN' and as_lamp_data.sun_mode == 'distant':
            return 'directional_light'
        if lamp_type == 'SUN' and as_lamp_data.sun_mode == 'sun':
            return 'sun_light'

    def __get_area_mesh_params(self):
        lamp_data = self.bl_lamp.data
        as_lamp_data = lamp_data.appleseed

        shape_params = {'primitive': as_lamp_data.area_shape}

        if as_lamp_data.area_shape == 'grid':
            shape_params['width'] = lamp_data.size
            shape_params['height'] = lamp_data.size_y

        elif as_lamp_data.area_shape == 'disk':
            shape_params['radius'] = self.bl_lamp.data.size / 2

        else:
            shape_params['radius'] = self.bl_lamp.data.size / 2
            shape_params['resolution_u'] = 4
            shape_params['resolution_v'] = 4

        return shape_params

    def __get_area_mesh_instance_params(self):
        lamp_data = self.bl_lamp.data
        as_lamp_data = lamp_data.appleseed

        lamp_inst_params = {'visibility': {'camera': False}} if not as_lamp_data.area_visibility else {}

        return lamp_inst_params

    def __set_shadergroup(self):
        as_lamp_data = self.bl_lamp.data.appleseed

        shader_name = f"{self.bl_lamp.name_full}_tree"

        if self.__as_area_lamp_shadergroup is None:
            shader_group = asr.ShaderGroup(shader_name)
        else:
            shader_group = self.__as_area_lamp_shadergroup

        shader_group.clear()

        shader_dir_path = self.__find_shader_dir()
        shader_path = self.asset_handler.process_path(os.path.join(shader_dir_path, "as_blender_areaLight.oso"), AssetType.SHADER_ASSET)
        surface_path = self.asset_handler.process_path(os.path.join(shader_dir_path, "as_closure2surface.oso"), AssetType.SHADER_ASSET)

        lamp_color = " ".join(map(str, as_lamp_data.area_color))

        lamp_params = {'in_color': f"color {lamp_color}",
                       'in_intensity': f"float {as_lamp_data.area_intensity}",
                       'in_intensity_scale': f"float {as_lamp_data.area_intensity_scale}",
                       'in_exposure': f"float {as_lamp_data.area_exposure}",
                       'in_normalize': f"int {as_lamp_data.area_normalize}"}

        shader_group.add_shader("shader", shader_path, "asAreaLight", lamp_params)
        shader_group.add_shader("surface", surface_path, "asClosure2Surface", {})
        shader_group.add_connection("asAreaLight", "out_output", "asClosure2Surface", "in_input")

        return shader_group

    def __convert_area_matrix(self, m):
        rot = mathutils.Matrix.Rotation(math.radians(-90), 4, 'X')
        m = m @ rot

        return self._convert_matrix(m)

    @staticmethod
    def __find_shader_dir():
        for directory in get_osl_search_paths():
            if os.path.basename(directory) in ('shaders', 'blenderseed'):

                return directory
