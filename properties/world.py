
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


def sun_enumerator(self, context):
    sun = []
    for object in context.scene.objects:
        if object.type == 'LAMP':
            if object.data.type == 'SUN':
                sun.append((object.name, object.name, ""))
    return sun


class AppleseedSkySettings(bpy.types.PropertyGroup):

    @classmethod
    def register(cls):
        bpy.types.Scene.appleseed_sky = bpy.props.PointerProperty(name="appleseed Sky",
                                                                  description="appleseed Sky",
                                                                  type=cls)

        cls.env_type = bpy.props.EnumProperty(items=[("constant", "Constant", "Use constant color for sky"),
                                                     ("gradient", "Gradient", "Use sky color gradient"),
                                                     ("constant_hemisphere", "Per-Hemisphere Constant", "Use constant color per hemisphere"),
                                                     ("latlong_map", "Latitude-Longitude Map", "Use latlong map texture"),
                                                     ("mirrorball_map", "Mirror Ball Map", "Use mirror ball texture"),
                                                     ("sunsky", "Physical Sun/Sky", "")],
                                              name="Environment Type",
                                              description="Select environment type",
                                              default="gradient")

        cls.sun_model = bpy.props.EnumProperty(items=[("hosek_environment_edf", "Hosek-Wilkie", 'Hosek-Wilkie physical sun/sky model'),
                                                      ('preetham_environment_edf', "Preetham", 'Preetham physical sun/sky model')],
                                               name="Sun Model",
                                               description="Physical sun/sky model",
                                               default="hosek_environment_edf")

        cls.env_tex = bpy.props.StringProperty(name="Environment Texture",
                                               description="Texture to influence environment",
                                               default="")

        cls.env_tex_mult = bpy.props.FloatProperty(name="Radiance Multiplier",
                                                   description="",
                                                   default=1.0,
                                                   min=0.0,
                                                   max=2.0)

        cls.sun_theta = bpy.props.FloatProperty(name="Sun Theta Angle",
                                                description='',
                                                default=0.0,
                                                min=-180,
                                                max=180)

        cls.sun_phi = bpy.props.FloatProperty(name="Sun Phi Angle",
                                              description='',
                                              default=0.0,
                                              min=-180,
                                              max=180)

        cls.sun_lamp = bpy.props.EnumProperty(items=sun_enumerator,
                                              name="Sun Lamp",
                                              description="Sun lamp to export")

        cls.horiz_shift = bpy.props.FloatProperty(name="Horizon Shift",
                                                  description='',
                                                  default=0.0,
                                                  min=-2.0,
                                                  max=2.0)

        cls.luminance_multiplier = bpy.props.FloatProperty(name="Sky Luminance Multiplier",
                                                           description='',
                                                           default=1.0,
                                                           min=0.0,
                                                           max=20.0)

        cls.radiance_multiplier = bpy.props.FloatProperty(name="Sun Radiance Multiplier",
                                                          description='',
                                                          default=0.05,
                                                          min=0.0,
                                                          max=1.0)

        cls.saturation_multiplier = bpy.props.FloatProperty(name="Saturation Multiplier",
                                                            description='',
                                                            default=1.0,
                                                            min=0.0,
                                                            max=10.0)

        cls.turbidity = bpy.props.FloatProperty(name="Turbidity",
                                                description='',
                                                default=4.0,
                                                min=0.0,
                                                max=10.0)

        cls.turbidity_max = bpy.props.FloatProperty(name="Turbidity Max",
                                                    description='',
                                                    default=6.0,
                                                    min=0,
                                                    max=10.0)

        cls.turbidity_min = bpy.props.FloatProperty(name="Turbidity Min",
                                                    description='',
                                                    default=2.0,
                                                    min=0,
                                                    max=10.0)

        cls.ground_albedo = bpy.props.FloatProperty(name="Ground Albedo",
                                                    description='',
                                                    default=0.3,
                                                    min=0.0,
                                                    max=1.0)

        cls.env_radiance_multiplier = bpy.props.FloatProperty(name="Environment Energy Multiplier",
                                                              description="Multiply the exitance of the environment by this factor",
                                                              min=0.0,
                                                              max=1000.0,
                                                              default=1.0,
                                                              subtype='FACTOR')

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.appleseed_sky


def register():
    pass


def unregister():
    pass
