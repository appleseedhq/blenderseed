
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


class AppleseedRenderPanelBase(object):
    bl_context = "render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

class AppleseedAOVPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Render Passes"
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "render_layer"

    def draw_header(self, context):
        header = self.layout
        asr_scene_props = context.scene.appleseed
        header.prop(asr_scene_props, "enable_aovs", text="")

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed

        layout.active = asr_scene_props.enable_aovs

        row = layout.row()
        row.prop(asr_scene_props, "diffuse_aov", text="Diffuse")
        row.prop(asr_scene_props, "glossy_aov", text="Glossy")

        row = layout.row()
        row.prop(asr_scene_props, "direct_diffuse_aov", text="Direct Diffuse")
        row.prop(asr_scene_props, "direct_glossy_aov", text="Direct Glossy")

        row = layout.row()
        row.prop(asr_scene_props, "indirect_diffuse_aov", text="Indirect Diffuse")
        row.prop(asr_scene_props, "indirect_glossy_aov", text="Indirect Glossy")

        row = layout.row()
        row.prop(asr_scene_props, "normal_aov", text="Normals")
        row.prop(asr_scene_props, "uv_aov", text="UV Coordinates")

        row = layout.row()
        row.prop(asr_scene_props, "depth_aov", text="Depth")


def register():
    bpy.types.SCENE_PT_scene.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_color_management.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_audio.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_unit.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_keying_sets.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_keying_set_paths.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_physics.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_rigid_body_world.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_rigid_body_cache.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_rigid_body_field_weights.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.SCENE_PT_custom_props.COMPAT_ENGINES.add('APPLESEED_RENDER')
    util.safe_register_class(AppleseedAOVPanel)


def unregister():
    util.safe_unregister_class(AppleseedAOVPanel)
    bpy.types.SCENE_PT_custom_props.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_rigid_body_field_weights.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_rigid_body_cache.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_rigid_body_world.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_physics.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_keying_set_paths.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_keying_sets.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_unit.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_audio.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_color_management.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.SCENE_PT_scene.COMPAT_ENGINES.remove('APPLESEED_RENDER')
