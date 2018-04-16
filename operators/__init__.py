
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
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
import os
import imghdr
from ..util import get_osl_search_paths


class AppleseedConvertTextures(bpy.types.Operator):
    bl_label = "Convert Textures"
    bl_description = "Convert textures"
    bl_idname = "appleseed.convert_textures"

    def execute(self, context):
        scene = context.scene
        textures = scene.appleseed

        tool_dir, shader_dir = get_osl_search_paths()

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

        for tree in bpy.data.node_groups:
            for node in tree.nodes:
                for param in node.parameter_types:
                    if node.parameter_types[param] == 'string':
                        string = getattr(node, param)
                        if imghdr.what(string):
                            if string not in existing_textures:
                                collection.add()
                                num = collection.__len__()
                                collection[num - 1].name = string

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
        num = collection.__len__()
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
        num = collection.__len__()
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
        num = collection.__len__()
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
        num = collection.__len__()
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
        nodetree = bpy.data.node_groups.new('%s appleseed OSL Nodetree' % material.name, 'AppleseedOSLNodeTree')
        nodetree.use_fake_user = True
        material.appleseed.osl_node_tree = nodetree
        return {'FINISHED'}


def register():
    bpy.utils.register_class(AppleseedConvertTextures)
    bpy.utils.register_class(AppleseedRefreshTexture)
    bpy.utils.register_class(AppleseedAddTexture)
    bpy.utils.register_class(AppleseedRemoveTexture)
    bpy.utils.register_class(AppleseedNewOSLNodeTree)
    bpy.utils.register_class(AppleseedAddSssSet)
    bpy.utils.register_class(AppleseedRemoveSssSet)


def unregister():
    bpy.utils.unregister_class(AppleseedRemoveSssSet)
    bpy.utils.unregister_class(AppleseedAddSssSet)
    bpy.utils.unregister_class(AppleseedNewOSLNodeTree)
    bpy.utils.unregister_class(AppleseedRemoveTexture)
    bpy.utils.unregister_class(AppleseedAddTexture)
    bpy.utils.unregister_class(AppleseedRefreshTexture)
    bpy.utils.unregister_class(AppleseedConvertTextures)
