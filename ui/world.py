
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


class AppleseedWorldPanel(bpy.types.Panel):
    bl_label = "Environment"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        if renderer.engine == 'APPLESEED_RENDER':
            return context.scene.world is not None
        return False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_sky_props = scene.appleseed_sky

        layout.prop(asr_sky_props, "env_type", text="Environment Type")

        if asr_sky_props.env_type == "sunsky":
            layout.prop(asr_sky_props, "sun_lamp", text="Sun Lamp")
            layout.prop(asr_sky_props, "sun_model", text="Sun Model")

            layout.prop(asr_sky_props, "sun_theta", text="Sun Theta Angle")
            layout.prop(asr_sky_props, "sun_phi", text="Sun Phi Angle")
            layout.prop(asr_sky_props, "turbidity", text="Turbidity")
            layout.prop(asr_sky_props, "turbidity_multiplier", text="Turbidity Multiplier")
            layout.prop(asr_sky_props, "luminance_multiplier", text="Luminance Multiplier")
            layout.prop(asr_sky_props, "luminance_gamma", text="Luminance Gamma")
            layout.prop(asr_sky_props, "saturation_multiplier", text="Saturation Multiplier")
            layout.prop(asr_sky_props, "horizon_shift", text="Horizon Shift")

            if asr_sky_props.sun_model == "hosek_environment_edf":
                layout.prop(asr_sky_props, "ground_albedo", text="Ground Albedo")

        elif asr_sky_props.env_type == "gradient":
            layout.prop(scene.world, "horizon_color", text="Horizon Radiance")
            layout.prop(scene.world, "zenith_color", text="Zenith Radiance")

        elif asr_sky_props.env_type == "constant":
            layout.prop(scene.world, "horizon_color", text="Radiance")

        elif asr_sky_props.env_type == "constant_hemisphere":
            layout.prop(scene.world, "zenith_color", text="Upper Hemisphere Radiance")
            layout.prop(scene.world, "horizon_color", text="Lower Hemisphere Radiance")

        elif asr_sky_props.env_type == "mirrorball_map":
            layout.prop_search(asr_sky_props, "env_tex", scene.world, "texture_slots", text="Environment Texture")
            layout.prop(asr_sky_props, "env_tex_mult", text="Radiance Multiplier")

        elif asr_sky_props.env_type == "latlong_map":
            layout.prop_search(asr_sky_props, "env_tex", scene.world, "texture_slots", text="Environment Texture")
            layout.prop(asr_sky_props, "env_tex_mult", text="Radiance Multiplier")
            layout.prop(asr_sky_props, "env_exposure", text="Exposure")
            layout.prop(asr_sky_props, "horizontal_shift", text="Horizontal Shift")
            layout.prop(asr_sky_props, "vertical_shift", text="Vertical Shift")

        layout.prop(asr_sky_props, "env_alpha", text="Alpha")


def register():
    bpy.types.WORLD_PT_context_world.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.WORLD_PT_custom_props.COMPAT_ENGINES.add('APPLESEED_RENDER')


def unregister():
    pass
