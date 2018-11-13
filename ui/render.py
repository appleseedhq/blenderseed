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

from .. import util


class AppleseedRenderPanelBase(object):
    bl_context = "render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'


class AppleseedRender(bpy.types.Panel, AppleseedRenderPanelBase):
    bl_label = "Render"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        rd = scene.render
        asr_scene_data = scene.appleseed

        layout.prop(asr_scene_data, "scene_export_mode", text="Rendering Mode")

        if asr_scene_data.scene_export_mode in ('render', 'export_render'):
            row = layout.row(align=True)
            row.operator("render.render", text="Render", icon='RENDER_STILL')
            row.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True

            split = layout.split(percentage=0.33)
            split.label(text="Display:")
            row = split.row(align=True)
            row.prop(rd, "display_mode", text="")
            row.prop(rd, "use_lock_interface", icon_only=True)
        else:
            row = layout.row(align=True)
            row.prop(asr_scene_data, "export_selected", text="Export Selected Objects Only", toggle=True)
            row = layout.row(align=True)
            row.operator("appleseed.export_scene", text="Export")


class AppleseedRenderSettingsPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "System"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column(align=True)
        col.prop(asr_scene_props, "threads_auto", text="Auto Threads", toggle=True)
        row = col.row(align=True)
        row.enabled = not asr_scene_props.threads_auto
        row.prop(asr_scene_props, "threads", text="Threads")

        layout.separator()

        box = layout.box()
        box.label(text="Render Logging")
        box.prop(asr_scene_props, "log_level", text="")

        layout.separator()

        col = layout.column(align=True)
        col.prop(asr_scene_props, "shading_override", text="Override Shading", toggle=True)
        row = col.row(align=True)
        row.enabled = asr_scene_props.shading_override
        row.prop(asr_scene_props, "override_mode", text="")

        box = layout.box()
        box.label(text="Texture Cache")
        box.prop(asr_scene_props, "tex_cache", text="Texture Cache Size")

        # Here be dragons
        box = layout.box()
        box.label(text="Experimental Features")
        box.prop(asr_scene_props, "use_embree", text="Use Embree", toggle=True)
        box.prop(asr_scene_props, "use_cpp_export", text="Use C++ Mesh Export", toggle=True)
        box.prop(asr_scene_props, "skip_triangulation", text="Skip Mesh Triangulation")


class AppleseedDenoiserPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Denoising"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed

        layout.prop(asr_scene_props, "denoise_mode")
        if asr_scene_props.denoise_mode == 'write_outputs':
            layout.prop(asr_scene_props, "denoise_output_dir", text="Output Directory")
        col = layout.column(align=True)
        col.active = asr_scene_props.denoise_mode != 'off'
        col.prop(asr_scene_props, "random_pixel_order", text="Random Pixe Order", toggle=True)
        col.prop(asr_scene_props, "skip_denoised", text="Skip Denoised Pixels", toggle=True)
        col.prop(asr_scene_props, "prefilter_spikes", text="Prefilter Spikes", toggle=True)
        col.prop(asr_scene_props, "mark_invalid_pixels", text="Mark Invalid Pixels", toggle=True)
        col.prop(asr_scene_props, "spike_threshold", text="Spike Threshold")
        col.prop(asr_scene_props, "patch_distance_threshold", text="Patch Distance")
        col.prop(asr_scene_props, "denoise_scales", text="Denoise Scales")


class AppleseedSamplingPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Image Sampling"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        layout.prop(asr_scene_props, "pixel_sampler", text="Sampling", expand=True)

        col = layout.column(align=True)
        col.prop(asr_scene_props, "renderer_passes", text="Passes")

        if asr_scene_props.pixel_sampler == 'adaptive':
            row = col.row(align=True)
            row.prop(asr_scene_props, "adaptive_batch_size", text="Batch Size")
            row.prop(asr_scene_props, "adaptive_max_samples", text="Max Samples")
            row = col.row(align=True)
            row.prop(asr_scene_props, "adaptive_noise_threshold", text="Noise Threshold")
            row.prop(asr_scene_props, "adaptive_min_samples", text="Min Samples")
        else:
            col.prop(asr_scene_props, "samples", text="Samples")

        box = layout.box()
        box.label(text="Interactive Render:")
        box.prop(asr_scene_props, "interactive_max_fps", text="FPS")
        box.prop(asr_scene_props, "interactive_max_samples", text="Max Samples")

        box = layout.box()
        box.label(text="Tile Pattern:")
        box.prop(asr_scene_props, "tile_ordering", text="")
        box.prop(asr_scene_props, "tile_size", text="Tile Size")

        box = layout.box()
        box.label(text="Pixel Filter:")
        box.prop(asr_scene_props, "pixel_filter", text="")
        box.prop(asr_scene_props, "pixel_filter_size", text="Filter Size")


class AppleseedLightingPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Lighting"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column()
        row = col.row()
        row.prop(asr_scene_props, "lighting_engine", text="Engine", expand=True)
        if asr_scene_props.lighting_engine == 'pt':
            layout.separator()
            col = layout.column()
            col.prop(asr_scene_props, "record_light_paths", text="Record Light Paths")
            col = layout.column(align=True)
            row = col.row(align=True)
            row.prop(asr_scene_props, "enable_dl", text="Directly Sample Lights", toggle=True)
            row.prop(asr_scene_props, "dl_light_samples", text="Samples")
            row = col.row()
            row.enabled = asr_scene_props.enable_dl
            row.prop(asr_scene_props, "dl_low_light_threshold", text="Low Light Threshold")
            col.separator()
            col = layout.column()
            col.enabled = asr_scene_props.next_event_estimation
            row = col.row(align=True)
            row.prop(asr_scene_props, "enable_ibl", text="Environment Emits Light", toggle=True)
            row.prop(asr_scene_props, "ibl_env_samples", text="Samples")
            layout.separator()
            layout.prop(asr_scene_props, "enable_caustics", text="Caustics", toggle=True)
            layout.prop(asr_scene_props, "enable_clamp_roughness", text="Clamp Roughness", toggle=True)

            layout.separator()
            layout.label("Bounces:")

            split = layout.split(percentage=0.25, align=True)
            split.label(text="Max")
            split = split.split(percentage=0.33)
            row = split.row()
            row.prop(asr_scene_props, "max_bounces_unlimited", text="Unlimited", toggle=True)
            row = split.row()
            row.enabled = not asr_scene_props.max_bounces_unlimited
            row.prop(asr_scene_props, "max_bounces", text="")

            split = layout.split(percentage=0.25, align=True)
            split.label(text="Diffuse")
            split = split.split(percentage=0.33)
            row = split.row()
            row.prop(asr_scene_props, "max_diffuse_bounces_unlimited", text="Unlimited", toggle=True)
            row = split.row()
            row.enabled = not asr_scene_props.max_diffuse_bounces_unlimited
            row.prop(asr_scene_props, "max_diffuse_bounces", text="")

            split = layout.split(percentage=0.25, align=True)
            split.label(text="Glossy")
            split = split.split(percentage=0.33)
            row = split.row()
            row.prop(asr_scene_props, "max_glossy_brdf_bounces_unlimited", text="Unlimited", toggle=True)
            row = split.row()
            row.enabled = not asr_scene_props.max_glossy_brdf_bounces_unlimited
            row.prop(asr_scene_props, "max_glossy_brdf_bounces", text="")

            split = layout.split(percentage=0.25, align=True)
            split.label(text="Specular")
            split = split.split(percentage=0.33)
            row = split.row()
            row.prop(asr_scene_props, "max_specular_bounces_unlimited", text="Unlimited", toggle=True)
            row = split.row()
            row.enabled = not asr_scene_props.max_specular_bounces_unlimited
            row.prop(asr_scene_props, "max_specular_bounces", text="")

            split = layout.split(percentage=0.25, align=True)
            split.label(text="Volume")
            split = split.split(percentage=0.33)
            row = split.row()
            row.prop(asr_scene_props, "max_volume_bounces_unlimited", text="Unlimited", toggle=True)
            row = split.row()
            row.enabled = not asr_scene_props.max_volume_bounces_unlimited
            row.prop(asr_scene_props, "max_volume_bounces", text="")

            layout.separator()

            split = layout.split(percentage=0.25, align=True)
            col = split.column()
            col.label(text="Max Ray Intensity")
            split = split.split(percentage=0.33)
            col = split.column()
            col.prop(asr_scene_props, "max_ray_intensity_unlimited", text="Unlimited", toggle=True)
            split = split.split(percentage=1.0, align=True)
            col = split.column()
            col.enabled = not asr_scene_props.max_ray_intensity_unlimited
            col.prop(asr_scene_props, "max_ray_intensity", text="")

            layout.separator()
            layout.prop(asr_scene_props, "rr_start", text="Russian Roulette Start Bounce")

            layout.separator()
            col = layout.column(align=True)
            col.prop(asr_scene_props, "optimize_for_lights_outside_volumes", text="Optimize for Lights Outside Volumes", toggle=True)
            col.prop(asr_scene_props, "volume_distance_samples", text="Volume Distance Samples")

        # SPPM UI
        elif asr_scene_props.lighting_engine == 'sppm':
            layout.separator()
            layout.prop(asr_scene_props, "sppm_dl_mode", text="Direct Lighting")
            row = layout.row(align=True)
            row.prop(asr_scene_props, "enable_ibl", text="Environment Emits Light", toggle=True)
            row.prop(asr_scene_props, "ibl_env_samples", text="Samples")
            layout.prop(asr_scene_props, "enable_caustics", text="Caustics", toggle=True)

            layout.label("Photon Tracing")

            col = layout.column(align=True)
            col.prop(asr_scene_props, "sppm_photon_max_length", text="Max Bounces")
            col.prop(asr_scene_props, "sppm_photon_rr_start", text="Russian Roulette Start Bounce")
            col.prop(asr_scene_props, "sppm_light_photons", text="Light Photons")
            col.prop(asr_scene_props, "sppm_env_photons", text="Environment Photons")

            layout.label("Radiance Estimation")

            col = layout.column(align=True)
            col.prop(asr_scene_props, "sppm_pt_max_length", text="Max Bounces")
            col.prop(asr_scene_props, "sppm_pt_rr_start", text="Russian Roulette Start Bounce")
            col.prop(asr_scene_props, "sppm_initial_radius", text="Initial Radius")
            col.prop(asr_scene_props, "sppm_max_per_estimate", text="Max Photons")
            col.prop(asr_scene_props, "sppm_alpha", text="Alpha")


