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
import os

import mathutils

import appleseed as asr
from ..assethandlers import AssetType
from ...logger import get_logger
from ..nodetree import NodeTreeTranslator
from ..textures import TextureTranslator
from ..translator import Translator
from ...utils.path_util import get_osl_search_paths

logger = get_logger()


class LampTranslator(Translator):
    def __init__(self, bl_lamp, asset_handler):
        super().__init__(bl_lamp, asset_handler)

        self.__lamp_name = str()

        self.__lamp_model = None
        self.__as_lamp_params = None
        self.__as_lamp_radiance = None
        
        self.__matrices = dict()

        self.__as_area_lamp = None
        self.__as_area_lamp_material = None
        self.__as_area_lamp_shadergroup = None
        self.__node_tree = None

    @property
    def bl_lamp(self):
        return self._bl_obj

    def add_instance_step(self, instance_id, bl_matrix):
        inst_id = f"{self.obj_name}|{instance_id}"
        self.__matrices[inst_id] = self.__convert_lamp_matrix(bl_matrix)

    def create_entities(self, bl_scene, context=None):
        self.__lamp_name = f"{self.obj_name}"
        as_lamp_data = self.bl_lamp.data.appleseed

        self.__lamp_model = self.__get_lamp_model()

        if self.bl_lamp.data.type != 'AREA':
            radiance = self._convert_color(as_lamp_data.radiance)
            lamp_radiance_name = f"{self.obj_name}_radiance"

            self.__as_lamp_radiance = asr.ColorEntity(
                lamp_radiance_name,
                {'color_space': 'linear_rgb'},
                radiance)

            if self.__lamp_model == 'point_light':
                self.__as_lamp_params = self.__get_point_lamp_params()
            if self.__lamp_model == 'spot_light':
                self.__as_lamp_params = self.__get_spot_lamp_params()
            if self.__lamp_model == 'directional_light':
                self.__as_lamp_params = self.__get_directional_lamp_params()
            if self.__lamp_model == 'sun_light':
                self.__as_lamp_params = self.__get_sun_lamp_params()
        else:
            shape_params = self._get_area_mesh_params()
            mesh_name = f"{self.obj_name}_mesh"

            self.__as_area_lamp = asr.create_primitive_mesh(mesh_name, shape_params)

            mat_name = f"{self.obj_name}_mat"

            shader_name = f"{self.obj_name}_tree"

            if not self.bl_lamp.data.use_nodes:
                self._set_shadergroup()
            else:
                self.__node_tree = NodeTreeTranslator(self.bl_lamp.data.node_tree, self._asset_handler, self.obj_name)
                self.__node_tree.create_entities(bl_scene)

            self.__as_area_lamp_material = asr.Material('osl_material', mat_name, {'osl_surface': shader_name})

    def flush_entities(self, as_scene, as_main_assembly, as_project):
        if self.__lamp_model != 'area_lamp':
            radiance_name = self.__as_lamp_radiance.get_name()
            as_main_assembly.colors().insert(self.__as_lamp_radiance)
            self.__as_lamp_radiance = as_main_assembly.colors().get_by_name(radiance_name)

            for key, transform_matrix in self.__matrices.items():
                as_lamp = asr.Light(self.__lamp_model, key, self.__as_lamp_params)
                as_lamp.set_transform(transform_matrix)
                as_main_assembly.lights().insert(as_lamp)
                transform_matrix = as_main_assembly.lights().get_by_name(key)
        
        else:
            mat_name = f"{self.obj_name}_mat"

            mesh_name = f"{self.obj_name}_mesh"

            as_main_assembly.materials().insert(self.__as_area_lamp_material)
            self.__as_area_lamp_material = as_main_assembly.materials().get_by_name(mat_name)

            as_main_assembly.objects().insert(self.__as_area_lamp)
            self.__as_area_lamp = as_main_assembly.objects().get_by_name(mesh_name)

            if self.__as_area_lamp_shadergroup is not None:
                shadergroup_name = self.__as_area_lamp_shadergroup.get_name()
                as_main_assembly.shader_groups().insert(self.__as_area_lamp_shadergroup)
                self.__as_area_lamp_shadergroup = as_main_assembly.shader_groups().get_by_name(shadergroup_name)
            else:
                self.__node_tree.flush_entities(as_scene, as_main_assembly, as_project)

            self.__instance_params = self._get_area_mesh_instance_params()

            for key, transform_matrix in self.__matrices.items():
                inst_name = f"{key}_inst"
                as_area_lamp_mesh_inst = asr.ObjectInstance(
                    inst_name,
                    self.__instance_params,
                    mesh_name,
                    transform_matrix,
                    {"default": mat_name},
                    {"default": "__null_material"})

                as_main_assembly.object_instances().insert(as_area_lamp_mesh_inst)
                transform_matrix = as_main_assembly.object_instances().get_by_name(inst_name)

    def __get_point_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        light_params = {
            'intensity': f"{self.obj_name}_radiance",
            'intensity_multiplier': as_lamp_data.radiance_multiplier,
            'exposure': as_lamp_data.exposure,
            'cast_indirect_light': as_lamp_data.cast_indirect,
            'importance_multiplier': as_lamp_data.importance_multiplier}

        return light_params

    def __get_spot_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        outer_angle = math.degrees(self.bl_lamp.data.spot_size)
        inner_angle = (1.0 - self.bl_lamp.data.spot_blend) * outer_angle

        intensity = f"{self.obj_name}_radiance"
        intensity_multiplier = as_lamp_data.radiance_multiplier

        if as_lamp_data.radiance_use_tex and as_lamp_data.radiance_tex is not None:
            intensity = f"{as_lamp_data.radiance_tex.name_full}_inst"

        if as_lamp_data.radiance_multiplier_use_tex and as_lamp_data.radiance_multiplier_tex is not None:
            intensity_multiplier = f"{as_lamp_data.radiance_multiplier_tex.name_full}_inst"

        light_params = {
            'intensity': intensity,
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
        light_params = {
            'irradiance': f"{self.obj_name}_radiance",
            'irradiance_multiplier': as_lamp_data.radiance_multiplier,
            'exposure': as_lamp_data.exposure,
            'cast_indirect_light': as_lamp_data.cast_indirect,
            'importance_multiplier': as_lamp_data.importance_multiplier}

        return light_params

    def __get_sun_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        light_params = {
            'radiance_multiplier': as_lamp_data.radiance_multiplier,
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

        return 'area_lamp'

    def _get_area_mesh_params(self):
        lamp_data = self.bl_lamp.data

        primitive = lamp_data.shape

        shape_params = dict()

        if primitive == 'RECTANGLE':
            shape_params['primitive'] = "grid"
            shape_params['resolution_u'] = 1
            shape_params['resolution_v'] = 1
            shape_params['width'] = lamp_data.size
            shape_params['height'] = lamp_data.size_y

        elif primitive == 'DISK':
            shape_params['primitive'] = "disk"
            shape_params['radius'] = self.bl_lamp.data.size / 2

        elif primitive == 'SQUARE':
            shape_params['primitive'] = "grid"
            shape_params['resolution_u'] = 1
            shape_params['resolution_v'] = 1
            shape_params['width'] = lamp_data.size
            shape_params['height'] = lamp_data.size

        return shape_params

    def _get_area_mesh_instance_params(self):
        lamp_data = self.bl_lamp.data
        as_lamp_data = lamp_data.appleseed

        lamp_inst_params = {'visibility': {'shadow': False}}

        if not as_lamp_data.area_visibility:
            lamp_inst_params['visibility']['camera'] = False

        return lamp_inst_params

    def _set_shadergroup(self):
        as_lamp_data = self.bl_lamp.data.appleseed

        shader_name = f"{self.obj_name}_tree"

        shader_group = asr.ShaderGroup(shader_name)

        shader_dir_path = self.__find_shader_dir()
        shader_path = self._asset_handler.process_path(
            os.path.join(shader_dir_path, "as_blender_areaLight.oso"),
            AssetType.SHADER_ASSET)

        surface_path = self._asset_handler.process_path(
            os.path.join(shader_dir_path, "as_closure2surface.oso"),
            AssetType.SHADER_ASSET)

        lamp_color = " ".join(map(str, as_lamp_data.area_color))

        lamp_params = {
            'in_color': f"color {lamp_color}",
            'in_intensity': f"float {as_lamp_data.area_intensity}",
            'in_intensity_scale': f"float {as_lamp_data.area_intensity_scale}",
            'in_exposure': f"float {as_lamp_data.area_exposure}",
            'in_normalize': f"int {as_lamp_data.area_normalize}"}

        shader_group.add_shader("shader", shader_path, "asAreaLight", lamp_params)
        shader_group.add_shader("surface", surface_path, "asClosure2Surface", {})
        shader_group.add_connection("asAreaLight", "out_output", "asClosure2Surface", "in_input")

        self.__as_area_lamp_shadergroup = shader_group

    def __convert_lamp_matrix(self, m):
        if self._bl_obj.data.type == 'AREA':
            rot = mathutils.Matrix.Rotation(math.radians(-90), 4, 'X')
            m = m @ rot

        matrix = asr.Matrix4d([m[0][0], m[0][1], m[0][2], m[0][3],
                               m[1][0], m[1][1], m[1][2], m[1][3],
                               m[2][0], m[2][1], m[2][2], m[2][3],
                               m[3][0], m[3][1], m[3][2], m[3][3]])

        rotation_modify = asr.Matrix4d.make_rotation(asr.Vector3d(1.0, 0.0, 0.0), math.radians(-90.0))

        matrix = rotation_modify * matrix

        return asr.Transformd(matrix)

    
    @staticmethod
    def __find_shader_dir():
        for directory in get_osl_search_paths():
            if os.path.basename(directory) in ('shaders', 'blenderseed'):

                return directory

