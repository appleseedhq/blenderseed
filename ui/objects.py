#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 Jonathan Dent, The appleseedhq Organization
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


class ASOBJECT_PT_obj_flags(bpy.types.Panel):
    bl_label = "appleseed Object Options"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE', 'EMPTY'}

    def draw(self, context):
        pass


class ASOBJECT_PT_obj_options(bpy.types.Panel):
    bl_label = "Visibility"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "ASOBJECT_PT_obj_flags"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        asr_obj = context.object.appleseed
        sss_lists = context.scene.appleseed_sss_sets

        layout.prop(asr_obj, "double_sided", text="Double Sided Shading")
        layout.prop(asr_obj, "photon_target", text="SPPM Photon Target")
        layout.prop(asr_obj, "medium_priority", text="Nested Glass Priority")
        layout.prop_search(asr_obj, "object_sss_set", sss_lists, "sss_sets", text="SSS Set")


class ASOBJECT_PT_obj_visibility(bpy.types.Panel):
    bl_label = "Ray Visibility"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "ASOBJECT_PT_obj_flags"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        asr_obj = context.object.appleseed

        layout.prop(asr_obj, "camera_visible", text="Camera")
        layout.prop(asr_obj, "light_visible", text="Light")
        layout.prop(asr_obj, "shadow_visible", text="Shadow")
        layout.prop(asr_obj, "diffuse_visible", text="Diffuse")
        layout.prop(asr_obj, "glossy_visible", text="Glossy")
        layout.prop(asr_obj, "specular_visible", text="Specular")
        layout.prop(asr_obj, "transparency_visible", text="Transparency")


class ASOBJECT_PT_obj_alpha(bpy.types.Panel):
    bl_label = "Alpha"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "ASOBJECT_PT_obj_flags"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        asr_obj = context.object.appleseed

        row = layout.row()
        row.active = asr_obj.object_alpha_texture is None
        row.prop(asr_obj, "object_alpha", text="Object Alpha")

        col = layout.column(align=True)
        col.template_ID(asr_obj, "object_alpha_texture", open="image.open")
        if asr_obj.object_alpha_texture is not None:
            as_alpha_tex = asr_obj.object_alpha_texture
            col.prop(as_alpha_tex.appleseed, "as_color_space", text="Color Space")
            col.prop(as_alpha_tex.appleseed, "as_wrap_mode", text="Wrap Mode")
            col.prop(as_alpha_tex.appleseed, "as_alpha_mode", text="Alpha Mode")


class ASOBJECT_PT_motion_blur(bpy.types.Panel):
    bl_label = "Motion Blur"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "ASOBJECT_PT_obj_flags"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        asr_obj = context.object.appleseed

        layout.prop(asr_obj, "use_deformation_blur", text="Use Deformation Blur")


class ASOBJECT_PT_export_override(bpy.types.Panel):
    bl_label = "Object Export"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "ASOBJECT_PT_obj_flags"

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


classes = (
    ASOBJECT_PT_obj_flags,
    ASOBJECT_PT_obj_options,
    ASOBJECT_PT_obj_visibility,
    ASOBJECT_PT_obj_alpha,
    ASOBJECT_PT_motion_blur,
    ASOBJECT_PT_export_override
)


def register():
    for cls in classes:
        util.safe_register_class(cls)


def unregister():
    for cls in reversed(classes):
        util.safe_unregister_class(cls)
