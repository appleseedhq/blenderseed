
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


class AppleseedAshikhminReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedAshikhminReflectance"
    bl_label = "Diffuse Reflectance"

    socket_value = AppleseedMatLayerProps.ashikhmin_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedAshikhminMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedAshikhminMultiplier"
    bl_label = "Diffuse Multiplier"

    socket_value = AppleseedMatLayerProps.ashikhmin_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedAshikhminGlossySocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedAshikhminGlossy"
    bl_label = "Glossy Reflectance"

    socket_value = AppleseedMatLayerProps.ashikhmin_glossy

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedAshikhminUSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedAshikhminU"
    bl_label = "Shininess U"

    socket_value = AppleseedMatLayerProps.ashikhmin_shininess_u

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedAshikhminVSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedAshikhminV"
    bl_label = "Shininess V"

    socket_value = AppleseedMatLayerProps.ashikhmin_shininess_v

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedAshikhminFresnelSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedAshikhminFresnel"
    bl_label = "Fresnel"

    socket_value = bpy.props.FloatProperty(name="Fresnel Multiplier",
                                           description="Ashikhmin fresnel multiplier",
                                           default=1,
                                           min=0,
                                           max=1)

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedAshikhminNode(Node, AppleseedNode):
    bl_idname = "AppleseedAshikhminNode"
    bl_label = "Ashikhmin-Shirley BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'ashikhmin'

    def init(self, context):
        self.inputs.new('AppleseedAshikhminReflectance', "Reflectance")
        self.inputs.new('AppleseedAshikhminMultiplier', "Multiplier")
        self.inputs.new('AppleseedAshikhminGlossy', "Glossy Reflectance")
        self.inputs.new('AppleseedAshikhminU', "Shininess U")
        self.inputs.new('AppleseedAshikhminV', "Shininess V")
        self.inputs.new('AppleseedAshikhminFresnel', "Fresnel Multiplier")
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
    bpy.utils.register_class(AppleseedAshikhminMultiplierSocket)
    bpy.utils.register_class(AppleseedAshikhminReflectanceSocket)
    bpy.utils.register_class(AppleseedAshikhminGlossySocket)
    bpy.utils.register_class(AppleseedAshikhminUSocket)
    bpy.utils.register_class(AppleseedAshikhminVSocket)
    bpy.utils.register_class(AppleseedAshikhminFresnelSocket)
    bpy.utils.register_class(AppleseedAshikhminNode)


def unregister():
    bpy.utils.unregister_class(AppleseedAshikhminNode)
    bpy.utils.unregister_class(AppleseedAshikhminMultiplierSocket)
    bpy.utils.unregister_class(AppleseedAshikhminReflectanceSocket)
    bpy.utils.unregister_class(AppleseedAshikhminGlossySocket)
    bpy.utils.unregister_class(AppleseedAshikhminUSocket)
    bpy.utils.unregister_class(AppleseedAshikhminVSocket)
    bpy.utils.unregister_class(AppleseedAshikhminFresnelSocket)
