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

import bpy
import bpy_extras
from mathutils import Matrix

import appleseed as asr
from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class CameraTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, camera, asset_handler):
        super(CameraTranslator, self).__init__(camera, asset_handler)
        self._xform_seq = asr.TransformSequence()

        self.__cam_map = None
        self.__cam_map_inst = None

    #
    # Properties.
    #

    @property
    def bl_camera(self):
        return self._bl_obj

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        logger.debug("Creating camera entity for camera: %s" % self.appleseed_name)

        cam_mapping = {'PERSP': 'pinhole_camera',
                       'ORTHO': 'orthographic_camera',
                       'PANO': 'spherical_camera'}

        model = cam_mapping[self.bl_camera.data.type]

        if model == 'pinhole_camera' and self.bl_camera.data.appleseed.enable_dof:
            model = 'thinlens_camera'

        cam_key = self.appleseed_name
        self.__as_camera = asr.Camera(model, cam_key, {})

        self._xform_seq.set_transform(0.0, self._convert_matrix(self.bl_camera.matrix_world))

        self.__set_params(scene)

    def flush_entities(self, scene):
        self._xform_seq.optimize()

        logger.debug("Creating camera entity for camera: %s, num xform keys = %s" % (self.bl_camera.name, self._xform_seq.size()))

        self.__as_camera.set_transform_sequence(self._xform_seq)

        # Insert the camera into the scene.
        cam_name = self.__as_camera.get_name()
        scene.cameras().insert(self.__as_camera)
        self.__as_camera = scene.cameras().get_by_name(cam_name)

        if self.__cam_map is not None:
            cam_map_name = self.__cam_map.get_name()
            cam_map_inst_name = self.__cam_map_inst.get_name()
            scene.textures().insert(self.__cam_map)
            scene.texture_instances().insert(self.__cam_map_inst)

            self.__cam_map = scene.textures().get_by_name(cam_map_name)
            self.__cam_map_inst = scene.texture_instances().get_by_name(cam_map_inst_name)

    #
    # Internal methods.
    #

    def __set_params(self, scene):
        camera = self.bl_camera.data

        width, height = self._get_frame_aspect_ratio(scene)

        aspect_ratio = width / height

        film_width, film_height = self.__calc_film_dimensions(aspect_ratio)

        model = self.__as_camera.get_model()

        if model == 'pinhole_camera':
            cam_params = self.__create_pinhole_camera(scene, aspect_ratio, film_width, film_height)

        elif model == 'thinlens_camera':
            cam_params = self.__create_thin_lens_camera(scene, aspect_ratio, film_width, film_height)

        elif model == 'spherical_camera':
            cam_params = self.__create_spherical_camera(scene)

        else:
            cam_params = self.__create_ortho_camera(scene, aspect_ratio)

        self.__as_camera.set_parameters(cam_params)

    def set_transform_key(self, time, key_times):
        self._xform_seq.set_transform(time, self._convert_matrix(self.bl_camera.matrix_world))

    def __create_ortho_camera(self, scene, aspect_ratio):
        camera = self.bl_camera.data
        cam_params = {'aspect_ratio': aspect_ratio,
                      'near_z': camera.appleseed.near_z,
                      'shutter_open_end_time': scene.appleseed.shutter_open_end_time,
                      'shutter_open_begin_time': scene.appleseed.shutter_open,
                      'shutter_close_begin_time': scene.appleseed.shutter_close_begin_time,
                      'shutter_close_end_time': scene.appleseed.shutter_close}

        if camera.sensor_fit == 'HORIZONTAL' or (camera.sensor_fit == 'AUTO' and aspect_ratio > 1):
            cam_params['film_width'] = camera.ortho_scale
        else:
            cam_params['film_height'] = camera.ortho_scale

        return cam_params

    def __create_spherical_camera(self, scene):
        cam_params = {'shutter_open_end_time': scene.appleseed.shutter_open_end_time,
                      'shutter_open_begin_time': scene.appleseed.shutter_open,
                      'shutter_close_begin_time': scene.appleseed.shutter_close_begin_time,
                      'shutter_close_end_time': scene.appleseed.shutter_close}

        return cam_params

    def __create_pinhole_camera(self, scene, aspect_ratio, film_width, film_height):
        camera = self.bl_camera
        cam_params = {'aspect_ratio': aspect_ratio,
                      'film_dimensions': asr.Vector2f(film_width, film_height),
                      'near_z': camera.data.appleseed.near_z,
                      'shutter_open_end_time': scene.appleseed.shutter_open_end_time,
                      'shutter_open_begin_time': scene.appleseed.shutter_open,
                      'shutter_close_begin_time': scene.appleseed.shutter_close_begin_time,
                      'shutter_close_end_time': scene.appleseed.shutter_close}

        return cam_params

    def __create_thin_lens_camera(self, scene, aspect_ratio, film_width, film_height):
        camera = self.bl_camera
        if camera.dof_object is not None:
            cam_target = bpy.data.objects[camera.dof_object.name]
            focal_distance = (cam_target.location - self.bl_camera.location).magnitude
        else:
            focal_distance = camera.dof_distance
        cam_params = {'aspect_ratio': aspect_ratio,
                      'film_dimensions': asr.Vector2f(film_width, film_height),
                      'near_z': camera.data.appleseed.near_z,
                      'f_stop': camera.data.appleseed.f_number,
                      'autofocus_enabled': False,
                      'diaphragm_blades': camera.data.appleseed.diaphragm_blades,
                      'diaphragm_tilt_angle': camera.data.appleseed.diaphragm_angle,
                      'focal_distance': focal_distance,
                      'shutter_open_end_time': scene.appleseed.shutter_open_end_time,
                      'shutter_open_begin_time': scene.appleseed.shutter_open,
                      'shutter_close_begin_time': scene.appleseed.shutter_close_begin_time,
                      'shutter_close_end_time': scene.appleseed.shutter_close}
        if camera.data.appleseed.enable_autofocus:
            cam_params['autofocus_target'] = self._find_auto_focus_point(scene)
            cam_params['autofocus_enabled'] = True
        if camera.data.appleseed.diaphragm_map != "":
            filename = self.asset_handler.resolve_path(camera.appleseed.diaphragm_map)
            self.__cam_map = asr.Texture('disk_texture_2d', 'cam_map',
                                         {'filename': filename, 'color_space': camera.appleseed.diaphragm_map_colorspace}, [])
            self.__cam_map_inst = asr.TextureInstance("cam_map_inst", {'addressing_mode': 'wrap',
                                                                       'filtering_mode': 'bilinear'},
                                                      "cam_map", asr.Transformf(asr.Matrix4f.identity()))

            cam_params['diaphragm_map'] = 'cam_map_inst'
            del cam_params['diaphragm_blades']

        return cam_params

    @staticmethod
    def _find_auto_focus_point(scene):
        cam = scene.camera
        co = scene.cursor_location
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, co)
        y = 1 - co_2d.y
        logger.debug("2D Coords:{0} {1}".format(co_2d.x, y))

        return asr.Vector2f(co_2d.x, y)

    def __calc_film_dimensions(self, aspect_ratio):
        """
        Fit types:
        Horizontal = Horizontal size manually set.  Vertical size derived from aspect ratio.

        Vertical = Vertical size manaually set.  Horizontal size derived from aspect ratio.

        Auto = sensor_width bpy property sets the horizontal size when the aspect ratio is over 1 and
        the vertical size when it is below 1.  Other dimension is derived from aspect ratio.

        Much thanks to the Radeon ProRender plugin for clarifying this behavior
        """

        horizontal_fit = self.bl_camera.data.sensor_fit == 'HORIZONTAL' or \
                         (self.bl_camera.data.sensor_fit == 'AUTO' and aspect_ratio > 1)

        if self.bl_camera.data.sensor_fit == 'VERTICAL':
            film_height = self.bl_camera.data.sensor_height / 1000
            film_width = film_height * aspect_ratio
        elif horizontal_fit:
            film_width = self.bl_camera.data.sensor_width / 1000
            film_height = film_width / aspect_ratio
        else:
            film_height = self.bl_camera.data.sensor_width / 1000
            film_width = film_height * aspect_ratio

        return film_width, film_height

    @staticmethod
    def _get_frame_aspect_ratio(scene):
        render = scene.render
        scale = render.resolution_percentage / 100.0
        width = int(render.resolution_x * scale)
        height = int(render.resolution_y * scale)
        xratio = width * render.pixel_aspect_x
        yratio = height * render.pixel_aspect_y

        return xratio, yratio


