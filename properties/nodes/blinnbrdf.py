
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


class AppleseedBlinnExponentSocket(NodeSocket, AppleseedSocket):
    bl_idname = "AppleseedBlinnExponent"
    bl_label = "Exponent"

    socket_value = AppleseedMatProps.blinn_brdf_exponent

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return 0.5, 0.5, 0.5, 1.0


class AppleseedBlinnNode(Node, AppleseedNode):
    """appleseed Metal BRDF Node"""
    bl_idname = "AppleseedBlinnNode"
    bl_label = "Blinn BRDF"
    bl_icon = 'SMOOTH'

    node_type = 'blinn'

    ior = bpy.props.FloatProperty(name="ior",
                                  description="Index of refraction",
                                  default=1.5,
                                  min=1,
                                  max=2.5)

    def init(self, context):
        self.inputs.new('AppleseedBlinnExponent', "Exponent")
        self.outputs.new('NodeSocketShader', "BRDF")

    def draw_buttons(self, context, layout):
        layout.prop(self, "ior", text="Index of Refraction")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedBlinnExponentSocket)
    bpy.utils.register_class(AppleseedBlinnNode)


def unregister():
    bpy.utils.unregister_class(AppleseedBlinnNode)
    bpy.utils.unregister_class(AppleseedBlinnExponentSocket)
