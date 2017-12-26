
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
# appleseed Lamps panel.
#------------------------------------


class AppleseedLampPanel(bpy.types.Panel):
    bl_label = "Lamp"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        renderer = context.scene.render.engine
        return ob is not None and ob.type == 'LAMP' and renderer == 'APPLESEED_RENDER'

    def draw(self, context):
        layout = self.layout
        lamp_data = context.object.data
        asr_lamp = lamp_data.appleseed

        layout.prop(lamp_data, "type", expand=True)

        if lamp_data.type == 'SPOT':
            split = layout.split(percentage=0.40)
            col = split.column()
            col.label("Intensity:")
            split = split.split(percentage=0.83)
            col = split.column()
            col.prop(asr_lamp, "radiance", text="")

            col = split.column()
            col.prop(asr_lamp, "radiance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)

            if asr_lamp.radiance_use_tex:
                layout.prop_search(asr_lamp, "radiance_tex", lamp_data, "texture_slots", text="")
                if asr_lamp.radiance_tex != '' and asr_lamp.radiance_use_tex:
                    radiance_tex = bpy.data.textures[asr_lamp.radiance_tex]
                    layout.prop(radiance_tex.image.colorspace_settings, "name", text="Color Space")

            split = layout.split(percentage=0.90)
            col = split.column()
            col.prop(asr_lamp, "radiance_multiplier", text="Intensity Multiplier")

            col = split.column()
            col.prop(asr_lamp, "radiance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)

            if asr_lamp.radiance_multiplier_use_tex:
                layout.prop_search(asr_lamp, "radiance_multiplier_tex", lamp_data, "texture_slots", text="")
                if asr_lamp.radiance_multiplier_tex != '' and asr_lamp.radiance_multiplier_use_tex:
                    radiance_multiplier_tex = bpy.data.textures[asr_lamp.radiance_multiplier_tex]
                    layout.prop(radiance_multiplier_tex.image.colorspace_settings, "name", text="Color Space")

            layout.prop(lamp_data, "spot_blend", text="Inner Angle")
            layout.prop(lamp_data, "spot_size", text="Outer Angle")
            layout.prop(asr_lamp, "tilt_angle", text="Tilt Angle")
            layout.prop(lamp_data, "show_cone")
            layout.prop(asr_lamp, "exposure", text="Exposure")
            layout.prop(asr_lamp, "cast_indirect", text="Cast Indirect Light")
            layout.prop(asr_lamp, "importance_multiplier", text="Importance Multiplier")

        if lamp_data.type == 'POINT':
            layout.prop(asr_lamp, "radiance", text="Intensity")
            layout.prop(asr_lamp, "radiance_multiplier", text="Intensity Multiplier")
            layout.prop(asr_lamp, "cast_indirect", text="Cast Indirect Light")
            layout.prop(asr_lamp, "importance_multiplier", text="Importance Multiplier")

        if lamp_data.type == 'SUN':
            layout.prop(asr_lamp, "turbidity", text="Turbidity")
            layout.prop(asr_lamp, "radiance_multiplier", text="Radiance Multiplier")
            layout.prop(asr_lamp, "cast_indirect", text="Cast Indirect Light")
            layout.prop(asr_lamp, "importance_multiplier", text="Importance Multiplier")

        if lamp_data.type == 'HEMI':
            layout.prop(asr_lamp, "radiance", text="Irradiance")

        if lamp_data.type == 'AREA':
            layout.label("Area lights are unsupported in blenderseed")


def register():
    bpy.utils.register_class(AppleseedLampPanel)


def unregister():
    bpy.utils.unregister_class(AppleseedLampPanel)
