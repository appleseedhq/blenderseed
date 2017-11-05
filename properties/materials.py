
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


def refresh_preview(self, context):
    """
    Triggers a refresh of the material preview.
    """

    if hasattr(context, "material"):
        if context.material is not None:
            context.material.preview_render_type = context.material.preview_render_type

    if hasattr(context, "texture"):
        if context.texture is not None:
            context.texture.type = context.texture.type


class AppleseedMatLayerProps(bpy.types.PropertyGroup):
    """
    appleseed Material Layer Properties.
    """

    name = bpy.props.StringProperty(name="BSDF Name",
                                    description="BSDF layer name",
                                    default="", update=refresh_preview)

    bsdf_type = bpy.props.EnumProperty(items=[('ashikhmin_brdf', "Ashikhmin-Shirley BRDF", ""),
                                              ('diffuse_btdf', "Diffuse BTDF", ""),
                                              ('disney_brdf', "Disney BRDF", ""),
                                              ('kelemen_brdf', "Kelemen BRDF", ""),
                                              ('lambertian_brdf', "Lambertian BRDF", ""),
                                              ('microfacet_brdf', "Microfacet BRDF", ""),
                                              ('orennayar_brdf', "Oren-Nayar BRDF", ""),
                                              ('specular_btdf', "Specular BTDF", ""),
                                              ('specular_brdf', "Specular BRDF", "")],
                                       name="BSDF Model",
                                       description="BSDF model for current material layer",
                                       default="lambertian_brdf",
                                       update=refresh_preview)

    transmittance_multiplier = bpy.props.FloatProperty(
        name="Transmittance multiplier", description="Multiplier for material transmittance", default=1.0, min=0.0, max=2.0, update=refresh_preview)

    transmittance_use_mult_tex = bpy.props.BoolProperty(name="", description="Use texture to influence transmittance", default=False,
                                                        update=refresh_preview)

    transmittance_mult_tex = bpy.props.StringProperty(name="", description="Texture to influence transmittance", default="", update=refresh_preview)

    transmittance_color = bpy.props.FloatVectorProperty(
        name="Transmittance Color", description="Transmittance color", default=(0.8, 0.8, 0.8), subtype='COLOR', min=0.0, max=1.0,
        update=refresh_preview)

    transmittance_use_diff_tex = bpy.props.BoolProperty(name="", description="Use texture to influence diffuse color", default=False,
                                                        update=refresh_preview)

    transmittance_diff_tex = bpy.props.StringProperty(name="", description="Texture to influence diffuse color", default="", update=refresh_preview)

    transmittance_weight = bpy.props.FloatProperty(name="Diffuse BTDF Blending Weight",
                                                   description="Blending weight of Diffuse BTDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                                   update=refresh_preview)

    transmittance_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                                   update=refresh_preview)

    transmittance_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                                     update=refresh_preview)

    # -----------------------

    kelemen_matte_reflectance = bpy.props.FloatVectorProperty(
        name="Matte Reflectance", description="Kelemen matte reflectance", default=(0.8, 0.8, 0.8), subtype='COLOR', min=0.0, max=1.0,
        update=refresh_preview)

    kelemen_use_diff_tex = bpy.props.BoolProperty(name="", description="Use texture to influence matte reflectance", default=False,
                                                  update=refresh_preview)

    kelemen_diff_tex = bpy.props.StringProperty(name="", description="Texture to influence matte reflectance", default="", update=refresh_preview)

    kelemen_matte_multiplier = bpy.props.FloatProperty(name="Matte Reflectance Multiplier",
                                                       description="Kelemen matte reflectance multiplier", default=1.0, min=0.0, max=1.0,
                                                       update=refresh_preview)

    kelemen_roughness = bpy.props.FloatProperty(name="Roughness", description="Kelemen roughness", default=0.0, min=0.0, max=1.0,
                                                update=refresh_preview)

    kelemen_specular_reflectance = bpy.props.FloatVectorProperty(
        name="Specular Reflectance", description="Kelemen specular reflectance", default=(0.8, 0.8, 0.8), subtype='COLOR', min=0.0, max=1.0,
        update=refresh_preview)

    kelemen_use_spec_tex = bpy.props.BoolProperty(name="", description="Use texture to influence specular reflectance", default=False,
                                                  update=refresh_preview)

    kelemen_spec_tex = bpy.props.StringProperty(name="", description="Texture to influence specular reflectance", default="", update=refresh_preview)

    kelemen_specular_multiplier = bpy.props.FloatProperty(name="Specular Reflectance Multiplier",
                                                          description="Kelemen specular reflectance multiplier", default=1.0, min=0.0, max=1.0,
                                                          update=refresh_preview)

    kelemen_weight = bpy.props.FloatProperty(name="Kelemen Blending Weight",
                                             description="Blending weight of Kelemen BRDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                             update=refresh_preview)

    kelemen_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                             update=refresh_preview)

    kelemen_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                               update=refresh_preview)

    # -------------------------

    microfacet_fresnel = bpy.props.FloatProperty(
        name="Fresnel Multiplier", description="Microfacet fresnel multiplier", default=1.0, min=0.0, max=1.0, update=refresh_preview)

    microfacet_model = bpy.props.EnumProperty(items=[
        ("ggx", "GGX", ""),
        ("ward", "Ward", ""),
        ("beckmann", "Beckmann", ""),
        ("blinn", "Blinn", "")],
        name="Microfacet model", description="Microfacet distribution function model", default="beckmann", update=refresh_preview)

    microfacet_mdf = bpy.props.FloatProperty(name="Glossiness", description="Microfacet glossiness", default=0.5, min=0.0, max=1.0,
                                             update=refresh_preview)

    microfacet_mdf_multiplier = bpy.props.FloatProperty(
        name="Glossiness Multiplier", description="Microfacet glossiness multiplier", default=1.0, min=0.0, max=1.0, update=refresh_preview)

    microfacet_reflectance = bpy.props.FloatVectorProperty(
        name="Microfacet Reflectance", description="Microfacet reflectance", default=(0.8, 0.8, 0.8), subtype="COLOR", min=0.0, max=1.0,
        update=refresh_preview)

    microfacet_multiplier = bpy.props.FloatProperty(name="Microfacet Reflectance Multiplier",
                                                    description="Microfacet reflectance multiplier", default=1.0, min=0.0, max=1.0,
                                                    update=refresh_preview)

    microfacet_use_diff_tex = bpy.props.BoolProperty(name="", description="Use texture to influence reflectance", default=False,
                                                     update=refresh_preview)

    microfacet_diff_tex = bpy.props.StringProperty(name="", description="Texture to influence reflectance", default="", update=refresh_preview)

    microfacet_use_spec_tex = bpy.props.BoolProperty(
        name="", description="Use texture to influence distribution function (glossiness)", default=False, update=refresh_preview)

    microfacet_spec_tex = bpy.props.StringProperty(name="", description="Texture to influence distribution function (glossiness)", default="",
                                                   update=refresh_preview)

    microfacet_weight = bpy.props.FloatProperty(name="Microfacet Blending Weight",
                                                description="Blending weight of Microfacet BRDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                                update=refresh_preview)

    microfacet_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                                update=refresh_preview)

    microfacet_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                                  update=refresh_preview)

    # ------------------------------

    ashikhmin_reflectance = bpy.props.FloatVectorProperty(
        name="Diffuse Reflectance", description="Ashikhmin-Shirley diffuse reflectance", default=(0.8, 0.8, 0.8), subtype="COLOR", min=0.0, max=1.0,
        update=refresh_preview)

    ashikhmin_use_diff_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence diffuse reflectance", default=False,
                                                    update=refresh_preview)

    ashikhmin_diffuse_tex = bpy.props.StringProperty(name="", description="Diffuse reflectance texture", default="", update=refresh_preview)

    ashikhmin_multiplier = bpy.props.FloatProperty(name="Diffuse Reflectance Multiplier",
                                                   description="Ashikhmin-Shirley diffuse reflectance multiplier", default=1.0, min=0.0, max=1.0,
                                                   update=refresh_preview)

    ashikhmin_fresnel = bpy.props.FloatProperty(name="Fresnel Multiplier", description="", default=1.0, min=0.0, max=2.0, update=refresh_preview)

    ashikhmin_glossy = bpy.props.FloatVectorProperty(
        name="Glossy Reflectance", description="Ashikhmin-Shirley glossy reflectance", default=(0.8, 0.8, 0.8), subtype="COLOR", min=0.0, max=1.0,
        update=refresh_preview)

    ashikhmin_use_gloss_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence gglossy reflectance", default=False,
                                                     update=refresh_preview)

    ashikhmin_gloss_tex = bpy.props.StringProperty(name="", description="Texture to influence glossy reflectance", default="", update=refresh_preview)

    ashikhmin_glossy_multiplier = bpy.props.FloatProperty(name="Glossy Reflectance Multiplier",
                                                          description="Ashikhmin-Shirley glossy reflectance multiplier", default=1.0, min=0.0,
                                                          max=1.0, update=refresh_preview)

    ashikhmin_shininess_u = bpy.props.FloatProperty(name="Shininess U", description="", default=200.0, min=0.0, max=1000.0, update=refresh_preview)

    ashikhmin_shininess_v = bpy.props.FloatProperty(name="Shininess V", description="", default=200.0, min=0.0, max=1000.0, update=refresh_preview)

    ashikhmin_weight = bpy.props.FloatProperty(name="Ashikhmin Blending Weight",
                                               description="Blending weight of Ashikhmin-Shirley BRDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                               update=refresh_preview)

    ashikhmin_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                               update=refresh_preview)

    ashikhmin_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                                 update=refresh_preview)

    # --------------------------------

    lambertian_reflectance = bpy.props.FloatVectorProperty(
        name="Lambertian Reflectance", description="Lambertian diffuse reflectance", default=(0.8, 0.8, 0.8), subtype="COLOR", min=0.0, max=1.0,
        update=refresh_preview)

    lambertian_multiplier = bpy.props.FloatProperty(
        name="Reflectance Multiplier", description="Lambertian reflectance multiplier", default=1.0, min=0.0, max=2.0, update=refresh_preview)

    lambertian_weight = bpy.props.FloatProperty(name="Lambertian Blending Weight",
                                                description="Blending weight of Lambertian BRDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                                update=refresh_preview)

    lambertian_use_diff_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence diffuse color", default=False,
                                                     update=refresh_preview)

    lambertian_diffuse_tex = bpy.props.StringProperty(name="", description="Diffuse color texture", default="", update=refresh_preview)

    lambertian_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                                update=refresh_preview)

    lambertian_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                                  update=refresh_preview)

    # --------------------------------

    orennayar_reflectance = bpy.props.FloatVectorProperty(
        name="Oren-Nayar Reflectance", description="Oren-Nayar diffuse reflectance", default=(0.8, 0.8, 0.8), subtype="COLOR", min=0.0, max=1.0,
        update=refresh_preview)

    orennayar_multiplier = bpy.props.FloatProperty(
        name="Reflectance Multiplier", description="Oren-Nayar reflectance multiplier", default=1.0, min=0.0, max=2.0, update=refresh_preview)

    orennayar_roughness = bpy.props.FloatProperty(name="Roughness", description="Oren-Nayar roughness", default=0.5, min=0.0, max=1.0,
                                                  update=refresh_preview)

    orennayar_weight = bpy.props.FloatProperty(name="Oren-Nayar Blending Weight",
                                               description="Blending weight of Oren-Nayar BRDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                               update=refresh_preview)

    orennayar_use_diff_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence diffuse color", default=False,
                                                    update=refresh_preview)

    orennayar_diffuse_tex = bpy.props.StringProperty(name="", description="Diffuse color texture", default="", update=refresh_preview)

    orennayar_use_rough_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence roughness", default=False,
                                                     update=refresh_preview)

    orennayar_rough_tex = bpy.props.StringProperty(name="", description="Roughness texture", default="", update=refresh_preview)

    orennayar_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                               update=refresh_preview)

    orennayar_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                                 update=refresh_preview)

    # ---------------------------------

    specular_reflectance = bpy.props.FloatVectorProperty(
        name="Specular Reflectance", description="Specular BRDF reflectance", default=(0.8, 0.8, 0.8), subtype="COLOR", min=0.0, max=1.0,
        update=refresh_preview)

    specular_use_gloss_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence specular reflectance", default=False,
                                                    update=refresh_preview)

    specular_gloss_tex = bpy.props.StringProperty(name="", description="Texture to influence specular reflectance", default="",
                                                  update=refresh_preview)

    specular_multiplier = bpy.props.FloatProperty(name="Specular Reflectance Multiplier",
                                                  description="Specular BRDF relectance multiplier", default=1.0, min=0.0, max=1.0,
                                                  update=refresh_preview)

    specular_weight = bpy.props.FloatProperty(name="Specular Blending Weight",
                                              description="Blending weight of Specular BRDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                              update=refresh_preview)

    specular_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                              update=refresh_preview)

    specular_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                                update=refresh_preview)

    # ---------------------------------

    spec_btdf_reflectance = bpy.props.FloatVectorProperty(
        name="Specular Reflectance", description="Specular BTDF reflectance", default=(0.8, 0.8, 0.8), subtype='COLOR', min=0.0, max=1.0,
        update=refresh_preview)

    spec_btdf_use_spec_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence specular reflectance", default=False,
                                                    update=refresh_preview)

    spec_btdf_spec_tex = bpy.props.StringProperty(name="", description="Texture to influence specular reflectance", default="",
                                                  update=refresh_preview)

    spec_btdf_refl_mult = bpy.props.FloatProperty(name="Specular Reflectance Multiplier",
                                                  description="Specular BTDF reflectance multiplier", default=1.0, min=0.0, max=1.0,
                                                  update=refresh_preview)

    spec_btdf_transmittance = bpy.props.FloatVectorProperty(
        name="Specular Transmittance", description="Specular BTDF transmittance", default=(1, 1, 1), subtype="COLOR", min=0.0, max=1.0,
        update=refresh_preview)

    spec_btdf_use_trans_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence specular transmittance", default=False,
                                                     update=refresh_preview)

    spec_btdf_trans_tex = bpy.props.StringProperty(name="", description="Texture to influence specular transmittance", default="",
                                                   update=refresh_preview)

    spec_btdf_trans_mult = bpy.props.FloatProperty(name="Specular Transmittance Multiplier",
                                                   description="Specular BTDF transmittance multiplier", default=1.0, min=0.0, max=1.0,
                                                   update=refresh_preview)

    spec_btdf_ior = bpy.props.FloatProperty(name="IOR", description="Index of refraction", default=1.33, min=1.0, max=2.5,
                                            update=refresh_preview)

    spec_btdf_weight = bpy.props.FloatProperty(name="Specular BTDF Blending Weight",
                                               description="Blending weight of Specular BTDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                               update=refresh_preview)

    spec_btdf_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                               update=refresh_preview)

    spec_btdf_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                                 update=refresh_preview)

    # ---------------------------------

    disney_base = bpy.props.FloatVectorProperty(name="Base Coat Color", description="Base coat color",
                                                default=(0.5, 0.5, 0.5), subtype='COLOR', min=0.0, max=1.0, update=refresh_preview)

    disney_use_base_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence base coat color", default=False,
                                                 update=refresh_preview)

    disney_base_tex = bpy.props.StringProperty(name="", description="Texture to influence base coat color", default="", update=refresh_preview)

    disney_aniso = bpy.props.FloatProperty(name="Anisotropic", description="Anisotropic", default=0, min=0, soft_max=1.0, update=refresh_preview)

    disney_use_aniso_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence anisotropy", default=False, update=refresh_preview)

    disney_aniso_tex = bpy.props.StringProperty(name="", description="Texture to influence anisotropy", default="", update=refresh_preview)

    disney_clearcoat = bpy.props.FloatProperty(name="Clear Coat", description="Clear coat", default=0, min=0, soft_max=10.0, update=refresh_preview)

    disney_use_clearcoat_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence clear coat", default=False,
                                                      update=refresh_preview)

    disney_clearcoat_tex = bpy.props.StringProperty(name="", description="Texture to influence clear coat", default="", update=refresh_preview)

    disney_clearcoat_gloss = bpy.props.FloatProperty(name="Clear Coat Gloss", description="Clear coat gloss", default=1, min=0, soft_max=1.0,
                                                     update=refresh_preview)

    disney_use_clearcoat_gloss_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence clear coat gloss", default=False,
                                                            update=refresh_preview)

    disney_clearcoat_gloss_tex = bpy.props.StringProperty(name="", description="Texture to influence clear coat gloss", default="",
                                                          update=refresh_preview)

    disney_metallic = bpy.props.FloatProperty(name="Metallic", description="Metalness", default=0, min=0, soft_max=1.0, update=refresh_preview)

    disney_use_metallic_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence metalness", default=False,
                                                     update=refresh_preview)

    disney_metallic_tex = bpy.props.StringProperty(name="", description="Texture to influence metalness", default="", update=refresh_preview)

    disney_roughness = bpy.props.FloatProperty(name="Roughness", description="Specular / metallic roughness", default=0.5, min=0, soft_max=1.0,
                                               update=refresh_preview)

    disney_use_roughness_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence roughness", default=False,
                                                      update=refresh_preview)

    disney_roughness_tex = bpy.props.StringProperty(name="", description="Texture to influence roughness", default="", update=refresh_preview)

    disney_sheen = bpy.props.FloatProperty(name="Sheen", description="Sheen", default=0, min=0, soft_max=1.0, update=refresh_preview)

    disney_use_sheen_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence sheen", default=False, update=refresh_preview)

    disney_sheen_tex = bpy.props.StringProperty(name="", description="Texture to influence sheen", default="", update=refresh_preview)

    disney_sheen_tint = bpy.props.FloatProperty(name="Sheen Tint", description="Sheen tint", default=0.5, min=0, soft_max=1.0, update=refresh_preview)

    disney_use_sheen_tint_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence sheen tint", default=False,
                                                       update=refresh_preview)

    disney_sheen_tint_tex = bpy.props.StringProperty(name="", description="Texture to influence sheen tint", default="", update=refresh_preview)

    disney_spec = bpy.props.FloatProperty(name="Specular", description="Specular", default=0.5, min=0, soft_max=1.0, update=refresh_preview)

    disney_use_spec_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence specular", default=False, update=refresh_preview)

    disney_spec_tex = bpy.props.StringProperty(name="", description="Texture to influence specular", default="", update=refresh_preview)

    disney_spec_tint = bpy.props.FloatProperty(name="Specular Tint", description="Specular tint", default=0, min=0, soft_max=1.0,
                                               update=refresh_preview)

    disney_use_spec_tint_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence specular tint", default=False,
                                                      update=refresh_preview)

    disney_spec_tint_tex = bpy.props.StringProperty(name="", description="Texture to influence specular tint", default="", update=refresh_preview)

    disney_subsurface = bpy.props.FloatProperty(name="Subsurface", description="Subsurface", default=0, min=0, soft_max=1.0, update=refresh_preview)

    disney_use_subsurface_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence subsurface", default=False,
                                                       update=refresh_preview)

    disney_subsurface_tex = bpy.props.StringProperty(name="", description="Texture to influence subsurface", default="", update=refresh_preview)

    disney_weight = bpy.props.FloatProperty(name="Disney BRDF Blending Weight",
                                            description="Blending weight of Disney BRDF in BSDF mix", default=1.0, min=0.0, max=1.0,
                                            update=refresh_preview)

    disney_use_tex = bpy.props.BoolProperty(name="", description="Use texture to influence the layer weight in the BSDF mix", default=False,
                                            update=refresh_preview)

    disney_mix_tex = bpy.props.StringProperty(name="", description="Texture to influence layer weight in the BSDF mix", default="",
                                              update=refresh_preview)