class AppleseedPostProcessingStagesSlots(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        stage = item.name
        if 'DEFAULT' in self.layout_type:
            layout.label(text=stage, translate=False, icon_value=icon)


class AppleseedPostProcessingStagesPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "appleseed Post Processing"

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed
        pp_stages = asr_scene_props.post_processing_stages

        row = layout.row()
        row.template_list("AppleseedPostProcessingStagesSlots", "", asr_scene_props,
                          "post_processing_stages", asr_scene_props, "post_processing_stages_index",
                          rows=1, maxrows=16, type="DEFAULT")

        row = layout.row(align=True)
        row.operator("appleseed.add_pp_stage", text="Add Stage", icon="ZOOMIN")
        row.operator("appleseed.remove_pp_stage", text="Remove Stage", icon="ZOOMOUT")

        if pp_stages:
            current_stage = pp_stages[asr_scene_props.post_processing_stages_index]
            layout.prop(current_stage, "model", text="Model", expand=True)
            if current_stage.model == 'render_stamp_post_processing_stage':
                layout.label(text="Render Stamp")
                layout.prop(current_stage, "render_stamp", text="")
                layout.prop_menu_enum(current_stage, "render_stamp_patterns", text="Add Stamp Data Block")
            else:
                layout.label(text="Color Map")
                layout.prop(current_stage, "color_map", text="Mode")
                row = layout.row()
                row.enabled = current_stage.color_map == 'custom'
                row.prop(current_stage, "color_map_file_path", text="Custom Map")

                col = layout.column(align=True)
                col.prop(current_stage, "add_legend_bar", text="Add Legends Bar", toggle=True)
                row = col.row(align=True)
                row.enabled = current_stage.add_legend_bar
                row.prop(current_stage, "legend_bar_ticks", text="Ticks")

                col = layout.column(align=True)
                col.prop(current_stage, "auto_range", text="Auto Range", toggle=True)
                row = col.row(align=True)
                row.enabled = not current_stage.auto_range
                row.prop(current_stage, "range_min", text="Min Range")
                row = col.row(align=True)
                row.enabled = not current_stage.auto_range
                row.prop(current_stage, "range_max", text="Max Range")

                col = layout.column(align=True)
                col.prop(current_stage, "render_isolines", text="Render Isolines", toggle=True)
                col.prop(current_stage, "line_thickness", text="Line Thickness")


class AppleseedMotionBlurPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Motion Blur"

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed

        col = layout.column(align=True)
        col.prop(asr_scene_props, "shutter_open", text="Shutter Open Begin")
        col.prop(asr_scene_props, "shutter_open_end_time", text="Shutter Open End")
        col = layout.column(align=True)
        col.prop(asr_scene_props, "shutter_close_begin_time", text="Shutter Close Begin")
        col.prop(asr_scene_props, "shutter_close", text="Shutter Close End")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(asr_scene_props, "enable_camera_blur", text="Camera Blur", toggle=True)
        row.prop(asr_scene_props, "camera_blur_samples", text="Samples")
        row = col.row(align=True)
        row.prop(asr_scene_props, "enable_object_blur", text="Object Blur", toggle=True)
        row.prop(asr_scene_props, "object_blur_samples", text="Samples")
        row = col.row(align=True)
        row.prop(asr_scene_props, "enable_deformation_blur", text="Deformation Blur", toggle=True)
        row.prop(asr_scene_props, "deformation_blur_samples", text="Samples")


class AppleseedPostProcessing(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Blender Post Processing"

    def draw(self, context):
        layout = self.layout

        rd = context.scene.render

        col = layout.column()
        col.prop(rd, "use_compositing")
        col.prop(rd, "use_sequencer")


def register():
    bpy.types.RENDER_PT_dimensions.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.RENDER_PT_output.COMPAT_ENGINES.add('APPLESEED_RENDER')
    util.safe_register_class(AppleseedRender)
    util.safe_register_class(AppleseedRenderSettingsPanel)
    util.safe_register_class(AppleseedDenoiserPanel)
    util.safe_register_class(AppleseedSamplingPanel)
    util.safe_register_class(AppleseedLightingPanel)
    util.safe_register_class(AppleseedPostProcessingStagesSlots)
    util.safe_register_class(AppleseedPostProcessingStagesPanel)
    util.safe_register_class(AppleseedMotionBlurPanel)
    util.safe_register_class(AppleseedPostProcessing)


def unregister():
    util.safe_unregister_class(AppleseedPostProcessing)
    util.safe_unregister_class(AppleseedMotionBlurPanel)
    util.safe_unregister_class(AppleseedPostProcessingStagesPanel)
    util.safe_unregister_class(AppleseedPostProcessingStagesSlots)
    util.safe_unregister_class(AppleseedLightingPanel)
    util.safe_unregister_class(AppleseedSamplingPanel)
    util.safe_unregister_class(AppleseedDenoiserPanel)
    util.safe_unregister_class(AppleseedRenderSettingsPanel)
    util.safe_unregister_class(AppleseedRender)
    bpy.types.RENDER_PT_dimensions.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.RENDER_PT_output.COMPAT_ENGINES.remove('APPLESEED_RENDER')
