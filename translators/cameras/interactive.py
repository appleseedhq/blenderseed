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

from mathutils import Matrix

import appleseed as asr
from ..translator import Translator
from ...logger import get_logger
from ...utils import util

logger = get_logger()


class InteractiveCameraTranslator(Translator):
    """
    This translator is responsible for translating the Blender camera into an appleseed
    camera object for final rendering.  This includes support for stereoscopic rendering.
    """

    def __init__(self, cam, asset_handler):
        logger.debug("Creating interactive camera translator")
        super().__init__(cam, asset_handler)

        self.__as_camera = None

        self.__cam_model = None
        self.__view_cam_type = None
        self.__cam_params = None
        self.__xform_matrix = None

    @property
    def bl_camera(self):
        return self._bl_obj

    def create_entities(self, bl_scene, context, engine=None):
        self.__view_cam_type = f"{context.region_data.view_perspective}"

        self.__model = self.__get_model()

        self.__cam_params = self.__get_cam_params(bl_scene, context)

        self.__as_camera = asr.Camera(self.__model, "Camera", self.__cam_params)

    def flush_entities(self, as_scene, as_main_assembly, as_project):
        self.__as_camera.transform_sequence().optimize()

        as_scene.cameras().insert(self.__as_camera)
        self.__as_camera = as_scene.cameras().get_by_name("Camera")

    def add_cam_xform(self, engine, time):
        self.__as_camera.transform_sequence().set_transform(time, self._convert_matrix(self.__xform_matrix))

    def __get_model(self):
        cam_mapping = {'PERSP': 'pinhole_camera',
                       'ORTHO': 'orthographic_camera',
                       'PANO': 'spherical_camera'}

        if self.__view_cam_type == "CAMERA":
            model = cam_mapping[self.bl_camera.data.type]

            if model == 'spherical_camera' and not self.bl_camera.data.appleseed.fisheye_projection_type == 'none':
                model = 'fisheyelens_camera'

            if model == 'pinhole_camera' and self.bl_camera.data.appleseed.enable_dof:
                model = 'thinlens_camera'
        else:
            model = cam_mapping[self.__view_cam_type]

        return model

    def __get_cam_params(self, bl_scene, context=None):
        params = dict()

        view_cam_type = self.__view_cam_type

        width = context.region.width
        height = context.region.height

        aspect_ratio = width / height

        self.__lens = context.space_data.lens
        self.__zoom = None
        self.__extent_base = None
        self.__shift_x = None
        self.__shift_y = None

        if view_cam_type == "ORTHO":
            self.__zoom = 2.25
            self.__extent_base = context.space_data.region_3d.view_distance * 32.0 / self.__lens
            params = self.__set_ortho_camera_params(context, aspect_ratio)

        elif view_cam_type == "PERSP":
            self.__zoom = 2.25
            params = self.__set_persp_camera_params(context, aspect_ratio)

        elif view_cam_type == "CAMERA":
            # Borrowed from Cycles source code, since for something this nutty there's no reason to reinvent the wheel
            self.__zoom = 4 / ((math.sqrt(2) + context.region_data.view_camera_zoom / 50) ** 2)
            params = self.__set_view_camera_params(context, aspect_ratio)

        return params

    def __set_ortho_camera_params(self, context, aspect_ratio):
        self.__xform_matrix = Matrix(context.region_data.view_matrix).inverted()
        sensor_width = self.__zoom * self.__extent_base * 1
        params = {'film_width': sensor_width, 'aspect_ratio': aspect_ratio}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        return params

    def __set_persp_camera_params(self, context, aspect_ratio):
        sensor_size = 32 * self.__zoom
        self.__xform_matrix = Matrix(context.region_data.view_matrix).inverted()
        params = {'focal_length': context.space_data.lens,
                  'aspect_ratio': aspect_ratio,
                  'film_width': sensor_size}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        return params

    def __set_view_camera_params(self, context, aspect_ratio):
        film_width, film_height = util.calc_film_dimensions(aspect_ratio, self.bl_camera.data, self.__zoom)

        offset = tuple(context.region_data.view_camera_offset)

        x_aspect_comp = 1 if aspect_ratio > 1 else 1 / aspect_ratio
        y_aspect_comp = aspect_ratio if aspect_ratio > 1 else 1

        self.__shift_x = ((offset[0] * 2 + (self.bl_camera.data.shift_x * x_aspect_comp)) / self.__zoom) * film_width
        self.__shift_y = ((offset[1] * 2 + (self.bl_camera.data.shift_y * y_aspect_comp)) / self.__zoom) * film_height

        self.__xform_matrix = self.bl_camera.matrix_world.copy()

        if self.__model == 'orthographic_camera':
            sensor_width = self.bl_camera.data.ortho_scale * self.__zoom
            params = {'film_width': sensor_width,
                      'aspect_ratio': aspect_ratio}

            if self.bl_camera.data.sensor_fit == 'VERTICAL' or (self.bl_camera.data.sensor_fit == 'AUTO' and aspect_ratio < 1):
                params['film_height'] = params.pop('film_width')

        else:
            aspect_ratio = util.calc_film_aspect_ratio(context.scene)
            params = {'focal_length': self.bl_camera.data.lens / 1000,
                      'aspect_ratio': aspect_ratio,
                      'shift_x': self.__shift_x,
                      'shift_y': self.__shift_y,
                      'film_dimensions': asr.Vector2f(film_width, film_height)}

        if self.__model == 'fisheyelens_camera':
            if self.bl_camera.data.appleseed.fisheye_projection_type is not 'none':
                params['projection_type'] = self.bl_camera.data.appleseed.fisheye_projection_type

        if self.__model == 'thinlens_camera':
            params.update({'f_stop': self.bl_camera.data.appleseed.f_number,
                           'autofocus_enabled': False,
                           'diaphragm_blades': self.bl_camera.data.appleseed.diaphragm_blades,
                           'diaphragm_tilt_angle': self.bl_camera.data.appleseed.diaphragm_angle,
                           'focal_distance': util.get_focal_distance(self.bl_camera)})

            if self.bl_camera.data.appleseed.diaphragm_map is not None:
                tex_name = f"{self.bl_camera.data.appleseed.diaphragm_map.name_full}_inst"
                params.update({'diaphragm_map': tex_name})
                del params['diaphragm_blades']

        return params

    def _convert_matrix(self, m):
        matrix = asr.Matrix4d([m[0][0], m[0][1], m[0][2], m[0][3],
                               m[2][0], m[2][1], m[2][2], m[2][3],
                               -m[1][0], -m[1][1], -m[1][2], -m[1][3],
                               m[3][0], m[3][1], m[3][2], m[3][3]])

        return asr.Transformd(matrix)
