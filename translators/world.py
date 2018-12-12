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
from .assethandlers import AssetType
from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class WorldTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, scene, asset_handler):
        super(WorldTranslator, self).__init__(scene, asset_handler)
        self.__env_tex = None
        self.__env_tex_inst = None
        self.__colors = []

    #
    # Properties.
    #

    @property
    def bl_scene(self):
        return self._bl_obj

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        as_sky = self.bl_scene.world.appleseed_sky
        env_type = as_sky.env_type
        if env_type == 'sunsky':
            env_type = as_sky.sun_model

        if env_type == 'constant':
            self.__colors.append(asr.ColorEntity('horizon_radiance_color', {'color_space': 'linear_rgb'},
                                                 self._convert_color(self.bl_scene.world.horizon_color)))

        elif env_type in ('gradient', 'constant_hemisphere'):
            self.__colors.append(asr.ColorEntity('horizon_radiance_color', {'color_space': 'srgb'},
                                                 self._convert_color(self.bl_scene.world.horizon_color)))
            self.__colors.append(asr.ColorEntity('zenith_radiance_color', {'color_space': 'linear_rgb'},
                                                 self._convert_color(self.bl_scene.world.zenith_color)))

        if env_type in ('latlong_map', 'mirrorball_map'):
            try:
                filename = self.asset_handler.process_path(as_sky.env_tex.filepath, AssetType.TEXTURE_ASSET)
            except:
                logger.warning("No Texture Selected!")
                filename = ""
                
            tex_inst_params = {'addressing_mode': 'wrap',
                               'filtering_mode': 'bilinear'}

            self.__env_tex = asr.Texture('disk_texture_2d', 'environment_tex', {'filename': filename,
                                                                                'color_space': as_sky.env_tex_colorspace}, [])

            self.__env_tex_inst = asr.TextureInstance('environment_tex_inst', tex_inst_params, 'environment_tex',
                                                      asr.Transformf(asr.Matrix4f.identity()))

        if env_type == 'latlong_map':
            edf_params = {'radiance': "environment_tex_inst",
                          'radiance_multiplier': as_sky.env_tex_mult,
                          'exposure': as_sky.env_exposure}

        elif env_type == 'mirrorball_map':
            edf_params = {'radiance': "environment_tex_inst",
                          'exposure': as_sky.env_exposure,
                          'radiance_multiplier': as_sky.env_tex_mult}

        elif env_type == 'constant':
            edf_params = {'radiance': 'horizon_radiance_color'}

        elif env_type == 'gradient':
            edf_params = {'horizon_radiance': "horizon_radiance_color",
                          'zenith_radiance': "zenith_radiance_color"}

        elif env_type == 'constant_hemisphere':
            edf_params = {'lower_hemi_radiance': "horizon_radiance_color",
                          'upper_hemi_radiance': "zenith_radiance_color"}

        else:
            edf_params = {'ground_albedo': as_sky.ground_albedo,
                          'sun_phi': as_sky.sun_phi,
                          'sun_theta': as_sky.sun_theta,
                          'turbidity': as_sky.turbidity,
                          'turbidity_multiplier': as_sky.turbidity_multiplier,
                          'luminance_multiplier': as_sky.luminance_multiplier,
                          'luminance_gamma': as_sky.luminance_gamma,
                          'saturation_multiplier': as_sky.saturation_multiplier,
                          'horizon_shift': as_sky.horizon_shift}

        self.__as_env_edf = asr.EnvironmentEDF(env_type + "_environment_edf", "sky_edf", edf_params)

        self.__as_env_shader = asr.EnvironmentShader("edf_environment_shader", "sky_shader", {'environment_edf': 'sky_edf',
                                                                                              'alpha_value': as_sky.env_alpha})

        self.__as_env = asr.Environment("sky", {"environment_edf": "sky_edf", "environment_shader": "sky_shader"})

        self.__as_env_edf.transform_sequence().set_transform(0.0, asr.Transformd(self._convert_matrix(asr.Matrix4d.identity())))

    def flush_entities(self, as_scene):
        for index, color in enumerate(self.__colors):
            color_name = color.get_name()
            as_scene.colors().insert(color)
            self.__colors[index] = as_scene.colors().get_by_name(color_name)

        if self.__env_tex is not None:
            env_tex_name = self.__env_tex.get_name()
            as_scene.textures().insert(self.__env_tex)
            self.__env_tex = as_scene.textures().get_by_name(env_tex_name)

            env_tex_inst_name = self.__env_tex_inst.get_name()
            as_scene.texture_instances().insert(self.__env_tex_inst)
            self.__env_tex_inst = as_scene.texture_instances().get_by_name(env_tex_inst_name)

        as_env_edf_name = self.__as_env_edf.get_name()
        as_scene.environment_edfs().insert(self.__as_env_edf)
        self.__as_env_edf = as_scene.environment_edfs().get_by_name(as_env_edf_name)

        as_env_shader_name = self.__as_env_shader.get_name()
        as_scene.environment_shaders().insert(self.__as_env_shader)
        self.__as_env_shader = as_scene.environment_shaders().get_by_name(as_env_shader_name)

        as_scene.set_environment(self.__as_env)

    def update(self, scene, as_scene):

        for color in self.__colors:
            as_scene.colors().remove(color)

        if self.__env_tex is not None:
            as_scene.textures().remove(self.__env_tex)
            as_scene.texture_instances().remove(self.__env_tex_inst)

        as_scene.environment_shaders().remove(self.__as_env_shader)

        as_scene.environment_edfs().remove(self.__as_env_edf)

        self._reset(scene)

        if self.bl_scene.world.appleseed_sky.env_type == 'none':
            as_scene.set_environment(asr.Environment('environment', {}))
        else:
            self.create_entities(scene)
            self.flush_entities(as_scene)

    def _reset(self, scene):
        super(WorldTranslator, self)._reset(scene)
        self.__colors = []
        self.__env_tex = None
        self.__env_tex_inst = None

    def _convert_matrix(self, m):
        as_sky = self.bl_scene.world.appleseed_sky
        vertical_shift = asr.Matrix4d.make_rotation(asr.Vector3d(1.0, 0.0, 0.0), math.radians(as_sky.vertical_shift))
        horizontal_shift = asr.Matrix4d.make_rotation(asr.Vector3d(0.0, 1.0, 0.0), math.radians(as_sky.horizontal_shift))
        m = vertical_shift * horizontal_shift * m

        return m
