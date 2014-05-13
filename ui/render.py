
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2013 Franz Beaune, Joel Daniels, Esteban Tovagliari.
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

class AppleseedRenderPanelBase( object):
    bl_context = "render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

class AppleseedRenderButtons( bpy.types.Panel, AppleseedRenderPanelBase):
    bl_label = "Render"
    
    def draw( self, context):
        scene = context.scene
        layout = self.layout

        if scene.appleseed.display_mode != 'STUDIO':
            row = layout.row( align=True)
            row.operator( "render.render", text="Render", icon = 'RENDER_STILL')
            row.operator( "render.render", text = "Animation", icon = 'RENDER_ANIMATION').animation = True
            
        else:
            layout.operator( "render.render", text="Render", icon='RENDER_STILL')

        layout.prop( scene.appleseed, "display_mode")
        if not scene.appleseed.display_mode == 'STUDIO':
            layout.prop(scene.appleseed, "refresh_time")

        if scene.appleseed.display_mode == 'STUDIO':
            layout.prop( scene.appleseed, "studio_rendering_mode")

class AppleseedRenderSettingsPanel( bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Settings"

    def draw( self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        layout.prop( asr_scene_props, "project_path", text = "Project Path")
        layout.prop( asr_scene_props, "img_extension")
        split = layout.split()
        col = split.column()
        col.label( "Render Threads:")
        col = split.column()        
        col.prop( asr_scene_props, "threads")
        layout.prop( asr_scene_props, "generate_mesh_files")
            
class AppleseedSamplingPanel( bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Sampling"

    def draw( self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        row = layout.row( align=True)
        row.prop( asr_scene_props, "pixel_filter")
        row.prop( asr_scene_props, "filter_size")

        layout.separator()
        layout.prop( asr_scene_props, "pixel_sampler")
        layout.prop( asr_scene_props, "renderer_passes")
        
        if asr_scene_props.pixel_sampler == 'adaptive':
            row = layout.row( align = True)
            row.prop( asr_scene_props, "sampler_min_samples")
            row.prop( asr_scene_props, "sampler_max_samples")
            layout.prop( asr_scene_props, "sampler_max_contrast")
            layout.prop( asr_scene_props, "sampler_max_variation")
        else:
            row = layout.row()
            row.prop( asr_scene_props, "decorrelate_pixels")
            row.prop( asr_scene_props, "force_aa")
            layout.prop( asr_scene_props, "sampler_max_samples")
        
class AppleseedLightingPanel( bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Lighting"

    def draw( self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed

        col = layout.column()
        col.prop( asr_scene_props, "lighting_engine")
        split = layout.split()

        # Pathtracing UI.
        if asr_scene_props.lighting_engine == 'pt':
            col = split.column()
            col.prop( asr_scene_props, "caustics_enable")
            col.prop( asr_scene_props, "next_event_est")
            col = split.column()
            col.prop( asr_scene_props, "enable_diagnostics", text = "Enable Diagnostics")
            col.prop( asr_scene_props, "quality")
            if asr_scene_props.next_event_est == True:
                row = layout.row()
                row.prop( asr_scene_props, "ibl_enable")
                if asr_scene_props.ibl_enable == True:
                    row.prop( asr_scene_props, "ibl_env_samples")
                row = layout.row()
                row.prop( asr_scene_props, "direct_lighting")
                if asr_scene_props.direct_lighting == True:
                    row.prop( asr_scene_props, "dl_light_samples")
            layout.prop( asr_scene_props, "max_bounces")  
            layout.prop( asr_scene_props, "rr_start")

        # Direct Lighting UI.
        elif asr_scene_props.lighting_engine == 'drt':
            row = layout.row()
            row.prop( asr_scene_props, "ibl_enable")
            if asr_scene_props.ibl_enable == True:
                row.prop( asr_scene_props, "ibl_env_samples")
            layout.prop( asr_scene_props, "decorrelate_pixels")
            layout.prop( asr_scene_props, "max_bounces")  
            layout.prop( asr_scene_props, "rr_start")

        # SPPM UI.
        elif asr_scene_props.lighting_engine == 'sppm':
            layout.label( "Components")
            layout.prop( asr_scene_props, "sppm_dl_mode")
            row = layout.row()
            row.prop( asr_scene_props, "ibl_enable")
            row.prop( asr_scene_props, "caustics_enable")

            layout.separator()
            layout.label( "Photon Tracing")
            box = layout.box()
            row = box.row()
            row.prop( asr_scene_props, "sppm_light_photons")
            row.prop( asr_scene_props, "sppm_env_photons")
            box.prop( asr_scene_props, "sppm_photon_max_length")
            box.prop( asr_scene_props, "sppm_photon_rr_start")

            layout.separator()
            layout.label( "Radiance Estimation")
            box = layout.box()
            box.prop( asr_scene_props, "sppm_max_per_estimate")
            row = box.row()
            row.prop( asr_scene_props, "sppm_initial_radius")
            row.prop( asr_scene_props, "sppm_alpha")
            box.prop( asr_scene_props, "sppm_pt_max_length")
            box.prop( asr_scene_props, "sppm_pt_rr_start")
            
        # Meshlights.
        layout.separator()
        layout.separator()
        layout.prop( asr_scene_props, "export_emitting_obj_as_lights")     
        if asr_scene_props.export_emitting_obj_as_lights:
            layout.prop( asr_scene_props, "light_mats_exitance_mult")  

class AppleseedMotionBlurPanel( bpy.types.Panel, AppleseedRenderPanelBase):
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_label = "Motion Blur"

    def draw_header( self, context):
        header = self.layout
        asr_scene_props = context.scene.appleseed
        header.prop( asr_scene_props, "mblur_enable")

    def draw( self, context):
        layout = self.layout
        asr_scene_props = context.scene.appleseed
        layout.active = asr_scene_props.mblur_enable

        layout.prop( asr_scene_props, "ob_mblur")
        layout.prop( asr_scene_props, "def_mblur")
        layout.prop( asr_scene_props, "cam_mblur")
        if asr_scene_props.cam_mblur:
            row = layout.row( align = True)
            row.prop( asr_scene_props, "shutter_open")
            row.prop( asr_scene_props, "shutter_close")

def register():
    bpy.types.RENDER_PT_dimensions.COMPAT_ENGINES.add( 'APPLESEED_RENDER')
    bpy.utils.register_class( AppleseedRenderButtons)
    bpy.utils.register_class( AppleseedRenderSettingsPanel)
    bpy.utils.register_class( AppleseedSamplingPanel)
    bpy.utils.register_class( AppleseedLightingPanel)
    bpy.utils.register_class( AppleseedMotionBlurPanel)

def unregister():
    bpy.utils.unregister_class( AppleseedRenderButtons)
    bpy.utils.unregister_class( AppleseedRenderSettingsPanel)
    bpy.utils.unregister_class( AppleseedSamplingPanel)
    bpy.utils.unregister_class( AppleseedLightingPanel)
    bpy.utils.unregister_class( AppleseedMotionBlurPanel)
