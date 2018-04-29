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

        rd = context.scene.render
        scene = context.scene
        rd = scene.render

        row = layout.row(align=True)
        row.operator("render.render", text="Render", icon='RENDER_STILL')
        row.operator("render.render", text="Animation", icon='RENDER_ANIMATION').animation = True

        row = layout.row(align=True)
        row.operator("appleseed.export_scene", text="Export Frame")
        row.operator("appleseed.export_anim_scene", text="Export Animation")

        split = layout.split(percentage=0.33)

        split.label(text="Display:")
        row = split.row(align=True)
        row.prop(rd, "display_mode", text="")
        row.prop(rd, "use_lock_interface", icon_only=True)


class AppleseedRenderSettingsPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "General"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        split = layout.split()
        col = split.column()
        col.prop(asr_scene_props, "threads_auto", text="Auto Threads")
        split = split.split()
        col = split.column()
        col.enabled = not asr_scene_props.threads_auto
        col.prop(asr_scene_props, "threads", text="Threads")

        row = layout.row()
        row.prop(asr_scene_props, "generate_mesh_files", text="Export Geometry")
        if asr_scene_props.generate_mesh_files:
            row.prop(asr_scene_props, "export_mode", text="")
            # layout.prop(asr_scene_props, "export_hair", text="Export Hair")
        row = layout.row()
        row.prop(asr_scene_props, "clean_cache", text="Delete Cache")

        layout.prop(asr_scene_props, "tile_ordering", text="Tile Ordering")


class AppleseedRenderStampPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Render Stamp"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        header = self.layout
        asr_scene_props = context.scene.appleseed
        header.prop(asr_scene_props, "enable_render_stamp", text="")

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed

        layout.active = asr_scene_props.enable_render_stamp
        layout.prop(asr_scene_props, "render_stamp", text="Stamp Text")
        layout.prop(asr_scene_props, "render_stamp_patterns", text="Stamp Type")


class AppleseedDenoiserPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Denoiser"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed

        layout.prop(asr_scene_props, "denoise_mode")
        if asr_scene_props.denoise_mode == 'write_outputs':
            layout.prop(asr_scene_props, "denoise_output_file_name", text="Output File Name")
        col = layout.column(align=True)
        col.active = asr_scene_props.denoise_mode != 'off'
        col.prop(asr_scene_props, "prefilter_spikes", text="Prefilter Spikes", toggle=True)
        col.prop(asr_scene_props, "spike_threshold", text="Spike Threshold")
        col.prop(asr_scene_props, "patch_distance_threshold", text="Patch Distance")
        col.prop(asr_scene_props, "denoise_scales", text="Denoise Scales")


class AppleseedSamplingPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Sampling"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        row = layout.row(align=True)
        row.label("Tile Size:")
        row.prop(asr_scene_props, "tile_width", text="Width")
        row.prop(asr_scene_props, "tile_height", text="Height")

        row = layout.row(align=True)
        layout.prop(asr_scene_props, "pixel_filter", text="Filter")
        layout.prop(asr_scene_props, "pixel_filter_size", text="Filter Size")

        layout.separator()
        layout.prop(asr_scene_props, "pixel_sampler", text="Pixel Sampler")
        layout.prop(asr_scene_props, "renderer_passes", text="Passes")

        if asr_scene_props.pixel_sampler == 'adaptive':
            row = layout.row(align=True)
            row.prop(asr_scene_props, "sampler_min_samples", text="Min Samples")
            row.prop(asr_scene_props, "sampler_max_samples", text="Max Samples")
        else:
            layout.prop(asr_scene_props, "sampler_max_samples", text="Samples")
            split = layout.split()
            row = split.row()
            row.enabled = asr_scene_props.sampler_max_samples == 1
            row.prop(asr_scene_props, "force_aa", text="Force Anti-Aliasing")
            split = split.split()
            row = split.row()
            row.prop(asr_scene_props, "decorrelate_pixels", text="Decorrelate Pixels")


class AppleseedLightingPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Lighting"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column()
        col.prop(asr_scene_props, "lighting_engine", text="Engine")
        col.prop(asr_scene_props, "light_sampler", text="Light Sampler")
        if asr_scene_props.lighting_engine == 'pt':
            layout.separator()
            col = layout.column()
            col.prop(asr_scene_props, "record_light_paths", text="Record Light Paths")
        split = layout.split()

        # Path tracing UI
        if asr_scene_props.lighting_engine == 'pt':
            if asr_scene_props.pixel_sampler == 'adaptive':
                row = layout.row()
                row.prop(asr_scene_props, "adaptive_sampler_enable_diagnostics", text="Diagnostics")
                row.prop(asr_scene_props, "adaptive_sampler_quality", text="Quality")
            layout.prop(asr_scene_props, "next_event_estimation", text="Next Event Estimation")
            if asr_scene_props.next_event_estimation:
                row = layout.row()
                row.prop(asr_scene_props, "enable_dl", text="Direct Lighting")
                if asr_scene_props.enable_dl:
                    row.prop(asr_scene_props, "dl_light_samples", text="DL Samples")
                    row = layout.row()
                    row.prop(asr_scene_props, "dl_low_light_threshold", text="Low Light Threshold")
                row = layout.row()
                row.prop(asr_scene_props, "enable_ibl", text="Image-Based Lighting")
                if asr_scene_props.enable_ibl:
                    row.prop(asr_scene_props, "ibl_env_samples", text="IBL Samples")

            layout.prop(asr_scene_props, "enable_caustics", text="Caustics")

            layout.label("Bounces")

            split = layout.split()
            col = split.column()
            col.prop(asr_scene_props, "max_bounces_unlimited", text="Unlimited")
            split = split.split()
            col = split.column()
            col.enabled = not asr_scene_props.max_bounces_unlimited
            col.prop(asr_scene_props, "max_bounces", text="Global")

            split = layout.split()
            col = split.column()
            col.prop(asr_scene_props, "max_diffuse_bounces_unlimited", text="Unlimited")
            split = split.split()
            col = split.column()
            col.enabled = not asr_scene_props.max_diffuse_bounces_unlimited
            col.prop(asr_scene_props, "max_diffuse_bounces", text="Diffuse")

            split = layout.split()
            col = split.column()
            col.prop(asr_scene_props, "max_glossy_brdf_bounces_unlimited", text="Unlimited")
            split = split.split()
            col = split.column()
            col.enabled = not asr_scene_props.max_glossy_brdf_bounces_unlimited
            col.prop(asr_scene_props, "max_glossy_brdf_bounces", text="Glossy")

            split = layout.split()
            col = split.column()
            col.prop(asr_scene_props, "max_specular_bounces_unlimited", text="Unlimited")
            split = split.split()
            col = split.column()
            col.enabled = not asr_scene_props.max_specular_bounces_unlimited
            col.prop(asr_scene_props, "max_specular_bounces", text="Specular")

            split = layout.split()
            col = split.column()
            col.prop(asr_scene_props, "max_volume_bounces_unlimited", text="Unlimited")
            split = split.split()
            col = split.column()
            col.enabled = not asr_scene_props.max_volume_bounces_unlimited
            col.prop(asr_scene_props, "max_volume_bounces", text="Volume")

            split = layout.split()
            col = split.column()
            col.prop(asr_scene_props, "max_ray_intensity_unlimited", text="Unlimited")
            split = split.split()
            col = split.column()
            col.enabled = not asr_scene_props.max_ray_intensity_unlimited
            col.prop(asr_scene_props, "max_ray_intensity", text="Max Ray Intensity")
            layout.prop(asr_scene_props, "rr_start", text="Russian Roulette Start Bounce")

            layout.separator()

            layout.prop(asr_scene_props, "volume_distance_samples", text="Volume Distance Samples")
            layout.prop(asr_scene_props, "optimize_for_lights_outside_volumes", text="Optimize for Lights Outside Volumes")

            layout.separator()

            layout.prop(asr_scene_props, "light_mats_radiance_multiplier", text="Mesh Light Multiplier")
            layout.prop(asr_scene_props, "export_emitting_obj_as_lights", text="Export Mesh Lights")

        # SPPM UI
        elif asr_scene_props.lighting_engine == 'sppm':
            layout.prop(asr_scene_props, "sppm_dl_mode", text="Direct Lighting")
            layout.prop(asr_scene_props, "enable_ibl", text="Image-Based Lighting")
            layout.prop(asr_scene_props, "enable_caustics", text="Caustics")

            layout.label("Photon Tracing")

            layout.prop(asr_scene_props, "sppm_photon_max_length", text="Max Bounces")
            layout.prop(asr_scene_props, "sppm_photon_rr_start", text="Russian Roulette Start Bounce")
            layout.prop(asr_scene_props, "sppm_light_photons", text="Light Photons")
            layout.prop(asr_scene_props, "sppm_env_photons", text="Environment Photons")

            layout.label("Radiance Estimation")

            layout.prop(asr_scene_props, "sppm_pt_max_length", text="Max Bounces")
            layout.prop(asr_scene_props, "sppm_pt_rr_start", text="Russian Roulette Start Bounce")
            layout.prop(asr_scene_props, "sppm_initial_radius", text="Initial Radius")
            layout.prop(asr_scene_props, "sppm_max_per_estimate", text="Max Photons")
            layout.prop(asr_scene_props, "sppm_alpha", text="Alpha")

            layout.separator()

            layout.prop(asr_scene_props, "light_mats_radiance_multiplier", text="Mesh Light Multiplier")
            layout.prop(asr_scene_props, "export_emitting_obj_as_lights", text="Export Mesh Lights")


