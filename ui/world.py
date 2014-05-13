
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

class AppleseedWorldPanelOld( bpy.types.Panel):
    bl_label = "Appleseed Environment"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_context = "world"
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        if renderer.engine == 'APPLESEED_RENDER':
            return context.scene.world != None
        return False
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_sky_props = scene.appleseed_sky

        layout.prop(asr_sky_props, "env_type", text = '')
        
        if asr_sky_props.env_type == "sunsky":
            layout.label("Sun to export:")
            layout.prop(asr_sky_props, "sun_lamp", text = '')
            layout.prop(asr_sky_props, "sun_model")
            
            layout.prop(asr_sky_props, "luminance_multiplier")
            layout.prop(asr_sky_props, "radiance_multiplier")
            layout.prop(asr_sky_props, "saturation_multiplier")
            row = layout.row(align = True)
            row.prop(asr_sky_props, "sun_theta")
            row.prop(asr_sky_props, "sun_phi")
            layout.prop(asr_sky_props, "turbidity")
            row = layout.row(align = True)
            row.prop(asr_sky_props, "turbidity_min")
            row.prop(asr_sky_props, "turbidity_max")
            layout.prop(asr_sky_props, "horiz_shift")
            if asr_sky_props.sun_model == "hosek_environment_edf":
                layout.prop(asr_sky_props, "ground_albedo")
            
        elif asr_sky_props.env_type == "gradient":
            split = layout.split()
            col = split.column()
            col.prop(scene.world, "horizon_color")
            col = split.column()
            col.prop(scene.world, "zenith_color")
        
        elif asr_sky_props.env_type == "constant":
            col = layout.column()
            col.prop(scene.world, "horizon_color", text = "Constant Color")
        
        elif asr_sky_props.env_type == "constant_hemisphere":
            split = layout.split()
            col = split.column()
            col.prop(scene.world, "horizon_color", text = "Lower Hemisphere")
            col = split.column()
            col.prop(scene.world, "zenith_color", text = "Upper Hemisphere")
            
        elif asr_sky_props.env_type == "mirrorball_map":
            layout.label("Mirror Ball Map:")
            layout.prop_search(asr_sky_props, "env_tex", scene.world, "texture_slots", text = "")
            layout.prop(asr_sky_props, "env_tex_mult")
        elif asr_sky_props.env_type == "latlong_map":
            layout.label("Latitude-Longitude Map:")
            layout.prop_search(asr_sky_props, "env_tex", scene.world, "texture_slots", text = "")
            layout.prop(asr_sky_props, "env_tex_mult")

def register():
    bpy.types.WORLD_PT_context_world.COMPAT_ENGINES.add( 'APPLESEED_RENDER')
    bpy.types.WORLD_PT_custom_props.COMPAT_ENGINES.add( 'APPLESEED_RENDER')
    bpy.types.WORLD_PT_preview.COMPAT_ENGINES.add( 'APPLESEED_RENDER')

def unregister():
    pass
