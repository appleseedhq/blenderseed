
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


class AppleseedSpecBTDFReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedSpecBTDFReflectance"
    bl_label = "Reflectance"

    socket_value = AppleseedMatLayerProps.specular_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedSpecBTDFMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedSpecBTDFMultiplier"
    bl_label = "Multiplier"

    socket_value = AppleseedMatLayerProps.specular_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedSpecBTDFTransmittanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedSpecBTDFTransmittance"
    bl_label = "Transmittance"

    socket_value = AppleseedMatLayerProps.spec_btdf_transmittance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedSpecBTDFTransMultSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedSpecBTDFTransMult"
    bl_label = "Multiplier"

    socket_value = AppleseedMatLayerProps.spec_btdf_trans_mult

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)

        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedSpecBTDFNode(Node, AppleseedNode):
    bl_idname = "AppleseedSpecBTDFNode"
    bl_label = "Specular BTDF"
    bl_icon = 'SMOOTH'

    node_type = 'specular_btdf'

    ior = AppleseedMatLayerProps.spec_btdf_ior

    def init(self, context):
        self.inputs.new('AppleseedSpecBTDFReflectance', "Reflectance")
        self.inputs.new('AppleseedSpecBTDFMultiplier', "Multiplier")
        self.inputs.new('AppleseedSpecBTDFTransmittance', "Transmittance")
        self.inputs.new('AppleseedSpecBTDFTransMult', "Multiplier")
        self.outputs.new('NodeSocketShader', "BTDF")

    def draw_buttons(self, context, layout):
        layout.prop(self, "ior")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedSpecBTDFMultiplierSocket)
    bpy.utils.register_class(AppleseedSpecBTDFReflectanceSocket)
    bpy.utils.register_class(AppleseedSpecBTDFTransmittanceSocket)
    bpy.utils.register_class(AppleseedSpecBTDFTransMultSocket)
    bpy.utils.register_class(AppleseedSpecBTDFNode)


def unregister():
    bpy.utils.unregister_class(AppleseedSpecBTDFNode)
    bpy.utils.unregister_class(AppleseedSpecBTDFMultiplierSocket)
    bpy.utils.unregister_class(AppleseedSpecBTDFReflectanceSocket)
    bpy.utils.unregister_class(AppleseedSpecBTDFTransmittanceSocket)
    bpy.utils.unregister_class(AppleseedSpecBTDFTransMultSocket)
