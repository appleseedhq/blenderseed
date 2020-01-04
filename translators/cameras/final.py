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

from ..translator import Translator
from ...logger import get_logger
from ...utils import util

logger = get_logger()


class RenderCameraTranslator(Translator):

    def __init__(self, cam, asset_handler):
        super().__init__(cam, asset_handler)

        self.__as_camera = None

        self.__cam_model = None

    @property
    def bl_camera(self):
        return self._bl_obj

    def create_entities(self, depsgraph, context=None, engine=None):
        self.__cam_model = self.__get_model()

        self.__as_camera = asr.Camera(self.__cam_model, "Camera", {})

        self.__as_cam_params = self.__get_cam_params(depsgraph.scene_eval, engine)

        self.__as_camera.set_parameters(self.__as_cam_params)

    def flush_entities(self, as_scene, as_main_assembly, as_project):
        logger.debug("Flushing camera entity, num xform keys = %s", self.__as_camera.transform_sequence().size())

        self.__as_camera.transform_sequence().optimize()

        as_scene.cameras().insert(self.__as_camera)
        self.__as_camera = as_scene.cameras().get_by_name("Camera")

    def add_cam_xform(self, time, engine=None):
        self.__as_camera.transform_sequence().set_transform(
            time,
            self._convert_matrix(engine.camera_model_matrix(self.bl_camera)))

    def update_mult_cam_xform(self, engine, bl_scene, time):
        camera = self.bl_camera

        aspect_ratio = util.calc_film_aspect_ratio(bl_scene)

        film_width, film_height = util.calc_film_dimensions(aspect_ratio, camera.data, 1)

        self.__as_camera.transform_sequence().set_transform(
            time,
            self._convert_matrix(engine.camera_model_matrix(self.bl_camera)))

        params = self.__as_camera.get_parameters()

        x_aspect_comp = 1 if aspect_ratio > 1 else 1 / aspect_ratio

        params['shift_x'] = (engine.camera_shift_x(camera) + camera.data.shift_x) * x_aspect_comp * film_width

        self.__as_camera.set_parameters(params)

    # Internal methods
    def __get_model(self):
        cam_mapping = {'PERSP': 'pinhole_camera',
                       'ORTHO': 'orthographic_camera',
                       'PANO': 'spherical_camera'}

        model = cam_mapping[self.bl_camera.data.type]

        if model == 'spherical_camera' and not self.bl_camera.data.appleseed.fisheye_projection_type == 'none':
            model = 'fisheyelens_camera'

        if model == 'pinhole_camera' and self.bl_camera.data.appleseed.enable_dof:
            model = 'thinlens_camera'

        return model

    def __get_cam_params(self, bl_scene, engine):
        camera = self.bl_camera.data

        aspect_ratio = util.calc_film_aspect_ratio(bl_scene)

        film_width, film_height = util.calc_film_dimensions(aspect_ratio, camera, 1)

        model = self.__as_camera.get_model()

        if model == 'pinhole_camera':
            cam_params = self.__base_camera_params(bl_scene, engine, aspect_ratio, film_width, film_height)

        elif model == 'thinlens_camera':
            cam_params = self.__thin_lens_camera_params(bl_scene, engine, aspect_ratio, film_width, film_height)

        elif model == 'spherical_camera':
            cam_params = self.__spherical_camera_params(bl_scene)

        elif model == 'fisheyelens_camera':
            cam_params = self.__fisheye_camera_params(bl_scene, engine, aspect_ratio, film_width, film_height)

        else:
            cam_params = self.__ortho_camera_params(bl_scene, aspect_ratio)

        return cam_params

    def __ortho_camera_params(self, bl_scene, aspect_ratio):
        camera = self.bl_camera.data
        cam_params = {
            'aspect_ratio': aspect_ratio,
            'near_z': camera.appleseed.near_z,
            'shutter_open_end_time': bl_scene.appleseed.shutter_open_end_time,
            'shutter_open_begin_time': bl_scene.appleseed.shutter_open,
            'shutter_close_begin_time': bl_scene.appleseed.shutter_close_begin_time,
            'shutter_close_end_time': bl_scene.appleseed.shutter_close}

        if camera.sensor_fit == 'HORIZONTAL' or (camera.sensor_fit == 'AUTO' and aspect_ratio > 1):
            cam_params['film_width'] = camera.ortho_scale
        else:
            cam_params['film_height'] = camera.ortho_scale

        return cam_params

    def __spherical_camera_params(self, bl_scene):
        cam_params = {
            'shutter_open_end_time': bl_scene.appleseed.shutter_open_end_time,
            'shutter_open_begin_time': bl_scene.appleseed.shutter_open,
            'shutter_close_begin_time': bl_scene.appleseed.shutter_close_begin_time,
            'shutter_close_end_time': bl_scene.appleseed.shutter_close}

        return cam_params

    def __base_camera_params(self, bl_scene, engine, aspect_ratio, film_width, film_height):
        camera = self.bl_camera
        x_aspect_comp = 1 if aspect_ratio > 1 else 1 / aspect_ratio
        y_aspect_comp = aspect_ratio if aspect_ratio > 1 else 1
        cam_params = {
            'aspect_ratio': aspect_ratio,
            'focal_length': camera.data.lens / 1000,  # mm to meters.
            'film_dimensions': asr.Vector2f(film_width, film_height),
            'near_z': camera.data.appleseed.near_z,
            'shift_x': (engine.camera_shift_x(camera) + camera.data.shift_x) * x_aspect_comp * film_width,
            'shift_y': camera.data.shift_y * y_aspect_comp * film_height,
            'shutter_open_end_time': bl_scene.appleseed.shutter_open_end_time,
            'shutter_open_begin_time': bl_scene.appleseed.shutter_open,
            'shutter_close_begin_time': bl_scene.appleseed.shutter_close_begin_time,
            'shutter_close_end_time': bl_scene.appleseed.shutter_close}

        return cam_params

    def __fisheye_camera_params(self, scene, engine, aspect_ratio, film_width, film_height):
        camera = self.bl_camera

        cam_params = self.__base_camera_params(scene, engine, aspect_ratio, film_width, film_height)

        cam_params.update({'projection_type': camera.data.appleseed.fisheye_projection_type})

        return cam_params

    def __thin_lens_camera_params(self, bl_scene, engine, aspect_ratio, film_width, film_height):
        camera = self.bl_camera

        cam_params = self.__base_camera_params(
            bl_scene,
            engine,
            aspect_ratio,
            film_width,
            film_height)

        cam_params.update({'f_stop': camera.data.appleseed.f_number,
                           'autofocus_enabled': False,
                           'diaphragm_blades': camera.data.appleseed.diaphragm_blades,
                           'diaphragm_tilt_angle': camera.data.appleseed.diaphragm_angle,
                           'focal_distance': util.get_focal_distance(camera)})

        if camera.data.appleseed.enable_autofocus:
            x, y = util.find_autofocus_point(bl_scene)
            cam_params['autofocus_target'] = asr.Vector2f(x, y)
            cam_params['autofocus_enabled'] = True

        if camera.data.appleseed.diaphragm_map is not None:
            tex_name = f"{camera.data.appleseed.diaphragm_map.name_full}_inst"
            cam_params['diaphragm_map'] = tex_name
            del cam_params['diaphragm_blades']

        return cam_params

    def _convert_matrix(self, m):
        matrix = asr.Matrix4d([m[0][0], m[0][1], m[0][2], m[0][3],
                               m[1][0], m[1][1], m[1][2], m[1][3],
                               m[2][0], m[2][1], m[2][2], m[2][3],
                               m[3][0], m[3][1], m[3][2], m[3][3]])

        rotation_modify = asr.Matrix4d.make_rotation(asr.Vector3d(1.0, 0.0, 0.0), math.radians(-90.0))

        matrix = rotation_modify * matrix

        return asr.Transformd(matrix)