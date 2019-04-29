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

import os
import subprocess

import bpy

from ..utils import util, path_util


# Material operators


class AppleseedNewMat(bpy.types.Operator):
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
            dupli_node_tree.name = context.object.active_material.name + "_tree"
            context.object.active_material.appleseed.osl_node_tree = dupli_node_tree
        else:
            bpy.ops.appleseed.add_osl_nodetree()

        return {'FINISHED'}


class AppleseedNewOSLNodeTree(bpy.types.Operator):
    """
    appleseed material node tree generator.
    """

    bl_idname = "appleseed.add_osl_nodetree"
    bl_label = "Add appleseed OSL Material Node Tree"
    bl_description = "Create an appleseed OSL material node tree and link it to the current material"

    def execute(self, context):
        material = context.object.active_material
        nodetree = bpy.data.node_groups.new('%s_tree' % material.name, 'AppleseedOSLNodeTree')
        surface = nodetree.nodes.new('AppleseedasClosure2SurfaceNode')
        surface.location = (0, 0)
        disney_node = nodetree.nodes.new('AppleseedasDisneyMaterialNode')
        disney_node.location = (-300, 0)
        nodetree.links.new(disney_node.outputs[0], surface.inputs[0])
        material.appleseed.osl_node_tree = nodetree
        return {'FINISHED'}


class AppleseedViewNodeTree(bpy.types.Operator):
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
                            space.tree_type = node_tree.bl_idname
                            space.node_tree = node_tree
                            return {"FINISHED"}

        return {"CANCELLED"}


class AppleseedNewLampOSLNodeTree(bpy.types.Operator):
    """
    appleseed lamp node tree generator.
    """

    bl_idname = "appleseed.add_lap_osl_nodetree"
    bl_label = "Add appleseed OSL Material Node Tree"
    bl_description = "Create an appleseed OSL material node tree and link it to the current lamp"

    def execute(self, context):
        lamp = context.object.data
        nodetree = bpy.data.node_groups.new('%s_tree' % lamp.name, 'AppleseedOSLNodeTree')
        nodetree.use_fake_user = True
        surface = nodetree.nodes.new('AppleseedasClosure2SurfaceNode')
        surface.location = (0, 0)
        area_lamp_node = nodetree.nodes.new('AppleseedasAreaLightNode')
        area_lamp_node.location = (-300, 0)
        nodetree.links.new(area_lamp_node.outputs[0], surface.inputs[0])
        lamp.appleseed.osl_node_tree = nodetree
        return {'FINISHED'}


# Texture operators


class AppleseedConvertTextures(bpy.types.Operator):
    """
    Converts base textures into mipmapped .tx textures for rendering
    """
    bl_label = "Convert Textures"
    bl_description = "Convert textures"
    bl_idname = "appleseed.convert_textures"

    def execute(self, context):
        scene = context.scene
        textures = scene.appleseed

        for tex in textures.textures:
            filename = bpy.path.abspath(tex.name.filepath)
            if textures.tex_output_use_cust_dir:
                tex_name = os.path.basename(filename).split('.')[0]
                out_path = os.path.join(textures.tex_output_dir, '{0}.tx'.format(tex_name))
            else:
                out_path = filename.split('.')[0] + ".tx"

            import appleseed as asr

            asr.oiio_make_texture(filename, out_path, tex.input_space, tex.output_depth)

            subbed_filename = "{0}.tx".format(os.path.splitext(filename)[0])
            bpy.ops.image.open(filepath=subbed_filename)

        return {'FINISHED'}


class AppleseedRefreshTexture(bpy.types.Operator):
    """
    Operator for refreshing texture list to convert.
    """

    bl_label = "Refresh Texture"
    bl_description = "Refresh textures for conversion"
    bl_idname = "appleseed.refresh_textures"

    def invoke(self, context, event):
        scene = context.scene
        collection = scene.appleseed.textures

        existing_textures = [x.name for x in collection]

        scene_textures = []

        for tree in bpy.data.node_groups:
            for node in tree.nodes:
                for param in node.filepaths:
                    texture_block = getattr(node, param)
                    if texture_block not in scene_textures:
                        scene_textures.append(texture_block)
                        if texture_block not in existing_textures:
                            collection.add()
                            num = len(collection)
                            collection[num - 1].name = texture_block

        texture_index = len(collection) - 1
        while texture_index > -1:
            texture = collection[texture_index]
            if texture.name not in scene_textures:
                collection.remove(texture_index)
            texture_index -= 1

        return {'FINISHED'}


class AppleseedAddTexture(bpy.types.Operator):
    """
    Operator for adding a texture to convert.
    """

    bl_label = "Add Texture"
    bl_description = "Add new texture"
    bl_idname = "appleseed.add_texture"

    def invoke(self, context, event):
        scene = context.scene
        collection = scene.appleseed.textures

        collection.add()

        return {'FINISHED'}


class AppleseedRemoveTexture(bpy.types.Operator):
    """
    Operator for removing a texture to convert.
    """

    bl_label = "Remove Texture"
    bl_description = "Remove texture"
    bl_idname = "appleseed.remove_texture"

    def invoke(self, context, event):
        scene = context.scene
        collection = scene.appleseed.textures
        index = scene.appleseed.textures_index

        collection.remove(index)
        num = len(collection)
        if index >= num:
            index = num - 1
        if index < 0:
            index = 0
        scene.appleseed.textures_index = index

        return {'FINISHED'}


# Post processing operators


class AppleseedAddPostProcess(bpy.types.Operator):
    bl_label = "Add Stage"
    bl_description = "Add new Post Processing stage"
    bl_idname = "appleseed.add_pp_stage"

    def invoke(self, context, event):
        collection = context.scene.appleseed.post_processing_stages
        collection.add()
        num = len(collection)
        collection[num - 1].name = "Render Stamp"

        return {'FINISHED'}


class AppleseedRemovePostProcess(bpy.types.Operator):
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


class AppleseedAddSssSet(bpy.types.Operator):
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


class AppleseedRemoveSssSet(bpy.types.Operator):
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


def register():
    util.safe_register_class(AppleseedNewMat)
    util.safe_register_class(AppleseedViewNodeTree)
    util.safe_register_class(AppleseedConvertTextures)
    util.safe_register_class(AppleseedRefreshTexture)
    util.safe_register_class(AppleseedAddTexture)
    util.safe_register_class(AppleseedRemoveTexture)
    util.safe_register_class(AppleseedNewOSLNodeTree)
    util.safe_register_class(AppleseedNewLampOSLNodeTree)
    util.safe_register_class(AppleseedAddPostProcess)
    util.safe_register_class(AppleseedRemovePostProcess)
    util.safe_register_class(AppleseedAddSssSet)
    util.safe_register_class(AppleseedRemoveSssSet)


def unregister():
    util.safe_unregister_class(AppleseedRemoveSssSet)
    util.safe_unregister_class(AppleseedAddSssSet)
    util.safe_unregister_class(AppleseedRemovePostProcess)
    util.safe_unregister_class(AppleseedAddPostProcess)
    util.safe_unregister_class(AppleseedNewLampOSLNodeTree)
    util.safe_unregister_class(AppleseedNewOSLNodeTree)
    util.safe_unregister_class(AppleseedRemoveTexture)
    util.safe_unregister_class(AppleseedAddTexture)
    util.safe_unregister_class(AppleseedRefreshTexture)
    util.safe_unregister_class(AppleseedConvertTextures)
    util.safe_unregister_class(AppleseedViewNodeTree)
    util.safe_unregister_class(AppleseedNewMat)
