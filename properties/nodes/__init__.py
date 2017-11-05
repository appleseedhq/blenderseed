
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
import nodeitems_utils
from bpy.types import NodeTree
from bpy.app.handlers import persistent
from ...util import addon_dir, join_names_underscore
import os


class AppleseedNodeTree(NodeTree):
    """Class for appleseed node tree."""

    bl_idname = 'AppleseedNodeTree'
    bl_label = 'appleseed Node Tree'
    bl_icon = 'NODETREE'

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return renderer == 'APPLESEED_RENDER'


class AppleseedNode:
    """Base class for appleseed nodes."""

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return context.bl_idname == "AppleseedNodeTree" and renderer == 'APPLESEED_RENDER'

    def get_node_name(self):
        """Return the node's name, including appended pointer."""
        return join_names_underscore(self.name, str(self.as_pointer()))

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


class AppleseedNodeCategory(nodeitems_utils.NodeCategory):
    """Node category for extending the Add menu, toolbar panels and search operator.

    Base class for node categories.
    """

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        return context.space_data.tree_type == 'AppleseedNodeTree' and renderer == 'APPLESEED_RENDER'


# appleseed node categories
# Format: (identifier, label, items list)
appleseed_node_categories = [
    AppleseedNodeCategory("BSDF", "BSDF", items=[
        nodeitems_utils.NodeItem("AppleseedAshikhminNode"),
        nodeitems_utils.NodeItem("AppleseedDiffuseBTDFNode"),
        nodeitems_utils.NodeItem("AppleseedDisneyNode"),
        nodeitems_utils.NodeItem("AppleseedKelemenNode"),
        nodeitems_utils.NodeItem("AppleseedLambertianNode"),
        nodeitems_utils.NodeItem("AppleseedMicrofacetNode"),
        nodeitems_utils.NodeItem("AppleseedOrenNayarNode"),
        nodeitems_utils.NodeItem("AppleseedSpecBRDFNode"),
        nodeitems_utils.NodeItem("AppleseedSpecBTDFNode"),
        nodeitems_utils.NodeItem("AppleseedBlendNode")]),
    AppleseedNodeCategory("TEXTURES", "Texture", items=[
        nodeitems_utils.NodeItem("AppleseedTexNode"),
        nodeitems_utils.NodeItem("AppleseedNormalNode")]),
    AppleseedNodeCategory("OUTPUTS", "Output", items=[
        nodeitems_utils.NodeItem("AppleseedMaterialNode")])]


@persistent
def appleseed_scene_loaded(dummy):
    # Load images as icons
    icon16 = bpy.data.images.get('appleseed16')
    icon32 = bpy.data.images.get('appleseed32')
    if icon16 is None:
        img = bpy.data.images.load(os.path.join(os.path.join(addon_dir, 'icons'), 'appleseed16.png'))
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
        img = bpy.data.images.load(os.path.join(os.path.join(addon_dir, 'icons'), 'appleseed32.png'))
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
from . import ashikhmin_brdf
from . import bsdf_blend
from . import diffuse_btdf
from . import disney_brdf
from . import kelemen_brdf
from . import lambertian_brdf
from . import microfacet_brdf
from . import orennayar_brdf
from . import specular_brdf
from . import specular_btdf
from . import texture
from . import normal
from . import material


def register():
    bpy.app.handlers.load_post.append(appleseed_scene_loaded)
    bpy.app.handlers.scene_update_pre.append(appleseed_scene_loaded)
    nodeitems_utils.register_node_categories("APPLESEED", appleseed_node_categories)
    bpy.utils.register_class(AppleseedNodeTree)
    ashikhmin_brdf.register()
    bsdf_blend.register()
    diffuse_btdf.register()
    disney_brdf.register()
    kelemen_brdf.register()
    lambertian_brdf.register()
    microfacet_brdf.register()
    orennayar_brdf.register()
    specular_brdf.register()
    specular_btdf.register()
    texture.register()
    normal.register()
    material.register()


def unregister():
    nodeitems_utils.unregister_node_categories("APPLESEED")
    bpy.utils.unregister_class(AppleseedNodeTree)
    ashikhmin_brdf.unregister()
    bsdf_blend.unregister()
    disney_brdf.unregister()
    diffuse_btdf.unregister()
    kelemen_brdf.unregister()
    lambertian_brdf.unregister()
    microfacet_brdf.unregister()
    orennayar_brdf.unregister()
    specular_brdf.unregister()
    specular_btdf.unregister()
    texture.unregister()
    material.unregister()
    normal.unregister()
    bpy.app.handlers.load_post.remove(appleseed_scene_loaded)