class InteractiveCameraTranslator(Translator):

    def __init__(self, cam, context, asset_handler):
        super(InteractiveCameraTranslator, self).__init__(cam, asset_handler)

        self.__context = context

    def reset(self, cam, context):
        super(InteractiveCameraTranslator, self).reset(cam)

        self.__context = context

    @property
    def bl_camera(self):
        return self._bl_obj

    @property
    def context(self):
        return self.__context

    def create_entities(self, scene=None):
        logger.debug("Creating camera entity for camera: interactive camera")

        self.__set_cam_props()

        self.__as_int_camera = asr.Camera(self.__model, self.appleseed_name, self.__params)

    def set_transform_key(self, time, key_times):
        self.__as_int_camera.transform_sequence().set_transform(time, self._convert_matrix(self._matrix))

    def flush_entities(self, scene):
        logger.debug("Flushing camera entity for camera: interactive camera")

        # Insert the camera into the scene.
        cam_name = self.__as_int_camera.get_name()
        scene.cameras().insert(self.__as_int_camera)
        self.__as_int_camera = scene.cameras().get_by_name(cam_name)

    def check_for_camera_update(self, camera, context):
        """
        This function only needs to test for matrix changes and viewport lens/zoom changes.  All other camera
        changes are captured by a scene update
        """

        # Get current translation, zoom and lens from viewport
        current_translation = self._matrix
        zoom = self.__zoom
        lens = self.__lens
        extent_base = self.__extent_base

        self.reset(camera, context)

        self.__set_cam_props()

        # Check zoom
        if zoom != self.__zoom:
            return True

        # Check lens
        if lens != self.__lens:
            return True

        if current_translation != self._matrix:
            return True

        if extent_base != self.__extent_base:
            return True

        return False

    def update_camera(self, scene, camera=None, context=None):
        logger.debug("Update interactive camera")
        if camera is not None and context is not None:
            self.reset(camera, context)
        scene.cameras().remove(self.__as_int_camera)
        self.create_entities(scene)
        self.__as_int_camera.transform_sequence().set_transform(0.0, self._convert_matrix(self._matrix))
        self.flush_entities(scene)

    def __set_cam_props(self):
        # todo: add view offset
        params = {}
        model = None

        view_cam_type = self.context.region_data.view_perspective
        width = self.context.region.width
        height = self.context.region.height

        aspect_ratio = width / height

        self.__lens = self.context.space_data.lens
        self.__zoom = 2
        self.__extent_base = self.context.space_data.region_3d.view_distance * 32.0 / self.__lens

        if view_cam_type == "ORTHO":
            model, params = self.__create_ortho_camera(aspect_ratio)

        elif view_cam_type == "PERSP":
            model, params = self.__create_persp_camera(aspect_ratio)

        elif view_cam_type == "CAMERA":
            model, params = self.__create_view_camera(aspect_ratio)

        self.__model = model
        self.__params = params

    def __create_view_camera(self, aspect_ratio):
        # Borrowed from Cycles source code, since no sane person would figure this out on their own
        self.__zoom = 4 / ((math.sqrt(2) + self.context.region_data.view_camera_zoom / 50) ** 2)

        film_width, film_height = self.__calc_film_dimensions(aspect_ratio, self.__zoom)

        self._matrix = self.bl_camera.matrix_world
        cam_mapping = {'PERSP': 'pinhole_camera',
                       'ORTHO': 'orthographic_camera',
                       'PANO': 'spherical_camera'}
        model = cam_mapping[self.bl_camera.data.type]

        if model == 'pinhole_camera' and self.bl_camera.data.appleseed.enable_dof:
            model = 'thinlens_camera'

        if model == 'orthographic_camera':
            sensor_width = self.bl_camera.data.ortho_scale * self.__zoom
            params = {'film_width': sensor_width,
                      'aspect_ratio': aspect_ratio}

            if self.bl_camera.data.sensor_fit == 'VERTICAL' or (self.bl_camera.data.sensor_fit == 'AUTO' and aspect_ratio < 1):
                params['film_height'] = params.pop('film_width')

        elif model == 'spherical_camera':
            raise NotImplementedError("Spherical camera not supported for interactive rendering")

        elif model == 'thinlens_camera':
            if self.bl_camera.data.dof_object is not None:
                cam_target = bpy.data.objects[self.bl_camera.data.dof_object.name]
                focal_distance = (cam_target.location - self.bl_camera.location).magnitude
            else:
                focal_distance = self.bl_camera.data.dof_distance
            params = {'film_dimensions': asr.Vector2f(film_width, film_height),
                      'focal_length': self.bl_camera.data.lens / 1000,
                      'aspect_ratio': aspect_ratio,
                      'f_stop': self.bl_camera.data.appleseed.f_number,
                      'autofocus_enabled': False,
                      'diaphragm_blades': self.bl_camera.data.appleseed.diaphragm_blades,
                      'diaphragm_tilt_angle': self.bl_camera.data.appleseed.diaphragm_angle,
                      'focal_distance': focal_distance}
            if self.bl_camera.data.appleseed.enable_autofocus:
                params['autofocus_target'] = self._find_auto_focus_point(self.context.scene)
                params['autofocus_enabled'] = True

        else:
            params = {'focal_length': self.bl_camera.data.lens / 1000,
                      'aspect_ratio': aspect_ratio,
                      'film_dimensions': asr.Vector2f(film_width, film_height)}

        return model, params

    def __create_persp_camera(self, aspect_ratio):
        model = 'pinhole_camera'
        sensor_size = 32 * self.__zoom
        self._matrix = Matrix(self.context.region_data.view_matrix).inverted()
        params = {'focal_length': self.context.space_data.lens,
                  'aspect_ratio': aspect_ratio,
                  'film_width': sensor_size}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')
        return model, params

    def __create_ortho_camera(self, aspect_ratio):
        model = 'orthographic_camera'
        self._matrix = Matrix(self.context.region_data.view_matrix).inverted()
        sensor_width = self.__zoom * self.__extent_base * 1
        params = {'film_width': sensor_width,
                  'aspect_ratio': aspect_ratio}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        return model, params

    def __calc_film_dimensions(self, aspect_ratio, zoom):
        """
        Fit types:
        Horizontal = Horizontal size manually set.  Vertical size derived from aspect ratio.

        Vertical = Vertical size manaually set.  Horizontal size derived from aspect ratio.

        Auto = sensor_width bpy property sets the horizontal size when the aspect ratio is over 1 and
        the vertical size when it is below 1.  Other dimension is derived from aspect ratio.

        Much thanks to the Radeon ProRender plugin for clarifying this behavior
        """

        horizontal_fit = self.bl_camera.data.sensor_fit == 'HORIZONTAL' or \
                         (self.bl_camera.data.sensor_fit == 'AUTO' and aspect_ratio > 1)

        if self.bl_camera.data.sensor_fit == 'VERTICAL':
            film_height = self.bl_camera.data.sensor_height / 1000 * zoom
            film_width = film_height * aspect_ratio
        elif horizontal_fit:
            film_width = self.bl_camera.data.sensor_width / 1000 * zoom
            film_height = film_width / aspect_ratio
        else:
            film_height = self.bl_camera.data.sensor_width / 1000 * zoom
            film_width = film_height * aspect_ratio

        return film_width, film_height

    @staticmethod
    def _find_auto_focus_point(scene):
        cam = scene.camera
        co = scene.cursor_location
        co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, co)
        y = 1 - co_2d.y
        logger.debug("2D Coords:{0} {1}".format(co_2d.x, y))

        return asr.Vector2f(co_2d.x, y)
