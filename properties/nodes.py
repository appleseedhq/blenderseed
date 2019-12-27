#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2018-2019 The appleseedhq Organization
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

from ..logger import get_logger
from ..utils import osl_utils, util

logger = get_logger()


class AppleseedOSLSocket(bpy.types.NodeSocket):
    """appleseed OSL base socket"""

    bl_idname = "AppleseedOSLSocket"
    bl_label = "OSL Socket"

    socket_osl_id = ''

    def draw(self, context, layout, node, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        pass


class AppleseedOSLNode(bpy.types.Node):
    """appleseed OSL base node"""

    bl_idname = "AppleseedOSLNode"
    bl_label = "OSL Material"
    bl_icon = "NODE"
    bl_width_default = 240.0

    node_type = "osl"

    file_name = ""

    def traverse_tree(self, material_node):
        """Iterate inputs and traverse the tree backward if any inputs are connected.

        Nodes are added to a list attribute of the material output node.
        """
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                if hasattr(linked_node, "traverse_tree"):
                    linked_node.traverse_tree(material_node)
                else:
                    logger.error(f"Node {linked_node.name} is not an appleseed node, stopping traversal")
        material_node.tree.append(self)

    def draw_buttons(self, context, layout):
        pcoll = preview_collections["main"]

        my_icon = pcoll["as_icon"]

        if self.url_reference != '':
            layout.operator("wm.url_open", text="Node Reference", icon_value=my_icon.icon_id).url = self.url_reference
            
        layout.separator()
        socket_number = 0
        param_section = ""
        for x in self.input_params:
            if x['type'] != 'pointer':
                if 'hide_ui' in x.keys() and x['hide_ui'] is True:
                    continue
                if 'section' in x.keys():
                    if x['section'] != param_section and x['section'] is not None:
                        param_section = x['section']
                        icon = 'DISCLOSURE_TRI_DOWN' if getattr(self, param_section) else 'DISCLOSURE_TRI_RIGHT'
                        layout.prop(self, param_section, text=param_section, icon=icon, emboss=False)
                if x['name'] in self.filepaths:
                    layout.template_ID_preview(self, x['name'], open="image.open")
                    image = getattr(self, (x['name']))
                    layout.prop(image, "filepath", text="Filepath")
                else:
                    if getattr(self, param_section):
                        label_text = x['label']
                        if x['type'] in ('color', 'vector', 'float[2]'):
                            layout.label(text="%s:" % x['label'])
                            label_text = ""
                        if hasattr(self, "%s_use_node" % x['label']):
                            split_percentage = 1 - (150 / context.region.width)
                            split = layout.split(factor=split_percentage, align=True)
                            split.enabled = not self.inputs[socket_number].is_linked
                            col = split.column(align=True)
                            col.prop(self, x['name'], text=label_text)
                            col = split.column(align=True)
                            col.prop(self, "%s_use_node" % x['label'], text="", toggle=True, icon='NODETREE')
                            socket_number += 1
                        else:
                            layout.prop(self, x['name'], text=label_text)
            else:
                socket_number += 1

    def draw_buttons_ext(self, context, layout):
        for x in self.input_params:
            if x['type'] != 'pointer':
                if 'hide_ui' in x.keys() and x['hide_ui'] is True:
                    continue
                elif x['name'] in self.filepaths:
                    layout.template_ID_preview(self, x['name'], open="image.open")
                    layout.label(text="Image Path")
                    image_block = getattr(self, x['name'])
                    col = layout.column()
                    col.enabled = image_block.packed_file is None
                    col.prop(image_block, "filepath", text="")
                    layout.separator()
                else:
                    layout.prop(self, x['name'], text=x['label'])

    def init(self, context):
        if self.socket_input_names:
            for socket in self.socket_input_names:
                input = self.inputs.new(socket['socket_name'], socket['socket_label'])
                if socket['hide_ui'] is False:
                    input.hide = True
        if self.socket_output_names:
            for socket in self.socket_output_names:
                self.outputs.new(socket[0], socket[1])


class AppleseedOSLScriptNode(AppleseedOSLNode):
    bl_idname = "AppleseedOSLScriptNode"
    bl_label = "OSL Script"
    bl_icon = "NODE"
    bl_width_default = 240.0

    node_type = "osl_script"

    classes = list()

    def draw_buttons(self, context, layout):
        layout.prop(self, "script", text="")
        layout.operator('appleseed.compile_osl_script', text="Reload Parameters")
        socket_number = 0
        param_section = ""
        if hasattr(self, "input_params"):
            for x in self.input_params:
                if x['type'] != 'pointer':
                    if 'hide_ui' in x.keys() and x['hide_ui'] is True:
                        continue
                    if 'section' in x.keys():
                        if x['section'] != param_section and x['section'] is not None:
                            param_section = x['section']
                            icon = 'DISCLOSURE_TRI_DOWN' if getattr(self, param_section) else 'DISCLOSURE_TRI_RIGHT'
                            layout.prop(self, param_section, text=param_section, icon=icon, emboss=False)
                    if x['name'] in self.filepaths:
                        layout.template_ID_preview(self, x['name'], open="image.open")
                        image = getattr(self, (x['name']))
                        layout.prop(image, "filepath", text="Filepath")
                    else:
                        label_text = x['label']
                        if x['type'] in ('color', 'vector', 'float[2]'):
                            layout.label(text="%s:" % x['label'])
                            label_text = ""
                        if hasattr(self, "%s_use_node" % x['label']):
                            split_percentage = 1 - (150 / context.region.width)
                            split = layout.split(factor=split_percentage, align=True)
                            split.enabled = not self.inputs[socket_number].is_linked
                            col = split.column(align=True)
                            col.prop(self, x['name'], text=label_text)
                            col = split.column(align=True)
                            col.prop(self, "%s_use_node" % x['label'], text="", toggle=True, icon='NODETREE')
                            socket_number += 1
                        else:
                            layout.prop(self, x['name'], text=label_text)
                else:
                    socket_number += 1

    def draw_buttons_ext(self, context, layout):
        if hasattr(self, "input_params"):
            for x in self.input_params:
                if x['type'] != 'pointer':
                    if 'hide_ui' in x.keys() and x['hide_ui'] is True:
                        continue
                    elif x['name'] in self.filepaths:
                        layout.template_ID_preview(self, x['name'], open="image.open")
                        layout.label(text="Image Path")
                        image_block = getattr(self, x['name'])
                        col = layout.column()
                        col.enabled = image_block.packed_file is None
                        col.prop(image_block, "filepath", text="")
                        layout.separator()
                    else:
                        layout.prop(self, x['name'], text=x['label'])

    def init(self, context):
        if hasattr(self, "socket_input_names"):
            for socket in self.socket_input_names:
                input = self.inputs.new(socket['socket_name'], socket['socket_label'])
                if socket['hide_ui'] is False:
                    input.hide = True
        if hasattr(self, "socket_output_names"):
            for socket in self.socket_output_names:
                self.outputs.new(socket[0], socket[1])

    def traverse_tree(self, material_node):
        """Iterate inputs and traverse the tree backward if any inputs are connected.

        Nodes are added to a list attribute of the material output node.
        """
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                if hasattr(linked_node, "traverse_tree"):
                    linked_node.traverse_tree(material_node)
                else:
                    logger.error(f"Node {linked_node.name} is not an appleseed node, stopping traversal")
        material_node.tree.append(self)


class AppleseedOSLScriptBaseNode(AppleseedOSLScriptNode):
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


class AppleseedOSLNodeCategory(nodeitems_utils.NodeCategory):
    """
    Node category for extending the Add menu, toolbar panels and search operator
    """

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return renderer == 'APPLESEED_RENDER' and context.space_data.tree_type == 'ShaderNodeTree'


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
        AppleseedOSLNodeCategory("OSL_Surfaces", "appleseed - Surface", items=osl_surface),
        AppleseedOSLNodeCategory("OSL_Shaders", "appleseed - Shader", items=osl_shaders),
        AppleseedOSLNodeCategory("OSL_3D_Textures", "appleseed - Texture3D", items=osl_3d_textures),
        AppleseedOSLNodeCategory("OSL_2D_Textures", "appleseed - Texture2D", items=osl_2d_textures),
        AppleseedOSLNodeCategory("OSL_Color", "appleseed - Color", items=osl_color),
        AppleseedOSLNodeCategory("OSL_Utilities", "appleseed - Utility", items=osl_utilities),
        AppleseedOSLNodeCategory("OSL_Script", "appleseed - Script", items=[nodeitems_utils.NodeItem("AppleseedOSLScriptBaseNode")]),
        AppleseedOSLNodeCategory("OSL_Other", "appleseed - No Category", items=osl_other)]

    return appleseed_node_categories


osl_node_names = list()

classes = [AppleseedOSLScriptBaseNode]

preview_collections = dict()


def register():
    import bpy.utils.previews
    import os
    pcoll = bpy.utils.previews.new()
    my_icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons")

    # load a preview thumbnail of a file and store in the previews collection
    pcoll.load("as_icon", os.path.join(my_icons_dir, "appleseed32.png"), 'IMAGE')

    preview_collections["main"] = pcoll

    node_list = osl_utils.read_osl_shaders()
    for node in node_list:
        node_name, node_category, node_classes = osl_utils.generate_node(node, AppleseedOSLNode)
        classes.extend(node_classes)
        osl_node_names.append([node_name, node_category])

    for cls in classes:
        util.safe_register_class(cls)

    nodeitems_utils.register_node_categories("APPLESEED", node_categories(osl_node_names))


def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    nodeitems_utils.unregister_node_categories("APPLESEED")

    for cls in reversed(classes):
        util.safe_unregister_class(cls)
