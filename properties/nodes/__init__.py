
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
from nodeitems_utils import NodeItem, NodeCategory
from bpy.types import NodeTree
from bpy.app.handlers import persistent
import os
from ... import util


class AppleseedOSLNodeTree(NodeTree):
    """Class for appleseed node tree."""

    bl_idname = 'AppleseedOSLNodeTree'
    bl_label = 'appleseed OSL Node Tree'
    bl_icon = 'MATERIAL'

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return renderer == 'APPLESEED_RENDER'

    # This following code is required to avoid a max recursion error when Blender checks for node updates
    def update(self):
        self.refresh = True

    def acknowledge_connection(self, context):
        while self.refresh:
            self.refresh = False
            break

    refresh = bpy.props.BoolProperty(name='Links Changed', default=False, update=acknowledge_connection)


class AppleseedNode:
    """Base class for appleseed nodes."""

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return context.bl_idname == "AppleseedNodeTree" and renderer == 'APPLESEED_RENDER'

    def get_node_name(self):
        """Return the node's name, including appended pointer."""
        return util.join_names_underscore(self.name, str(self.as_pointer()))

    def traverse_tree(self, material_node):
        """Iterate inputs and traverse the tree backward if any inputs are connected.

        Nodes are added to a list attribute of the material output node.
        """
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_tree(material_node)
        material_node.tree.append(self)


class AppleseedSocket(object):
    """Base class for appleseed sockets."""

    socket_value = None

    def get_socket_value(self, texture_only=True):
        """
        Method to return socket's value, if not linked.
        If linked, return the name of the node with appended pointer.
        """
        if self.is_linked:
            linked_node = self.links[0].from_node
            if texture_only and linked_node.node_type == 'texture':
                # The socket only accepts image textures.
                return linked_node.get_node_name() + "_inst"
            if not texture_only:
                return linked_node.get_node_name()
        # Return socket value if not linked, or if the incoming node is incompatible.
        return self.socket_value


class AppleseedOSLNodeCategory(NodeCategory):
    """Node category for extending the Add menu, toolbar panels and search operator.

    Base class for node categories.
    """

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return context.space_data.tree_type == 'AppleseedOSLNodeTree' and renderer == 'APPLESEED_RENDER'

    """
    appleseed node categories
    Format: (identifier, label, items list)
    """


def node_categories(osl_nodes):
    osl_shaders = []
    osl_textures = []
    osl_utilities = []
    osl_3d_textures = []
    osl_surface = []

    for node in osl_nodes:
        node_item = NodeItem(node[0])
        node_category = node[1]
        if node_category == 'shader':
            osl_shaders.append(node_item)
        elif node_category == 'texture':
            osl_textures.append(node_item)
        elif node_category == 'utility':
            osl_utilities.append(node_item)
        elif node_category == '3d_texture':
            osl_3d_textures.append(node_item)
        else:
            osl_surface.append(node_item)

    appleseed_node_categories = [
        AppleseedOSLNodeCategory("OSL_Surfaces", "OSL Surface", items=osl_surface),
        AppleseedOSLNodeCategory("OSL_Shaders", "OSL Shader", items=osl_shaders),
        AppleseedOSLNodeCategory("OSL_Textures", "OSL Texture", items=osl_textures),
        AppleseedOSLNodeCategory("OSL_3D_Textures", "OSL 3D Texture", items=osl_3d_textures),
        AppleseedOSLNodeCategory("OSL_Utilities", "OSL Utility", items=osl_utilities)
    ]

    return appleseed_node_categories


@persistent
def appleseed_scene_loaded(dummy):
    # Load images as icons
    icon16 = bpy.data.images.get('appleseed16')
    icon32 = bpy.data.images.get('appleseed32')
    if icon16 is None:
        img = bpy.data.images.load(os.path.join(os.path.join(util.addon_dir, 'icons'), 'appleseed16.png'))
        img.name = 'appleseed16'
        img.use_alpha = True
        img.user_clear()
    # remove scene_update handler
    elif "appleseed16" not in icon16.keys():
        icon16["appleseed16"] = True
        for f in bpy.app.handlers.scene_update_pre:
            if f.__name__ == "appleseed_scene_loaded":
                bpy.app.handlers.scene_update_pre.remove(f)
    if icon32 is None:
        img = bpy.data.images.load(os.path.join(os.path.join(util.addon_dir, 'icons'), 'appleseed32.png'))
        img.name = 'appleseed32'
        img.use_alpha = True
        img.user_clear()  # Won't get saved into .blend files
    # remove scene_update handler
    elif "appleseed32" not in icon32.keys():
        icon32["appleseed32"] = True
        for f in bpy.app.handlers.scene_update_pre:
            if f.__name__ == "appleseed_scene_loaded":
                bpy.app.handlers.scene_update_pre.remove(f)


# Load the modules after classes have been created.
from . import oslnode

osl_node_names = []


def register():
    bpy.app.handlers.load_post.append(appleseed_scene_loaded)
    bpy.app.handlers.scene_update_pre.append(appleseed_scene_loaded)
    util.safe_register_class(AppleseedOSLNodeTree)
    node_list = util.read_osl_shaders()
    for node in node_list:
        try:
            if 'USE_APPLESEED_PYTHON' in os.environ:
                node_name, node_category = oslnode.generate_node_python(node)
            else:
                node_name, node_category = oslnode.generate_node_oslinfo(node)
            osl_node_names.append([node_name, node_category])
        except:
            pass
    nodeitems_utils.register_node_categories("APPLESEED", node_categories(osl_node_names))


def unregister():
    nodeitems_utils.unregister_node_categories("APPLESEED")
    util.safe_unregister_class(AppleseedOSLNodeTree)
    bpy.app.handlers.load_post.remove(appleseed_scene_loaded)
