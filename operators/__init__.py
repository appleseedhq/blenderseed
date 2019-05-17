#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2014-2019 The appleseedhq Organization
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


# Post processing operators


class ASPP_OT_add_pp(bpy.types.Operator):
    bl_label = "Add Stage"
    bl_description = "Add new Post Processing stage"
    bl_idname = "appleseed.add_pp_stage"

    def execute(self, context):
        collection = context.scene.appleseed.post_processing_stages
        collection.add()
        num = len(collection)
        collection[num - 1].name = "Render Stamp"

        return {'FINISHED'}


class ASPP_OT_remove_PP(bpy.types.Operator):
    bl_label = "Remove Stage"
    bl_description = "Remove Post Processing stage"
    bl_idname = "appleseed.remove_pp_stage"

    def execute(self, context):
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

    def execute(self, context):
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

    def execute(self, context):
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
