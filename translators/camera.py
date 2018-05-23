
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

import math

import appleseed as asr

import bpy
import bpy_extras


class CameraTranslator(Translator):

    def __init__(self, scene, camera):
        self.__bl_camera = camera
        self.__scene = scene

    def create_entities(self):

        cam_mapping = {'PERSP': 'pinhole_camera',
                       'ORTHO': 'orthographic_camera',
                       'PANO': 'spherical_camera'}

        model = cam_mapping[self.__bl_camera.data.type]

        if model == 'pinhole_camera' and self.__bl_camera.data.appleseed.enable_dof:
            model = 'thinlens_camera'

        camera = self.__bl_camera.data
        scene = self.__scene
        focal_length = camera.lens / 1000
        film_width = camera.sensor_width / 1000
        film_height = camera.sensor_height / 1000
        aspect_ratio = self.get_frame_aspect_ratio()

        if model == 'pinhole_camera':
            cam_params = {'film_dimensions': asr.Vector2f(film_width, film_height),
                          'focal_length': focal_length,
                          'aspect_ratio': aspect_ratio,
                          'near_z': camera.appleseed.near_z,
                          'shutter_open_begin_time': scene.appleseed.shutter_open,
                          'shutter_close_end_time': scene.appleseed.shutter_close}

        elif model == 'thinlens_camera':
            if camera.dof_object is not None:
                cam_target = bpy.data.objects[camera.dof_object.name]
                focal_distance = (cam_target.location - self.__bl_camera.location).magnitude
            else:
                focal_distance = camera.dof_distance
            cam_params = {'film_dimensions': asr.Vector2f(film_width, film_height),
                          'focal_length': focal_length,
                          'aspect_ratio': aspect_ratio,
                          'near_z': camera.appleseed.near_z,
                          'shutter_open_begin_time': scene.appleseed.shutter_open,
                          'shutter_close_end_time': scene.appleseed.shutter_close,
                          'f_stop': camera.appleseed.f_number,
                          'autofocus_enabled': False,
                          'diaphragm_blades': camera.appleseed.diaphragm_blades,
                          'diaphragm_tilt_angle': camera.appleseed.diaphragm_angle,
                          'focal_distance': focal_distance}
            if camera.appleseed.enable_autofocus:
                cam_params['autofocus_target'] = self.find_auto_focus_point()
                cam_params['autofocus_enabled'] = True

        elif model == 'spherical_camera':
            cam_params = {'shutter_open_begin_time': scene.appleseed.shutter_open,
                          'shutter_close_end_time': scene.appleseed.shutter_close}

        else:
            cam_params = {'film_width': camera.ortho_scale,
                          'aspect_ratio': aspect_ratio,
                          'near_z': camera.appleseed.near_z,
                          'shutter_open_begin_time': scene.appleseed.shutter_open,
                          'shutter_close_end_time': scene.appleseed.shutter_close}

        self.__as_camera = asr.Camera("pinhole_camera", self.__bl_camera.name, cam_params)

        self.__as_camera.transform_sequence().set_transform(0.0, self._convert_matrix(self.__bl_camera.matrix_world))

    def find_auto_focus_point(self):
        scene = self.__scene
        cam = scene.camera
        co = scene.cursor_location
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, co)
        print("2D Coords:", co_2d)

        return asr.Vector2f(co_2d.x, co_2d.y)

    def get_frame_aspect_ratio(self):
        render = self.__scene.render
        scale = render.resolution_percentage / 100.0
        width = int(render.resolution_x * scale)
        height = int(render.resolution_y * scale)
        xratio = width * render.pixel_aspect_x
        yratio = height * render.pixel_aspect_y
        return xratio / yratio

    def flush_entities(self, project):
        # Insert the camera into the project.
        scene = project.get_scene()
        scene.cameras().insert(self.__as_camera)