class AppleseedMotionBlurPanel(bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Motion Blur"

    def draw_header(self, context):
        header = self.layout
        asr_scene_props = context.scene.appleseed
        header.prop(asr_scene_props, "enable_motion_blur", text="")

    def draw(self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed

        layout.active = asr_scene_props.enable_motion_blur

        layout.prop(asr_scene_props, "shutter_open", text="Shutter Open")
        layout.prop(asr_scene_props, "shutter_close", text="Shutter Close")

        row = layout.row(align=True)
        row.prop(asr_scene_props, "enable_camera_blur", text="Camera Blur")
        row.prop(asr_scene_props, "enable_object_blur", text="Object Blur")
        layout.prop(asr_scene_props, "enable_deformation_blur", text="Deformation Blur")


def register():
    bpy.types.RENDER_PT_dimensions.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.RENDER_PT_output.COMPAT_ENGINES.add('APPLESEED_RENDER')
    util.safe_register_class(AppleseedRender)
    util.safe_register_class(AppleseedRenderStampPanel)
    util.safe_register_class(AppleseedRenderSettingsPanel)
    util.safe_register_class(AppleseedDenoiserPanel)
    util.safe_register_class(AppleseedSamplingPanel)
    util.safe_register_class(AppleseedLightingPanel)
    util.safe_register_class(AppleseedMotionBlurPanel)


def unregister():
    util.safe_unregister_class(AppleseedMotionBlurPanel)
    util.safe_unregister_class(AppleseedLightingPanel)
    util.safe_unregister_class(AppleseedSamplingPanel)
    util.safe_unregister_class(AppleseedDenoiserPanel)
    util.safe_unregister_class(AppleseedRenderSettingsPanel)
    util.safe_unregister_class(AppleseedRenderStampPanel)
    util.safe_unregister_class(AppleseedRender)
    bpy.types.RENDER_PT_dimensions.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.RENDER_PT_output.COMPAT_ENGINES.remove('APPLESEED_RENDER')
