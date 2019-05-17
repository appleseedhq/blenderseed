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
from ...logger import get_logger
from ..nodetree import NodeTreeTranslator
from ..textures import TextureTranslator
from ..translator import Translator
from ...utils.path_util import get_osl_search_paths

logger = get_logger()


class LampTranslator(Translator):
    def __init__(self, bl_lamp, asset_handler=None):
        logger.debug("Creating light translator for %s", bl_lamp.name_full)
        super().__init__(bl_lamp, asset_handler=asset_handler)

        self.__matrices = {}
        self.__instances = {}

        self._as_lamp_radiance = None

        self._as_area_lamp_material = None
        self._as_area_lamp_shadergroup = None

    @property
    def bl_lamp(self):
        return self._bl_obj

    def create_entities(self, bl_scene, textures_to_add, as_texture_translators):
        logger.debug("Creating light entity for %s", self.bl_lamp.name_full)
        as_lamp_data = self.bl_lamp.data.appleseed

        self.__lamp_model = self._get_lamp_model()

        if self.bl_lamp.data.type != 'AREA':
            radiance = self._convert_color(as_lamp_data.radiance)
            lamp_radiance_name = f"{self.appleseed_name}_radiance"
            self._as_lamp_radiance = asr.ColorEntity(lamp_radiance_name, {'color_space': 'linear_rgb'}, radiance)

            if self.__lamp_model == 'point_light':
                self.__as_lamp_params = self._get_point_lamp_params()
            if self.__lamp_model == 'spot_light':
                self.__as_lamp_params = self._get_spot_lamp_params(textures_to_add, as_texture_translators)
            if self.__lamp_model == 'directional_light':
                self.__as_lamp_params = self._get_directional_lamp_params()
            if self.__lamp_model == 'sun_light':
                self.__as_lamp_params = self._get_sun_lamp_params()

        else:
            primitive, shape_params = self._get_area_mesh_params()
            mesh_name = f"{self.appleseed_name}_mesh"

            self.__as_area_lamp = asr.Object(primitive, mesh_name, shape_params)

            mat_name = f"{self.appleseed_name}_mat"

            shader_name = f"{self.appleseed_name}_tree"

            if not self.bl_lamp.data.use_nodes:
                self._set_shadergroup()
            else:
                self.__node_tree = NodeTreeTranslator(self.bl_lamp.data.node_tree, self._asset_handler, self.appleseed_name)
                self.__node_tree.create_entities(bl_scene)

            self._as_area_lamp_material = asr.Material('osl_material',
                                                       mat_name,
                                                       {'osl_surface': shader_name})

    def flush_entities(self, as_assembly, as_project):
        logger.debug("Flushing light entity for %s", self.bl_lamp.name_full)
        if self.__lamp_model != 'area_lamp':
            radiance_name = self._as_lamp_radiance.get_name()
            as_assembly.colors().insert(self._as_lamp_radiance)
            self._as_lamp_radiance = as_assembly.colors().get_by_name(radiance_name)

            for key, transform_matrix in self.__matrices.items():
                as_lamp = asr.Light(self.__lamp_model, key, self.__as_lamp_params)
                as_lamp.set_transform(self._convert_matrix(transform_matrix))
                as_assembly.lights().insert(as_lamp)
                self.__instances[key] = as_assembly.lights().get_by_name(key)

        else:
            mat_name = f"{self.appleseed_name}_mat"

            mesh_name = f"{self.appleseed_name}_mesh"

            as_assembly.materials().insert(self._as_area_lamp_material)
            self._as_area_lamp_material = as_assembly.materials().get_by_name(mat_name)

            as_assembly.objects().insert(self.__as_area_lamp)
            self.__as_area_lamp = as_assembly.objects().get_by_name(mesh_name)

            if self._as_area_lamp_shadergroup is not None:
                shadergroup_name = self._as_area_lamp_shadergroup.get_name()
                as_assembly.shader_groups().insert(self._as_area_lamp_shadergroup)
                self._as_area_lamp_shadergroup = as_assembly.shader_groups().get_by_name(shadergroup_name)
            else:
                self.__node_tree.flush_entities(as_assembly, None)

            self.__instance_params = self._get_area_mesh_instance_params()
            for key, transform_matrix in self.__matrices.items():
                inst_name = f"{key}_inst"
                as_area_lamp_mesh_inst = asr.ObjectInstance(inst_name,
                                                            self.__instance_params,
                                                            mesh_name,
                                                            self._convert_area_matrix(transform_matrix),
                                                            {"default": mat_name},
                                                            {"default": "__null_material"})

                as_assembly.object_instances().insert(as_area_lamp_mesh_inst)
                self.__instances[key] = as_assembly.object_instances().get_by_name(inst_name)

    def update_lamp(self, context, as_assembly, textures_to_add, as_texture_translators):
        logger.debug("Updating light translator for %s", self.bl_lamp.name_full)
        if self.__lamp_model != 'area_lamp':
            as_assembly.colors().remove(self._as_lamp_radiance)
            for lamp in self.__instances.values():
                as_assembly.lights().remove(lamp)
        else:
            as_assembly.materials().remove(self._as_area_lamp_material)
            as_assembly.objects().remove(self.__as_area_lamp)
            if self._as_area_lamp_shadergroup is not None:
                as_assembly.shader_groups().remove(self._as_area_lamp_shadergroup)
                self._as_area_lamp_shadergroup = None
            else:
                self.__node_tree.delete(as_assembly)
                self.__node_tree = None
            for mesh_inst in self.__instances.values():
                as_assembly.object_instances().remove(mesh_inst)

        self.__instances.clear()

        self.create_entities(context.evaluated_depsgraph_get().scene, textures_to_add, as_texture_translators)
        self.flush_entities(as_assembly, None)

    def delete_instances(self, as_assembly, as_scene):
        if self.__lamp_model != 'area_lamp':
            for lamp in self.__instances.values():
                as_assembly.lights().remove(lamp)
        else:
            for mesh_inst in self.__instances.values():
                as_assembly.object_instances().remove(mesh_inst)

        self.__instances.clear()

    def xform_update(self, inst_key, bl_matrix, as_assembly, as_scene):
        logger.debug("Updating instances for %s", self.bl_lamp.name_full)
        if self.__lamp_model != 'area_lamp':
            as_lamp = asr.Light(self.__lamp_model, inst_key, self.__as_lamp_params)
            as_lamp.set_transform(self._convert_matrix(bl_matrix))
            as_assembly.lights().insert(as_lamp)
            self.__instances[inst_key] = as_assembly.lights().get_by_name(inst_key)
        else:
            mat_name = f"{self.appleseed_name}_mat"
            mesh_name = f"{self.appleseed_name}_mesh"
            inst_name = f"{inst_key}_inst"
            as_area_lamp_mesh_inst = asr.ObjectInstance(inst_name,
                                                        self.__instance_params,
                                                        mesh_name,
                                                        self._convert_area_matrix(bl_matrix),
                                                        {"default": mat_name},
                                                        {"default": "__null_material"})

            as_assembly.object_instances().insert(as_area_lamp_mesh_inst)
            self.__instances[inst_key] = as_assembly.object_instances().get_by_name(inst_name)

    def delete_lamp(self, as_scene, as_assembly):
        if self.__lamp_model != 'area_lamp':
            as_assembly.colors().remove(self._as_lamp_radiance)
            for lamp in self.__instances.values():
                as_assembly.lights().remove(lamp)
        else:
            as_assembly.materials().remove(self._as_area_lamp_material)
            as_assembly.objects().remove(self.__as_area_lamp)
            if self._as_area_lamp_shadergroup is not None:
                as_assembly.shader_groups().remove(self._as_area_lamp_shadergroup)
            else:
                self.__node_tree.delete(as_assembly)
            for mesh_inst in self.__instances.values():
                as_assembly.object_instances().remove(mesh_inst)

    def add_instance(self, inst_key, bl_matrix):
        logger.debug("Adding instance to %s", self.bl_lamp.name_full)
        self.__matrices[inst_key] = bl_matrix

    def _get_point_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        light_params = {'intensity': f"{self.appleseed_name}_radiance",
                        'intensity_multiplier': as_lamp_data.radiance_multiplier,
                        'exposure': as_lamp_data.exposure,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier}

        return light_params

    def _get_spot_lamp_params(self, textures_to_add, as__texture_translators):
        as_lamp_data = self.bl_lamp.data.appleseed
        outer_angle = math.degrees(self.bl_lamp.data.spot_size)
        inner_angle = (1.0 - self.bl_lamp.data.spot_blend) * outer_angle

        intensity = f"{self.appleseed_name}_radiance"
        intensity_multiplier = as_lamp_data.radiance_multiplier

        if as_lamp_data.radiance_use_tex and as_lamp_data.radiance_tex is not None:
            tex_id = as_lamp_data.radiance_tex.name_full
            if tex_id not in as__texture_translators:
                textures_to_add[tex_id] = TextureTranslator(as_lamp_data.radiance_tex,
                                                            self.asset_handler)
            intensity = f"{as_lamp_data.radiance_tex.name_full}_inst"

        if as_lamp_data.radiance_multiplier_use_tex and as_lamp_data.radiance_multiplier_tex is not None:
            tex_id = as_lamp_data.radiance_multiplier_tex.name_full
            if tex_id not in as__texture_translators:
                textures_to_add[tex_id] = TextureTranslator(as_lamp_data.radiance_multiplier_tex,
                                                            self.asset_handler)
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

    def _get_directional_lamp_params(self):
        as_lamp_data = self.bl_lamp.data.appleseed
        light_params = {'irradiance': f"{self.appleseed_name}_radiance",
                        'irradiance_multiplier': as_lamp_data.radiance_multiplier,
                        'exposure': as_lamp_data.exposure,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier}

        return light_params

    def _get_sun_lamp_params(self):
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

    def _get_lamp_model(self):
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
        as_lamp_data = lamp_data.appleseed

        primitive = as_lamp_data.area_shape

        shape_params = dict()

        if primitive == 'rectangle_object':
            shape_params['width'] = lamp_data.size
            shape_params['height'] = lamp_data.size_y

        elif primitive == 'disk_object':
            shape_params['radius'] = self.bl_lamp.data.size / 2

        else:
            shape_params['radius'] = self.bl_lamp.data.size / 2

        return primitive, shape_params

    def _get_area_mesh_instance_params(self):
        lamp_data = self.bl_lamp.data
        as_lamp_data = lamp_data.appleseed

        lamp_inst_params = {'visibility': {'camera': False}} if not as_lamp_data.area_visibility else {}

        return lamp_inst_params

    def _set_shadergroup(self):
        as_lamp_data = self.bl_lamp.data.appleseed

        shader_name = f"{self.appleseed_name}_tree"

        shader_group = asr.ShaderGroup(shader_name)

        shader_dir_path = self._find_shader_dir()
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

        self._as_area_lamp_shadergroup = shader_group

    def _convert_area_matrix(self, m):
        rot = mathutils.Matrix.Rotation(math.radians(-90), 4, 'X')
        m = m @ rot

        return self._convert_matrix(m)

    @staticmethod
    def _find_shader_dir():
        for directory in get_osl_search_paths():
            if os.path.basename(directory) in ('shaders', 'blenderseed'):

                return directory
