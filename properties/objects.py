
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
from .. import util


class AppleseedObjSettings(bpy.types.PropertyGroup):

    enable_motion_blur = bpy.props.BoolProperty(name="enable_motion_blur",
                                                description="Enable rendering of motion blur",
                                                default=False)

    motion_blur_type = bpy.props.EnumProperty(name="Motion Blur Type",
                                              items=[('object', 'Object', 'Object motion blur'),
                                                     ('deformation', 'Deformation', 'Deformation motion blur. Warning: this will increase export time')],
                                              description="Type of motion blur to render",
                                              default='object')

    enable_visibility_flags = bpy.props.BoolProperty(name="enable_visibility_flags",
                                                     description="Enable visibility flags for object",
                                                     default=False)

    camera_visible = bpy.props.BoolProperty(name="camera_visible",
                                            description="Visibility to camera",
                                            default=True)

    light_visible = bpy.props.BoolProperty(name="light_visible",
                                           description="Visibility to lights",
                                           default=True)

    shadow_visible = bpy.props.BoolProperty(name="shadow_visible",
                                            description="Visibility to shadows",
                                            default=True)

    transparency_visible = bpy.props.BoolProperty(name="transparency_visible",
                                                  description="Visibility to transparency",
                                                  default=True)

    probe_visible = bpy.props.BoolProperty(name="probe_visible",
                                           description="Visibility to probes",
                                           default=True)

    diffuse_visible = bpy.props.BoolProperty(name="diffuse_visible",
                                             description="Visibility to diffuse rays",
                                             default=True)

    glossy_visible = bpy.props.BoolProperty(name="glossy_visible",
                                            description="Visibility to glossy rays",
                                            default=True)

    specular_visible = bpy.props.BoolProperty(name="specular_visible",
                                              description="Visibility to specular rays",
                                              default=True)

    medium_priority = bpy.props.IntProperty(name="medium_priority",
                                            description="Medium priority for nested dielectrics.  Higher numbers take priority over lower numbers.",
                                            default=0)

    double_sided = bpy.props.BoolProperty(name="double_sided",
                                          default=True)

    object_alpha = bpy.props.FloatProperty(name="object_alpha",
                                           description="Object Alpha",
                                           default=1.0,
                                           min=0.0,
                                           max=1.0)

    object_sss_set = bpy.props.StringProperty(name="object_sss_set",
                                              description="SSS set",
                                              default="")

    object_alpha_use_texture = bpy.props.BoolProperty(name="object_alpha_use_texture",
                                                      description="Use a texture to influence object alpha",
                                                      default=False)

    object_alpha_texture = bpy.props.StringProperty(name="object_alpha_texture",
                                                    description="Texture to use for alpha channel",
                                                    default="",
                                                    subtype='FILE_PATH')

    object_alpha_texture_colorspace = bpy.props.EnumProperty(name="Color Space",
                                                             description="Color space",
                                                             items=[('srgb', "sRGB", ""),
                                                                    ('linear_rgb', "Linear", "")],
                                                             default='linear_rgb')

    object_alpha_texture_wrap_mode = bpy.props.EnumProperty(name="Texture Wrapping",
                                                            description="Texture wrapping method",
                                                            items=[('clamp', "Clamp", ""),
                                                                   ('wrap', "Wrap", "")],
                                                            default='wrap')

    object_alpha_mode = bpy.props.EnumProperty(name="object_alpha_mode",
                                               items=[
                                                   ('alpha_channel', "Alpha Channel", ""),
                                                   ('luminance', "Luminance", ""),
                                                   ('detect', "Detect", "")],
                                               default='detect')


def register():
    util.safe_register_class(AppleseedObjSettings)
    bpy.types.Object.appleseed = bpy.props.PointerProperty(type=AppleseedObjSettings)


def unregister():
    del bpy.types.Object.appleseed
    util.safe_unregister_class(AppleseedObjSettings)
