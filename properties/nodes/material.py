
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
from ...util import filter_params, asUpdate
from ..materials import AppleseedMatProps
from . import AppleseedNode, AppleseedSocket


class AppleseedBSDFSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedMaterialBSDF"
    bl_label = "BSDF"

    socket_value = "__default_material_bsdf"

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0

    def get_socket_value(self, texture_only=True):
        """Method to return socket's value, if not linked.

        If linked, return the name of the node with appended pointer.
        """
        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.node_type in {'ashikhmin',
                                         'bsdf_blend',
                                         'diffuse_btdf',
                                         'lambertian',
                                         'kelemen',
                                         'microfacet',
                                         'orennayar',
                                         'specular_btdf',
                                         'specular_brdf'}:
                return linked_node.get_node_name()
        # Return a default BSDF if not linked, or if the incoming node is incompatible.
        return self.socket_value


class AppleseedAlphaSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedAlpha"
    bl_label = "Alpha"

    socket_value = AppleseedMatProps.material_alpha

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedNormalSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedNormal"
    bl_label = "Normal"

    # Default socket_value is empty string instead of None
    # for purposes of project_file_writer's __emit_material_element() function.
    socket_value = ""

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return 0.67, 0.45, 1.0, 1.0

    def get_socket_value(self, texture_only=True):
        """
        Method to return socket's value, if not linked. 
        If linked, return the name of the node with appended pointer.
        """
        if self.is_linked:
            linked_node = self.links[0].from_node
            if linked_node.node_type == 'normal' and linked_node.inputs[0].is_linked:
                img_node = linked_node.inputs[0].links[0].from_node
                if img_node.node_type == 'texture':
                    return img_node.get_node_name()
        # Return socket value if not linked, or if the incoming node is incompatible.
        return self.socket_value

    def get_normal_params(self):
        linked_node = self.links[0].from_node
        bump_amplitude = linked_node.material_bump_amplitude
        use_normalmap = linked_node.material_use_normalmap
        return bump_amplitude, use_normalmap


class AppleseedEmissionColorSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedEmissionColor"
    bl_label = "Emission Color"

    socket_value = AppleseedMatProps.light_color

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0


class AppleseedEmissionStrengthSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedEmissionStrength"
    bl_label = "Emission Strength"

    socket_value = bpy.props.FloatProperty(name="Emission Strength",
                                           description="Light emission strength of material",
                                           default=0.0,
                                           min=0.0,
                                           max=10000)

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedMaterialNode(Node, AppleseedNode):
    bl_idname = "AppleseedMaterialNode"
    bl_label = "Material"
    bl_icon = 'SMOOTH'

    node_type = 'material'

    tree = []

    importance_multiplier = AppleseedMatProps.importance_multiplier
    cast_indirect = AppleseedMatProps.cast_indirect
    light_near_start = AppleseedMatProps.light_near_start

    def init(self, context):
        self.inputs.new('AppleseedMaterialBSDF', "BSDF")
        self.inputs.new('AppleseedAlpha', "Alpha")
        self.inputs.new('AppleseedNormal', "Normal")
        self.inputs.new('AppleseedEmissionStrength', "Emission Strength")
        self.inputs.new('AppleseedEmissionColor', "Emission Color")

    def draw_buttons(self, context, layout):
        img = bpy.data.images.get('appleseed32')
        if img is not None:
            icon = layout.icon(img)
            layout.label(text="appleseed", icon_value=icon)
        if self.inputs["Emission Strength"].socket_value > 0.0 or self.inputs["Emission Strength"].is_linked:
            layout.prop(self, "cast_indirect")
            layout.prop(self, "importance_multiplier")
            layout.prop(self, "light_near_start")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label

    def traverse_tree(self):
        """Iterate inputs and traverse the tree backward if any inputs are connected.

        Nodes are added to a list attribute of the material output node.
        Return the tree as a list of all the nodes.
        """
        self.tree.clear()
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_tree(self)
        return filter_params(self.tree)


def register():
    bpy.utils.register_class(AppleseedNormalSocket)
    bpy.utils.register_class(AppleseedAlphaSocket)
    bpy.utils.register_class(AppleseedEmissionColorSocket)
    bpy.utils.register_class(AppleseedEmissionStrengthSocket)
    bpy.utils.register_class(AppleseedBSDFSocket)
    bpy.utils.register_class(AppleseedMaterialNode)


def unregister():
    bpy.utils.unregister_class(AppleseedMaterialNode)
    bpy.utils.unregister_class(AppleseedNormalSocket)
    bpy.utils.unregister_class(AppleseedAlphaSocket)
    bpy.utils.unregister_class(AppleseedEmissionColorSocket)
    bpy.utils.unregister_class(AppleseedBSDFSocket)
    bpy.utils.unregister_class(AppleseedEmissionStrengthSocket)
