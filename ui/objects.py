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


class AppleseedExportOverridePanel(bpy.types.Panel):
    bl_label = "Object Export"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE', 'EMPTY'}

    def draw(self, context):
        layout = self.layout
        asr_obj = context.object.appleseed

        layout.prop(asr_obj, "object_export", text="Object Export")
        row = layout.row()
        row.enabled = asr_obj.object_export == 'archive_assembly'
        row.prop(asr_obj, "archive_path", text="Archive Path")


class AppleseedObjFlagsPanel(bpy.types.Panel):
    bl_label = "Visibility"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE'}

    def draw(self, context):
        layout = self.layout
        asr_obj = context.object.appleseed
        sss_lists = context.scene.appleseed_sss_sets

        box = layout.box()
        box.label(text="Ray Visibility:")
        box.prop(asr_obj, "camera_visible", text="Camera", toggle=True)
        box.prop(asr_obj, "light_visible", text="Light", toggle=True)
        box.prop(asr_obj, "shadow_visible", text="Shadow", toggle=True)
        box.prop(asr_obj, "diffuse_visible", text="Diffuse", toggle=True)
        box.prop(asr_obj, "glossy_visible", text="Glossy", toggle=True)
        box.prop(asr_obj, "specular_visible", text="Specular", toggle=True)
        box.prop(asr_obj, "transparency_visible", text="Transparency", toggle=True)

        layout.separator()
        box = layout.box()
        box.label(text="Ray Bias:")
        box.prop(asr_obj, "object_ray_bias_method", text="Method")
        box.prop(asr_obj, "object_ray_bias_distance", text="Distance")

        layout.separator()
        layout.label(text="Object Alpha:")
        row = layout.row()
        row.active = asr_obj.object_alpha_texture is None
        row.prop(asr_obj, "object_alpha", text="")

        col = layout.column()
        col.template_ID(asr_obj, "object_alpha_texture", open="image.open")
        col.prop(asr_obj, "object_alpha_texture_colorspace", text="Color Space")
        col.prop(asr_obj, "object_alpha_texture_wrap_mode", text="Wrap Mode")
        col.prop(asr_obj, "object_alpha_mode", text="Alpha Mode")

        layout.separator()

        layout.prop(asr_obj, "double_sided", text="Double Sided Shading")
        layout.prop(asr_obj, "photon_target", text="SPPM Photon Target")
        layout.prop(asr_obj, "medium_priority", text="Nested Glass Priority")
        layout.prop_search(asr_obj, "object_sss_set", sss_lists, "sss_sets", text="SSS Set")


class AppleseedObjectBlurPanel(bpy.types.Panel):
    bl_label = "Motion Blur"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE'}

    def draw(self, context):
        layout = self.layout
        asr_obj = context.object.appleseed

        layout.prop(asr_obj, "use_deformation_blur", text="Use Deformation Blur", toggle=True)


def register():
    util.safe_register_class(AppleseedObjFlagsPanel)
    util.safe_register_class(AppleseedExportOverridePanel)
    util.safe_register_class(AppleseedObjectBlurPanel)


def unregister():
    util.safe_unregister_class(AppleseedObjectBlurPanel)
    util.safe_unregister_class(AppleseedExportOverridePanel)
    util.safe_unregister_class(AppleseedObjFlagsPanel)
