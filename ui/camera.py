
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


class AppleseedCameraDoF(bpy.types.Panel):
    bl_label = "Depth of Field"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.active_object.type == 'CAMERA'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_cam_props = scene.camera.data.appleseed

        row = layout.row()
        row.prop(asr_cam_props, "camera_type", text='Model')

        if asr_cam_props.camera_type == "thinlens":
            layout.prop(asr_cam_props, "camera_dof", text="F-Stop")

            layout.prop(context.active_object.data, "dof_distance", text="Focal Distance")
            layout.active = context.active_object.data.dof_object is None
            layout.prop(context.active_object.data, "dof_object", text='Autofocus')

            layout.prop(asr_cam_props, "diaphragm_blades")
            layout.prop(asr_cam_props, "diaphragm_angle")

            layout.prop(asr_cam_props, "diaphragm_map")


def register():
    bpy.types.DATA_PT_camera.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.DATA_PT_camera_display.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.CAMERA_MT_presets.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.DATA_PT_lens.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.DATA_PT_custom_props_camera.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.DATA_PT_context_camera.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.utils.register_class(AppleseedCameraDoF)


def unregister():
    bpy.utils.unregister_class(AppleseedCameraDoF)
