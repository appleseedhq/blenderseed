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


class ASLAMP_PT_lamp(bpy.types.Panel):
    bl_label = "Lamp"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        renderer = context.scene.render.engine
        return ob is not None and ob.type == 'LIGHT' and renderer == 'APPLESEED_RENDER'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        lamp_data = context.object.data
        asr_lamp = lamp_data.appleseed

        if lamp_data.type == 'SPOT':
            split = layout.split(factor=0.40)
            col = split.column()
            col.label(text="Intensity:")
            split = split.split(factor=0.83, align=True)
            col = split.column()
            col.prop(asr_lamp, "radiance", text="")

            col = split.column(align=True)
            col.prop(asr_lamp, "radiance_use_tex", text="", icon="TEXTURE", toggle=True)

            if asr_lamp.radiance_use_tex:
                col = layout.column(align=True)
                col.template_ID(asr_lamp, "radiance_tex", open="image.open")
                if asr_lamp.radiance_tex is not None:
                    as_rad_tex = asr_lamp.radiance_tex
                    col.prop(as_rad_tex.appleseed, "as_color_space", text="Color Space")
                    col.prop(as_rad_tex.appleseed, "as_wrap_mode", text="Wrap Mode")
                    col.prop(as_rad_tex.appleseed, "as_alpha_mode", text="Alpha Mode")

            split = layout.split(factor=0.90, align=True)
            col = split.column(align=True)
            col.prop(asr_lamp, "radiance_multiplier", text="Intensity Multiplier")

            col = split.column(align=True)
            col.prop(asr_lamp, "radiance_multiplier_use_tex", text="", icon="TEXTURE", toggle=True)

            if asr_lamp.radiance_multiplier_use_tex:
                col = layout.column(align=True)
                col.template_ID(asr_lamp, "radiance_multiplier_tex", open="image.open")
                if asr_lamp.radiance_multiplier_tex is not None:
                    as_rad_mult_tex = asr_lamp.radiance_multiplier_tex
                    col.prop(as_rad_mult_tex.appleseed, "as_color_space", text="Color Space")
                    col.prop(as_rad_mult_tex.appleseed, "as_wrap_mode", text="Wrap Mode")
                    col.prop(as_rad_mult_tex.appleseed, "as_alpha_mode", text="Alpha Mode")

            layout.prop(lamp_data, "spot_blend", text="Inner Angle")
            layout.prop(lamp_data, "spot_size", text="Outer Angle")
            layout.prop(asr_lamp, "tilt_angle", text="Tilt Angle")
            layout.prop(lamp_data, "show_cone")
            layout.prop(asr_lamp, "exposure", text="Exposure")
            layout.prop(asr_lamp, "exposure_multiplier", text="Exposure Multiplier")
            layout.prop(asr_lamp, "cast_indirect", text="Cast Indirect Light")
            layout.prop(asr_lamp, "importance_multiplier", text="Importance Multiplier")

        if lamp_data.type == 'POINT':
            layout.prop(asr_lamp, "radiance", text="Intensity")
            layout.prop(asr_lamp, "radiance_multiplier", text="Intensity Multiplier")
            layout.prop(asr_lamp, "cast_indirect", text="Cast Indirect Light")
            layout.prop(asr_lamp, "importance_multiplier", text="Importance Multiplier")

        if lamp_data.type == 'SUN':
            layout.prop(asr_lamp, "sun_mode", text="Sun Lamp Mode")
            if asr_lamp.sun_mode == 'sun':
                layout.prop(asr_lamp, "use_edf", text="Use Environment For Sun Direction")
                if asr_lamp.use_edf and context.scene.world.appleseed_sky.env_type != 'sunsky':
                    layout.label(text="WARNING: Must select 'Physical Sky' for environemnt model")
                layout.prop(asr_lamp, "turbidity", text="Turbidity")
                layout.prop(asr_lamp, "distance", text="Sun Distance")
                layout.prop(asr_lamp, "size_multiplier", text="Size Multiplier")
                layout.prop(asr_lamp, "radiance_multiplier", text="Radiance Multiplier")
                layout.prop(asr_lamp, "cast_indirect", text="Cast Indirect Light")
                layout.prop(asr_lamp, "importance_multiplier", text="Importance Multiplier")

            if asr_lamp.sun_mode == 'distant':
                layout.prop(asr_lamp, "radiance", text="Intensity")
                layout.prop(asr_lamp, "radiance_multiplier", text="Intensity Multiplier")
                layout.prop(asr_lamp, "exposure", text="Exposure")
                layout.prop(asr_lamp, "cast_indirect", text="Cast Indirect Light")
                layout.prop(asr_lamp, "importance_multiplier", text="Importance Multiplier")

        if lamp_data.type == 'AREA':
            layout.prop(asr_lamp, "area_shape", expand=True, text="Shape")
            col = layout.column(align=True)
            if asr_lamp.area_shape == 'rectangle_object':
                col.prop(lamp_data, "size", text="Size X")
                col.prop(lamp_data, "size_y", text="Size Y")
            else:
                col.prop(lamp_data, "size", text="Size")

            layout.prop(asr_lamp, "area_visibility", text="Camera Visibility")
            if not lamp_data.use_nodes:
                layout.prop(asr_lamp, "area_color", text="Color")
                layout.prop(asr_lamp, "area_intensity", text="Intensity")
                layout.prop(asr_lamp, "area_intensity_scale", text="Intensity Scale")
                layout.prop(asr_lamp, "area_exposure", text="Exposure")
                layout.prop(asr_lamp, "area_normalize", text="Normalize")


def register():
    util.safe_register_class(ASLAMP_PT_lamp)


def unregister():
    util.safe_unregister_class(ASLAMP_PT_lamp)
