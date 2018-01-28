
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


class AppleseedObjFlagsPanel(bpy.types.Panel):
    bl_label = "Appleseed Object Flags"
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
        layout.prop(asr_obj, "enable_visibility_flags", text="Enable Visibility Flags")
        col = layout.column()
        col.active = asr_obj.enable_visibility_flags
        row = col.row()
        row.prop(asr_obj, "camera_visible", text="Camera")
        row.prop(asr_obj, "light_visible", text="Light")
        row = col.row()
        row.prop(asr_obj, "shadow_visible", text="Shadow")
        row.prop(asr_obj, "transparency_visible", text="Transparency")
        row = col.row()
        row.prop(asr_obj, "probe_visible", text="Probe")
        row.prop(asr_obj, "diffuse_visible", text="Diffuse")
        row = col.row()
        row.prop(asr_obj, "glossy_visible", text="Glossy")
        row.prop(asr_obj, "specular_visible", text="Specular")


class AppleseedObjOptionsPanel(bpy.types.Panel):
    bl_label = "Appleseed Object Options"
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
        scene = context.scene
        sss_lists = scene.appleseed_sss_sets
        
        layout.prop_search(asr_obj, "object_sss_set", sss_lists, "sss_sets", text="SSS Set")
        layout.label(text="SSS sets are created in the world tab")
        layout.prop(asr_obj, "medium_priority", text="Nested Dielectric Medium Priority")
        layout.prop(asr_obj, "ray_bias_method")
        row = layout.row()
        row.enabled = asr_obj.ray_bias_method != 'none'
        row.prop(asr_obj, "ray_bias_distance", text="Ray Bias Distance")

        split = layout.split(percentage=0.90)
        col = split.column()
        col.prop(asr_obj, "object_alpha", text="Object Alpha")

        if asr_obj.object_alpha_use_texture:
            layout.prop(asr_obj, "object_alpha_texture", text="Alpha Texture")
            layout.prop(asr_obj, "object_alpha_texture_colorspace")
            layout.prop(asr_obj, "object_alpha_texture_wrap_mode")

        col = split.column()
        col.prop(asr_obj, "object_alpha_use_texture", text="", icon="TEXTURE_SHADED", toggle=True)


class AppleseedObjMBlurPanel(bpy.types.Panel):
    bl_label = "Appleseed Motion Blur"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE'}

    def draw_header(self, context):
        header = self.layout
        asr_obj = context.object.appleseed
        header.prop(asr_obj, "enable_motion_blur", text="")

    def draw(self, context):
        layout = self.layout
        asr_obj = context.object.appleseed
        layout.active = asr_obj.enable_motion_blur
        layout.prop(asr_obj, "motion_blur_type", text="Type")


def register():
    import bl_ui.properties_object as properties_object
    for member in dir(properties_object):
        subclass = getattr(properties_object, member)
        try:
            subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
        except:
            pass
    del properties_object


def unregister():
    import bl_ui.properties_object as properties_object
    for member in dir(properties_object):
        subclass = getattr(properties_object, member)
        try:
            subclass.COMPAT_ENGINES.remove('APPLESEED_RENDER')
        except:
            pass
    del properties_object
