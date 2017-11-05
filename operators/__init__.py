
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
import os
import subprocess
from .. import project_file_writer
from .. import util


class AppleseedAddMatLayer(bpy.types.Operator):
    """
    Operator for adding material layers.
    """

    bl_label = "Add Layer"
    bl_description = "Add new BSDF layer"
    bl_idname = "appleseed.add_matlayer"

    def invoke(self, context, event):
        scene = context.scene
        material = context.object.active_material
        collection = material.appleseed.layers
        index = material.appleseed.layer_index

        collection.add()
        num = collection.__len__()
        collection[num - 1].name = "BSDF Layer " + str(num)

        return {'FINISHED'}


class AppleseedRemoveMatLayer(bpy.types.Operator):
    """
    Operator for removing material layers.
    """

    bl_label = "Remove Layer"
    bl_description = "Remove BSDF layer"
    bl_idname = "appleseed.remove_matlayer"

    def invoke(self, context, event):
        scene = context.scene
        material = context.object.active_material
        collection = material.appleseed.layers
        index = material.appleseed.layer_index

        collection.remove(index)
        num = collection.__len__()
        if index >= num:
            index = num - 1
        if index < 0:
            index = 0
        material.appleseed.layer_index = index

        return {'FINISHED'}


class AppleseedNewNodeTree(bpy.types.Operator):
    """
    appleseed material node tree generator.
    """

    bl_idname = "appleseed.add_material_nodetree"
    bl_label = "Add appleseed Material Node Tree"
    bl_description = "Create an appleseed material node tree and link it to the current material"

    def execute(self, context):
        material = context.object.active_material
        nodetree = bpy.data.node_groups.new('%s appleseed Nodetree' % material.name, 'AppleseedNodeTree')
        nodetree.use_fake_user = True
        node = nodetree.nodes.new('AppleseedMaterialNode')
        material.appleseed.node_tree = nodetree.name
        material.appleseed.node_output = node.name

        return {'FINISHED'}


class AppleseedExportOperator(bpy.types.Operator):
    """
    appleseed export operator.
    """

    bl_idname = "appleseed.export"
    bl_label = "Export"

    inst_set = set()
    psysob_set = set()
    exported_obs = set()

    def execute(self, context):
        scene = context.scene
        if scene.appleseed.project_path == '':
            return {'CANCELLED'}

        file_path = os.path.join(util.realpath(scene.appleseed.project_path), scene.name + ".appleseed")

        exporter = project_file_writer.Exporter()
        exporter.export(scene, file_path)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(AppleseedAddMatLayer)
    bpy.utils.register_class(AppleseedRemoveMatLayer)
    bpy.utils.register_class(AppleseedExportOperator)


def unregister():
    bpy.utils.unregister_class(AppleseedAddMatLayer)
    bpy.utils.unregister_class(AppleseedRemoveMatLayer)
    bpy.utils.unregister_class(AppleseedExportOperator)
