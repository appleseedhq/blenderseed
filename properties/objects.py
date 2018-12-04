
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


class AppleseedObjSettings(bpy.types.PropertyGroup):
    object_export = bpy.props.EnumProperty(name="object_export",
                                             items=[('normal', "Normal", ""),
                                                    ('archive_assembly', "Archive Assembly", "")],
                                             default='normal')

    archive_path = bpy.props.StringProperty(name="archive_path",
                                            default="",
                                            subtype="FILE_PATH")

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

    photon_target = bpy.props.BoolProperty(name="photon_target",
                                           default=False)

    object_alpha = bpy.props.FloatProperty(name="object_alpha",
                                           description="Object Alpha",
                                           default=1.0,
                                           min=0.0,
                                           max=1.0)

    object_alpha_use_texture = bpy.props.BoolProperty(name="object_alpha_use_texture",
                                                      description="Use a texture to influence object alpha",
                                                      default=False)

    object_alpha_texture = bpy.props.PointerProperty(name="object_alpha_texture",
                                                     type=bpy.types.Image)

    object_alpha_texture_colorspace = bpy.props.EnumProperty(name="object_alpha_texture_colorspace",
                                                             description="Color space",
                                                             items=[('srgb', "sRGB", ""),
                                                                    ('linear_rgb', "Linear", "")],
                                                             default='linear_rgb')

    object_alpha_texture_wrap_mode = bpy.props.EnumProperty(name="object_alpha_texture_wrap_mode",
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

    object_sss_set = bpy.props.StringProperty(name="object_sss_set",
                                              description="SSS set",
                                              default="")

    object_ray_bias_method = bpy.props.EnumProperty(name="object_ray_bias_method",
                                                    items=[
                                                        ('none', "No Ray Bias", ""),
                                                        ('normal', "Shift Along Surface Normal", ""),
                                                        ('incoming_direction', "Shift Along Incoming Direction", ""),
                                                        ('outgoing_direction', "Shift Along Outgoing Direction", "")],
                                                    default='none')

    object_ray_bias_distance = bpy.props.FloatProperty(name="object_ray_bias_distance",
                                                       default=0.0)

    use_deformation_blur = bpy.props.BoolProperty(name="use_deformation_blur",
                                                  default=True)


def register():
    util.safe_register_class(AppleseedObjSettings)
    bpy.types.Object.appleseed = bpy.props.PointerProperty(type=AppleseedObjSettings)


def unregister():
    del bpy.types.Object.appleseed
    util.safe_unregister_class(AppleseedObjSettings)
