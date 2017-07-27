
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

#------------------------------------
# appleseed Lamp properties
#------------------------------------


class AppleseedLampProps(bpy.types.PropertyGroup):

    @classmethod
    def register(cls):
        bpy.types.Lamp.appleseed = bpy.props.PointerProperty(name="appleseed Lamp",
                                                             description="appleseed Lamp",
                                                             type=cls)

        cls.radiance = bpy.props.FloatVectorProperty(name="",
                                                     description="Color of light emitted by lamp",
                                                     default=(0.8, 0.8, 0.8),
                                                     min=0.0,
                                                     max=1.0,
                                                     subtype='COLOR')

        cls.radiance_use_tex = bpy.props.BoolProperty(name="",
                                                      description="Use texture to influence lamp intensity",
                                                      default=False)

        cls.radiance_tex = bpy.props.StringProperty(name="",
                                                    description="Texture to influence lamp intensity",
                                                    default="")

        cls.radiance_multiplier = bpy.props.FloatProperty(name="Intensity Multiplier",
                                                          description="Multiplier of lamp intensity",
                                                          default=1,
                                                          min=0,
                                                          soft_max=10,
                                                          max=9999)

        cls.radiance_multiplier_use_tex = bpy.props.BoolProperty(name="",
                                                                 description="Use texture to influence intensity multiplier",
                                                                 default=False)

        cls.radiance_multiplier_tex = bpy.props.StringProperty(name="",
                                                               description="Texture to influence intensity multiplier",
                                                               default="")

        cls.cast_indirect = bpy.props.BoolProperty(name="Cast Indirect Light",
                                                   description="Lamp casts indirect light",
                                                   default=True)

        cls.importance_multiplier = bpy.props.FloatProperty(name="Importance Multiplier",
                                                            description="Multiple importance sampling multiplier",
                                                            default=1,
                                                            min=0,
                                                            soft_max=10,
                                                            max=100)

        cls.turbidity = bpy.props.FloatProperty(name="Turbidity",
                                                description="Sun lamp turbidity. If physical sky environment is also used, environment turbidity value will be used instead",
                                                default=4,
                                                min=0,
                                                max=8)

        cls.tilt_angle = bpy.props.FloatProperty(name="Tilt Angle",
                                                 description="Spot lamp tilt angle",
                                                 default=0,
                                                 min=-360,
                                                 max=360)

    @classmethod
    def unregister(cls):
        del bpy.types.Lamp.appleseed


def register():
    pass


def unregister():
    pass
