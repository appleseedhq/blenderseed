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


class AppleseedMaterialSlots(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_label = "Material"
    bl_region_type = 'WINDOW'
    bl_context = "material"

    # COMPAT_ENGINES must be defined in each subclass, external engines can add themselves here

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material or context.object) and engine == 'APPLESEED_RENDER'

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data

        if ob:
            is_sortable = (len(ob.material_slots) > 1)

            rows = 1
            if is_sortable:
                rows = 4

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.65)

        if ob:
            row = split.row(align=True)
            sub = row.split(align=True, percentage=1 / (context.region.width * 0.015))
            sub.prop_search(ob, "active_material", bpy.data, "materials", icon='MATERIAL', text="")
            row = sub.row(align=True)
            if ob.active_material:
                row.prop(ob.active_material, "name", text="")
                row.prop(ob.active_material, "use_fake_user", text="", toggle=True, icon="FONT_DATA")  # :^)
                text_new = ""
            else:
                text_new = "New"

            row.operator("appleseed.new_mat", text=text_new, icon='ZOOMIN')

            # split.template_ID(ob, "active_material", new="appleseed.new_mat")
            
            row = split.row()
            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()


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
        obj = context.object
        material = obj.active_material
        asr_mat = material.appleseed

        if material.appleseed.osl_node_tree is None:
            layout.operator('appleseed.add_osl_nodetree', text="Add appleseed Material Node", icon='NODETREE')
        else:
            layout.operator('appleseed.view_nodetree', text="View Nodetree", icon='NODETREE')

        layout.prop(asr_mat, "shader_lighting_samples", text="Lighting Samples")

        layout.prop(asr_mat, "mode", text="Shading Mode")

        if asr_mat.mode == 'volume':
            layout.prop(asr_mat, "volume_phase_function_model", text="Volume")
            if asr_mat.volume_phase_function_model != 'none':
                # Absorption
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Absorption:")
                col = split.column()
                col.prop(asr_mat, "volume_absorption", text="")

                # Absorption Multiplier
                col = layout.column()
                col.prop(asr_mat, "volume_absorption_multiplier", text="Absorption Multiplier")

                # Volume Scattering
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Scattering:")
                col = split.column()
                col.prop(asr_mat, "volume_scattering", text="")

                # Scattering Multiplier
                col = layout.column()
                col.prop(asr_mat, "volume_scattering_multiplier", text="Scattering Multiplier")

                if asr_mat.volume_phase_function_model == 'henyey':
                    col.prop(asr_mat, "volume_average_cosine", text="Average Cosine")


def register():
    util.safe_register_class(AppleseedMaterialSlots)
    util.safe_register_class(AppleseedMaterialPreview)
    util.safe_register_class(AppleseedMaterialShading)


def unregister():
    util.safe_unregister_class(AppleseedMaterialShading)
    util.safe_unregister_class(AppleseedMaterialPreview)
    util.safe_unregister_class(AppleseedMaterialSlots)
