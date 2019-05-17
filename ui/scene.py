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


class ASAOV_PT_panel_base(object):
    bl_context = "view_layer"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'


class ASAOV_PT_aovs(bpy.types.Panel, ASAOV_PT_panel_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Render Passes"

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed

        col = layout.column(align=True)
        col.prop(asr_scene_props, "diffuse_aov", text="Diffuse", toggle=True)
        col.prop(asr_scene_props, "direct_diffuse_aov", text="Direct Diffuse", toggle=True)
        col.prop(asr_scene_props, "indirect_diffuse_aov", text="Indirect Diffuse", toggle=True)

        layout.separator()

        col = layout.column(align=True)
        col.prop(asr_scene_props, "glossy_aov", text="Glossy", toggle=True)
        col.prop(asr_scene_props, "direct_glossy_aov", text="Direct Glossy", toggle=True)
        col.prop(asr_scene_props, "indirect_glossy_aov", text="Indirect Glossy", toggle=True)

        layout.separator()

        col = layout.column(align=True)
        col.prop(asr_scene_props, "albedo_aov", text="Albedo", toggle=True)
        col.prop(asr_scene_props, "emission_aov", text="Emission", toggle=True)

        layout.separator()

        col = layout.column(align=True)
        col.prop(asr_scene_props, "npr_shading_aov", text="NPR Shading", toggle=True)
        col.prop(asr_scene_props, "npr_contour_aov", text="NPR Contour", toggle=True)

        layout.separator()

        col = layout.column(align=True)
        col.prop(asr_scene_props, "normal_aov", text="Normals", toggle=True)
        col.prop(asr_scene_props, "position_aov", text="Position", toggle=True)
        col.prop(asr_scene_props, "uv_aov", text="UV Coordinates", toggle=True)
        col.prop(asr_scene_props, "depth_aov", text="Depth", toggle=True)
        col.prop(asr_scene_props, "screen_space_velocity_aov", text="Screen Space Velocity", toggle=True)
        col.prop(asr_scene_props, "pixel_time_aov", text="Pixel Time", toggle=True)
        col.prop(asr_scene_props, "pixel_variation_aov", text="Pixel Variation", toggle=True)
        col.prop(asr_scene_props, "pixel_sample_count_aov", text="Sample Count", toggle=True)
        col.prop(asr_scene_props, "invalid_samples_aov", text="Invalid Samples", toggle=True)

        layout.separator()
        col = layout.column(align=True)
        col.prop(asr_scene_props, "cryptomatte_object_aov", text="Cryptomatte Object", toggle=True)
        col.prop(asr_scene_props, "cryptomatte_material_aov", text="Cryptomatte Material", toggle=True)


def register():
    util.safe_register_class(ASAOV_PT_aovs)


def unregister():
    util.safe_unregister_class(ASAOV_PT_aovs)
