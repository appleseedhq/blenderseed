
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

from . import render_layers

class AppleseedMatLayerProps( bpy.types.PropertyGroup):
    name = bpy.props.StringProperty( name=  "BSDF Name", 
                                     description = "BSDF layer name -- This must be a unique name per layer!", 
                                     default = "")

    bsdf_type = bpy.props.EnumProperty( items = [('ashikhmin_brdf', "Ashikhmin-Shirley BRDF", ""),
                                                ('diffuse_btdf', "Diffuse BTDF", ""),
                                                ('kelemen_brdf', "Kelemen BRDF", ""),
                                                ('lambertian_brdf', "Lambertian BRDF", ""),
                                                ('microfacet_brdf', "Microfacet BRDF", ""),
                                                ('orennayar_brdf', "Oren-Nayar BRDF", ""),
                                                ('specular_brdf', "Specular BRDF (mirror)", ""),
                                                ('specular_btdf', "Specular BTDF (glass)", "")],
                                                name = "BSDF Model", 
                                                description = "BSDF model for current material layer", 
                                                default = "lambertian_brdf")
        
    transmittance_multiplier = bpy.props.FloatProperty( name = "Transmittance multiplier", description = "Multiplier for material transmittance", default = 0.0, min = 0.0, max = 2.0)

    transmittance_use_mult_tex = bpy.props.BoolProperty(name = "", description = "Use texture to influence transmittance", default = False)
    
    transmittance_mult_tex = bpy.props.StringProperty(name = "", description = "Texture to influence transmittance", default = "")
    
    transmittance_color = bpy.props.FloatVectorProperty(name = "Transmittance color", description = "Transmittance color", default = (0.8, 0.8, 0.8), subtype = 'COLOR',min = 0.0, max = 1.0)
    
    transmittance_use_diff_tex = bpy.props.BoolProperty(name = "", description = "Use texture to influence diffuse color", default = False)
    
    transmittance_diff_tex = bpy.props.StringProperty(name = "", description = "Texture to influence diffuse color", default = "")
    
    transmittance_weight = bpy.props.FloatProperty(name = "Diffuse BTDF Blending Weight", description = "Blending weight of Diffuse BTDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)

    transmittance_use_tex = bpy.props.BoolProperty( name = "Use Texture", description = "Use texture to influence the layer weight in the BSDF mix", default = False)

    transmittance_mix_tex = bpy.props.StringProperty( name = "", description = "Texture to influence layer weight in the BSDF mix", default = "")

    #-----------------------
    
    kelemen_matte_reflectance = bpy.props.FloatVectorProperty(name = "Matte Reflectance", description = "Kelemen matte reflectance", default = (0.8, 0.8, 0.8), subtype = 'COLOR', min = 0.0, max = 1.0)
    
    kelemen_use_diff_tex = bpy.props.BoolProperty(name= "", description = "Use texture to influence matte reflectance", default = False)
    
    kelemen_diff_tex = bpy.props.StringProperty(name = "", description = "Texture to influence matte reflectance", default = "")
    
    kelemen_matte_multiplier = bpy.props.FloatProperty(name = "Matte Reflectance Multiplier", description = "Kelemen matte reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    kelemen_roughness = bpy.props.FloatProperty(name = "Roughness", description = "Kelemen roughness", default = 0.0, min = 0.0, max = 1.0)
    
    kelemen_specular_reflectance = bpy.props.FloatVectorProperty(name = "Specular Reflectance", description = "Kelemen specular reflectance", default = (0.8, 0.8, 0.8), subtype = 'COLOR', min = 0.0, max = 1.0)
    
    kelemen_use_spec_tex = bpy.props.BoolProperty(name= "", description = "Use texture to influence specular reflectance", default = False)
    
    kelemen_spec_tex = bpy.props.StringProperty(name = "", description = "Texture to influence specular reflectance", default = "")
    
    kelemen_specular_multiplier = bpy.props.FloatProperty(name = "Specular Reflectance Multiplier", description = "Kelemen specular reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)       
    
    kelemen_weight = bpy.props.FloatProperty(name = "Kelemen Blending Weight", description = "Blending weight of Kelemen BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)

    kelemen_use_tex = bpy.props.BoolProperty( name = "Use Texture", description = "Use texture to influence the layer weight in the BSDF mix", default = False) 

    kelemen_mix_tex = bpy.props.StringProperty( name = "", description = "Texture to influence layer weight in the BSDF mix", default = "")
    #-------------------------

    
    microfacet_fresnel = bpy.props.FloatProperty(name = "Fresnel Multiplier", description = "Microfacet fresnel multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    microfacet_model = bpy.props.EnumProperty(items = [
                                    ("ggx", "GGX", ""),
                                    ("ward", "Ward", ""),
                                    ("beckmann", "Beckmann", ""),
                                    ("blinn", "Blinn", "")],
                                    name = "Microfacet model", description = "Microfacet distribution function model", default = "beckmann")
                                    
    microfacet_mdf_blinn = bpy.props.FloatProperty(name = "Distribution Function", description = "Blinn model microfacet distribution function", default = 1.0, min = 0.0)
                                    
    microfacet_mdf = bpy.props.FloatProperty(name = "Distribution Function", description = "Microfacet distribution function (glossiness: lower values = more glossy)", default = 0.5, min = 0.0, max = 1.0)
    
    microfacet_reflectance = bpy.props.FloatVectorProperty(name = "Microfacet Reflectance", description = "Microfacet reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    microfacet_multiplier = bpy.props.FloatProperty(name = "Microfacet Reflectance Multiplier", description = "Microfacet reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    microfacet_use_diff_tex = bpy.props.BoolProperty(name= "", description = "Use texture to influence reflectance", default = False)
    
    microfacet_diff_tex = bpy.props.StringProperty(name = "", description = "Texture to influence reflectance", default = "")
    
    microfacet_use_spec_tex = bpy.props.BoolProperty(name= "", description = "Use texture to influence distribution function (glossiness)", default = False)
    
    microfacet_spec_tex = bpy.props.StringProperty(name = "", description = "Texture to influence distribution function (glossiness)", default = "")
    
    microfacet_weight = bpy.props.FloatProperty(name = "Microfacet Blending Weight", description = "Blending weight of Microfacet BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)

    microfacet_use_tex = bpy.props.BoolProperty( name = "Use Texture", description = "Use texture to influence the layer weight in the BSDF mix", default = False)

    microfacet_mix_tex = bpy.props.StringProperty( name = "", description = "Texture to influence layer weight in the BSDF mix", default = "")
    #------------------------------

    ashikhmin_reflectance = bpy.props.FloatVectorProperty(name = "Diffuse Reflectance", description = "Ashikhmin-Shirley diffuse reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    ashikhmin_use_diff_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence diffuse reflectance", default = False)
    
    ashikhmin_diffuse_tex = bpy.props.StringProperty(name = "", description = "Diffuse reflectance texture", default = "")
    
    ashikhmin_multiplier = bpy.props.FloatProperty(name= "Diffuse Reflectance Multiplier", description = "Ashikhmin-Shirley diffuse reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    ashikhmin_fresnel = bpy.props.FloatProperty(name = "Fresnel Multiplier", description = "", default = 1.0, min = 0.0, max = 2.0)
    ashikhmin_glossy = bpy.props.FloatVectorProperty(name = "Glossy Reflectance", description = "Ashikhmin-Shirley glossy reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    ashikhmin_use_gloss_tex = bpy.props.BoolProperty(name= "", description = "Use a texture to influence gglossy reflectance", default = False)
    
    ashikhmin_gloss_tex = bpy.props.StringProperty(name= "", description = "Texture to influence glossy reflectance", default = "")
    
    ashikhmin_glossy_multiplier = bpy.props.FloatProperty(name = "Glossy Reflectance Multiplier", description = "Ashikhmin-Shirley glossy reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    ashikhmin_shininess_u = bpy.props.FloatProperty(name = "Shininess U", description = "", default = 200.0, min = 0.0, max = 1000.0)
    
    ashikhmin_shininess_v = bpy.props.FloatProperty(name = "Shininess V", description = "", default = 200.0, min = 0.0, max = 1000.0)
    ashikhmin_weight = bpy.props.FloatProperty(name = "Ashikhmin Blending Weight", description = "Blending weight of Ashikhmin-Shirley BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)

    ashikhmin_use_tex = bpy.props.BoolProperty( name = "Use Texture", description = "Use texture to influence the layer weight in the BSDF mix", default = False)

    ashikhmin_mix_tex = bpy.props.StringProperty( name = "", description = "Texture to influence layer weight in the BSDF mix", default = "")
    #--------------------------------
    
    lambertian_reflectance = bpy.props.FloatVectorProperty(name = "Lambertian Reflectance", description = "Lambertian diffuse reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    lambertian_multiplier = bpy.props.FloatProperty(name = "Reflectance Multiplier", description = "Lambertian reflectance multiplier", default = 1.0, min = 0.0, max = 2.0)
    
    lambertian_weight = bpy.props.FloatProperty(name = "Lambertian Blending Weight", description = "Blending weight of Lambertian BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)

    lambertian_use_diff_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence diffuse color", default = False)
    
    lambertian_diffuse_tex = bpy.props.StringProperty(name = "", description = "Diffuse color texture", default = "")

    lambertian_use_tex = bpy.props.BoolProperty( name = "Use Texture", description = "Use texture to influence the layer weight in the BSDF mix", default = False)

    lambertian_mix_tex = bpy.props.StringProperty( name = "", description = "Texture to influence layer weight in the BSDF mix", default = "")
    #--------------------------------
    
    orennayar_reflectance = bpy.props.FloatVectorProperty(name = "Oren-Nayar Reflectance", description = "Oren-Nayar diffuse reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    orennayar_multiplier = bpy.props.FloatProperty(name = "Reflectance Multiplier", description = "Oren-Nayar reflectance multiplier", default = 1.0, min = 0.0, max = 2.0)

    orennayar_roughness = bpy.props.FloatProperty(name = "Roughness", description = "Oren-Nayar roughness", default = 0.1, min = 0.0, max = 1.0)
    
    orennayar_weight = bpy.props.FloatProperty(name = "Oren-Nayar Blending Weight", description = "Blending weight of Oren-Nayar BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0)

    orennayar_use_diff_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence diffuse color", default = False)
    
    orennayar_diffuse_tex = bpy.props.StringProperty(name = "", description = "Diffuse color texture", default = "")

    orennayar_use_rough_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence roughness", default = False)
    
    orennayar_rough_tex = bpy.props.StringProperty(name = "", description = "Roughness texture", default = "")

    orennayar_use_tex = bpy.props.BoolProperty( name = "Use Texture", description = "Use texture to influence the layer weight in the BSDF mix", default = False)

    orennayar_mix_tex = bpy.props.StringProperty( name = "", description = "Texture to influence layer weight in the BSDF mix", default = "")
    #---------------------------------
    
    specular_reflectance = bpy.props.FloatVectorProperty(name = "Specular Reflectance", description = "Specular BRDF reflectance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    specular_use_gloss_tex = bpy.props.BoolProperty(name= "Use Texture", description = "Use a texture to influence specular reflectance", default = False)
    
    specular_gloss_tex = bpy.props.StringProperty(name= "", description = "Texture to influence specular reflectance", default = "")
    
    specular_multiplier = bpy.props.FloatProperty(name = "Specular Reflectance Multiplier", description = "Specular BRDF relectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    specular_weight = bpy.props.FloatProperty(name = "Specular Blending Weight", description = "Blending weight of Specular BRDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0) 

    specular_use_tex = bpy.props.BoolProperty( name = "Use Texture", description = "Use texture to influence the layer weight in the BSDF mix", default = False)

    specular_mix_tex = bpy.props.StringProperty( name = "", description = "Texture to influence layer weight in the BSDF mix", default = "")
    #---------------------------------
    
    spec_btdf_reflectance = bpy.props.FloatVectorProperty(name = "Specular Reflectance", description = "Specular BTDF reflectance", default = (0.8, 0.8, 0.8), subtype = 'COLOR', min = 0.0, max = 1.0)
    
    spec_btdf_use_spec_tex = bpy.props.BoolProperty(name= "Use Texture", description = "Use a texture to influence specular reflectance", default = False)
    
    spec_btdf_spec_tex = bpy.props.StringProperty(name= "", description = "Texture to influence specular reflectance", default = "")
    
    spec_btdf_ref_mult = bpy.props.FloatProperty(name = "Specular Reflectance Multiplier", description = "Specular BTDF reflectance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    spec_btdf_transmittance = bpy.props.FloatVectorProperty(name = "Specular Transmittance", description = "Specular BTDF transmittance", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
    spec_btdf_use_trans_tex = bpy.props.BoolProperty(name= "Use Texture", description = "Use a texture to influence specular transmittance", default = False)
    
    spec_btdf_trans_tex = bpy.props.StringProperty(name= "", description = "Texture to influence specular transmittance", default = "")
    
    spec_btdf_trans_mult = bpy.props.FloatProperty(name = "Specular Transmittance Multiplier", description = "Specular BTDF transmittance multiplier", default = 1.0, min = 0.0, max = 1.0)
    
    spec_btdf_from_ior = bpy.props.FloatProperty(name = "From IOR", description = "From index of refraction", default = 1.0, min = 1.0, max = 4.01)
    
    spec_btdf_to_ior = bpy.props.FloatProperty(name = "To IOR", description = "To index of refraction", default = 1.0, min = 1.0, max = 4.01)
    
    spec_btdf_weight = bpy.props.FloatProperty(name = "Specular BTDF Blending Weight", description = "Blending weight of Specular BTDF in BSDF mix", default = 1.0, min = 0.0, max = 1.0) 

    spec_btdf_use_tex = bpy.props.BoolProperty( name = "Use Texture", description = "Use texture to influence the layer weight in the BSDF mix", default = False)

    spec_btdf_mix_tex = bpy.props.StringProperty( name = "", description = "Texture to influence layer weight in the BSDF mix", default = "")

class AppleseedMatProps( bpy.types.PropertyGroup):
    
    #Per layer properties are stored in AppleseedMatLayerProps
    layers = bpy.props.CollectionProperty( type = AppleseedMatLayerProps, 
                                           name = "Appleseed Material Layers", 
                                           description = "")
    
    layer_index = bpy.props.IntProperty( name = "Layer Index", description = "", default = 0, min = 0, max = 16)
    
    
    use_light_emission = bpy.props.BoolProperty(name = "", description = "Enable material light emission", default = False)
    
    light_emission = bpy.props.FloatProperty(name = "Emission strength", description = "Light emission strength", default = 0.0, min = 0.0, max = 10000.0)
    
    light_color = bpy.props.FloatVectorProperty(name = "Emission Color", description = "Light emission color", default = (0.8, 0.8, 0.8), subtype = "COLOR", min = 0.0, max = 1.0)
    
#    sss_use_shader = bpy.props.BoolProperty(name = "", description = "Enable Appleseed FastSSS shader (experimental)", default = False)
#    
#    sss_albedo_use_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence SSS color", default = False)
#    
#    sss_ambient = bpy.props.FloatProperty(name = "Ambient SSS", description = "Ambient SSS value", default = 1.0, min = 0.0, max = 10.0)
#    
#    sss_diffuse = bpy.props.FloatProperty(name = "Diffuse Lighting", description = "", default = 1.0, min = 0.0, max = 10.0)
#    
#    sss_distortion = bpy.props.FloatProperty(name = "Normal Distortion", description = "", default = 1.0, min = 0.0, max = 10.0)
#    
#    sss_light_samples = bpy.props.IntProperty(name = "Light Samples", description = "", default = 1, min = 0, max = 100)
#    
#    sss_occlusion_samples = bpy.props.IntProperty(name = "Occlusion Samples", description = "", default = 1, min = 0, max = 100)
#    
#    sss_power = bpy.props.FloatProperty(name = "Power", description = "", default = 1.0, min = 0.0, max = 10.0)
#    
#    sss_scale = bpy.props.FloatProperty(name = "Geometric Scale", description = "", default = 1.0, min = 0.0, max = 10.0)
#    
#    sss_view_dep = bpy.props.FloatProperty(name = "View-dependent SSS", description = "", default = 1.0, min = 0.0, max = 10.0)
#    
#    sss_albedo_tex = bpy.props.StringProperty(name = '', description = 'Texture to influence SSS albedo', default = "")

    material_use_bump_tex = bpy.props.BoolProperty(name = "", description = "Use a texture to influence bump / normal", default = False)
    
    material_bump_tex = bpy.props.StringProperty(name = "", description = "Bump / normal texture", default = "")
    
    material_use_normalmap = bpy.props.BoolProperty(name = "", description = "Use texture as normal map", default = False)
    
    material_bump_amplitude  = bpy.props.FloatProperty(name = "Bump Amplitude", description = "Maximum height influence of bump / normal map", default = 1.0, min = 0.0, max = 1.0)
    
    material_use_alpha = bpy.props.BoolProperty(name = "", description = "Use a texture to influence alpha", default = False)
    
    material_alpha_map = bpy.props.StringProperty(name = "", description = "Alpha texture", default = "")

    material_alpha = bpy.props.FloatProperty(name = "Alpha", description = "Alpha", default = 1.0, min = 0.0, max = 1.0)

    preview_quality = bpy.props.IntProperty(name = "Preview Quality", description = "Number of samples used for preview rendering", default = 2, min = 1, max = 16)
    
def register():
    bpy.utils.register_class( AppleseedMatLayerProps)
    bpy.utils.register_class( AppleseedMatProps)
    bpy.types.Material.appleseed = bpy.props.PointerProperty( type = AppleseedMatProps)

def unregister():
    del bpy.types.Material.appleseed
    bpy.utils.unregister_class( AppleseedMatLayerProps)
    bpy.utils.unregister_class( AppleseedMatProps)


