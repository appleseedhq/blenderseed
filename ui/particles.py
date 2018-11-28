#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2014-2018 The appleseedhq Organization
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

from ..utils import util


class AppleseedPsysPanel(bpy.types.Panel):
    bl_label = "Hair Rendering"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "particle"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine
        psys = context.particle_system
        return renderer == 'APPLESEED_RENDER' and context.object is not None and psys and psys.settings.type == 'HAIR'

    def draw_header(self, context):
        pass

    def draw(self, context):
        layout = self.layout
        asr_psys = context.particle_system.settings.appleseed

        layout.prop(asr_psys, "shape", text="Strand Shape")
        layout.prop(asr_psys, "resolution", text="Resolution")

        layout.label("Thickness:")
        row = layout.row()
        row.prop(asr_psys, "root_size", text="Root")
        row.prop(asr_psys, "tip_size", text="Tip")
        layout.prop(asr_psys, "scaling", text="Scaling")


def register():
    util.safe_register_class(AppleseedPsysPanel)


def unregister():
    util.safe_unregister_class(AppleseedPsysPanel)
