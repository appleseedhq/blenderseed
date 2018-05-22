
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

from .translator import Translator

import appleseed as asr


class WorldTranslator(Translator):

    def __init__(self, scene):
        self.__bl_world = scene
        self.__horizon_radiance = None
        self.__zenith_radiance = None

    def create_entities(self):
        as_data = self.__bl_world.appleseed_sky
        env_type = as_data.env_type
        if env_type == 'sunsky':
            env_type = as_data.sun_model

        self.__as_env_edf = asr.EnvironmentEDF(env_type + "_environment_edf", "sky_edf", {})
        self.__as_env_shader = asr.EnvironmentShader("edf_environment_shader", "sky_shader", {'environment_edf': 'sky_edf',
                                                                                              'alpha_value': as_data.env_alpha})
        self.__as_env = asr.Environment("sky", {"environment_edf": "sky_edf", "environment_shader": "sky_shader"})

        if env_type == 'constant':
            self.__horizon_radiance = asr.ColorEntity('horizon_radiance_color', {'color_space': 'linear_rgb'},
                                                      self._convert_color(self.__bl_world.world.horizon_color))

        elif env_type in ('gradient', 'constant_hemisphere'):
            self.__horizon_radiance = asr.ColorEntity('horizon_radiance_color', {'color_space': 'srgb'},
                                                      self._convert_color(self.__bl_world.world.horizon_color))
            self.__zenith_radiance = asr.ColorEntity('zenith_radiance_color', {'color_space': 'linear_rgb'},
                                                     self._convert_color(self.__bl_world.world.zenith_color))

        if env_type in ('latlong_map', 'mirrorball_map'):
            pass

        self.set_edf_params()

    def set_edf_params(self):
        as_sky = self.__bl_world.appleseed_sky
        edf_params = {}

        if as_sky.env_type == 'latlong_map':
            edf_params = {'radiance': as_sky.env_tex + "_inst",
                          'radiance_multiplier': as_sky.env_tex_mult + "_inst",
                          'exposure': as_sky.env_exposure,
                          'vertical_shift': as_sky.vertical_shift,
                          'horizontal_shift': as_sky.horizontal_shift}

        elif as_sky.env_type == 'mirrorball_map':
            edf_params = {'radiance': as_sky.env_tex + "_inst",
                          'radiance_multiplier': as_sky.env_tex_mult + "_inst",
                          'exposure': as_sky.env_exposure}

        elif as_sky.env_type == 'constant':
            edf_params = {'radiance': 'horizon_radiance_color'}

        elif as_sky.env_type == 'gradient':
            edf_params = {'horizon_radiance': "horizon_radiance_color",
                          'zenith_radiance': "zenith_radiance_color"}

        elif as_sky.env_type == 'constant_hemisphere':
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
        if as_sky.sun_model == 'preetham':
            del edf_params['ground_albedo']

        self.__as_env_edf.set_parameters(edf_params)

    def flush_entities(self, project):

        scene = project.get_scene()

        if self.__horizon_radiance is not None:
            scene.colors().insert(self.__horizon_radiance)
        if self.__zenith_radiance is not None:
            scene.colors().insert(self.__zenith_radiance)

        scene.environment_edfs().insert(self.__as_env_edf)
        scene.environment_shaders().insert(self.__as_env_shader)
        scene.set_environment(self.__as_env)
