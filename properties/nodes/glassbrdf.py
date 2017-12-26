
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


class AppleseedGlassTransmittanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassTransmittance"
    bl_label = "Transmittance"

    socket_value = AppleseedMatLayerProps.glass_bsdf_surface_transmittance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedGlassTransmittanceMultiplierSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassTransmittanceMultiplier"
    bl_label = "Transmittance Multiplier"

    socket_value = AppleseedMatLayerProps.glass_bsdf_surface_transmittance_multiplier

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedGlassReflectionTintSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassReflectionTint"
    bl_label = "Reflection Tint"

    socket_value = AppleseedMatLayerProps.glass_bsdf_reflection_tint

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedGlassRefractionTintSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassRefractionTint"
    bl_label = "Reflection Tint"

    socket_value = AppleseedMatLayerProps.glass_bsdf_refraction_tint

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedGlassRoughnessSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassRoughness"
    bl_label = "Roughness"

    socket_value = AppleseedMatLayerProps.glass_bsdf_roughness

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedGlassAnisotropySocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassAnisotropy"
    bl_label = "Anisotropy"

    socket_value = AppleseedMatLayerProps.glass_bsdf_anisotropy

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedGlassVolumeTransmittanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassVolumeTransmittance"
    bl_label = "Volume Transmittance"

    socket_value = AppleseedMatLayerProps.glass_bsdf_volume_transmittance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedGlassVolumeTransmittanceDistanceSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassVolumeTransmittanceDistance"
    bl_label = "Volume Transmittance Distance"

    socket_value = AppleseedMatLayerProps.glass_bsdf_volume_transmittance_distance

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedGlassVolumeAbsorptionSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassVolumeAbsorption"
    bl_label = "Volume Absorption"

    socket_value = AppleseedMatLayerProps.glass_bsdf_volume_absorption

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedGlassVolumeDensitySocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedGlassVolumeDensity"
    bl_label = "Volume Density"

    socket_value = AppleseedMatLayerProps.glass_bsdf_volume_density 

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedGlassNode(Node, AppleseedNode):
    """appleseed Glass BRDF Node"""
    bl_idname = "AppleseedGlassNode"
    bl_label = "Glass BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'glass'

    glass_brdf_mdf = bpy.props.EnumProperty(name="Microfacet Type",
                                 description="",
                                 items=[('beckmann', "Beckmann", ""),
                                        ('ggx', "GGX", ""),
                                        ('std', "STD", "")],
                                 default='ggx')

    glass_brdf_ior = bpy.props.FloatProperty(name="glass_bsdf_ior",
                                  description="Glass index of refraction",
                                  default=1.5,
                                  min=1.0,
                                  max=2.5)

    glass_brdf_falloff = bpy.props.FloatProperty(name="falloff",
                                      description="",
                                      default=0.4,
                                      min=0.0,
                                      max=1.0)

    glass_brdf_volume_parameterization = bpy.props.EnumProperty(name="Volume Type",
                                                     items=[('absorption', "Absorption", ""),
                                                            ('transmittance', "Transmittance", "")],
                                                     default='transmittance')

    glass_brdf_volume_scale = bpy.props.FloatProperty(name="glass_bsdf_volume_scale",
                                           description="Scale of the glass volume",
                                           default=1.0,
                                           min=0.0,
                                           soft_max=10.0)

    def init(self, context):
        self.inputs.new('AppleseedGlassTransmittance', "Transmittance")
        self.inputs.new('AppleseedGlassTransmittanceMultiplier', "Transmittance Multiplier")
        self.inputs.new('AppleseedGlassReflectionTint', "Reflection Tint")
        self.inputs.new('AppleseedGlassRefractionTint', "Refraction Tint")
        self.inputs.new('AppleseedGlassRoughness', "Roughness")
        self.inputs.new('AppleseedGlassAnisotropy', "Anisotropy")
        self.inputs.new('AppleseedGlassVolumeTransmittance', "Volume Transmittance")
        self.inputs.new('AppleseedGlassVolumeTransmittanceDistance', "Volume Transmittance Distance")
        self.inputs.new('AppleseedGlassVolumeAbsorption', "Volume Absorption")
        self.inputs.new('AppleseedGlassVolumeDensity', "Volume Density")
        self.outputs.new('NodeSocketShader', "BRDF")

    def draw_buttons(self, context, layout):
        layout.prop(self, "glass_brdf_mdf")
        layout.prop(self, "glass_brdf_ior", text="Index of Refraction")
        layout.prop(self, "glass_brdf_falloff", text="Highlight Falloff")
        layout.prop(self, "glass_brdf_volume_parameterization")
        layout.prop(self, "glass_brdf_volume_scale", text="Volume Scale")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedGlassTransmittanceSocket)
    bpy.utils.register_class(AppleseedGlassTransmittanceMultiplierSocket)
    bpy.utils.register_class(AppleseedGlassReflectionTintSocket)
    bpy.utils.register_class(AppleseedGlassRefractionTintSocket)
    bpy.utils.register_class(AppleseedGlassRoughnessSocket)
    bpy.utils.register_class(AppleseedGlassAnisotropySocket)
    bpy.utils.register_class(AppleseedGlassVolumeTransmittanceSocket)
    bpy.utils.register_class(AppleseedGlassVolumeTransmittanceDistanceSocket)
    bpy.utils.register_class(AppleseedGlassVolumeAbsorptionSocket)
    bpy.utils.register_class(AppleseedGlassVolumeDensitySocket)
    bpy.utils.register_class(AppleseedGlassNode)


def unregister():
    bpy.utils.unregister_class(AppleseedGlassNode)
    bpy.utils.unregister_class(AppleseedGlassVolumeDensitySocket)
    bpy.utils.unregister_class(AppleseedGlassVolumeAbsorptionSocket)
    bpy.utils.unregister_class(AppleseedGlassVolumeTransmittanceDistanceSocket)
    bpy.utils.unregister_class(AppleseedGlassVolumeTransmittanceSocket)
    bpy.utils.unregister_class(AppleseedGlassAnisotropySocket)
    bpy.utils.unregister_class(AppleseedGlassRoughnessSocket)
    bpy.utils.unregister_class(AppleseedGlassReflectionTintSocket)
    bpy.utils.unregister_class(AppleseedGlassRefractionTintSocket)
    bpy.utils.unregister_class(AppleseedGlassTransmittanceMultiplierSocket)
    bpy.utils.unregister_class(AppleseedGlassTransmittanceSocket)
