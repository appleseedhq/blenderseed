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
        logger.debug(f"appleseed: Creating interactive camera translator for {cam.name_full}")
        super().__init__(cam, asset_handler)

        self.__as_camera = None

        self.__model = None

        self.__cam_model = None
        self.__view_cam_type = None
        self.__cam_params = None
        self.__xform_matrix = None

        self._bl_obj.appleseed.obj_name = self._bl_obj.name_full

    @property
    def bl_camera(self):
        return self._bl_obj

    def create_entities(self, depsgraph, context, engine=None):
        logger.debug(f"appleseed: Creating interactive camera entity for {self.bl_camera.name_full}")
        self.__view_cam_type = context.region_data.view_perspective

        self.__model = self.__get_model()

        self.__cam_params = self.__get_cam_params(depsgraph.scene_eval, context)

        self.__as_camera = asr.Camera(self.__model, "Camera", self.__cam_params)

    def flush_entities(self, as_scene, as_main_assembly, as_project):
        logger.debug(f"appleseed: Flushing interactive camera entity for {self.bl_camera.name_full} into project")
        self.__as_camera.transform_sequence().optimize()

        as_scene.cameras().insert(self.__as_camera)
        self.__as_camera = as_scene.cameras().get_by_name("Camera")

    def add_cam_xform(self, time, engine=None):
        self.__as_camera.transform_sequence().set_transform(time, self._convert_matrix(self.__xform_matrix))

    def check_for_updates(self, context, bl_scene):
        updates = dict()

        updates['cam_xform'] = self.__is_matrix_updated(context)
        updates['cam_params'] = self.__are_cam_params_updated(context, bl_scene)
        updates['cam_model'] = self.__is_camera_model_updated(context)

        return updates

    def update_cam_params(self):
        self.__as_camera.set_parameters(self.__cam_params)

    def update_cam_model(self, as_scene):
        as_scene.cameras().remove(self.__as_camera)

        self.__as_camera = asr.Camera(self.__model, "Camera", self.__cam_params)
        
        as_scene.cameras().insert(self.__as_camera)
        self.__as_camera = as_scene.cameras().get_by_name("Camera")

    # Internal methods.
    def __is_matrix_updated(self, context):
        current_matrix = self.__xform_matrix

        self.__set_matrix(context)

        if current_matrix != self.__xform_matrix:
            return True
        
        return False

    def __is_camera_model_updated(self, context):
        current_view_cam = self.__view_cam_type
        current_model = self.__model
        
        self.__view_cam_type = context.region_data.view_perspective

        self.__model = self.__get_model()

        if current_view_cam != self.__view_cam_type or current_model != self.__model:
            return True
        
        return False

    def __are_cam_params_updated(self, context, bl_scene):
        current_params = self.__cam_params

        self.__cam_params = self.__get_cam_params(bl_scene, context)

        if current_params != self.__cam_params:
            return True

        return False

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
        self.__set_matrix(context)
        sensor_width = self.__zoom * self.__extent_base * 1
        params = {'film_width': sensor_width, 'aspect_ratio': aspect_ratio}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        return params

    def __set_persp_camera_params(self, context, aspect_ratio):
        self.__set_matrix(context)
        sensor_size = 32 * self.__zoom
        params = {'focal_length': context.space_data.lens,
                  'aspect_ratio': aspect_ratio,
                  'film_width': sensor_size}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        return params

    def __set_matrix(self, context):
        if self.__view_cam_type in ("ORTHO", "PERSP"):
            self.__xform_matrix = Matrix(context.region_data.view_matrix).inverted()
        else:
            self.__xform_matrix = self.bl_camera.matrix_world

    def __set_view_camera_params(self, context, aspect_ratio):
        film_width, film_height = util.calc_film_dimensions(aspect_ratio, self.bl_camera.data, self.__zoom)

        offset = tuple(context.region_data.view_camera_offset)

        x_aspect_comp = 1 if aspect_ratio > 1 else 1 / aspect_ratio
        y_aspect_comp = aspect_ratio if aspect_ratio > 1 else 1

        self.__shift_x = ((offset[0] * 2 + (self.bl_camera.data.shift_x * x_aspect_comp)) / self.__zoom) * film_width
        self.__shift_y = ((offset[1] * 2 + (self.bl_camera.data.shift_y * y_aspect_comp)) / self.__zoom) * film_height

        self.__set_matrix(context)

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
        matrix = asr.Matrix4d(super()._convert_matrix(m))

        return asr.Transformd(matrix)
