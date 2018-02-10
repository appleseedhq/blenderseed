
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
from ..materials import AppleseedMatProps
from . import AppleseedNode, AppleseedSocket


class AppleseedPlasticSpecularReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedPlasticSpecularReflectance"
    bl_label = "Specular Reflectance"

    socket_value = AppleseedMatProps.plastic_brdf_specular_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedPlasticSpecularReflectanceMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedPlasticSpecularReflectanceMultiplier"
    bl_label = "Specular Reflectance Multiplier"

    socket_value = AppleseedMatProps.plastic_brdf_specular_reflectance_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedPlasticRoughnessSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedPlasticRoughness"
    bl_label = "Roughness"

    socket_value = AppleseedMatProps.plastic_brdf_roughness

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedPlasticDiffuseReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedPlasticDiffuseReflectance"
    bl_label = "Diffuse Reflectance"

    socket_value = AppleseedMatProps.plastic_brdf_diffuse_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedPlasticDiffuseReflectanceMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedPlasticDiffuseReflectanceMultiplier"
    bl_label = "Diffuse Reflectance Multiplier"

    socket_value = AppleseedMatProps.plastic_brdf_diffuse_reflectance_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedPlasticNode(Node, AppleseedNode):
    """appleseed Plastic BRDF Node"""
    bl_idname = "AppleseedPlasticNode"
    bl_label = "Plastic BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'plastic'

    plastic_brdf_mdf = bpy.props.EnumProperty(name="Microfacet Type",
                                 description="",
                                 items=[('beckmann', "Beckmann", ""),
                                        ('ggx', "GGX", ""),
                                        ('std', "STD", ""),
                                        ('gtr1', "GTR1", "")],
                                 default='ggx')

    plastic_brdf_ior = bpy.props.FloatProperty(name="ior",
                                  description="Plastic index of refraction",
                                  default=1.5,
                                  min=1.0,
                                  max=2.5)

    plastic_brdf_falloff = bpy.props.FloatProperty(name="falloff",
                                      description="",
                                      default=0.4,
                                      min=0.0,
                                      max=1.0)

    def init(self, context):
        self.inputs.new('AppleseedPlasticSpecularReflectance', "Specular Reflectance")
        self.inputs.new('AppleseedPlasticSpecularReflectanceMultiplier', "Specular Reflectance Multiplier")
        self.inputs.new('AppleseedPlasticRoughness', "Roughness")
        self.inputs.new('AppleseedPlasticDiffuseReflectance', "Diffuse Reflectance")
        self.inputs.new('AppleseedPlasticDiffuseReflectanceMultiplier', "Diffuse Reflectance Multiplier")
        self.outputs.new('NodeSocketShader', "BRDF")

    def draw_buttons(self, context, layout):
        layout.prop(self, "plastic_brdf_mdf")
        layout.prop(self, "plastic_brdf_ior", text="Index of Refraction")
        layout.prop(self, "plastic_brdf_falloff", text="Highlight Falloff")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedPlasticSpecularReflectanceSocket)
    bpy.utils.register_class(AppleseedPlasticSpecularReflectanceMultiplierSocket)
    bpy.utils.register_class(AppleseedPlasticRoughnessSocket)
    bpy.utils.register_class(AppleseedPlasticDiffuseReflectanceSocket)
    bpy.utils.register_class(AppleseedPlasticDiffuseReflectanceMultiplierSocket)
    bpy.utils.register_class(AppleseedPlasticNode)


def unregister():
    bpy.utils.unregister_class(AppleseedPlasticNode)
    bpy.utils.unregister_class(AppleseedPlasticDiffuseReflectanceMultiplierSocket)
    bpy.utils.unregister_class(AppleseedPlasticDiffuseReflectanceSocket)
    bpy.utils.unregister_class(AppleseedPlasticRoughnessSocket)
    bpy.utils.unregister_class(AppleseedPlasticSpecularReflectanceMultiplierSocket)
    bpy.utils.unregister_class(AppleseedPlasticSpecularReflectanceSocket)
