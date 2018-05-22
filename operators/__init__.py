
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
import subprocess
from ..util import image_extensions
from .. import util
import os


class AppleseedViewNode(bpy.types.Operator):
    bl_label = "View OSL Nodetree"
    bl_description = ""
    bl_idname = "appleseed.view_nodetree"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.active_material and obj.active_material.appleseed.osl_node_tree

    def execute(self, context):
        mat = context.active_object.active_material
        node_tree = mat.appleseed.osl_node_tree

        for area in context.screen.areas:
            if area.type == "NODE_EDITOR":
                for space in area.spaces:
                    if space.type == "NODE_EDITOR":
                        space.tree_type = node_tree.bl_idname
                        space.node_tree = node_tree
                        return {"FINISHED"}

        self.report({"ERROR"}, "Open a node editor first")
        return {"CANCELLED"}


class AppleseedConvertTextures(bpy.types.Operator):
    bl_label = "Convert Textures"
    bl_description = "Convert textures"
    bl_idname = "appleseed.convert_textures"

    def execute(self, context):
        scene = context.scene
        textures = scene.appleseed

        tool_dir, shader_dir = util.get_osl_search_paths()

        for tex in textures.textures:
            filename = bpy.path.abspath(tex.name)
            cmd = ['maketx', '--oiio --monochrome-detect -u --constant-color-detect --opaque-detect', '"{0}"'.format(filename)]
            if tex.input_space != 'linear':
                cmd.insert(-1, '--colorconvert {0} linear --unpremult'.format(tex.input_space))
            if tex.output_depth != 'default':
                cmd.insert(-1, '-d {0}'.format(tex.output_depth))
            if tex.command_string:
                cmd.insert(-1, '{0}'.format(tex.command_string))
            process = subprocess.Popen(" ".join(cmd), cwd=tool_dir, shell=True, bufsize=1)
            process.wait()

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
                for param in node.parameter_types:
                    if node.parameter_types[param] == 'string':
                        string = getattr(node, param)
                        if string.endswith(image_extensions):
                            scene_textures.append(string)
                            if string not in existing_textures:
                                collection.add()
                                num = len(collection)
                                collection[num - 1].name = string

        texture_index = len(collection) - 1
        while texture_index > -1:
            texture = collection[texture_index]
            if texture.name not in scene_textures:
                collection.remove(texture_index)
                if scene.appleseed.del_unused_tex:
                    converted_texture = os.path.realpath(texture.name.split(".")[0] + '.tx')
                    try:
                        os.remove(converted_texture)
                    except:
                        self.report[{'ERROR'}, "[appleseed] {0} does not exist".format(converted_texture)]
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
        num = len(collection)
        collection[num - 1].name = ""

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


class AppleseedNewOSLNodeTree(bpy.types.Operator):
    """
    appleseed material node tree generator.
    """

    bl_idname = "appleseed.add_osl_nodetree"
    bl_label = "Add appleseed OSL Material Node Tree"
    bl_description = "Create an appleseed OSL material node tree and link it to the current material"

    def execute(self, context):
        material = context.object.active_material
        nodetree = bpy.data.node_groups.new('%s_appleseed_osl_nodetree' % material.name, 'AppleseedOSLNodeTree')
        nodetree.use_fake_user = True
        surface = nodetree.nodes.new('AppleseedasClosure2SurfaceNode')
        surface.location = (0, 0)
        disney_node = nodetree.nodes.new('AppleseedasDisneyMaterialNode')
        disney_node.location = (-300, 0)
        nodetree.links.new(disney_node.outputs[0], surface.inputs[0])
        material.appleseed.osl_node_tree = nodetree
        return {'FINISHED'}


def register():
    util.safe_register_class(AppleseedViewNode)
    util.safe_register_class(AppleseedConvertTextures)
    util.safe_register_class(AppleseedRefreshTexture)
    util.safe_register_class(AppleseedAddTexture)
    util.safe_register_class(AppleseedRemoveTexture)
    util.safe_register_class(AppleseedNewOSLNodeTree)
    util.safe_register_class(AppleseedAddSssSet)
    util.safe_register_class(AppleseedRemoveSssSet)


def unregister():
    util.safe_unregister_class(AppleseedRemoveSssSet)
    util.safe_unregister_class(AppleseedAddSssSet)
    util.safe_unregister_class(AppleseedNewOSLNodeTree)
    util.safe_unregister_class(AppleseedRemoveTexture)
    util.safe_unregister_class(AppleseedAddTexture)
    util.safe_unregister_class(AppleseedRefreshTexture)
    util.safe_unregister_class(AppleseedConvertTextures)
    util.safe_unregister_class(AppleseedViewNode)
