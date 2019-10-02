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


class ASRENDER_PT_base(object):
    bl_context = "render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'


class ASRENDER_PT_export(bpy.types.Panel, ASRENDER_PT_base):
    bl_label = "Rendering Mode"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_scene_props = scene.appleseed

        layout.prop(asr_scene_props, "scene_export_mode", text="")
        # layout.operator("appleseed.export_scene", text="Export")
        if asr_scene_props.scene_export_mode == 'export_only':
            layout.prop(asr_scene_props, "export_path", text="Export Path")
            layout.prop(asr_scene_props, "export_selected", text="Only Export Selected Objects")


class ASRENDER_PT_settings(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "System"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column(align=True)
        row = col.row(align=True)
        row.enabled = not asr_scene_props.threads_auto
        row.prop(asr_scene_props, "threads", text="Threads")
        col.prop(asr_scene_props, "threads_auto", text="Auto Threads")

        layout.separator()

        col = layout.column(align=True)
        col.prop(asr_scene_props, "noise_seed", text="Noise Seed")
        col.prop(asr_scene_props, "per_frame_noise", text="Vary per Frame")

        layout.separator()

        layout.prop(asr_scene_props, "log_level", text="Render Log")

        layout.separator()

        layout.prop(asr_scene_props, "tex_cache", text="Tex Cache")

        # Here be dragons
        box = layout.box()
        box.label(text="Experimental Features")
        box.prop(asr_scene_props, "use_embree", text="Use Embree")


class ASRENDER_PT_shading_override(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Shading Override"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column(align=True)
        col.prop(asr_scene_props, "shading_override", text="Override Shading")
        row = col.row(align=True)
        row.enabled = asr_scene_props.shading_override
        row.prop(asr_scene_props, "override_mode", text="Mode")


class ASRENDER_PT_denoise(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Denoising"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        asr_scene_props = context.scene.appleseed

        layout.prop(asr_scene_props, "denoise_mode", text="Mode")
        if asr_scene_props.denoise_mode == 'write_outputs':
            layout.prop(asr_scene_props, "denoise_output_dir", text="Output Directory")
        col = layout.column(align=True)
        col.active = asr_scene_props.denoise_mode != 'off'
        col.prop(asr_scene_props, "spike_threshold", text="Spike Threshold")
        col.prop(asr_scene_props, "patch_distance_threshold", text="Patch Distance")
        col.prop(asr_scene_props, "denoise_scales", text="Denoise Scales")
        col.prop(asr_scene_props, "random_pixel_order", text="Random Pixe Order")
        col.prop(asr_scene_props, "skip_denoised", text="Skip Denoised Pixels")
        col.prop(asr_scene_props, "prefilter_spikes", text="Prefilter Spikes")
        col.prop(asr_scene_props, "mark_invalid_pixels", text="Mark Invalid Pixels")


class ASRENDER_PT_sampling(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Image Sampling"

    def draw(self, context):
        pass


class ASRENDER_PT_sampling_sampler(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Sampler"
    bl_parent_id = "ASRENDER_PT_sampling"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_scene_props = scene.appleseed

        layout.prop(asr_scene_props, "pixel_sampler", text="Sampler")

        col = layout.column(align=True)
        col.prop(asr_scene_props, "renderer_passes", text="Passes")

        if asr_scene_props.pixel_sampler == 'adaptive':
            col = layout.column(align=True)
            col.prop(asr_scene_props, "adaptive_batch_size", text="Batch Size")
            col.prop(asr_scene_props, "adaptive_max_samples", text="Max Samples")
            col = layout.column(align=True)
            col.prop(asr_scene_props, "adaptive_noise_threshold", text="Noise Threshold")
            col.prop(asr_scene_props, "adaptive_min_samples", text="Min Samples")
        elif asr_scene_props.pixel_sampler == 'uniform':
            col.prop(asr_scene_props, "samples", text="Samples")
        else:
            col = layout.column(align=True)
            col.prop(asr_scene_props, "texture_sampler_filepath", text="Texture Path")
            col = layout.column(align=True)
            col.prop(asr_scene_props, "adaptive_max_samples", text="Max Samples")
            col.prop(asr_scene_props, "adaptive_min_samples", text="Min Samples")


class ASRENDER_PT_sampling_interactive(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Interactive Rendering"
    bl_parent_id = "ASRENDER_PT_sampling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column(align=True)
        col.prop(asr_scene_props, "interactive_max_fps", text="FPS")
        col.prop(asr_scene_props, "interactive_max_samples", text="Max Samples")
        col.prop(asr_scene_props, "interactive_max_time", text="Max Time in Seconds")


class ASRENDER_PT_sampling_filter(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Filter"
    bl_parent_id = "ASRENDER_PT_sampling"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column(align=True)
        col.prop(asr_scene_props, "tile_ordering", text="Tile Order")
        col.prop(asr_scene_props, "tile_size", text="Size")

        layout.separator()

        col = layout.column(align=True)
        col.prop(asr_scene_props, "pixel_filter", text="Pixel Filter")
        col.prop(asr_scene_props, "pixel_filter_size", text="Size")


class ASRENDER_PT_lighting(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Lighting"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_scene_props = scene.appleseed

        layout.prop(asr_scene_props, "lighting_engine", text="Engine")


class ASRENDER_PT_lighting_pt(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Path Tracing"
    bl_parent_id = "ASRENDER_PT_lighting"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.scene.appleseed.lighting_engine == 'pt'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        layout.use_property_split = True

        col = layout.column()
        col.prop(asr_scene_props, "record_light_paths", text="Record Light Paths")

        layout.separator()

        col = layout.column(align=True)
        col.prop(asr_scene_props, "enable_dl", text="Directly Sample Lights")
        col = col.column(align=True)
        col.enabled = asr_scene_props.enable_dl
        col.prop(asr_scene_props, "enable_light_importance_sampling", text="Light Importance Sampling")
        col.prop(asr_scene_props, "dl_light_samples", text="Samples")
        col.prop(asr_scene_props, "dl_low_light_threshold", text="Low Light Threshold")

        layout.separator()
        col = layout.column(align=True)
        col.enabled = asr_scene_props.next_event_estimation
        col.prop(asr_scene_props, "enable_ibl", text="Environment Emits Light")
        col = col.column(align=True)
        col.enabled = asr_scene_props.enable_ibl
        col.prop(asr_scene_props, "ibl_env_samples", text="Samples")

        layout.separator()
        col = layout.column()
        col.prop(asr_scene_props, "enable_caustics", text="Caustics")
        col.prop(asr_scene_props, "enable_clamp_roughness", text="Clamp Roughness")

        col = layout.column(align=True)
        col.prop(asr_scene_props, "max_ray_intensity_unlimited", text="Max Ray Intensity Unlimited")
        col = col.column(align=True)
        col.enabled = not asr_scene_props.max_ray_intensity_unlimited
        col.prop(asr_scene_props, "max_ray_intensity", text="Max Ray Intensity")


class ASRENDER_PT_lighting_bounces(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Bounces"
    bl_parent_id = "ASRENDER_PT_lighting_pt"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        layout.use_property_split = True

        col = layout.column(align=True)
        col.prop(asr_scene_props, "max_bounces_unlimited", text="Max Bounce Unlimited")
        col.prop(asr_scene_props, "max_diffuse_bounces_unlimited", text="Diffuse Bounce Unlimited")
        col.prop(asr_scene_props, "max_glossy_brdf_bounces_unlimited", text="Glossy Bounce Unlimited")
        col.prop(asr_scene_props, "max_specular_bounces_unlimited", text="Specular Bounce Unlimited")
        col.prop(asr_scene_props, "max_volume_bounces_unlimited", text="Volume Bounce Unlimited")

        col = layout.column(align=True)
        col.enabled = not asr_scene_props.max_bounces_unlimited
        col.prop(asr_scene_props, "max_bounces", text="Max Bounces")

        col = layout.column(align=True)
        col.enabled = not asr_scene_props.max_diffuse_bounces_unlimited
        col.prop(asr_scene_props, "max_diffuse_bounces", text="Diffuse Bounces")

        col = layout.column(align=True)
        col.enabled = not asr_scene_props.max_glossy_brdf_bounces_unlimited
        col.prop(asr_scene_props, "max_glossy_brdf_bounces", text="Glossy Bounces")

        col = layout.column(align=True)
        col.enabled = not asr_scene_props.max_specular_bounces_unlimited
        col.prop(asr_scene_props, "max_specular_bounces", text="Specular Bounces")

        col = layout.column(align=True)
        col.enabled = not asr_scene_props.max_volume_bounces_unlimited
        col.prop(asr_scene_props, "max_volume_bounces", text="Volume Bounces")


class ASRENDER_PT_lighting_sppm(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "SPPM"
    bl_parent_id = "ASRENDER_PT_lighting"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.scene.appleseed.lighting_engine == 'sppm'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        layout.use_property_split = True

        layout.prop(asr_scene_props, "sppm_dl_mode", text="Direct Lighting")
        col = layout.column(align=True)
        col.enabled = asr_scene_props.next_event_estimation
        col.prop(asr_scene_props, "enable_ibl", text="Environment Emits Light")
        col = col.column(align=True)
        col.enabled = asr_scene_props.enable_ibl
        col.prop(asr_scene_props, "ibl_env_samples", text="Samples")
        layout.prop(asr_scene_props, "enable_caustics", text="Caustics")


class ASRENDER_PT_lighting_sppm_tracing(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Photon Tracing"
    bl_parent_id = "ASRENDER_PT_lighting_sppm"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        layout.use_property_split = True

        col = layout.column(align=True)
        col.prop(asr_scene_props, "sppm_photon_max_length", text="Max Bounces")
        col.prop(asr_scene_props, "sppm_photon_rr_start", text="Russian Roulette Start Bounce")
        col.prop(asr_scene_props, "sppm_light_photons", text="Light Photons")
        col.prop(asr_scene_props, "sppm_env_photons", text="Environment Photons")


class ASRENDER_PT_lighting_sppm_radiance(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Radiance Estimation"
    bl_parent_id = "ASRENDER_PT_lighting_sppm"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        layout.use_property_split = True

        col = layout.column()
        col.prop(asr_scene_props, "sppm_pt_max_ray_intensity_unlimited", text="Max Ray Intensity Unlimited")
        row = col.row()
        row.enabled = not asr_scene_props.sppm_pt_max_ray_intensity_unlimited
        row.prop(asr_scene_props, "sppm_pt_max_ray_intensity", text="Max Ray Intensity")

        col = layout.column(align=True)
        col.prop(asr_scene_props, "sppm_pt_max_length", text="Max Bounces")
        col.prop(asr_scene_props, "sppm_pt_rr_start", text="Russian Roulette Start Bounce")
        col.prop(asr_scene_props, "sppm_initial_radius", text="Initial Radius")
        col.prop(asr_scene_props, "sppm_max_per_estimate", text="Max Photons")
        col.prop(asr_scene_props, "sppm_alpha", text="Alpha")


class ASRENDER_PT_lighting_advanced(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Advanced"
    bl_parent_id = "ASRENDER_PT_lighting"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        scene = context.scene
        asr_scene_props = scene.appleseed

        layout.prop(asr_scene_props, "rr_start", text="Russian Roulette Start Bounce")
        col = layout.column(align=True)
        col.prop(asr_scene_props, "volume_distance_samples", text="Volume Distance Samples")
        col.prop(asr_scene_props, "optimize_for_lights_outside_volumes", text="Optimize for Lights Outside Volumes")


class ASRENDER_UL_post_processing(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        stage = item.name
        if 'DEFAULT' in self.layout_type:
            layout.label(text=stage, translate=False, icon_value=icon)


class ASRENDER_PT_post_process_stages(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "appleseed Post Process"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        asr_scene_props = context.scene.appleseed
        pp_stages = asr_scene_props.post_processing_stages

        row = layout.row()
        row.template_list("ASRENDER_UL_post_processing", "", asr_scene_props,
                          "post_processing_stages", asr_scene_props, "post_processing_stages_index",
                          rows=1, maxrows=16, type="DEFAULT")

        row = layout.row(align=True)
        row.operator("appleseed.add_pp_stage", text="Add Stage", icon="ADD")
        row.operator("appleseed.remove_pp_stage", text="Remove Stage", icon="REMOVE")

        if pp_stages:
            current_stage = pp_stages[asr_scene_props.post_processing_stages_index]
            layout.prop(current_stage, "model", text="Model")
            if current_stage.model == 'render_stamp_post_processing_stage':
                layout.prop(current_stage, "render_stamp", text="Stamp")
                layout.prop(current_stage, "render_stamp_patterns", text="Add Stamp")
            else:
                layout.prop(current_stage, "color_map", text="Mode")
                row = layout.row()
                row.enabled = current_stage.color_map == 'custom'
                row.prop(current_stage, "color_map_file_path", text="Custom Map")

                col = layout.column(align=True)
                col.prop(current_stage, "add_legend_bar", text="Add Legends Bar")
                row = col.row(align=True)
                row.enabled = current_stage.add_legend_bar
                row.prop(current_stage, "legend_bar_ticks", text="Ticks")

                col = layout.column(align=True)
                col.prop(current_stage, "auto_range", text="Auto Range")
                row = col.row(align=True)
                row.enabled = not current_stage.auto_range
                row.prop(current_stage, "range_min", text="Min Range")
                row = col.row(align=True)
                row.enabled = not current_stage.auto_range
                row.prop(current_stage, "range_max", text="Max Range")

                col = layout.column(align=True)
                col.prop(current_stage, "render_isolines", text="Render Isolines")
                row = col.row(align=True)
                row.enabled = current_stage.render_isolines
                row.prop(current_stage, "line_thickness", text="Line Thickness")


class ASRENDER_PT_motion_blur(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Motion Blur"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        asr_scene_props = context.scene.appleseed

        col = layout.column(align=True)
        col.prop(asr_scene_props, "shutter_open", text="Shutter Open Begin")
        col.prop(asr_scene_props, "shutter_open_end_time", text="Shutter Open End")
        col = layout.column(align=True)
        col.prop(asr_scene_props, "shutter_close_begin_time", text="Shutter Close Begin")
        col.prop(asr_scene_props, "shutter_close", text="Shutter Close End")

        col = layout.column(align=True)
        col.prop(asr_scene_props, "enable_camera_blur", text="Camera Blur")
        col.prop(asr_scene_props, "camera_blur_samples", text="Samples")

        col = layout.column(align=True)
        col.prop(asr_scene_props, "enable_object_blur", text="Object Blur")
        col.prop(asr_scene_props, "object_blur_samples", text="Samples")

        col = layout.column(align=True)
        col.prop(asr_scene_props, "enable_deformation_blur", text="Deformation Blur")
        col.prop(asr_scene_props, "deformation_blur_samples", text="Samples")


class ASRENDER_PT_b_post_processing(bpy.types.Panel, ASRENDER_PT_base):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Blender Post Processing"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        rd = context.scene.render

        col = layout.column()
        col.prop(rd, "use_compositing")
        col.prop(rd, "use_sequencer")


classes = (
    ASRENDER_PT_export,
    ASRENDER_PT_settings,
    ASRENDER_PT_shading_override,
    ASRENDER_PT_denoise,
    ASRENDER_PT_sampling,
    ASRENDER_PT_sampling_sampler,
    ASRENDER_PT_sampling_interactive,
    ASRENDER_PT_sampling_filter,
    ASRENDER_PT_lighting,
    ASRENDER_PT_lighting_pt,
    ASRENDER_PT_lighting_bounces,
    ASRENDER_PT_lighting_sppm,
    ASRENDER_PT_lighting_sppm_tracing,
    ASRENDER_PT_lighting_sppm_radiance,
    ASRENDER_PT_lighting_advanced,
    ASRENDER_UL_post_processing,
    ASRENDER_PT_post_process_stages,
    ASRENDER_PT_motion_blur,
    ASRENDER_PT_b_post_processing
)


def register():
    for cls in classes:
        util.safe_register_class(cls)


def unregister():
    for cls in reversed(classes):
        util.safe_unregister_class(cls)
