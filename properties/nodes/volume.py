
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
from bpy.types import Node
from ...util import asUpdate
from . import AppleseedNode


class AppleseedVolumeNode(Node, AppleseedNode):
    """appleseed Volume Node"""

    bl_idname = "AppleseedVolumeNode"
    bl_label = "Volume"
    bl_icon = 'SMOOTH'

    node_type = 'volume'

    volume_absorption = bpy.props.FloatVectorProperty(name="volume_absorption",
                                                      description="Volume absorption",
                                                      default=(0.5, 0.5, 0.5),
                                                      subtype='COLOR',
                                                      min=0.0,
                                                      max=1.0)

    volume_absorption_multiplier = bpy.props.FloatProperty(name="volume_absorption_multiplier",
                                                           description="Volume absorption multiplier",
                                                           default=1.0,
                                                           min=0.0,
                                                           max=200.0)

    volume_scattering = bpy.props.FloatVectorProperty(name="volume_scattering",
                                                      description="Volume scattering",
                                                      default=(0.5, 0.5, 0.5),
                                                      subtype='COLOR',
                                                      min=0.0,
                                                      max=1.0)

    volume_scattering_multiplier = bpy.props.FloatProperty(name="volume_scattering_multiplier",
                                                           description="Volume absorption multiplier",
                                                           default=1.0,
                                                           min=0.0,
                                                           max=200.0)

    volume_phase_function_model = bpy.props.EnumProperty(name="Phase Function Model",
                                                         description="Volume phase function model",
                                                         items=[('henyey', "Henyey-Greenstein", ""),
                                                                ('isotropic', "Isotropic", "")],
                                                         default="isotropic")

    volume_average_cosine = bpy.props.FloatProperty(name="volume_average_cosine",
                                                    description="Volume average cosine",
                                                    default=0.0,
                                                    min=-1.0,
                                                    max=1.0)

    def init(self, context):
        self.outputs.new('NodeSocketShader', "Volume")

    def draw_buttons(self, context, layout):
        layout.prop(self, "volume_absorption", text="Absorption")
        layout.prop(self, "volume_absorption_multiplier", text="Absorption Multiplier")
        layout.prop(self, "volume_scattering", text="Scattering")
        layout.prop(self, "volume_scattering_multiplier", text="Scattering Multiplier")
        layout.prop(self, "volume_phase_function_model", text="Phase Function Model")
        if self.volume_phase_function_model == 'henyey':
            layout.prop(self, "volume_average_cosine", text="Average Cosine")

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        asUpdate("Removing node ", self)

    def draw_label(self):
        return self.bl_label


def register():
    bpy.utils.register_class(AppleseedVolumeNode)


def unregister():
    bpy.utils.unregister_class(AppleseedVolumeNode)
