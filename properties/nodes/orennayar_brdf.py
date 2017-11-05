
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
from ..materials import AppleseedMatLayerProps
from . import AppleseedNode, AppleseedSocket


class AppleseedOrenNayarReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedOrenNayarReflectance"
    bl_label = "Reflectance"

    socket_value = AppleseedMatLayerProps.orennayar_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedOrenNayarMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedOrenNayarMultiplier"
    bl_label = "Multiplier"

    socket_value = AppleseedMatLayerProps.orennayar_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedOrenNayarRoughnessSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedOrenNayarRoughness"
    bl_label = "Roughness"

    socket_value = AppleseedMatLayerProps.orennayar_roughness

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedOrenNayarNode(Node, AppleseedNode):
    bl_idname = "AppleseedOrenNayarNode"
    bl_label = "Oren-Nayar BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'orennayar'

    def init(self, context):
        self.inputs.new('AppleseedOrenNayarReflectance', "Reflectance")
        self.inputs.new('AppleseedOrenNayarMultiplier', "Multiplier")
        self.inputs.new('AppleseedOrenNayarRoughness', "Roughness")
        self.outputs.new('NodeSocketShader', "BRDF")

    def draw_buttons(self, context, layout):
        pass

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedOrenNayarMultiplierSocket)
    bpy.utils.register_class(AppleseedOrenNayarReflectanceSocket)
    bpy.utils.register_class(AppleseedOrenNayarRoughnessSocket)
    bpy.utils.register_class(AppleseedOrenNayarNode)


def unregister():
    bpy.utils.unregister_class(AppleseedOrenNayarNode)
    bpy.utils.unregister_class(AppleseedOrenNayarMultiplierSocket)
    bpy.utils.unregister_class(AppleseedOrenNayarReflectanceSocket)
    bpy.utils.unregister_class(AppleseedOrenNayarRoughnessSocket)
