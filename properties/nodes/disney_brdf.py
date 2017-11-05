
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

from . import AppleseedNode, AppleseedSocket
from ..materials import AppleseedMatLayerProps
from ...util import asUpdate


class AppleseedDisneyBaseSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneyBase"
    bl_label = "Base Color"

    socket_value = AppleseedMatLayerProps.disney_base

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedDisneyAnisoSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneyAniso"
    bl_label = "Anisotropy"

    socket_value = AppleseedMatLayerProps.disney_aniso

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneyClearCoatSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneyClearCoat"
    bl_label = "Clear Coat"

    socket_value = AppleseedMatLayerProps.disney_clearcoat

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneyClearCoatGlossSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneyClearCoatGloss"
    bl_label = "Clear Coat Gloss"

    socket_value = AppleseedMatLayerProps.disney_clearcoat_gloss

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneyMetallicSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneyMetallic"
    bl_label = "Metallic"

    socket_value = AppleseedMatLayerProps.disney_metallic

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneyRoughnessSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneyRoughness"
    bl_label = "Roughness"

    socket_value = AppleseedMatLayerProps.disney_roughness

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneySheenSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneySheen"
    bl_label = "Sheen"

    socket_value = AppleseedMatLayerProps.disney_sheen

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneySheenTintSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneySheenTint"
    bl_label = "Sheen Tint"

    socket_value = AppleseedMatLayerProps.disney_sheen_tint

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneySpecSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneySpec"
    bl_label = "Specular"

    socket_value = AppleseedMatLayerProps.disney_spec

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneySpecTintSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneySpecTint"
    bl_label = "Specular Tint"

    socket_value = AppleseedMatLayerProps.disney_spec_tint

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneySubsurfaceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedDisneySubsurface"
    bl_label = "Subsurface"

    socket_value = AppleseedMatLayerProps.disney_subsurface

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedDisneyNode(Node, AppleseedNode):
    bl_idname = "AppleseedDisneyNode"
    bl_label = "Disney BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'disney'

    def init(self, context):
        self.inputs.new('AppleseedDisneyBase', "Base Color")
        self.inputs.new('AppleseedDisneySpec', "Specular")
        self.inputs.new('AppleseedDisneySpecTint', "Specular Tint")
        self.inputs.new('AppleseedDisneyAniso', "Anisotropy")
        self.inputs.new('AppleseedDisneyMetallic', "Metallic")
        self.inputs.new('AppleseedDisneyRoughness', "Roughness")
        self.inputs.new('AppleseedDisneyClearCoat', "Clear Coat")
        self.inputs.new('AppleseedDisneyClearCoatGloss', "Clear Coat Gloss")
        self.inputs.new('AppleseedDisneySheen', "Sheen")
        self.inputs.new('AppleseedDisneySheenTint', "Sheen Tint")
        self.inputs.new('AppleseedDisneySubsurface', "Subsurface")
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
    bpy.utils.register_class(AppleseedDisneyBaseSocket)
    bpy.utils.register_class(AppleseedDisneySpecSocket)
    bpy.utils.register_class(AppleseedDisneySpecTintSocket)
    bpy.utils.register_class(AppleseedDisneyAnisoSocket)
    bpy.utils.register_class(AppleseedDisneyMetallicSocket)
    bpy.utils.register_class(AppleseedDisneyRoughnessSocket)
    bpy.utils.register_class(AppleseedDisneyClearCoatSocket)
    bpy.utils.register_class(AppleseedDisneyClearCoatGlossSocket)
    bpy.utils.register_class(AppleseedDisneySheenSocket)
    bpy.utils.register_class(AppleseedDisneySheenTintSocket)
    bpy.utils.register_class(AppleseedDisneySubsurfaceSocket)
    bpy.utils.register_class(AppleseedDisneyNode)


def unregister():
    bpy.utils.unregister_class(AppleseedDisneyNode)
    bpy.utils.unregister_class(AppleseedDisneyBaseSocket)
    bpy.utils.unregister_class(AppleseedDisneySpecSocket)
    bpy.utils.unregister_class(AppleseedDisneySpecTintSocket)
    bpy.utils.unregister_class(AppleseedDisneyAnisoSocket)
    bpy.utils.unregister_class(AppleseedDisneyMetallicSocket)
    bpy.utils.unregister_class(AppleseedDisneyRoughnessSocket)
    bpy.utils.unregister_class(AppleseedDisneyClearCoatSocket)
    bpy.utils.unregister_class(AppleseedDisneyClearCoatGlossSocket)
    bpy.utils.unregister_class(AppleseedDisneySheenSocket)
    bpy.utils.unregister_class(AppleseedDisneySheenTintSocket)
    bpy.utils.unregister_class(AppleseedDisneySubsurfaceSocket)
