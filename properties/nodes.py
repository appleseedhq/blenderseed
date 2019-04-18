#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2018 The appleseedhq Organization
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
import nodeitems_utils

from ..utils import util, osl_utils


class AppleseedOSLScriptBaseNode(osl_utils.AppleseedOSLScriptNode):
    bl_idname = "AppleseedOSLScriptBaseNode"
    bl_label = "OSL Script Base"
    bl_icon = "NODE"
    bl_width_default = 240.0

    node_type = "osl_script"

    script: bpy.props.PointerProperty(name="script",
                                      type=bpy.types.Text)

    def draw_buttons(self, context, layout):
        layout.prop(self, "script", text="")
        layout.operator('appleseed.compile_osl_script', text="Create Parameters")


class AppleseedOSLNodeTree(bpy.types.NodeTree):
    """Class for appleseed node tree."""

    bl_idname = 'AppleseedOSLNodeTree'
    bl_label = 'appleseed OSL Node Tree'
    bl_icon = 'MATERIAL'

    @classmethod
    def get_from_context(cls, context):
        """
        Switches the displayed node tree when user selects object/material
        """
        obj = context.active_object

        if obj and obj.type not in {"LIGHT", "CAMERA"}:
            mat = obj.active_material

            if mat:
                # ID pointer
                node_tree = mat.appleseed.osl_node_tree

                if node_tree:
                    return node_tree, mat, mat

        elif obj and obj.type == "LIGHT":
            node_tree = obj.data.appleseed.osl_node_tree

            if node_tree:
                return node_tree, None, None

        return None, None, None

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return renderer == 'APPLESEED_RENDER'

    def update(self):
        if hasattr(bpy.context, "material"):
            bpy.context.material.preview_render_type = bpy.context.material.preview_render_type


class AppleseedOSLNodeCategory(nodeitems_utils.NodeCategory):
    """Node category for extending the Add menu, toolbar panels and search operator.

    Base class for node categories.
    """

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return context.space_data.tree_type == 'AppleseedOSLNodeTree' and renderer == 'APPLESEED_RENDER'


def node_categories(osl_nodes):
    osl_surface = []
    osl_shaders = []
    osl_2d_textures = []
    osl_3d_textures = []
    osl_color = []
    osl_utilities = []
    osl_other = []

    for node in osl_nodes:
        node_item = nodeitems_utils.NodeItem(node[0])
        node_category = node[1]
        if node_category == 'shader':
            osl_shaders.append(node_item)
        elif node_category == 'texture2d':
            osl_2d_textures.append(node_item)
        elif node_category == 'utility':
            osl_utilities.append(node_item)
        elif node_category == 'texture3d':
            osl_3d_textures.append(node_item)
        elif node_category == 'surface':
            osl_surface.append(node_item)
        elif node_category == 'color':
            osl_color.append(node_item)
        else:
            osl_other.append(node_item)

    appleseed_node_categories = [
        AppleseedOSLNodeCategory("OSL_Surfaces", "Surface", items=osl_surface),
        AppleseedOSLNodeCategory("OSL_Shaders", "Shader", items=osl_shaders),
        AppleseedOSLNodeCategory("OSL_3D_Textures", "Texture3D", items=osl_3d_textures),
        AppleseedOSLNodeCategory("OSL_2D_Textures", "Texture2D", items=osl_2d_textures),
        AppleseedOSLNodeCategory("OSL_Color", "Color", items=osl_color),
        AppleseedOSLNodeCategory("OSL_Utilities", "Utility", items=osl_utilities),
        AppleseedOSLNodeCategory("OSL_Script", "Script", items=[nodeitems_utils.NodeItem("AppleseedOSLScriptBaseNode")]),
        AppleseedOSLNodeCategory("OSL_Other", "No Category", items=osl_other)]

    return appleseed_node_categories


osl_node_names = []

classes = []


def register():
    util.safe_register_class(AppleseedOSLNodeTree)
    util.safe_register_class(AppleseedOSLScriptBaseNode)
    node_list = osl_utils.read_osl_shaders()
    for node in node_list:
        node_name, node_category, node_classes = osl_utils.generate_node(node, osl_utils.AppleseedOSLNode)
        classes.extend(node_classes)
        osl_node_names.append([node_name, node_category])

    for cls in classes:
        util.safe_register_class(cls)

    nodeitems_utils.register_node_categories("APPLESEED", node_categories(osl_node_names))


def unregister():
    nodeitems_utils.unregister_node_categories("APPLESEED")

    for cls in reversed(classes):
        util.safe_unregister_class(cls)

    util.safe_unregister_class(AppleseedOSLScriptBaseNode)
    util.safe_unregister_class(AppleseedOSLNodeTree)
