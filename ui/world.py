#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 Jonathan Dent, The appleseedhq Organization
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


class ASWORLD_PT_world(bpy.types.Panel):
    bl_label = "Environment"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_context = "world"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        if renderer.engine == 'APPLESEED_RENDER':
            return context.scene.world is not None
        return False

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_sky_props = scene.world.appleseed_sky

        layout.prop(asr_sky_props, "env_type", text="Type")

        if asr_sky_props.env_type == "sunsky":
            layout.prop(asr_sky_props, "sun_model", text="Sky Model")
            layout.prop(asr_sky_props, "sun_theta", text="Sun Theta Angle")
            layout.prop(asr_sky_props, "sun_phi", text="Sun Phi Angle")
            layout.prop(asr_sky_props, "turbidity", text="Turbidity")
            layout.prop(asr_sky_props, "turbidity_multiplier", text="Turbidity Multiplier")
            layout.prop(asr_sky_props, "luminance_multiplier", text="Luminance Multiplier")
            layout.prop(asr_sky_props, "luminance_gamma", text="Luminance Gamma")
            layout.prop(asr_sky_props, "saturation_multiplier", text="Saturation Multiplier")
            layout.prop(asr_sky_props, "horizon_shift", text="Horizon Shift")

            if asr_sky_props.sun_model == "hosek_environment_edf":
                layout.prop(asr_sky_props, "ground_albedo", text="Ground Albedo")

        elif asr_sky_props.env_type == "gradient":
            layout.prop(asr_sky_props, "horizon_color", text="Horizon Radiance")
            layout.prop(asr_sky_props, "zenith_color", text="Zenith Radiance")

        elif asr_sky_props.env_type == "constant":
            layout.prop(asr_sky_props, "horizon_color", text="Radiance")

        elif asr_sky_props.env_type == "constant_hemisphere":
            layout.prop(asr_sky_props, "zenith_color", text="Upper Radiance")
            layout.prop(asr_sky_props, "horizon_color", text="Lower Radiance")

        elif asr_sky_props.env_type == "mirrorball_map":
            col = layout.column(align=True)
            col.template_ID(asr_sky_props, "env_tex", open="image.open")
            if asr_sky_props.env_tex is not None:
                as_rad_tex = asr_sky_props.env_tex
                col.prop(as_rad_tex.appleseed, "as_color_space", text="Color Space")
                col.prop(as_rad_tex.appleseed, "as_wrap_mode", text="Wrap Mode")
                col.prop(as_rad_tex.appleseed, "as_alpha_mode", text="Alpha Mode")
            col.prop(asr_sky_props, "env_tex_mult", text="Radiance Multiplier")

            col = layout.column()
            col.prop(asr_sky_props, "env_exposure", text="Exposure")
            col.prop(asr_sky_props, "env_exposure_multiplier", text="Exposure Multiplier")

        elif asr_sky_props.env_type == "latlong_map":
            col = layout.column()
            col.template_ID(asr_sky_props, "env_tex", open="image.open")
            if asr_sky_props.env_tex is not None:
                as_rad_tex = asr_sky_props.env_tex
                col.prop(as_rad_tex.appleseed, "as_color_space", text="Color Space")
                col.prop(as_rad_tex.appleseed, "as_wrap_mode", text="Wrap Mode")
                col.prop(as_rad_tex.appleseed, "as_alpha_mode", text="Alpha Mode")
            col.prop(asr_sky_props, "env_tex_mult", text="Radiance Multiplier")

            col = layout.column()
            col.prop(asr_sky_props, "env_exposure", text="Exposure")
            col.prop(asr_sky_props, "env_exposure_multiplier", text="Exposure Multiplier")

            col = layout.column()
            col.prop(asr_sky_props, "horizontal_shift", text="Horizontal Shift")
            col.prop(asr_sky_props, "vertical_shift", text="Vertical Shift")

        layout.prop(asr_sky_props, "env_alpha", text="Alpha")


class ASSSS_UL_sss_props(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        sss_set = item.name
        if 'DEFAULT' in self.layout_type:
            layout.label(text=sss_set, translate=False, icon_value=icon)


class ASWORLD_PT_sss_sets(bpy.types.Panel):
    bl_label = 'SSS Sets'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        world = scene.appleseed_sss_sets

        row = layout.row()
        row.template_list("ASSSS_UL_sss_props", "", world,
                          "sss_sets", world, "sss_sets_index", rows=1, maxrows=16, type="DEFAULT")

        row = layout.row(align=True)
        row.operator("appleseed.add_sss_set", text="Add Set", icon="ADD")
        row.operator("appleseed.remove_sss_set", text="Remove Set", icon="REMOVE")

        if world.sss_sets:
            current_set = world.sss_sets[world.sss_sets_index]
            layout.prop(current_set, "name", text="SSS Set Name")


class ASTEXTURE_UL_texture_slots(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        texture = item.name.name
        if 'DEFAULT' in self.layout_type:
            layout.label(text=texture, translate=False, icon_value=icon)


class ASTEXTURE_PT_texture_converter(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "world"
    bl_label = "Texture Converter"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        textures = asr_scene_props.textures

        row = layout.row()
        row.template_list("ASTEXTURE_UL_texture_slots", "", asr_scene_props,
                          "textures", asr_scene_props, "textures_index", rows=1, maxrows=16, type="DEFAULT")

        col = layout.column(align=True)

        row = col.row(align=True)
        row.operator("appleseed.add_texture", text="Add Texture", icon="ADD")
        row.operator("appleseed.remove_texture", text="Remove Texture", icon="REMOVE")
        row = col.row(align=True)
        row.operator("appleseed.refresh_textures", text="Refresh", icon='FILE_REFRESH')
        row.operator("appleseed.convert_textures", text="Convert", icon='PLAY')

        layout.prop(asr_scene_props, "sub_textures", text="Use Converted Textures", toggle=True)
        col = layout.column(align=True)
        col.prop(asr_scene_props, "tex_output_use_cust_dir", text="Use Custom Output Directory", toggle=True)
        row = col.row(align=True)
        row.enabled = asr_scene_props.tex_output_use_cust_dir
        row.prop(asr_scene_props, "tex_output_dir", text="")

        if textures:
            current_set = textures[asr_scene_props.textures_index]
            col = layout.column(align=True)
            col.prop_search(current_set, "name", bpy.data, "images", text="Texture")
            col.prop(current_set, "input_space", text="Color Space")
            col.prop(current_set, "output_depth", text="Depth")
            col.prop(current_set, "command_string", text="Command")


classes = (
    ASWORLD_PT_world,
    ASSSS_UL_sss_props,
    ASWORLD_PT_sss_sets,
    ASTEXTURE_UL_texture_slots,
    ASTEXTURE_PT_texture_converter
)


def register():
    for cls in classes:
        util.safe_register_class(cls)


def unregister():
    for cls in reversed(classes):
        util.safe_unregister_class(cls)
