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

from . import osl_ops, texture_ops
from ..utils import util


# Material operators


class ASMAT_OT_new_mat(bpy.types.Operator):
    bl_label = "New Material"
    bl_description = "Add a new appleseed material"
    bl_idname = "appleseed.new_mat"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj

    def execute(self, context):
        mat_name = "Material"
        obj = context.object
        dupli_node_tree = None
        if context.object.active_material is not None and context.object.active_material.appleseed.osl_node_tree is not None:
            mat_name = context.object.active_material.name
            dupli_node_tree = context.object.active_material.appleseed.osl_node_tree.copy()

        mat = bpy.data.materials.new(name=mat_name)

        if obj.material_slots:
            obj.material_slots[obj.active_material_index].material = mat
        else:
            obj.data.materials.append(mat)

        if dupli_node_tree is not None:
            dupli_node_tree.name = context.object.active_material.name
            context.object.active_material.appleseed.osl_node_tree = dupli_node_tree
        else:
            bpy.ops.appleseed.add_osl_nodetree()

        return {'FINISHED'}


class ASMAT_OT_new_node_tree(bpy.types.Operator):
    """
    appleseed material node tree generator.
    """

    bl_idname = "appleseed.add_osl_nodetree"
    bl_label = "Add appleseed OSL Material Node Tree"
    bl_description = "Create an appleseed OSL material node tree and link it to the current material"

    def execute(self, context):
        material = context.object.active_material
        nodetree = bpy.data.node_groups.new(material.name, 'AppleseedOSLNodeTree')
        nodetree.use_fake_user = True
        surface = nodetree.nodes.new('AppleseedasClosure2SurfaceNode')
        surface.location = (0, 0)
        disney_node = nodetree.nodes.new('AppleseedasDisneyMaterialNode')
        disney_node.location = (-300, 0)
        nodetree.links.new(disney_node.outputs[0], surface.inputs[0])
        material.appleseed.osl_node_tree = nodetree
        return {'FINISHED'}


class ASMAT_OT_view_nodetree(bpy.types.Operator):
    bl_label = "View OSL Nodetree"
    bl_description = "View the node tree attached to this material"
    bl_idname = "appleseed.view_nodetree"

    def execute(self, context):
        node_tree = None
        ob = context.active_object if hasattr(context, "active_object") else None
        if ob:
            if ob.type == 'LAMP':
                if ob.data.type == 'AREA':
                    lamp = ob.data.appleseed
                    node_tree = lamp.osl_node_tree
                else:
                    return {"CANCELLED"}
            elif ob.type == 'MESH':
                mat = ob.active_material

                if mat:
                    node_tree = mat.appleseed.osl_node_tree
            else:
                return {"CANCELLED"}

        if node_tree is not None:
            for area in context.screen.areas:
                if area.type == "NODE_EDITOR":
                    for space in area.spaces:
                        if space.type == "NODE_EDITOR":
                            space.tree_type = "AppleseedOSLNodeTree"
                            space.node_tree = node_tree
                            return {"FINISHED"}

        return {"CANCELLED"}


class ASLAMP_OT_new_node_tree(bpy.types.Operator):
    """
    appleseed lamp node tree generator.
    """

    bl_idname = "appleseed.add_lap_osl_nodetree"
    bl_label = "Add appleseed OSL Material Node Tree"
    bl_description = "Create an appleseed OSL material node tree and link it to the current lamp"

    def execute(self, context):
        lamp = context.object.data
        nodetree = bpy.data.node_groups.new('%s' % lamp.name, 'AppleseedOSLNodeTree')
        nodetree.use_fake_user = True
        surface = nodetree.nodes.new('AppleseedasClosure2SurfaceNode')
        surface.location = (0, 0)
        area_lamp_node = nodetree.nodes.new('AppleseedasAreaLightNode')
        area_lamp_node.location = (-300, 0)
        nodetree.links.new(area_lamp_node.outputs[0], surface.inputs[0])
        lamp.appleseed.osl_node_tree = nodetree
        return {'FINISHED'}


# Texture operators


# Post processing operators


class ASPP_OT_add_pp(bpy.types.Operator):
    bl_label = "Add Stage"
    bl_description = "Add new Post Processing stage"
    bl_idname = "appleseed.add_pp_stage"

    def invoke(self, context, event):
        collection = context.scene.appleseed.post_processing_stages
        collection.add()
        num = len(collection)
        collection[num - 1].name = "Render Stamp"

        return {'FINISHED'}


class ASPP_OT_remove_PP(bpy.types.Operator):
    bl_label = "Remove Stage"
    bl_description = "Remove Post Processing stage"
    bl_idname = "appleseed.remove_pp_stage"

    def invoke(self, context, event):
        scene = context.scene.appleseed
        collection = scene.post_processing_stages
        index = scene.post_processing_stages_index

        collection.remove(index)
        num = len(collection)
        if index >= num:
            index = num - 1
        if index < 0:
            index = 0
            scene.post_processing_stages_index = index

        return {'FINISHED'}


# SSS set operators


class ASSSS_OT_add_sss_set(bpy.types.Operator):
    """Operator for adding SSS sets"""

    bl_label = "Add Set"
    bl_description = "Add new SSS Set"
    bl_idname = "appleseed.add_sss_set"

    def invoke(self, context, event):
        world = context.scene.appleseed_sss_sets
        collection = world.sss_sets

        collection.add()
        num = len(collection)
        collection[num - 1].name = "SSS Set " + str(num)

        return {'FINISHED'}


class ASSSS_OT_remove_sss_set(bpy.types.Operator):
    """Operator for removing SSS sets"""

    bl_label = "Remove Set"
    bl_description = "Remove SSS Set"
    bl_idname = "appleseed.remove_sss_set"

    def invoke(self, context, event):
        world = context.scene.appleseed_sss_sets
        collection = world.sss_sets
        index = world.sss_sets_index

        collection.remove(index)
        num = len(collection)
        if index >= num:
            index = num - 1
        if index < 0:
            index = 0
        world.sss_sets_layer_index = index

        return {'FINISHED'}


classes = (
    ASMAT_OT_new_mat,
    ASMAT_OT_view_nodetree,
    ASMAT_OT_new_node_tree,
    ASLAMP_OT_new_node_tree,
    ASPP_OT_add_pp,
    ASPP_OT_remove_PP,
    ASSSS_OT_add_sss_set,
    ASSSS_OT_remove_sss_set
)


def register():
    osl_ops.register()
    texture_ops.register()
    for cls in classes:
        util.safe_register_class(cls)


def unregister():
    for cls in reversed(classes):
        util.safe_unregister_class(cls)
    texture_ops.unregister()
    osl_ops.unregister()
