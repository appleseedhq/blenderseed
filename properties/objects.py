
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2014-2017 The appleseedhq Organization
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


class AppleseedObjSettings(bpy.types.PropertyGroup):

    @classmethod
    def register(cls):
        bpy.types.Object.appleseed = bpy.props.PointerProperty(name="appleseed_object",
                                                               description="appleseed Object",
                                                               type=cls)

        cls.enable_motion_blur = bpy.props.BoolProperty(name="enable_motion_blur",
                                                        description="Enable rendering of motion blur",
                                                        default=False)

        cls.motion_blur_type = bpy.props.EnumProperty(name="Motion Blur Type",
                                                      items=[('object', 'Object', 'Object motion blur'),
                                                             ('deformation', 'Deformation', 'Deformation motion blur. Warning: this will increase export time')],
                                                      description="Type of motion blur to render",
                                                      default='object')

        cls.enable_visibility_flags = bpy.props.BoolProperty(name="enable_visibility_flags",
                                                             description="Enable visibility flags for object",
                                                             default=False)

        cls.camera_visible = bpy.props.BoolProperty(name="camera_visible",
                                                    description="Visibility to camera",
                                                    default=True)

        cls.light_visible = bpy.props.BoolProperty(name="light_visible",
                                                   description="Visibility to lights",
                                                   default=True)

        cls.shadow_visible = bpy.props.BoolProperty(name="shadow_visible",
                                                    description="Visibility to shadows",
                                                    default=True)

        cls.transparency_visible = bpy.props.BoolProperty(name="transparency_visible",
                                                          description="Visibility to transparency",
                                                          default=True)

        cls.probe_visible = bpy.props.BoolProperty(name="probe_visible",
                                                   description="Visibility to probes",
                                                   default=True)

        cls.diffuse_visible = bpy.props.BoolProperty(name="diffuse_visible",
                                                     description="Visibility to diffuse rays",
                                                     default=True)

        cls.glossy_visible = bpy.props.BoolProperty(name="glossy_visible",
                                                    description="Visibility to glossy rays",
                                                    default=True)

        cls.specular_visible = bpy.props.BoolProperty(name="specular_visible",
                                                      description="Visibility to specular rays",
                                                      default=True)

        cls.medium_priority = bpy.props.IntProperty(name="medium_priority",
                                                    description="Medium priority for nested dielectrics.  Higher numbers take priority over lower numbers.",
                                                    default=0)

    @classmethod
    def unregister(cls):
        del bpy.types.Object.appleseed


def register():
    pass


def unregister():
    pass
