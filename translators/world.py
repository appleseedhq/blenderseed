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

import appleseed as asr
from .textures import TextureTranslator
from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class WorldTranslator(Translator):
    """
    This class translates a Blender world block into an appleseed environment
    """

    # Constructor.
    def __init__(self, world, asset_handler):
        super().__init__(world, asset_handler)

        self.__as_colors = list()

        self.__as_env_type = None
        self.__as_env = None
        self.__as_env_shader = None

        self.__as_env_edf = None
        self.__as_edf_params = dict()

        self._bl_obj.appleseed_sky.obj_name = self._bl_obj.name_full

    @property
    def bl_world(self):
        return self._bl_obj

    def create_entities(self, depsgraph):
        as_world = self.bl_world.appleseed_sky

        self.__as_env_type = as_world.env_type

        if self.__as_env_type != 'none':

            self.__as_env_type = as_world.env_type if as_world.env_type != 'sunsky' else as_world.sun_model

            self.__set_colors()

            self.__as_edf_params = self.__create_params()

            self.__as_env_edf = asr.EnvironmentEDF(
                self.__as_env_type + "_environment_edf",
                "sky_edf",
                self.__as_edf_params)

            self.__as_env_shader = asr.EnvironmentShader("edf_environment_shader",
                                                         "sky_shader",
                                                         {'environment_edf': 'sky_edf', 'alpha_value': as_world.env_alpha})

            self.__as_env = asr.Environment("sky",
                                            {"environment_edf": "sky_edf", "environment_shader": "sky_shader"})

        else:
            self.__as_env = asr.Environment("environment", {})

    def flush_entities(self, as_scene, as_assembly, as_project):
        if self.__as_env_type != 'none':
            self.__as_env_edf.transform_sequence().set_transform(0.0, asr.Transformd(self._convert_matrix(asr.Matrix4d.identity())))

            for index, color in enumerate(self.__as_colors):
                color_name = color.get_name()
                as_scene.colors().insert(color)
                self.__as_colors[index] = as_scene.colors().get_by_name(color_name)

            as_env_edf_name = self.__as_env_edf.get_name()
            as_scene.environment_edfs().insert(self.__as_env_edf)
            self.__as_env_edf = as_scene.environment_edfs().get_by_name(as_env_edf_name)

            as_env_shader_name = self.__as_env_shader.get_name()
            as_scene.environment_shaders().insert(self.__as_env_shader)
            self.__as_env_shader = as_scene.environment_shaders().get_by_name(as_env_shader_name)

        as_scene.set_environment(self.__as_env)

    def update_world(self, as_scene, depsgraph):
        as_world = self.bl_world.appleseed_sky

        current_env_type = self.__as_env_type

        self.__as_env_type = as_world.env_type if as_world.env_type != 'sunsky' else as_world.sun_model            

        if current_env_type == 'none': # Create new environment entities.
            self.create_entities(depsgraph)
            self.flush_entities(as_scene, None, None)
        elif self.__as_env_type == 'none': # Delete current world entities.
            self.delete_world(as_scene)
        elif current_env_type == self.__as_env_type:
            self.__as_edf_params = self.__create_params()
            self.__as_env_edf.set_parameters(self.__as_edf_params)

            env_shader_params = self.__as_env_shader.get_parameters()
            env_shader_params['alpha_value'] = as_world.env_alpha
            self.__as_env_shader.set_parameters(env_shader_params)

            for color in self.__as_colors:
                as_scene.colors().remove(color)
            
            self.__as_colors.clear()

            self.__set_colors()

            for index, color in enumerate(self.__as_colors):
                color_name = color.get_name()
                as_scene.colors().insert(color)
                self.__as_colors[index] = as_scene.colors().get_by_name(color_name)
        else: # World still exists but needs to be changed.
            self.delete_world(as_scene)
            self.create_entities(depsgraph)
            self.flush_entities(as_scene, None, None)

    def delete_world(self, as_scene):
        for color in self.__as_colors:
            as_scene.colors().remove(color)
            
        self.__as_colors.clear()

        if self.__as_env_edf is not None:
            as_scene.environment_edfs().remove(self.__as_env_edf)
            self.__as_env_edf = None

        if self.__as_env_shader is not None:
            as_scene.environment_shaders().remove(self.__as_env_shader)
            self.__as_env_shader = None

        as_scene.set_environment(asr.Environment("environment", {}))

    # Internal methods.
    def __set_colors(self):
        as_world = self.bl_world.appleseed_sky

        if self.__as_env_type == 'constant':
            self.__as_colors.append(asr.ColorEntity('horizon_radiance_color',
                                                    {'color_space': 'linear_rgb'},
                                                    self._convert_color(as_world.horizon_color)))

        elif self.__as_env_type in ('gradient', 'constant_hemisphere'):
            self.__as_colors.append(asr.ColorEntity('horizon_radiance_color',
                                                    {'color_space': 'linear_rgb'},
                                                    self._convert_color(as_world.horizon_color)))

            self.__as_colors.append(asr.ColorEntity('zenith_radiance_color',
                                                    {'color_space': 'linear_rgb'},
                                                    self._convert_color(as_world.zenith_color)))

    def _convert_matrix(self, m):
        as_world = self.bl_world.appleseed_sky
        vertical_shift = asr.Matrix4d.make_rotation(asr.Vector3d(1.0, 0.0, 0.0), math.radians(as_world.vertical_shift))
        horizontal_shift = asr.Matrix4d.make_rotation(asr.Vector3d(0.0, 1.0, 0.0), math.radians(as_world.horizontal_shift))
        m = vertical_shift * horizontal_shift * m

        return m

    def __create_params(self):
        as_world = self.bl_world.appleseed_sky

        params = dict()

        if self.__as_env_type == 'latlong_map':
            if as_world.env_tex is not None:
                tex_name = f"{as_world.env_tex.name_full}_inst"
                params = {'radiance': tex_name, 'radiance_multiplier': as_world.env_tex_mult, 'exposure': as_world.env_exposure}
            else:
                return params

        elif self.__as_env_type == 'mirrorball_map':
            if as_world.env_tex is not None:
                tex_name = f"{as_world.env_tex.name_full}_inst"
                params = {'radiance': tex_name, 'exposure': as_world.env_exposure, 'radiance_multiplier': as_world.env_tex_mult}
            else:
                return params

        elif self.__as_env_type == 'constant':
            params = {'radiance': 'horizon_radiance_color'}

        elif self.__as_env_type == 'gradient':
            params = {'horizon_radiance': "horizon_radiance_color",
                      'zenith_radiance': "zenith_radiance_color"}

        elif self.__as_env_type == 'constant_hemisphere':
            params = {'lower_hemi_radiance': "horizon_radiance_color",
                      'upper_hemi_radiance': "zenith_radiance_color"}

        else:
            params = {'ground_albedo': as_world.ground_albedo,
                      'sun_phi': as_world.sun_phi,
                      'sun_theta': as_world.sun_theta,
                      'turbidity': as_world.turbidity,
                      'turbidity_multiplier': as_world.turbidity_multiplier,
                      'luminance_multiplier': as_world.luminance_multiplier,
                      'luminance_gamma': as_world.luminance_gamma,
                      'saturation_multiplier': as_world.saturation_multiplier,
                      'horizon_shift': as_world.horizon_shift}

        return params

