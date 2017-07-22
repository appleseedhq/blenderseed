
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2013 Franz Beaune, Joel Daniels, Esteban Tovagliari, Luke Kliber.
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


class AppleseedRenderLayers(bpy.types.Panel):
    bl_label = "Render Layers"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render_layer"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        appleseed_layers = scene.appleseed_layers

        row = layout.row()
        row.template_list("UI_UL_list", "appleseed_render_layers", appleseed_layers, "layers", appleseed_layers, "layer_index")

        row = layout.row(align=True)
        row.operator("appleseed.add_renderlayer", icon="ZOOMIN")
        row.operator("appleseed.remove_renderlayer", icon="ZOOMOUT")

        if appleseed_layers.layers:
            current_layer = appleseed_layers.layers[appleseed_layers.layer_index]
            layout.prop(current_layer, "name", text="Layer Name")

            row = layout.row(align=True)
            row.operator("appleseed.add_to_renderlayer", text="Add Selected", icon="ZOOMIN")
            row.operator("appleseed.remove_from_renderlayer", text="Remove", icon="ZOOMOUT")


def register():
    bpy.utils.register_class(AppleseedRenderLayers)
#    bpy.utils.register_class( AppleseedRenderPasses)


def unregister():
    bpy.utils.unregister_class(AppleseedRenderLayers)
#    bpy.utils.unregister_class( AppleseedRenderPasses)
