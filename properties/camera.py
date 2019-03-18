#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
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

import bpy

from ..utils import util


def get_shutter_min(self, context):
    return context.scene.camera.appleseed.shutter_open


def get_shutter_max(self, context):
    return context.scene.camera.appleseed.shutter_close


class AppleseedCameraSettings(bpy.types.PropertyGroup):
    fisheye_projection_type = bpy.props.EnumProperty(name="fisheye_projection_type",
                                                     items=[
                                                         ('none', "None", ""),
                                                         ('equisolid_angle', "Equisolid Angle", ""),
                                                         ('equidistant', "Equidistant", ""),
                                                         ('stereographic', "Stereographic", ""),
                                                         ('thoby', "Thoby", "")],
                                                     default='equisolid_angle')

    near_z = bpy.props.FloatProperty(name="near_z",
                                     description="Near clipping distance",
                                     default=-0.001)

    enable_dof = bpy.props.BoolProperty(name="enable_dof",
                                        description="Enable depth of field",
                                        default=False)

    enable_autofocus = bpy.props.BoolProperty(name="enable_autofocus",
                                              description="",
                                              default=False)

    f_number = bpy.props.FloatProperty(name="f_number",
                                       description="Thin lens camera f-stop value",
                                       default=8.0,
                                       min=0.0,
                                       max=32.0,
                                       step=3,
                                       precision=1)

    diaphragm_blades = bpy.props.IntProperty(name="diaphragm_blades",
                                             description="Number of diaphragm blades. Use minimum of 3 for geometric bokeh",
                                             default=3,
                                             max=32,
                                             min=0)

    diaphragm_angle = bpy.props.FloatProperty(name="diaphragm_angle",
                                              description="Diaphragm tilt angle",
                                              default=0,
                                              min=-360,
                                              max=360,
                                              precision=3)

    diaphragm_map = bpy.props.StringProperty(name="diaphragm_map",
                                             description="Image texture to define bokeh",
                                             default='',
                                             subtype='FILE_PATH')

    diaphragm_map_colorspace = bpy.props.EnumProperty(name="env_tex_colorspace",
                                                      description="Color space of input texture",
                                                      items=[
                                                          ('srgb', "sRGB", ""),
                                                          ('linear_rgb', "Linear RGB", ""),
                                                          ('ciexyz', "CIE XYZ", "")],
                                                      default="linear_rgb")


def register():
    util.safe_register_class(AppleseedCameraSettings)
    bpy.types.Camera.appleseed = bpy.props.PointerProperty(type=AppleseedCameraSettings)


def unregister():
    del bpy.types.Camera.appleseed
    util.safe_unregister_class(AppleseedCameraSettings)
