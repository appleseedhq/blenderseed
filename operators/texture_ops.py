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

import os
import subprocess

from ..utils import path_util, util


class ASTEX_OT_convert_textures(bpy.types.Operator):
    """
    Converts base textures into mipmapped .tx textures for rendering
    """
    bl_label = "Convert Textures"
    bl_description = "Convert textures"
    bl_idname = "appleseed.convert_textures"

    def execute(self, context):
        scene = context.scene
        textures = scene.appleseed

        tool_dir = path_util.get_appleseed_tool_dir()

        for tex in textures.textures:
            filename = bpy.path.abspath(tex.name.filepath)
            cmd = ['maketx', '--oiio --monochrome-detect -u --constant-color-detect --opaque-detect', '"{0}"'.format(filename)]
            if tex.input_space != 'linear':
                cmd.insert(-1, '--colorconvert {0} linear --unpremult'.format(tex.input_space))
            if tex.output_depth != 'default':
                cmd.insert(-1, '-d {0}'.format(tex.output_depth))
            if tex.command_string:
                cmd.insert(-1, '{0}'.format(tex.command_string))
            if textures.tex_output_use_cust_dir:
                tex_name = os.path.basename(filename).split('.')[0]
                out_path = os.path.join(textures.tex_output_dir, '{0}.tx'.format(tex_name))
                cmd.insert(-1, '-o "{0}"'.format(out_path))
            process = subprocess.Popen(" ".join(cmd), cwd=tool_dir, shell=True, bufsize=1)
            process.wait()

            subbed_filename = "{0}.tx".format(os.path.splitext(filename)[0])
            bpy.ops.image.open(filepath=subbed_filename)

        return {'FINISHED'}


class ASTEX_OT_refresh_texture(bpy.types.Operator):
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


class ASTES_OT_add_texture(bpy.types.Operator):
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


class ASTEX_OT_remove_texture(bpy.types.Operator):
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


classes = (
    ASTEX_OT_convert_textures,
    ASTEX_OT_refresh_texture,
    ASTES_OT_add_texture,
    ASTEX_OT_remove_texture
)


def register():
    for cls in classes:
        util.safe_register_class(cls)


def unregister():
    for cls in reversed(classes):
        util.safe_unregister_class(cls)
