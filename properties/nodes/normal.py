
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
from bpy.types import NodeSocket, Node
from ...util import asUpdate
from . import AppleseedNode, AppleseedSocket
from ..materials import AppleseedMatProps


class AppleseedNormalInputSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedNormalInput"
    bl_label = "Image"

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0

    def get_socket_value(self, texture_only=True):
        """Method to return socket's value, if not linked.

        If linked, return the name of the node with appended pointer.
        """

        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.node_type == 'texture':
                # The socket only accepts image textures.
                return linked_node.get_node_name()
        # Return socket value if not linked, or if the incoming node is incompatible.
        return self.socket_value


class AppleseedNormalNode(Node, AppleseedNode):
    bl_idname = "AppleseedNormalNode"
    bl_label = "Bump / Normal"
    bl_icon = 'SMOOTH'

    node_type = 'normal'

    material_use_normalmap = AppleseedMatProps.material_use_normalmap
    material_bump_amplitude = AppleseedMatProps.material_bump_amplitude

    def init(self, context):
        self.inputs.new("AppleseedNormalInput", "Image")
        self.outputs.new("AppleseedNormal", "Normal")

    def draw_buttons(self, context, layout):
        layout.prop(self, "material_use_normalmap", "Normal Map")
        layout.prop(self, "material_bump_amplitude", text="Amplitude")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedNormalInputSocket)
    bpy.utils.register_class(AppleseedNormalNode)


def unregister():
    bpy.utils.unregister_class(AppleseedNormalInputSocket)
    bpy.utils.unregister_class(AppleseedNormalNode)
