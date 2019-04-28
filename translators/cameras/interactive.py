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
from ..textures import TextureTranslator
from ..translator import Translator
from ...logger import get_logger
from ...utils import util

logger = get_logger()


class InteractiveCameraTranslator(Translator):
    """
    This translator is responsible for translating the Blender camera into an appleseed
    camera object for final rendering.  This includes support for stereoscopic rendering.
    """

    def __init__(self, asset_handler, engine, context, camera=None):
        logger.debug("Creating interactive camera translator")
        super().__init__(camera, asset_handler)

        self.__as_camera = None
        self.__xform_seq = asr.TransformSequence()
        self.__engine = engine
        self.__context = context
        self.__model = None
        self.__view_cam_type = None
        self.__params = None
        self.__matrix = None

    @property
    def bl_camera(self):
        return self._bl_obj

    def create_entities(self, bl_scene, textures_to_add, as_texture_translators):
        logger.debug("Creating entity for camera")

        self.__view_cam_type = self.__context.region_data.view_perspective

        self.__model = self.__get_model()

        self.__get_cam_params(bl_scene, textures_to_add, as_texture_translators)

        self.__as_camera = asr.Camera(self.__model, "Camera", self.__params)

    def set_xform_step(self, time):
        self.__as_camera.transform_sequence().set_transform(time, self._convert_matrix(self.__matrix))

    def flush_entities(self, as_scene, as_assembly, as_project):
        logger.debug("Flushing camera entity, num xform keys = %s", self.__xform_seq.size())

        as_scene.cameras().insert(self.__as_camera)
        self.__as_camera = as_scene.cameras().get_by_name("Camera")

    def check_view(self, context):
        """
        This function only needs to test for matrix changes and viewport lens/zoom changes.  All other camera
        changes are captured by a scene update
        """
        cam_param_update = False
        cam_translate_update = False
        cam_model_update = False

        model = self.__model
        current_translation = self.__matrix
        zoom = self.__zoom
        lens = self.__lens
        extent_base = self.__extent_base
        shift_x = self.__shift_x
        shift_y = self.__shift_y

        self.__context = context

        self.__view_cam_type = self.__context.region_data.view_perspective

        self.__model = self.__get_model()

        self.__get_cam_params(context.depsgraph.scene_eval, None, None)

        if current_translation != self.__matrix:
            cam_translate_update = True

        if zoom != self.__zoom or extent_base != self.__extent_base or lens != self.__lens or \
                shift_x != self.__shift_x or shift_y != self.__shift_y:
            cam_param_update = True

        if model != self.__model:
            cam_model_update = True

        return cam_param_update, cam_translate_update, cam_model_update

    def update_camera(self, context, as_scene, cam_model_update, textures_to_add, as_texture_translators):
        logger.debug("Updating camera entity")
        self.__context = context
        if cam_model_update:
            as_scene.cameras().remove(self.__as_camera)
            self.create_entities(context.depsgraph.scene_eval, textures_to_add, as_texture_translators)
            self.flush_entities(as_scene, None, None)
        else:
            self.__as_camera.set_parameters(self.__params)

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

    def __get_cam_params(self, bl_scene, textures_to_add, as_texture_translators):
        view_cam_type = self.__context.region_data.view_perspective
        width = self.__context.region.width
        height = self.__context.region.height

        aspect_ratio = width / height

        self.__lens = self.__context.space_data.lens
        self.__zoom = None
        self.__extent_base = None
        self.__shift_x = None
        self.__shift_y = None

        if view_cam_type == "ORTHO":
            self.__zoom = 2.25
            self.__extent_base = self.__context.space_data.region_3d.view_distance * 32.0 / self.__lens
            self.__set_ortho_camera_params(aspect_ratio)

        elif view_cam_type == "PERSP":
            self.__zoom = 2.25
            self.__set_persp_camera_params(aspect_ratio)

        elif view_cam_type == "CAMERA":
            # Borrowed from Cycles source code, since for something this nutty there's no reason to reinvent the wheel
            self.__zoom = 4 / ((math.sqrt(2) + self.__context.region_data.view_camera_zoom / 50) ** 2)
            self.__set_view_camera_params(aspect_ratio, textures_to_add, as_texture_translators)

    def __set_ortho_camera_params(self, aspect_ratio):
        self.__matrix = Matrix(self.__context.region_data.view_matrix).inverted()
        sensor_width = self.__zoom * self.__extent_base * 1
        params = {'film_width': sensor_width,
                  'aspect_ratio': aspect_ratio}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        self.__params = params

    def __set_persp_camera_params(self, aspect_ratio):
        sensor_size = 32 * self.__zoom
        self.__matrix = Matrix(self.__context.region_data.view_matrix).inverted()
        params = {'focal_length': self.__context.space_data.lens,
                  'aspect_ratio': aspect_ratio,
                  'film_width': sensor_size}

        if aspect_ratio < 1:
            params['film_height'] = params.pop('film_width')

        self.__params = params

    def __set_view_camera_params(self, aspect_ratio, textures_to_add, as_texture_translators):
        film_width, film_height = util.calc_film_dimensions(aspect_ratio, self.bl_camera.data, self.__zoom)

        offset = tuple(self.__context.region_data.view_camera_offset)

        x_aspect_comp = 1 if aspect_ratio > 1 else 1 / aspect_ratio
        y_aspect_comp = aspect_ratio if aspect_ratio > 1 else 1

        self.__shift_x = ((offset[0] * 2 + (self.bl_camera.data.shift_x * x_aspect_comp)) / self.__zoom) * film_width
        self.__shift_y = ((offset[1] * 2 + (self.bl_camera.data.shift_y * y_aspect_comp)) / self.__zoom) * film_height

        self.__matrix = self.bl_camera.matrix_world

        if self.__model == 'orthographic_camera':
            sensor_width = self.bl_camera.data.ortho_scale * self.__zoom
            params = {'film_width': sensor_width,
                      'aspect_ratio': aspect_ratio}

            if self.bl_camera.data.sensor_fit == 'VERTICAL' or (self.bl_camera.data.sensor_fit == 'AUTO' and aspect_ratio < 1):
                params['film_height'] = params.pop('film_width')

        else:
            aspect_ratio = util.get_frame_aspect_ratio(self.__context.scene)
            params = {'focal_length': self.bl_camera.data.lens / 1000,
                      'aspect_ratio': aspect_ratio,
                      'shift_x': self.__shift_x,
                      'shift_y': self.__shift_y,
                      'film_dimensions': asr.Vector2f(film_width, film_height)}

        if self.__model == 'fisheyelens_camera':
            if self.bl_camera.data.appleseed.fisheye_projection_type is not 'none':
                params['projection_type'] = self.bl_camera.data.appleseed.fisheye_projection_type
            else:
                self.__engine.report({'ERROR'}, "Panoramic camera not supported in interactive mode")

        if self.__model == 'thinlens_camera':
            params.update({'f_stop': self.bl_camera.data.appleseed.f_number,
                           'autofocus_enabled': False,
                           'diaphragm_blades': self.bl_camera.data.appleseed.diaphragm_blades,
                           'diaphragm_tilt_angle': self.bl_camera.data.appleseed.diaphragm_angle,
                           'focal_distance': util.get_focal_distance(self.bl_camera)})

            if textures_to_add is not None and as_texture_translators is not None:
                if self.bl_camera.data.appleseed.diaphragm_map is not None:
                    tex_id = self.bl_camera.data.appleseed.diaphragm_map.name_full
                    if tex_id not in as_texture_translators:
                        textures_to_add[tex_id] = TextureTranslator(self.bl_camera.data.appleseed.diaphragm_map,
                                                                    self.asset_handler)
                    tex_name = f"{self.bl_camera.data.appleseed.diaphragm_map.name_full}_inst"
                    params.update({'diaphragm_map': tex_name})
                    del params['diaphragm_blades']

        self.__params = params
