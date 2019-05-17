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


class ASCAMERA_PT_lens(bpy.types.Panel):
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

        layout.use_property_split = True

        cam = context.camera

        asr_cam_props = cam.appleseed

        layout.row().prop(cam, "type")

        col = layout.column()
        if cam.type == 'PERSP':
            if cam.lens_unit == 'MILLIMETERS':
                col.prop(cam, "lens")
            elif cam.lens_unit == 'FOV':
                col.prop(cam, "angle")
            col.prop(cam, "lens_unit")

        elif cam.type == "PANO":
            col.prop(asr_cam_props, "fisheye_projection_type", text="Fisheye Projection")
            if cam.lens_unit == 'MILLIMETERS':
                col.prop(cam, "lens")
            elif cam.lens_unit == 'FOV':
                col.prop(cam, "angle")
            col.prop(cam, "lens_unit")

        elif cam.type == 'ORTHO':
            col.prop(cam, "ortho_scale")

        elif cam.type == "PANO":
            row = col.row()
            row.prop(asr_cam_props, "fisheye_projection_type", text="Fisheye Projection")
            row = col.row()
            if cam.lens_unit == 'MILLIMETERS':
                row.prop(cam, "lens")
            elif cam.lens_unit == 'FOV':
                row.prop(cam, "angle")
            row.prop(cam, "lens_unit", text="")


class ASCAMERA_PT_lens_shift(bpy.types.Panel):
    bl_parent_id = "ASCAMERA_PT_lens"
    bl_label = "Shift"
    bl_options = {'DEFAULT_CLOSED'}
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

        layout.use_property_split = True

        cam = context.camera

        col = layout.column(align=True)
        col.prop(cam, "shift_x", text="X")
        col.prop(cam, "shift_y", text="Y")


class ASCAMERA_PT_lens_clip(bpy.types.Panel):
    bl_parent_id = "ASCAMERA_PT_lens"
    bl_label = "Clip"
    bl_options = {'DEFAULT_CLOSED'}
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

        layout.use_property_split = True

        cam = context.camera
        scene = context.scene
        asr_cam_props = scene.camera.data.appleseed

        col = layout.column(align=True)
        col.prop(asr_cam_props, "near_z", text="Clip Start")
        col.prop(cam, "clip_end", text="End")


class ASCAMERA_PT_dof(bpy.types.Panel):
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
        layout.use_property_split = True
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
        layout.template_ID(asr_cam_props, "diaphragm_map", open="image.open")
        if asr_cam_props.diaphragm_map != None:
            as_diaphragm_map = asr_cam_props.diaphragm_map
            layout.prop(as_diaphragm_map.appleseed, "as_color_space", text="Color Space")
            layout.prop(as_diaphragm_map.appleseed, "as_wrap_mode", text="Wrap Mode")
            layout.prop(as_diaphragm_map.appleseed, "as_alpha_mode", text="Alpha Mode")


classes = (
    ASCAMERA_PT_dof,
    ASCAMERA_PT_lens,
    ASCAMERA_PT_lens_shift,
    ASCAMERA_PT_lens_clip
)


def register():
    for cls in classes:
        util.safe_register_class(cls)


def unregister():
    for cls in reversed(classes):
        util.safe_unregister_class(cls)
