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


class AppleseedCameraLens(bpy.types.Panel):
    bl_label = "Lens"
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

        cam = context.camera
        scene = context.scene
        asr_cam_props = scene.camera.data.appleseed

        layout.row().prop(cam, "type", expand=True)

        split = layout.split()

        col = split.column()
        if cam.type == 'PERSP':
            row = col.row()
            if cam.lens_unit == 'MILLIMETERS':
                row.prop(cam, "lens")
            elif cam.lens_unit == 'FOV':
                row.prop(cam, "angle")
            row.prop(cam, "lens_unit", text="")

        elif cam.type == 'ORTHO':
            row = col.row()
            row.prop(cam, "ortho_scale")

        elif cam.type == "PANO":
            row = col.row()
            row.prop(asr_cam_props, "fisheye_projection_type", text="Fisheye Projection")
            row = col.row()
            if cam.lens_unit == 'MILLIMETERS':
                row.prop(cam, "lens")
            elif cam.lens_unit == 'FOV':
                row.prop(cam, "angle")
            row.prop(cam, "lens_unit", text="")

        split = layout.split()

        col = split.column(align=True)
        col.label(text="Shift:")
        col.prop(cam, "shift_x", text="X")
        col.prop(cam, "shift_y", text="Y")

        col = split.column(align=True)
        col.label(text="Clipping:")
        col.prop(asr_cam_props, "near_z", text="Start")
        col.prop(cam, "clip_end", text="End")


class AppleseedCameraDoF(bpy.types.Panel):
    bl_label = "Depth of Field"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        is_context = renderer.engine == 'APPLESEED_RENDER' and context.active_object.type == 'CAMERA'
        is_model = context.active_object.data.type == 'PERSP' or (context.active_object.data.type == 'PANO' and context.active_object.data.appleseed.fisheye_projection_type is not 'none')
        return  is_context and is_model

    def draw_header(self, context):
        header = self.layout
        scene = context.scene
        asr_cam_props = scene.camera.data.appleseed
        header.prop(asr_cam_props, "enable_dof", text="")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_cam_props = scene.camera.data.appleseed

        layout.active = asr_cam_props.enable_dof
        layout.prop(asr_cam_props, "enable_autofocus", text="Enable Autofocus")
        col = layout.column()
        col.active = not context.active_object.data.appleseed.enable_autofocus
        row = col.row()
        row.active = context.active_object.data.dof_object is None
        row.prop(context.active_object.data, "dof_distance", text="Focal Distance")
        row = col.row()
        row.prop(context.active_object.data, "dof_object", text='Focus on Object')
        layout.prop(asr_cam_props, "f_number", text="F-Number")
        layout.prop(asr_cam_props, "diaphragm_blades", text="Blades")
        layout.prop(asr_cam_props, "diaphragm_angle", text="Tilt Angle")
        layout.prop(asr_cam_props, "diaphragm_map", text="Aperture Shape")
        row = layout.row()
        row.enabled = asr_cam_props.diaphragm_map != ""
        row.prop(asr_cam_props, "diaphragm_map_colorspace", text="Color Space")


def register():

    util.safe_register_class(AppleseedCameraLens)
    util.safe_register_class(AppleseedCameraDoF)


def unregister():
    util.safe_unregister_class(AppleseedCameraDoF)
    util.safe_unregister_class(AppleseedCameraLens)
