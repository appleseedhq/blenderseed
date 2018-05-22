
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
    light_near_start = bpy.props.FloatProperty(name="light_near_start",
                                               description="Amount by which to extend the start of light's influence away from the emissive material",
                                               default=0.0,
                                               min=0,
                                               max=10)

    light_emission_profile = bpy.props.EnumProperty(name="Profile",
                                                    description="Profile for emission",
                                                    items=[('diffuse_edf', "Diffuse EDF", ""),
                                                           ('cone_edf', "Cone EDF", "")],
                                                    default='diffuse_edf')

    light_cone_edf_angle = bpy.props.FloatProperty(name="light_cone_edf_angle",
                                                   description="Angle of spread for cone EDF",
                                                   default=90.0,
                                                   min=0.0,
                                                   max=180.0)

def register():
    util.safe_register_class(AppleseedLampProps)
    bpy.types.Lamp.appleseed = bpy.props.PointerProperty(type=AppleseedLampProps)


def unregister():
    del bpy.types.Lamp.appleseed
    util.safe_unregister_class(AppleseedLampProps)
