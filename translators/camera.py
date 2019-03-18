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
from mathutils import Matrix

import appleseed as asr
from .assethandlers import AssetType
from .translator import Translator
from ..logger import get_logger
from ..utils import util

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

        if model == 'spherical_camera' and not self.bl_camera.data.appleseed.fisheye_projection_type == 'none':
            model = 'fisheyelens_camera'

        if model == 'pinhole_camera' and self.bl_camera.data.appleseed.enable_dof:
            model = 'thinlens_camera'

        cam_key = self.appleseed_name
        self.__as_camera = asr.Camera(model, cam_key, {})

        self._xform_seq.set_transform(0.0, self._convert_matrix(self.bl_camera.matrix_world))

        self.__set_params(scene)

    def flush_entities(self, scene):
        self._xform_seq.optimize()

        logger.debug("Flushing camera entity for camera: %s, num xform keys = %s" % (self.bl_camera.name, self._xform_seq.size()))

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

    def set_transform_key(self, scene, time, key_times):
        self._xform_seq.set_transform(time, self._convert_matrix(self.bl_camera.matrix_world))

    #
    # Internal methods.
    #

    def __set_params(self, scene):
        camera = self.bl_camera.data

        aspect_ratio = util.get_frame_aspect_ratio(scene)

        film_width, film_height = util.calc_film_dimensions(aspect_ratio, camera, 1)

        model = self.__as_camera.get_model()

        if model == 'pinhole_camera':
            cam_params = self.__basic_camera_params(scene, aspect_ratio, film_width, film_height)

        elif model == 'thinlens_camera':
            cam_params = self.__thin_lens_camera_params(scene, aspect_ratio, film_width, film_height)

        elif model == 'spherical_camera':
            cam_params = self.__spherical_camera_params(scene)

        elif model == 'fisheyelens_camera':
            cam_params = self.__fisheye_camera_params(scene, aspect_ratio, film_width, film_height)

        else:
            cam_params = self.__ortho_camera_params(scene, aspect_ratio)

        self.__as_camera.set_parameters(cam_params)

    def __ortho_camera_params(self, scene, aspect_ratio):
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

    def __spherical_camera_params(self, scene):
        cam_params = {'shutter_open_end_time': scene.appleseed.shutter_open_end_time,
                      'shutter_open_begin_time': scene.appleseed.shutter_open,
                      'shutter_close_begin_time': scene.appleseed.shutter_close_begin_time,
                      'shutter_close_end_time': scene.appleseed.shutter_close}

        return cam_params

    def __basic_camera_params(self, scene, aspect_ratio, film_width, film_height):
        camera = self.bl_camera
        x_aspect_comp = 1 if aspect_ratio > 1 else 1 / aspect_ratio
        y_aspect_comp = aspect_ratio if aspect_ratio > 1 else 1
        cam_params = {'aspect_ratio': aspect_ratio,
                      'focal_length': camera.data.lens / 1000, # mm to meters.
                      'film_dimensions': asr.Vector2f(film_width, film_height),
                      'near_z': camera.data.appleseed.near_z,
                      'shift_x': camera.data.shift_x * x_aspect_comp * film_width,
                      'shift_y': camera.data.shift_y * y_aspect_comp * film_height,
                      'shutter_open_end_time': scene.appleseed.shutter_open_end_time,
                      'shutter_open_begin_time': scene.appleseed.shutter_open,
                      'shutter_close_begin_time': scene.appleseed.shutter_close_begin_time,
                      'shutter_close_end_time': scene.appleseed.shutter_close}

        return cam_params

    def __thin_lens_camera_params(self, scene, aspect_ratio, film_width, film_height):
        camera = self.bl_camera

        cam_params = self.__basic_camera_params(scene, aspect_ratio, film_width, film_height)
        cam_params.update({'f_stop': camera.data.appleseed.f_number,
                           'autofocus_enabled': False,
                           'diaphragm_blades': camera.data.appleseed.diaphragm_blades,
                           'diaphragm_tilt_angle': camera.data.appleseed.diaphragm_angle,
                           'focal_distance': util.get_focal_distance(camera)})

        if camera.data.appleseed.enable_autofocus:
            x, y = util.find_autofocus_point(scene)
            cam_params['autofocus_target'] = asr.Vector2f(x, y)
            cam_params['autofocus_enabled'] = True

        if camera.data.appleseed.diaphragm_map != "":
            filename = self.asset_handler.process_path(camera.data.appleseed.diaphragm_map, AssetType.TEXTURE_ASSET)
            self.__cam_map = asr.Texture('disk_texture_2d', 'cam_map',
                                         {'filename': filename, 'color_space': camera.data.appleseed.diaphragm_map_colorspace}, [])
            self.__cam_map_inst = asr.TextureInstance("cam_map_inst", {'addressing_mode': 'wrap',
                                                                       'filtering_mode': 'bilinear'},
                                                      "cam_map", asr.Transformf(asr.Matrix4f.identity()))

            cam_params['diaphragm_map'] = 'cam_map_inst'
            del cam_params['diaphragm_blades']

        return cam_params

    def __fisheye_camera_params(self, scene, aspect_ratio, film_width, film_height):
        camera = self.bl_camera

        cam_params = self.__basic_camera_params(scene, aspect_ratio, film_width, film_height)

        cam_params.update({'projection_type': camera.data.appleseed.fisheye_projection_type})

        return cam_params


class InteractiveCameraTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, cam, context, asset_handler):
        super(InteractiveCameraTranslator, self).__init__(cam, asset_handler)

        self.__context = context

    #
    # Properties.
    #

    @property
    def bl_camera(self):
        return self._bl_obj

    @property
    def context(self):
        return self.__context

    #
    # Entity translation.
    #

    def create_entities(self, scene=None):
        logger.debug("Creating camera entity for camera: interactive camera")

        self.__set_cam_props()

        self.__as_int_camera = asr.Camera(self.__model, "interactive_camera", self.__params)

    def set_transform_key(self, scene, time, key_times):
        self.set_transform(time)

    def flush_entities(self, scene):
        logger.debug("Flushing camera entity for camera: interactive camera")

        # Insert the camera into the scene.
        cam_name = self.__as_int_camera.get_name()
        scene.cameras().insert(self.__as_int_camera)
        self.__as_int_camera = scene.cameras().get_by_name(cam_name)

    def update(self, scene, camera=None, context=None):
        logger.debug("Update interactive camera")
        if camera is not None and context is not None:
            self._reset(camera, context)

        scene.cameras().remove(self.__as_int_camera)
        self.create_entities(scene)
        self.flush_entities(scene)

    #
    # Internal methods.
    #

    def set_transform(self, time):
        self.__as_int_camera.transform_sequence().set_transform(time, self._convert_matrix(self.__matrix))

    def check_for_camera_update(self, camera, context):
        """
        This function only needs to test for matrix changes and viewport lens/zoom changes.  All other camera
        changes are captured by a scene update
        """

        cam_param_update = False
        cam_translate_update = False

        # Get current translation, zoom and lens from viewport
        current_translation = self.__matrix
        zoom = self.__zoom
        lens = self.__lens
        extent_base = self.__extent_base
        shift_x = self.__shift_x
        shift_y = self.__shift_y

        self._reset(camera, context)

        self.__set_cam_props()

        # Check zoom
        if zoom != self.__zoom or extent_base != self.__extent_base or lens != self.__lens or shift_x != self.__shift_x or shift_y != self.__shift_y:
            cam_param_update = True

        if current_translation != self.__matrix:
            cam_translate_update = True

        return cam_param_update, cam_translate_update

    def _reset(self, cam, context):
        super(InteractiveCameraTranslator, self)._reset(cam)

        self.__context = context

    def __set_cam_props(self):
        # todo: add view offset

        view_cam_type = self.context.region_data.view_perspective
        width = self.context.region.width
        height = self.context.region.height

        aspect_ratio = width / height

        self.__lens = self.context.space_data.lens
        self.__zoom = None
        self.__extent_base = None
        self.__shift_x = None
        self.__shift_y = None

        if view_cam_type == "ORTHO":
            self.__zoom = 2
            self.__extent_base = self.context.space_data.region_3d.view_distance * 32.0 / self.__lens
            self.__model, self.__params = self.__ortho_camera_params(aspect_ratio)

        elif view_cam_type == "PERSP":
            self.__zoom = 2
            self.__model, self.__params = self.__persp_camera_params(aspect_ratio)

        elif view_cam_type == "CAMERA":
            # Borrowed from Cycles source code, since no sane person would figure this out on their own
            self.__zoom = 4 / ((math.sqrt(2) + self.context.region_data.view_camera_zoom / 50) ** 2)
            self.__model, self.__params = self.__view_camera_params(aspect_ratio)

    def __view_camera_params(self, aspect_ratio):
        film_width, film_height = util.calc_film_dimensions(aspect_ratio, self.bl_camera.data, self.__zoom)

        offset = tuple(self.context.region_data.view_camera_offset)

        x_aspect_comp = 1 if aspect_ratio > 1 else 1 / aspect_ratio
        y_aspect_comp = aspect_ratio if aspect_ratio > 1 else 1

        self.__shift_x = ((offset[0] * 2 + (self.bl_camera.data.shift_x * x_aspect_comp)) / self.__zoom) * film_width
        self.__shift_y = ((offset[1] * 2 + (self.bl_camera.data.shift_y * y_aspect_comp)) / self.__zoom) * film_height

        self.__matrix = self.bl_camera.matrix_world
        cam_mapping = {'PERSP': 'pinhole_camera',
                       'ORTHO': 'orthographic_camera',
                       'PANO': 'fisheyelens_camera'}

        model = cam_mapping[self.bl_camera.data.type]

        if model == 'pinhole_camera' and self.bl_camera.data.appleseed.enable_dof and self.bl_camera.data.type != 'PANO':
            model = 'thinlens_camera'

        if model == 'orthographic_camera':
            sensor_width = self.bl_camera.data.ortho_scale * self.__zoom
            params = {'film_width': sensor_width,
                      'aspect_ratio': aspect_ratio}

            if self.bl_camera.data.sensor_fit == 'VERTICAL' or (self.bl_camera.data.sensor_fit == 'AUTO' and aspect_ratio < 1):
                params['film_height'] = params.pop('film_width')

        else:
            aspect_ratio = util.get_frame_aspect_ratio(self.context.scene)
            params = {'focal_length': self.bl_camera.data.lens / 1000,
                      'aspect_ratio': aspect_ratio,
                      'shift_x': self.__shift_x,
                      'shift_y': self.__shift_y,
                      'film_dimensions': asr.Vector2f(film_width, film_height)}

        if model == 'fisheyelens_camera':
            if self.bl_camera.data.appleseed.fisheye_projection_type is not 'none':
                params['projection_type'] = self.bl_camera.data.appleseed.fisheye_projection_type
            else:
                print("Spherical camera not supported for interactive rendering")

        if model == 'thinlens_camera':
            params.update({'f_stop': self.bl_camera.data.appleseed.f_number,
                           'autofocus_enabled': False,
                           'diaphragm_blades': self.bl_camera.data.appleseed.diaphragm_blades,
                           'diaphragm_tilt_angle': self.bl_camera.data.appleseed.diaphragm_angle,
                           'focal_distance': util.get_focal_distance(self.bl_camera)})

        return model, params

    def __persp_camera_params(self, aspect_ratio):
        model = 'pinhole_camera'
        sensor_size = 32 * self.__zoom
        self.__matrix = Matrix(self.context.region_data.view_matrix).inverted()
        params = {'focal_length': self.context.space_data.lens,
                  'aspect_ratio': aspect_ratio,
                  'film_width': sensor_size}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        return model, params

    def __ortho_camera_params(self, aspect_ratio):
        model = 'orthographic_camera'
        self.__matrix = Matrix(self.context.region_data.view_matrix).inverted()
        sensor_width = self.__zoom * self.__extent_base * 1
        params = {'film_width': sensor_width,
                  'aspect_ratio': aspect_ratio}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        return model, params


