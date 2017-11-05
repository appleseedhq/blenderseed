
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


class AppleseedKelemenReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedKelemenReflectance"
    bl_label = "Diffuse Reflectance"

    socket_value = AppleseedMatLayerProps.kelemen_matte_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedKelemenMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedKelemenMultiplier"
    bl_label = "Diffuse Multiplier"

    socket_value = AppleseedMatLayerProps.kelemen_matte_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedKelemenRoughnessSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedKelemenRoughness"
    bl_label = "Roughness"

    socket_value = AppleseedMatLayerProps.kelemen_roughness

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedKelemenSpecReflSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedKelemenSpecRefl"
    bl_label = "Specular Reflectance"

    socket_value = AppleseedMatLayerProps.kelemen_specular_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedKelemenSpecMultSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedKelemenSpecMult"
    bl_label = "Specular Multiplier"

    socket_value = AppleseedMatLayerProps.kelemen_specular_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedKelemenNode(Node, AppleseedNode):
    bl_idname = "AppleseedKelemenNode"
    bl_label = "Kelemen BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'kelemen'

    def init(self, context):
        self.inputs.new('AppleseedKelemenReflectance', "Reflectance")
        self.inputs.new('AppleseedKelemenMultiplier', "Multiplier")
        self.inputs.new('AppleseedKelemenSpecRefl', "Specular Reflectance")
        self.inputs.new('AppleseedKelemenSpecMult', "Specular Multiplier")
        self.inputs.new('AppleseedKelemenRoughness', "Roughness")
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
    bpy.utils.register_class(AppleseedKelemenMultiplierSocket)
    bpy.utils.register_class(AppleseedKelemenReflectanceSocket)
    bpy.utils.register_class(AppleseedKelemenRoughnessSocket)
    bpy.utils.register_class(AppleseedKelemenSpecReflSocket)
    bpy.utils.register_class(AppleseedKelemenSpecMultSocket)
    bpy.utils.register_class(AppleseedKelemenNode)


def unregister():
    bpy.utils.unregister_class(AppleseedKelemenNode)
    bpy.utils.unregister_class(AppleseedKelemenMultiplierSocket)
    bpy.utils.unregister_class(AppleseedKelemenReflectanceSocket)
    bpy.utils.unregister_class(AppleseedKelemenRoughnessSocket)
    bpy.utils.unregister_class(AppleseedKelemenSpecReflSocket)
    bpy.utils.unregister_class(AppleseedKelemenSpecMultSocket)
