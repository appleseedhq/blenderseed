
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
        bpy.types.Scene.appleseed_sky = bpy.props.PointerProperty(name="appleseed_sky",
                                                                  description="appleseed Sky",
                                                                  type=cls)

        cls.env_type = bpy.props.EnumProperty(name="Environment Type",
                                              items=[("constant", "Constant", "Use constant color for sky"),
                                                     ("gradient", "Gradient", "Use sky color gradient"),
                                                     ("constant_hemisphere", "Per-Hemisphere Constant", "Use constant color per hemisphere"),
                                                     ("latlong_map", "Latitude-Longitude Map", "Use latlong map texture"),
                                                     ("mirrorball_map", "Mirror Ball Map", "Use mirror ball texture"),
                                                     ("sunsky", "Physical Sun/Sky", "")],
                                              description="Select environment type",
                                              default="gradient")

        cls.sun_model = bpy.props.EnumProperty(name="Sun Model",
                                               items=[("hosek_environment_edf", "Hosek-Wilkie", 'Hosek-Wilkie physical sun/sky model'),
                                                      ('preetham_environment_edf', "Preetham", 'Preetham physical sun/sky model')],
                                               description="Physical sun/sky model",
                                               default="hosek_environment_edf")

        cls.sun_lamp = bpy.props.EnumProperty(name="Sun Lamp",
                                              items=sun_enumerator,
                                              description="Sun lamp to export")

        cls.sun_theta = bpy.props.FloatProperty(name="sun_theta",
                                                description='',
                                                default=0.0,
                                                min=-180,
                                                max=180)

        cls.sun_phi = bpy.props.FloatProperty(name="sun_phi",
                                              description='',
                                              default=0.0,
                                              min=-180,
                                              max=180)

        cls.turbidity = bpy.props.FloatProperty(name="turbidity",
                                                description='',
                                                default=4.0,
                                                min=0.0,
                                                max=10.0)

        cls.turbidity_multiplier = bpy.props.FloatProperty(name="turbidity_multiplier",
                                                           description='',
                                                           default=2.0,
                                                           min=0,
                                                           max=10.0)

        cls.luminance_multiplier = bpy.props.FloatProperty(name="luminance_multiplier",
                                                           description='',
                                                           default=1.0,
                                                           min=0.0)

        cls.luminance_gamma = bpy.props.FloatProperty(name="luminance_gamma",
                                                      description='',
                                                      default=1.0,
                                                      min=0.0)

        cls.saturation_multiplier = bpy.props.FloatProperty(name="saturation_multiplier",
                                                            description='',
                                                            default=1.0,
                                                            min=0.0)

        cls.horizon_shift = bpy.props.FloatProperty(name="horizon_shift",
                                                    description='',
                                                    default=0.0,
                                                    min=-2.0,
                                                    max=2.0)

        cls.ground_albedo = bpy.props.FloatProperty(name="ground_albedo",
                                                    description='',
                                                    default=0.3,
                                                    min=0.0,
                                                    max=1.0)

        cls.env_tex_mult = bpy.props.FloatProperty(name="env_tex_mult",
                                                   description="",
                                                   default=1.0,
                                                   min=0.0)

        cls.env_tex = bpy.props.StringProperty(name="env_tex",
                                               description="Texture to influence environment",
                                               default="")

    @classmethod
    def unregister(cls):
        del bpy.types.Scene.appleseed_sky


def register():
    pass


def unregister():
    pass
