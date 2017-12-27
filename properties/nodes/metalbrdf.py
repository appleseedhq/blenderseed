
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


class AppleseedMetalNormalReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMetalNormalReflectance"
    bl_label = "Normal Reflectance"

    socket_value = AppleseedMatLayerProps.metal_brdf_normal_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedMetalReflectanceMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMetalReflectanceMultiplier"
    bl_label = "Reflectance Multiplier"

    socket_value = AppleseedMatLayerProps.metal_brdf_reflectance_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedMetalEdgeTintSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMetalEdgeTint"
    bl_label = "Edge Tint"

    socket_value = AppleseedMatLayerProps.metal_brdf_edge_tint

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedMetalRoughnessSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMetalRoughness"
    bl_label = "Roughness"

    socket_value = AppleseedMatLayerProps.metal_brdf_roughness

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedMetalAnisotropySocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMetalAnisotropy"
    bl_label = "Anisotropy"

    socket_value = AppleseedMatLayerProps.metal_brdf_anisotropy

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedMetalNode(Node, AppleseedNode):
    """appleseed Metal BRDF Node"""
    bl_idname = "AppleseedMetalNode"
    bl_label = "Metal BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'metal'

    metal_brdf_mdf = bpy.props.EnumProperty(name="Microfacet Type",
                                 description="",
                                 items=[('beckmann', "Beckmann", ""),
                                        ('ggx', "GGX", ""),
                                        ('std', "STD", "")],
                                 default='ggx')

    metal_brdf_falloff = bpy.props.FloatProperty(name="falloff",
                                      description="",
                                      default=0.4,
                                      min=0.0,
                                      max=1.0)

    def init(self, context):
        self.inputs.new('AppleseedMetalNormalReflectance', "Normal Reflectance")
        self.inputs.new('AppleseedMetalReflectanceMultiplier', "Reflectance Multiplier")
        self.inputs.new('AppleseedMetalEdgeTint', "Edge Tint")
        self.inputs.new('AppleseedMetalRoughness', "Roughness")
        self.inputs.new('AppleseedMetalAnisotropy', "Anisotropy")
        self.outputs.new('NodeSocketShader', "BRDF")

    def draw_buttons(self, context, layout):
        layout.prop(self, "metal_brdf_mdf")
        layout.prop(self, "metal_brdf_falloff", text="Highlight Falloff")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedMetalNormalReflectanceSocket)
    bpy.utils.register_class(AppleseedMetalReflectanceMultiplierSocket)
    bpy.utils.register_class(AppleseedMetalEdgeTintSocket)
    bpy.utils.register_class(AppleseedMetalRoughnessSocket)
    bpy.utils.register_class(AppleseedMetalAnisotropySocket)
    bpy.utils.register_class(AppleseedMetalNode)


def unregister():
    bpy.utils.unregister_class(AppleseedMetalNode)
    bpy.utils.unregister_class(AppleseedMetalAnisotropySocket)
    bpy.utils.unregister_class(AppleseedMetalRoughnessSocket)
    bpy.utils.unregister_class(AppleseedMetalEdgeTintSocket)
    bpy.utils.unregister_class(AppleseedMetalReflectanceMultiplierSocket)
    bpy.utils.unregister_class(AppleseedMetalNormalReflectanceSocket)
