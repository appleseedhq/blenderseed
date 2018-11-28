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


class AppleseedLampProps(bpy.types.PropertyGroup):
    radiance = bpy.props.FloatVectorProperty(name="radiance",
                                             description="Color of light emitted by lamp",
                                             default=(0.8, 0.8, 0.8),
                                             min=0.0,
                                             max=1.0,
                                             subtype='COLOR')

    radiance_use_tex = bpy.props.BoolProperty(name="radiance_use_tex",
                                              description="Use texture to influence lamp intensity",
                                              default=False)

    radiance_tex = bpy.props.StringProperty(name="radiance_tex",
                                            description="Texture to influence lamp intensity",
                                            default="",
                                            subtype='FILE_PATH')

    radiance_tex_color_space = bpy.props.EnumProperty(name="radiance_tex_color_space",
                                                      items=[('linear_rgb', "Linear", ""),
                                                             ('srgb', "sRGB", "")],
                                                      default='linear_rgb')

    radiance_multiplier = bpy.props.FloatProperty(name="radiance_multiplier",
                                                  description="Multiplier of lamp intensity",
                                                  default=1,
                                                  min=0,
                                                  soft_max=10)

    radiance_multiplier_use_tex = bpy.props.BoolProperty(name="radiance_multiplier_use_tex",
                                                         description="Use texture to influence intensity multiplier",
                                                         default=False)

    radiance_multiplier_tex = bpy.props.StringProperty(name="radiance_multiplier_tex",
                                                       description="Texture to influence intensity multiplier",
                                                       default="",
                                                       subtype='FILE_PATH')

    radiance_multiplier_tex_color_space = bpy.props.EnumProperty(name="radiance_multiplier_tex_color_space",
                                                                 items=[('linear_rgb', "Linear", ""),
                                                                        ('srgb', "sRGB", "")],
                                                                 default='linear_rgb')

    exposure = bpy.props.FloatProperty(name="exposure",
                                       description="Exposure",
                                       default=0.0,
                                       min=-64.0,
                                       max=64.0)

    exposure_multiplier = bpy.props.FloatProperty(name="exposure_multiplier",
                                                  description="Spotlight exposure multiplier",
                                                  default=1.0,
                                                  soft_min=-64.0,
                                                  soft_max=64.0)

    cast_indirect = bpy.props.BoolProperty(name="cast_indirect",
                                           description="Lamp casts indirect light",
                                           default=True)

    importance_multiplier = bpy.props.FloatProperty(name="importance_multiplier",
                                                    description="Adjust the sampling effort for this light with respect to the other lights",
                                                    default=1,
                                                    min=0,
                                                    soft_max=10)

    turbidity = bpy.props.FloatProperty(name="turbidity",
                                        description="Sun lamp turbidity. If physical sky environment is also used, environment turbidity value will be used instead",
                                        default=4,
                                        min=0,
                                        max=8)

    use_edf = bpy.props.BoolProperty(name="use_edf",
                                     description="Use the environment EDF to determine Sun angle",
                                     default=False)

    size_multiplier = bpy.props.FloatProperty(name="size_multiplier",
                                              description="The size multiplier allows to make the Sun bigger or smaller, hence making it cast softer or harder shadows",
                                              default=1.0,
                                              min=0.0,
                                              max=100.0)

    distance = bpy.props.FloatProperty(name="distance",
                                       description="Distance between Sun and scene (millions of km)",
                                       default=149.6,
                                       min=0.0,
                                       max=500.0)

    tilt_angle = bpy.props.FloatProperty(name="tilt_angle",
                                         description="Spot lamp tilt angle",
                                         default=0,
                                         min=-360,
                                         max=360)

    # Area lamp specific parameters.
    area_shape = bpy.props.EnumProperty(name="area_shape",
                                        description="",
                                        items=[('grid', "Rectangle", ""),
                                               ('disk', "Disk", ""),
                                               ('sphere', "Sphere", "")],
                                        default='grid')

    area_color = bpy.props.FloatVectorProperty(name="area_color",
                                               description="Color of area lamp",
                                               subtype='COLOR',
                                               default=(1.0, 1.0, 1.0))

    area_intensity = bpy.props.FloatProperty(name="area_intensity",
                                             description="Intensity of area light",
                                             default=1.0)

    area_intensity_scale = bpy.props.FloatProperty(name="area_intensity_scale",
                                                   description="Intensity of area light",
                                                   default=1.0)

    area_exposure = bpy.props.FloatProperty(name="exposure",
                                            description="Intensity of area light",
                                            default=1.0)

    area_normalize = bpy.props.BoolProperty(name="area_normalize",
                                            description="",
                                            default=False)

    area_visibility = bpy.props.BoolProperty(name="area_visibility",
                                             description="",
                                             default=True)

    osl_node_tree = bpy.props.PointerProperty(name="Lamp OSL Node Tree", type=bpy.types.NodeTree)


def register():
    util.safe_register_class(AppleseedLampProps)
    bpy.types.Lamp.appleseed = bpy.props.PointerProperty(type=AppleseedLampProps)


def unregister():
    del bpy.types.Lamp.appleseed
    util.safe_unregister_class(AppleseedLampProps)