class AppleseedMatProps(bpy.types.PropertyGroup):
    """
    appleseed Material Properties.
    """

    # Per-layer properties are stored in AppleseedMatLayerProps.
    layers = bpy.props.CollectionProperty(type=AppleseedMatLayerProps,
                                          name="appleseed Material Layers",
                                          description="")

    layer_index = bpy.props.IntProperty(name="Layer Index", description="", default=0, min=0, max=16, update=refresh_preview)

    use_light_emission = bpy.props.BoolProperty(name="", description="Enable material light emission", default=False, update=refresh_preview)

    light_emission = bpy.props.FloatProperty(name="Emission Strength", description="Light emission strength", default=1.0, min=0.0, max=10000.0,
                                             update=refresh_preview)

    light_color = bpy.props.FloatVectorProperty(name="Emission Color", description="Light emission color",
                                                default=(0.8, 0.8, 0.8), subtype="COLOR", min=0.0, max=1.0, update=refresh_preview)

    importance_multiplier = bpy.props.FloatProperty(
        name="Importance Multiplier", description="Multiple importance sampling multiplier", default=1, min=0, soft_max=10, max=100,
        update=refresh_preview)

    cast_indirect = bpy.props.BoolProperty(name="Cast Indirect Light", description="Emissive material casts indirect light", default=True,
                                           update=refresh_preview)

    light_near_start = bpy.props.FloatProperty(
        name="Light Near Start", description="Amount by which to extend the start of light's influence away from the emissive material", default=0.0,
        min=0, max=10, update=refresh_preview)

    material_use_bump_tex = bpy.props.BoolProperty(name="", description="Use a texture to influence bump / normal", default=False,
                                                   update=refresh_preview)

    material_bump_tex = bpy.props.StringProperty(name="", description="Bump / normal texture", default="", update=refresh_preview)

    material_use_normalmap = bpy.props.BoolProperty(name="", description="Use texture as normal map", default=False, update=refresh_preview)

    material_bump_amplitude = bpy.props.FloatProperty(
        name="Bump Amplitude", description="Maximum height influence of bump / normal map", default=1.0, min=0.0, max=1.0, update=refresh_preview)

    material_use_alpha = bpy.props.BoolProperty(name="", description="Use a texture to influence alpha", default=False, update=refresh_preview)

    material_alpha_map = bpy.props.StringProperty(name="", description="Alpha texture", default="", update=refresh_preview)

    material_alpha = bpy.props.FloatProperty(name="Alpha", description="Alpha", default=1.0, min=0.0, max=1.0, update=refresh_preview)

    shade_alpha_cutouts = bpy.props.BoolProperty(name="Shade Alpha Cutout", description="Shade alpha cutout", default=False, update=refresh_preview)

    preview_quality = bpy.props.IntProperty(
        name="Preview Quality", description="Number of samples used for preview rendering", default=2, min=1, max=16, update=refresh_preview)

    # Nodes
    node_tree = bpy.props.StringProperty(name="Node Tree",
                                         description="Material node tree to link to the current material", update=refresh_preview)

    node_output = bpy.props.StringProperty(name="Output Node",
                                           description="Material node tree output node to link to the current material", update=refresh_preview)


def register():
    bpy.utils.register_class(AppleseedMatLayerProps)
    bpy.utils.register_class(AppleseedMatProps)
    bpy.types.Material.appleseed = bpy.props.PointerProperty(type=AppleseedMatProps)


def unregister():
    del bpy.types.Material.appleseed
    bpy.utils.unregister_class(AppleseedMatLayerProps)
    bpy.utils.unregister_class(AppleseedMatProps)
