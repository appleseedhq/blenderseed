
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


class AppleseedWorldPanelOld(bpy.types.Panel):
    bl_label = "Environment"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        if renderer.engine == 'APPLESEED_RENDER':
            return context.scene.world != None
        return False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_sky_props = scene.appleseed_sky

        layout.prop(asr_sky_props, "env_type", text="")

        if asr_sky_props.env_type == "sunsky":
            layout.label("Sun Lamp:")
            layout.prop(asr_sky_props, "sun_lamp", text="")
            layout.prop(asr_sky_props, "sun_model", text="Sky Model")

            layout.prop(asr_sky_props, "luminance_multiplier")
            layout.prop(asr_sky_props, "radiance_multiplier")
            layout.prop(asr_sky_props, "saturation_multiplier")
            layout.prop(asr_sky_props, "sun_theta")
            layout.prop(asr_sky_props, "sun_phi")
            layout.prop(asr_sky_props, "turbidity")
            layout.prop(asr_sky_props, "turbidity_min")
            layout.prop(asr_sky_props, "turbidity_max")
            layout.prop(asr_sky_props, "horiz_shift")
            if asr_sky_props.sun_model == "hosek_environment_edf":
                layout.prop(asr_sky_props, "ground_albedo")

        elif asr_sky_props.env_type == "gradient":
            layout.prop(scene.world, "horizon_color", text="")
            layout.prop(scene.world, "zenith_color", text="")

        elif asr_sky_props.env_type == "constant":
            layout.prop(scene.world, "horizon_color", text="")

        elif asr_sky_props.env_type == "constant_hemisphere":
            layout.prop(scene.world, "horizon_color", text="")
            layout.prop(scene.world, "zenith_color", text="")

        elif asr_sky_props.env_type == "mirrorball_map":
            layout.prop_search(asr_sky_props, "env_tex", scene.world, "texture_slots", text="")
            layout.prop(asr_sky_props, "env_tex_mult")

        elif asr_sky_props.env_type == "latlong_map":
            layout.prop_search(asr_sky_props, "env_tex", scene.world, "texture_slots", text="")
            layout.prop(asr_sky_props, "env_tex_mult")


def register():
    bpy.types.WORLD_PT_context_world.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.WORLD_PT_custom_props.COMPAT_ENGINES.add('APPLESEED_RENDER')


def unregister():
    pass
