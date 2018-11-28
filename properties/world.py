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


class AppleseedSSSSetsProps(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="SSS Set Name",
                                    default="")


class AppleseedSSSSets(bpy.types.PropertyGroup):
    sss_sets = bpy.props.CollectionProperty(type=AppleseedSSSSetsProps,
                                            name="appleseed SSS Sets",
                                            description="")

    sss_sets_index = bpy.props.IntProperty(name="layer_index",
                                           description="",
                                           default=0)


class AppleseedSkySettings(bpy.types.PropertyGroup):
    env_type = bpy.props.EnumProperty(name="Environment Type",
                                      items=[("constant", "Constant", "Use constant color for sky", "", 1),
                                             ("gradient", "Gradient", "Use sky color gradient", "", 2),
                                             ("latlong_map", "HDRI Environment", "Use HDRI map texture", "", 3),
                                             ("mirrorball_map", "Mirror Ball", "Use mirror ball texture", "", 4),
                                             ("none", "None", "", "", 7),
                                             ("sunsky", "Physical Sky", "", "", 5),
                                             ("constant_hemisphere", "Per-Hemisphere Constant", "Use constant color per hemisphere", "", 6)],
                                      description="Select environment type",
                                      default="none")

    sun_model = bpy.props.EnumProperty(name="Sky Model",
                                       items=[('hosek', "Hosek-Wilkie", "Hosek-Wilkie physical sun/sky model")],
                                       description="Physical sun/sky model",
                                       default='hosek')

    sun_theta = bpy.props.FloatProperty(name="sun_theta",
                                        description="Sun polar (vertical) angle in degrees",
                                        default=0.0,
                                        min=-180,
                                        max=180)

    sun_phi = bpy.props.FloatProperty(name="sun_phi",
                                      description="Sun azimuthal (horizontal) angle in degrees",
                                      default=0.0,
                                      min=-180,
                                      max=180)

    turbidity = bpy.props.FloatProperty(name="turbidity",
                                        description='',
                                        default=4.0,
                                        min=0.0,
                                        max=10.0)

    turbidity_multiplier = bpy.props.FloatProperty(name="turbidity_multiplier",
                                                   description='',
                                                   default=2.0,
                                                   min=0,
                                                   max=10.0)

    luminance_multiplier = bpy.props.FloatProperty(name="luminance_multiplier",
                                                   description='',
                                                   default=1.0,
                                                   min=0.0)

    luminance_gamma = bpy.props.FloatProperty(name="luminance_gamma",
                                              description='',
                                              default=1.0,
                                              min=0.0)

    saturation_multiplier = bpy.props.FloatProperty(name="saturation_multiplier",
                                                    description='',
                                                    default=1.0,
                                                    min=0.0)

    horizon_shift = bpy.props.FloatProperty(name="horizon_shift",
                                            description='',
                                            default=0.0,
                                            min=-2.0,
                                            max=2.0)

    ground_albedo = bpy.props.FloatProperty(name="ground_albedo",
                                            description='',
                                            default=0.3,
                                            min=0.0,
                                            max=1.0)

    env_tex_mult = bpy.props.FloatProperty(name="env_tex_mult",
                                           description="",
                                           default=1)

    env_tex_colorspace = bpy.props.EnumProperty(name="env_tex_colorspace",
                                                description="Color space of input texture",
                                                items=[
                                                    ('srgb', "sRGB", ""),
                                                    ('linear_rgb', "Linear RGB", ""),
                                                    ('ciexyz', "CIE XYZ", "")],
                                                default='linear_rgb')

    env_tex = bpy.props.PointerProperty(name="env_tex",
                                        type=bpy.types.Image)

    horizontal_shift = bpy.props.FloatProperty(name="horizontal_shift",
                                               description="Environment texture horizontal shift in degrees",
                                               default=0.0,
                                               min=-360.0,
                                               max=360.0)

    vertical_shift = bpy.props.FloatProperty(name="vertical_shift",
                                             description="Environment texture vertical shift in degrees",
                                             default=0.0,
                                             min=-180.0,
                                             max=180.0)

    env_alpha = bpy.props.FloatProperty(name="env_alpha",
                                        description="Alpha value of the environment",
                                        default=1.0,
                                        min=0.0,
                                        max=1.0)

    env_exposure = bpy.props.FloatProperty(name="env_exposure",
                                           description="Environment exposure",
                                           default=0.0)

    env_exposure_multiplier = bpy.props.FloatProperty(name="env_exposure_multiplier",
                                                      description="",
                                                      default=1.0,
                                                      soft_min=-64.0,
                                                      soft_max=64.0)


def register():
    util.safe_register_class(AppleseedSSSSetsProps)
    util.safe_register_class(AppleseedSSSSets)
    util.safe_register_class(AppleseedSkySettings)
    bpy.types.Scene.appleseed_sss_sets = bpy.props.PointerProperty(type=AppleseedSSSSets)
    bpy.types.World.appleseed_sky = bpy.props.PointerProperty(type=AppleseedSkySettings)


def unregister():
    del bpy.types.World.appleseed_sky
    del bpy.types.Scene.appleseed_sss_sets
    util.safe_unregister_class(AppleseedSkySettings)
    util.safe_unregister_class(AppleseedSSSSets)
    util.safe_unregister_class(AppleseedSSSSetsProps)
