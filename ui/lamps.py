
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
            # Lamp radiance.
            # layout.label( "Intensity:")
            split = layout.split(percentage=0.90)
            col = split.column()
            col.prop(asr_lamp, "radiance", text="")

            col = split.column()
            col.prop(asr_lamp, "radiance_use_tex", icon="TEXTURE_SHADED", toggle=True)

            if asr_lamp.radiance_use_tex:
                layout.prop_search(asr_lamp, "radiance_tex", lamp_data, "texture_slots")
                if asr_lamp.radiance_tex != '' and asr_lamp.radiance_use_tex:
                    radiance_tex = bpy.data.textures[asr_lamp.radiance_tex]
                    layout.prop(radiance_tex.image.colorspace_settings, "name", text="Color Space")

            # Radiance multiplier.
            split = layout.split(percentage=0.90)
            col = split.column()
            col.prop(asr_lamp, "radiance_multiplier")

            col = split.column()
            col.prop(asr_lamp, "radiance_multiplier_use_tex", icon="TEXTURE_SHADED", toggle=True)

            if asr_lamp.radiance_multiplier_use_tex:
                layout.prop_search(asr_lamp, "radiance_multiplier_tex", lamp_data, "texture_slots")
                if asr_lamp.radiance_multiplier_tex != '' and asr_lamp.radiance_multiplier_use_tex:
                    radiance_multiplier_tex = bpy.data.textures[asr_lamp.radiance_multiplier_tex]
                    layout.prop(radiance_multiplier_tex.image.colorspace_settings, "name", text="Color Space")

            layout.prop(lamp_data, "spot_blend", text="Inner Angle")
            layout.prop(lamp_data, "spot_size", text="Outer Angle")
            layout.prop(asr_lamp, "tilt_angle")
            layout.prop(lamp_data, "show_cone")

        elif lamp_data.type in {'POINT', 'SUN', 'HEMI'}:
            # layout.label("Intensity:")
            layout.prop(asr_lamp, "radiance")
            layout.prop(asr_lamp, "radiance_multiplier")

            if lamp_data.type == 'SUN':
                layout.prop(asr_lamp, "turbidity")

        if lamp_data.type != 'AREA':
            layout.prop(asr_lamp, "cast_indirect")
            layout.prop(asr_lamp, "importance_multiplier")

        else:
            layout.label("Area lights are unsupported.")


def register():
    bpy.utils.register_class(AppleseedLampPanel)


def unregister():
    bpy.utils.unregister_class(AppleseedLampPanel)
