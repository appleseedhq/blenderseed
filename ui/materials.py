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


class AppleseedMaterialPreview(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "material"
    bl_label = "Preview"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine in cls.COMPAT_ENGINES and context.object is not None and context.object.active_material is not None

    def draw(self, context):
        layout = self.layout
        obj = context.object
        material = obj.active_material
        asr_mat = material.appleseed

        layout.template_preview(context.material, show_buttons=False)
        layout.prop(asr_mat, "preview_quality", text="Preview Quality")


class AppleseedMaterialShading(bpy.types.Panel):
    bl_label = 'Shader Model'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        material = context.object.active_material is not None
        if material:
            renderer = context.scene.render.engine == 'APPLESEED_RENDER'
            obj = context.object is not None
            obj_type = context.object.type == 'MESH'
            return renderer and obj and obj_type
        return False

    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        asr_mat = material.appleseed

        if material.appleseed.osl_node_tree is None:
            layout.operator('appleseed.add_osl_nodetree', text="Add appleseed Material Node", icon='NODETREE')
        else:
            layout.operator('appleseed.view_nodetree', text="View Nodetree")

        layout.prop(asr_mat, "shader_lighting_samples", text="Lighting Samples")


class TextureConvertSlots(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        texture = item.name
        if 'DEFAULT' in self.layout_type:
            layout.label(text=texture, translate=False, icon_value=icon)


class AppleseedTextureConverterPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "material"
    bl_label = "Texture Converter"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        material = context.object.active_material is not None
        if material:
            renderer = context.scene.render.engine == 'APPLESEED_RENDER'
            obj = context.object is not None
            obj_type = context.object.type == 'MESH'
            is_nodemat = context.object.active_material.appleseed.osl_node_tree is not None
            return renderer and obj and obj_type and is_nodemat
        return False

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        textures = asr_scene_props.textures

        row = layout.row()
        row.template_list("TextureConvertSlots", "", asr_scene_props,
                          "textures", asr_scene_props, "textures_index", rows=1, maxrows=16, type="DEFAULT")

        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator("appleseed.add_texture", text="Add Texture", icon="ZOOMIN")
        row.operator("appleseed.remove_texture", text="Remove Texture", icon="ZOOMOUT")
        row = col.row(align=True)
        row.operator("appleseed.refresh_textures", text="Refresh", icon='FILE_REFRESH')
        row.operator("appleseed.convert_textures", text="Convert", icon='PLAY')

        layout.prop(asr_scene_props, "del_unused_tex", text="Delete Unused .tx Files", toggle=True)
        layout.prop(asr_scene_props, "sub_textures", text="Use Converted Textures", toggle=True)

        if textures:
            current_set = textures[asr_scene_props.textures_index]
            layout.prop(current_set, "name", text="Texture")
            layout.prop(current_set, "input_space", text="Color Space")
            layout.prop(current_set, "output_depth", text="Depth")
            layout.prop(current_set, "command_string", text="Command")


def register():
    bpy.types.MATERIAL_PT_context_material.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.MATERIAL_PT_custom_props.COMPAT_ENGINES.add('APPLESEED_RENDER')
    util.safe_register_class(AppleseedMaterialPreview)
    util.safe_register_class(AppleseedMaterialShading)
    util.safe_register_class(TextureConvertSlots)
    util.safe_register_class(AppleseedTextureConverterPanel)


def unregister():
    util.safe_unregister_class(AppleseedTextureConverterPanel)
    util.safe_unregister_class(TextureConvertSlots)
    util.safe_unregister_class(AppleseedMaterialShading)
    util.safe_unregister_class(AppleseedMaterialPreview)
    bpy.types.MATERIAL_PT_context_material.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.MATERIAL_PT_custom_props.COMPAT_ENGINES.remove('APPLESEED_RENDER')
