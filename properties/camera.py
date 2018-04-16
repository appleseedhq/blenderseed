
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

import bpy


def get_shutter_min(self, context):
    return context.scene.camera.appleseed.shutter_open


def get_shutter_max(self, context):
    return context.scene.camera.appleseed.shutter_close


class AppleseedCameraSettings(bpy.types.PropertyGroup):

    @classmethod
    def register(cls):
        bpy.types.Camera.appleseed = bpy.props.PointerProperty(name="appleseed_camera",
                                                               description="appleseed Camera",
                                                               type=cls)

        cls.camera_model = bpy.props.EnumProperty(name="camera_model",
                                                  items=[('pinhole', 'Pinhole', ''),
                                                         ('thinlens', 'Thin Lens', ''),
                                                         ('spherical', 'Spherical', '')],
                                                  description="Camera model",
                                                  default='pinhole')

        cls.near_z = bpy.props.FloatProperty(name="near_z",
                                             description="Near clipping distance",
                                             default=-0.001)

        cls.enable_dof = bpy.props.BoolProperty(name="enable_dof",
                                                description="Enable depth of field",
                                                default=False)

        cls.f_number = bpy.props.FloatProperty(name="f_number",
                                               description="Thin lens camera f-stop value",
                                               default=32.0,
                                               min=0.0,
                                               max=32.0,
                                               step=3,
                                               precision=1)

        cls.diaphragm_blades = bpy.props.IntProperty(name="diaphragm_blades",
                                                     description="Number of diaphragm blades. Use minimum of 3 for geometric bokeh",
                                                     default=3,
                                                     max=32,
                                                     min=0)

        cls.diaphragm_angle = bpy.props.FloatProperty(name="diaphragm_angle",
                                                      description="Diaphragm tilt angle",
                                                      default=0,
                                                      min=-360,
                                                      max=360,
                                                      precision=3)

        cls.diaphragm_map = bpy.props.StringProperty(name="diaphragm_map",
                                                     description="Image texture to define bokeh",
                                                     default='',
                                                     subtype='FILE_PATH')

    @classmethod
    def unregister(cls):
        del bpy.types.Camera.appleseed


def register():
    pass


def unregister():
    pass
