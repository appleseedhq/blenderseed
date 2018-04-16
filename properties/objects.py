
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

        cls.ray_bias_distance = bpy.props.FloatProperty(name="ray_bias_distance",
                                                        description="Ray bias distance",
                                                        default=0.0)

        cls.ray_bias_method = bpy.props.EnumProperty(name="Ray Bias Method",
                                                     description="Ray bias method",
                                                     items=[('none', "None", ""),
                                                            ('incoming_direction', "Shift Along Incoming Direction", ""),
                                                            ('outgoing_direction', "Shift Along Outgoing Direction", ""),
                                                            ('normal', "Shift Along Surface Normal", "")],
                                                     default='none')

        cls.object_alpha = bpy.props.FloatProperty(name="object_alpha",
                                                   description="Object Alpha",
                                                   default=1.0,
                                                   min=0.0,
                                                   max=1.0)

        cls.object_sss_set = bpy.props.StringProperty(name="object_sss_set",
                                                      description="SSS set",
                                                      default="")

        cls.object_alpha_use_texture = bpy.props.BoolProperty(name="object_alpha_use_texture",
                                                              description="Use a texture to influence object alpha",
                                                              default=False)

        cls.object_alpha_texture = bpy.props.StringProperty(name="object_alpha_texture",
                                                            description="Texture to use for alpha channel",
                                                            default="",
                                                            subtype='FILE_PATH')

        cls.object_alpha_texture_colorspace = bpy.props.EnumProperty(name="Color Space",
                                                                     description="Color space",
                                                                     items=[('srgb', "sRGB", ""),
                                                                            ('linear_rgb', "Linear", "")],
                                                                     default='linear_rgb')

        cls.object_alpha_texture_wrap_mode = bpy.props.EnumProperty(name="Texture Wrapping",
                                                                    description="Texture wrapping method",
                                                                    items=[('clamp', "Clamp", ""),
                                                                           ('wrap', "Wrap", "")],
                                                                    default='wrap')

    @classmethod
    def unregister(cls):
        del bpy.types.Object.appleseed


def register():
    pass


def unregister():
    pass
