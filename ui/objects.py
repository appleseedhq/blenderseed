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

from .. import util


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
        col = layout.column()
        col.prop(asr_obj, "camera_visible", text="Camera")
        col.prop(asr_obj, "light_visible", text="Light")
        col.prop(asr_obj, "shadow_visible", text="Shadow")
        col.prop(asr_obj, "diffuse_visible", text="Diffuse")
        col.prop(asr_obj, "glossy_visible", text="Glossy")
        col.prop(asr_obj, "specular_visible", text="Specular")
        col.prop(asr_obj, "transparency_visible", text="Transparency")

        layout.separator()
        row = layout.row()
        row.active = asr_obj.object_alpha_texture == ""
        row.prop(asr_obj, "object_alpha", text="Object Alpha")

        col = layout.column()
        col.prop(asr_obj, "object_alpha_texture", text="")
        col.prop(asr_obj, "object_alpha_texture_colorspace", text="Color Space")
        col.prop(asr_obj, "object_alpha_texture_wrap_mode", text="Wrap Mode")

        layout.separator()

        layout.prop(asr_obj, "double_sided", text="Double Sided Shading")
        layout.prop(asr_obj, "medium_priority", text="Nested Glass Priority")
        layout.prop_search(asr_obj, "object_sss_set", sss_lists, "sss_sets", text="SSS Set")


class AppleseedObjMBlurPanel(bpy.types.Panel):
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

        col = layout.column()
        col.prop(asr_obj, "enable_motion_blur", text="Enable Motion Blur")
        row = col.row()
        row.active = asr_obj.enable_motion_blur
        row.prop(asr_obj, "motion_blur_type", text="Type")


def register():
    import bl_ui.properties_object as properties_object
    for member in dir(properties_object):
        subclass = getattr(properties_object, member)
        try:
            subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
        except:
            pass
    del properties_object
    util.safe_register_class(AppleseedObjFlagsPanel)
    util.safe_register_class(AppleseedObjMBlurPanel)


def unregister():
    util.safe_unregister_class(AppleseedObjMBlurPanel)
    util.safe_unregister_class(AppleseedObjFlagsPanel)
    import bl_ui.properties_object as properties_object
    for member in dir(properties_object):
        subclass = getattr(properties_object, member)
        try:
            subclass.COMPAT_ENGINES.remove('APPLESEED_RENDER')
        except:
            pass
    del properties_object
