
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


class AppleseedBSSRDFReflectanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedBSSRDFReflectance"
    bl_label = "Reflectance"

    socket_value = AppleseedMatProps.bssrdf_reflectance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedBSSDFReflectanceMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedBSSDFReflectanceMultiplier"
    bl_label = "Reflectance Multiplier"

    socket_value = AppleseedMatProps.bssrdf_reflectance_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedBSSRDFMfpSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedBSSRDFMfp"
    bl_label = "Mean Free Path"

    socket_value = AppleseedMatProps.bssrdf_mfp

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.


class AppleseedBSSRDFMfpMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedBSSRDFMfpMultiplier"
    bl_label = "Mean Free Path Multiplier"

    socket_value = AppleseedMatProps.bssrdf_mfp_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedBSSRDFWeightSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedBSSRDFWeight"
    bl_label = "Weight"

    socket_value = AppleseedMatProps.bssrdf_weight

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedBSSRDFNode(Node, AppleseedNode):
    """appleseed Metal BRDF Node"""
    bl_idname = "AppleseedBSSRDFNode"
    bl_label = "Subsurface BSSRDF"
    bl_icon = 'SMOOTH'

    node_type = 'bssrdf'

    bssrdf_model = bpy.props.EnumProperty(name="BSSRDF Model",
                                          description="BSSRDF model",
                                          items=[('normalized_diffusion_bssrdf', "Normalized Diffusion", ""),
                                                 ('better_dipole_bssrdf', "Dipole", ""),
                                                 ('gaussian_bssrdf', "Gaussian", "")],
                                          default='normalized_diffusion_bssrdf')

    bssrdf_ior = bpy.props.FloatProperty(name="bssrdf_ior",
                                         description="Index of Refraction",
                                         default=1.3,
                                         min=1.0,
                                         max=2.5)

    bssrdf_fresnel_weight = bpy.props.FloatProperty(name="bssrdf_fresnel_weight",
                                                    description="Fresnel Weight",
                                                    default=1.0,
                                                    min=0.0,
                                                    max=1.0)

    def init(self, context):
        self.inputs.new('AppleseedBSSRDFReflectance', "Reflectance")
        self.inputs.new('AppleseedBSSDFReflectanceMultiplier', "Reflectance Multiplier")
        self.inputs.new('AppleseedBSSRDFMfp', "Mean Free Path")
        self.inputs.new('AppleseedBSSRDFMfpMultiplier', "Mean Free Path Multiplier")
        self.inputs.new('AppleseedBSSRDFWeight', "Weight")
        self.outputs.new('NodeSocketShader', "BSSRDF")

    def draw_buttons(self, context, layout):
        layout.prop(self, "bssrdf_model", "BSSRDF Model")
        layout.prop(self, "bssrdf_ior", text="Index of Refraction")
        layout.prop(self, "bssrdf_fresnel_weight", text="Fresnel Weight")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedBSSRDFReflectanceSocket)
    bpy.utils.register_class(AppleseedBSSDFReflectanceMultiplierSocket)
    bpy.utils.register_class(AppleseedBSSRDFMfpSocket)
    bpy.utils.register_class(AppleseedBSSRDFMfpMultiplierSocket)
    bpy.utils.register_class(AppleseedBSSRDFWeightSocket)
    bpy.utils.register_class(AppleseedBSSRDFNode)


def unregister():
    bpy.utils.unregister_class(AppleseedBSSRDFNode)
    bpy.utils.unregister_class(AppleseedBSSRDFWeightSocket)
    bpy.utils.unregister_class(AppleseedBSSRDFMfpMultiplierSocket)
    bpy.utils.unregister_class(AppleseedBSSRDFMfpSocket)
    bpy.utils.unregister_class(AppleseedBSSDFReflectanceMultiplierSocket)
    bpy.utils.unregister_class(AppleseedBSSRDFReflectanceSocket)
