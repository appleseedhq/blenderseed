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
import mathutils
import os

from .translator import Translator, ProjectExportMode
from .assethandlers import AssetType
from ..logger import get_logger
from ..utils.path_util import get_osl_search_paths

logger = get_logger()


class LampTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, lamp, asset_handler):
        super(LampTranslator, self).__init__(lamp, asset_handler)
        self.__radiance_tex = None
        self.__radiance_tex_inst = None
        self.__radiance_mult_tex = None
        self.__radiance_mult_tex_inst = None

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

        model = type_mapping[lamp.data.type]

        light_params = {'intensity': "{0}_radiance".format(self.bl_lamp.name),
                        'intensity_multiplier': as_lamp_data.radiance_multiplier,
                        'exposure': as_lamp_data.exposure,
                        'cast_indirect_light': as_lamp_data.cast_indirect,
                        'importance_multiplier': as_lamp_data.importance_multiplier}

        if model == 'spot_light':
            self.__create_spot_lamp(as_lamp_data, lamp, light_params)

        if model == 'sun_light':
            self.__create_sun_lamp(as_lamp_data, light_params)

        if model == 'directional_light':
            light_params['irradiance'] = light_params.pop('intensity')
            light_params['irradiance_multiplier'] = light_params.pop('intensity_multiplier')

        self.__as_light = asr.Light(model, self.bl_lamp.name, light_params)
        self.__as_light.set_transform(self._convert_matrix(self.bl_lamp.matrix_world))

        radiance = self._convert_color(as_lamp_data.radiance)
        lamp_radiance_name = "{0}_radiance".format(self.bl_lamp.name)
        self.__as_light_radiance = asr.ColorEntity(lamp_radiance_name, {'color_space': 'linear_rgb'}, radiance)

    def flush_entities(self, assembly):

        radiance_name = self.__as_light_radiance.get_name()
        assembly.colors().insert(self.__as_light_radiance)
        self.__as_light_radiance = assembly.colors().get_by_name(radiance_name)

        lamp_name = self.__as_light.get_name()
        assembly.lights().insert(self.__as_light)
        self.__as_light = assembly.lights().get_by_name(lamp_name)

        if self.__radiance_tex is not None:
            rad_tex_name = self.__radiance_tex.get_name()
            assembly.textures().insert(self.__radiance_tex)
            self.__radiance_tex = assembly.textures().get_by_name(rad_tex_name)

        if self.__radiance_tex_inst is not None:
            rad_tex_inst_name = self.__radiance_tex_inst.get_name()
            assembly.texture_instances().insert(self.__radiance_tex_inst)
            self.__radiance_tex_inst = assembly.texture_instances().get_by_name(rad_tex_inst_name)

        if self.__radiance_mult_tex is not None:
            rad_mult_name = self.__radiance_mult_tex.get_name()
            assembly.textures().insert(self.__radiance_mult_tex)
            self.__radiance_mult_tex = assembly.textures().get_by_name(rad_mult_name)

        if self.__radiance_mult_tex_inst is not None:
            rad_mult_tex_inst_name = self.__radiance_mult_tex_inst.get_name()
            assembly.texture_instances().insert(self.__radiance_mult_tex_inst)
            self.__radiance_mult_tex_inst = assembly.texture_instances().get_by_name(rad_mult_tex_inst_name)

    def update(self, lamp, assembly, scene):

        assembly.colors().remove(self.__as_light_radiance)
        assembly.lights().remove(self.__as_light)

        if self.__radiance_tex is not None:
            assembly.textures().remove(self.__radiance_tex)
        if self.__radiance_tex_inst is not None:
            assembly.texture_instances().remove(self.__radiance_tex_inst)
        if self.__radiance_mult_tex is not None:
            assembly.textures().remove(self.__radiance_mult_tex)
        if self.__radiance_mult_tex_inst is not None:
            assembly.texture_instances().remove(self.__radiance_mult_tex_inst)

        self._reset(lamp)
        self.create_entities(scene)
        self.flush_entities(assembly)

    def __create_sun_lamp(self, as_lamp_data, light_params):
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

    def __create_spot_lamp(self, as_lamp_data, lamp, light_params):
        outer_angle = math.degrees(lamp.data.spot_size)
        inner_angle = (1.0 - lamp.data.spot_blend) * outer_angle
        light_params['exposure_multiplier'] = as_lamp_data.exposure_multiplier
        light_params['tilt_angle'] = as_lamp_data.tilt_angle
        light_params['inner_angle'] = inner_angle
        light_params['outer_angle'] = outer_angle
        if as_lamp_data.radiance_use_tex and as_lamp_data.radiance_tex != "":
            tex_path = self.asset_handler.process_path(as_lamp_data.radiance_tex, AssetType.TEXTURE_ASSET)
            light_params['intensity'] = lamp.name + "_radiance_tex_inst"
            self.__radiance_tex = asr.Texture('disk_texture_2d', lamp.name + "_radiance_tex",
                                              {'filename': tex_path,
                                               'color_space': as_lamp_data.radiance_tex_color_space}, [])
            self.__radiance_tex_inst = asr.TextureInstance(lamp.name + "_radiance_tex_inst",
                                                           {'addressing_mode': 'wrap',
                                                            'filtering_mode': 'bilinear'},
                                                           lamp.name + "_radiance_tex",
                                                           asr.Transformf(asr.Matrix4f.identity()))
        if as_lamp_data.radiance_multiplier_use_tex and as_lamp_data.radiance_multiplier_tex != "":
            tex_path = self.asset_handler.process_path(as_lamp_data.radiance_multiplier_tex, AssetType.TEXTURE_ASSET)
            light_params['intensity_multiplier'] = lamp.name + "_radiance_mult_tex_inst"
            self.__radiance_mult_tex = asr.Texture('disk_texture_2d', lamp.name + "_radiance_mult_tex",
                                                   {'filename': tex_path,
                                                    'color_space': as_lamp_data.radiance_multiplier_tex_color_space}, [])
            self.__radiance_mult_tex_inst = asr.TextureInstance(lamp.name + "_radiance_mult_tex_inst",
                                                                {'addressing_mode': 'wrap',
                                                                 'filtering_mode': 'bilinear'},
                                                                lamp.name + "_radiance_mult_tex",
                                                                asr.Transformf(asr.Matrix4f.identity()))

    def _reset(self, lamp):
        super(LampTranslator, self)._reset(lamp)
        self.__radiance_tex = None
        self.__radiance_tex_inst = None
        self.__radiance_mult_tex = None
        self.__radiance_mult_tex_inst = None


class AreaLampTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, lamp, export_mode, asset_handler):
        super(AreaLampTranslator, self).__init__(lamp, asset_handler)
        self.__export_mode = export_mode
        self.__lamp_shader_group = None
        self.__edf_mat = None
        self.__has_shadergroup = False

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
            shape_params['resolution_u'] = 4
            shape_params['resolution_v'] = 4

        mesh_name = self.bl_lamp.name + "_mesh"

        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            self.__as_area_mesh = asr.MeshObject(mesh_name, shape_params)
        else:
            self.__as_area_mesh = asr.create_primitive_mesh(mesh_name, shape_params)

        # Create area light object instance, set visibility flags
        lamp_inst_params = {'visibility': {'camera': False}} if not as_lamp_data.area_visibility else {}

        self.__as_area_mesh_inst = asr.ObjectInstance(self.bl_lamp.name + '_inst', lamp_inst_params, mesh_name,
                                                      self._convert_matrix(self.bl_lamp.matrix_world),
                                                      {"default": lamp_data.name + "_mat"}, {"default": "__null_material"})

        # Emit basic lamp shader group
        if lamp_data.appleseed.osl_node_tree is None:
            self.__create_material(as_lamp_data, lamp_data)

    def flush_entities(self, assembly):
        mesh_name = self.__as_area_mesh.get_name()
        assembly.objects().insert(self.__as_area_mesh)
        self.__as_area_mesh = assembly.objects().get_by_name(mesh_name)

        mesh_inst_name = self.__as_area_mesh_inst.get_name()
        assembly.object_instances().insert(self.__as_area_mesh_inst)
        self.__as_area_mesh_inst = assembly.object_instances().get_by_name(mesh_inst_name)

        if self.__edf_mat is not None:
            edf_name = self.__edf_mat.get_name()
            assembly.materials().insert(self.__edf_mat)
            self.__edf_mat = assembly.materials().get_by_name(edf_name)

        if self.__lamp_shader_group is not None and not self.__has_shadergroup:
            shader_group_name = self.__lamp_shader_group.get_name()
            assembly.shader_groups().insert(self.__lamp_shader_group)
            self.__lamp_shader_group = assembly.shader_groups().get_by_name(shader_group_name)
            self.__has_shadergroup = True

    def update(self, lamp, assembly, scene):
        assembly.objects().remove(self.__as_area_mesh)

        assembly.object_instances().remove(self.__as_area_mesh_inst)

        if self.__edf_mat is not None:
            assembly.materials().remove(self.__edf_mat)

        self._reset(lamp)

        self.create_entities(scene)
        self.flush_entities(assembly)

    #
    # Internal methods.
    #

    def _reset(self, lamp):
        super(AreaLampTranslator, self)._reset(lamp)
        self.__edf_mat = None

    def __create_material(self, as_lamp_data, lamp_data):
        shader_name = self.bl_lamp.name + "_tree"
        if self.__lamp_shader_group is None:
            self.__lamp_shader_group = asr.ShaderGroup(shader_name)
        lamp_params = {'in_color': "color {0}".format(" ".join(map(str, as_lamp_data.area_color))),
                       'in_intensity': "float {0}".format(as_lamp_data.area_intensity),
                       'in_intensity_scale': "float {0}".format(as_lamp_data.area_intensity_scale),
                       'in_exposure': "float {0}".format(as_lamp_data.area_exposure),
                       'in_normalize': "int {0}".format(as_lamp_data.area_normalize)}
        self.__lamp_shader_group.clear()

        shader_dir_path = self.__find_shader_dir()
        shader_path = self.asset_handler.process_path(os.path.join(shader_dir_path, "as_blender_areaLight.oso"), AssetType.SHADER_ASSET)
        surface_path = self.asset_handler.process_path(os.path.join(shader_dir_path, "as_closure2surface.oso"), AssetType.SHADER_ASSET)

        self.__lamp_shader_group.add_shader("shader", shader_path, "asAreaLight", lamp_params)
        self.__lamp_shader_group.add_shader("surface", surface_path, "asClosure2Surface", {})
        self.__lamp_shader_group.add_connection("asAreaLight", "out_output", "asClosure2Surface", "in_input")
        # Emit are lamp material and surface shader.
        self.__edf_mat = asr.Material('osl_material', lamp_data.name + "_mat", {'osl_surface': shader_name})

    def _convert_matrix(self, m):
        rot = mathutils.Matrix.Rotation(math.radians(-90), 4, 'X')
        m = m * rot

        return super(AreaLampTranslator, self)._convert_matrix(m)

    @staticmethod
    def __find_shader_dir():
        for directory in get_osl_search_paths():
            if os.path.basename(directory) in ('shaders', 'blenderseed'):

                return directory
