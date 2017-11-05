
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


class AppleseedMicrofacetReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMicrofacetReflectance"
    bl_label = "Diffuse Reflectance"

    socket_value = AppleseedMatLayerProps.microfacet_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedMicrofacetMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMicrofacetMultiplier"
    bl_label = "Diffuse Multiplier"

    socket_value = AppleseedMatLayerProps.microfacet_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedMicrofacetFresnelSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMicrofacetFresnel"
    bl_label = "Fresnel"

    socket_value = AppleseedMatLayerProps.microfacet_fresnel

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedMicrofacetGlossinessSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMicrofacetGlossiness"
    bl_label = "Glossiness"

    socket_value = AppleseedMatLayerProps.microfacet_mdf

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedMicrofacetGlossMultSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMicrofacetGlossMult"
    bl_label = "Glossiness Multiplier"

    socket_value = AppleseedMatLayerProps.microfacet_mdf_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedMicrofacetNode(Node, AppleseedNode):
    bl_idname = "AppleseedMicrofacetNode"
    bl_label = "Microfacet BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'microfacet'

    microfacet_model = AppleseedMatLayerProps.microfacet_model

    def init(self, context):
        self.inputs.new('AppleseedMicrofacetReflectance', "Reflectance")
        self.inputs.new('AppleseedMicrofacetMultiplier', "Multiplier")
        self.inputs.new('AppleseedMicrofacetGlossiness', "Glossiness")
        self.inputs.new('AppleseedMicrofacetGlossMult', "Gloss Multiplier")
        self.inputs.new('AppleseedMicrofacetFresnel', "Fresnel Multiplier")
        self.outputs.new('NodeSocketShader', "BRDF")

    def draw_buttons(self, context, layout):
        layout.prop(self, "microfacet_model")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedMicrofacetMultiplierSocket)
    bpy.utils.register_class(AppleseedMicrofacetReflectanceSocket)
    bpy.utils.register_class(AppleseedMicrofacetFresnelSocket)
    bpy.utils.register_class(AppleseedMicrofacetGlossinessSocket)
    bpy.utils.register_class(AppleseedMicrofacetGlossMultSocket)
    bpy.utils.register_class(AppleseedMicrofacetNode)


def unregister():
    bpy.utils.unregister_class(AppleseedMicrofacetNode)
    bpy.utils.unregister_class(AppleseedMicrofacetMultiplierSocket)
    bpy.utils.unregister_class(AppleseedMicrofacetReflectanceSocket)
    bpy.utils.unregister_class(AppleseedMicrofacetFresnelSocket)
    bpy.utils.unregister_class(AppleseedMicrofacetGlossinessSocket)
    bpy.utils.unregister_class(AppleseedMicrofacetGlossMultSocket)
