
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


class AppleseedMatProps(bpy.types.PropertyGroup):

    bsdf_type = bpy.props.EnumProperty(name="BSDF Model",
                                       items=[('ashikhmin_brdf', "Ashikhmin-Shirley BRDF", ""),
                                              ('blinn_brdf', "Blinn BRDF", ""),
                                              ('diffuse_btdf', "Diffuse BTDF", ""),
                                              ('disney_brdf', "Disney BRDF", ""),
                                              ('glass_bsdf', "Glass BSDF", ""),
                                              ('glossy_brdf', "Glossy BRDF", ""),
                                              ('kelemen_brdf', "Kelemen BRDF", ""),
                                              ('lambertian_brdf', "Lambertian BRDF", ""),
                                              ('metal_brdf', "Metal BRDF", ""),
                                              ('orennayar_brdf', "Oren-Nayar BRDF", ""),
                                              ('plastic_brdf', "Plastic BRDF", ""),
                                              ('sheen_brdf', "Sheen BRDF", ""),
                                              ('specular_brdf', "Specular BRDF", ""),
                                              ('specular_btdf', "Specular BTDF", ""),
                                              ('none', "None", "")],
                                       description="BSDF model for current material layer",
                                       default="lambertian_brdf",
                                       update=refresh_preview)

    #
    # Ashikhmin-Shirley BRDF.
    #

    ashikhmin_brdf_reflectance = bpy.props.FloatVectorProperty(name="ashikhmin_brdf_reflectance",
                                                               description="Ashikhmin-Shirley diffuse reflectance",
                                                               default=(0.8, 0.8, 0.8),
                                                               subtype="COLOR",
                                                               min=0.0,
                                                               max=1.0,
                                                               update=refresh_preview)

    ashikhmin_brdf_use_diffuse_tex = bpy.props.BoolProperty(name="ashikhmin_brdf_use_diffuse_tex",
                                                            description="Use a texture to influence diffuse reflectance",
                                                            default=False,
                                                            update=refresh_preview)

    ashikhmin_brdf_diffuse_tex = bpy.props.StringProperty(name="ashikhmin_brdf_diffuse_tex",
                                                          description="Diffuse reflectance texture",
                                                          default="",
                                                          update=refresh_preview)

    ashikhmin_brdf_multiplier = bpy.props.FloatProperty(name="ashikhmin_brdf_multiplier",
                                                        description="Ashikhmin-Shirley diffuse reflectance multiplier",
                                                        default=1.0,
                                                        min=0.0,
                                                        max=1.0,
                                                        update=refresh_preview)

    ashikhmin_brdf_fresnel = bpy.props.FloatProperty(name="ashikhmin_brdf_fresnel",
                                                     description="",
                                                     default=1.0,
                                                     min=0.0,
                                                     max=2.0,
                                                     update=refresh_preview)

    ashikhmin_brdf_glossy = bpy.props.FloatVectorProperty(name="ashikhmin_brdf_glossy",
                                                          description="Ashikhmin-Shirley glossy reflectance",
                                                          default=(0.8, 0.8, 0.8),
                                                          subtype="COLOR",
                                                          min=0.0,
                                                          max=1.0,
                                                          update=refresh_preview)

    ashikhmin_brdf_use_glossy_tex = bpy.props.BoolProperty(name="ashikhmin_brdf_use_glossy_tex",
                                                           description="Use a texture to influence gglossy reflectance",
                                                           default=False,
                                                           update=refresh_preview)

    ashikhmin_brdf_glossy_tex = bpy.props.StringProperty(name="ashikhmin_brdf_glossy_tex",
                                                         description="Texture to influence glossy reflectance",
                                                         default="",
                                                         update=refresh_preview)

    ashikhmin_brdf_glossy_multiplier = bpy.props.FloatProperty(name="ashikhmin_brdf_glossy_multiplier",
                                                               description="Ashikhmin-Shirley glossy reflectance multiplier",
                                                               default=1.0,
                                                               min=0.0,
                                                               max=1.0,
                                                               update=refresh_preview)

    ashikhmin_brdf_shininess_u = bpy.props.FloatProperty(name="ashikhmin_brdf_shininess_u",
                                                         description="",
                                                         default=200.0,
                                                         min=0.0,
                                                         max=1000.0,
                                                         update=refresh_preview)

    ashikhmin_brdf_shininess_v = bpy.props.FloatProperty(name="ashikhmin_brdf_shininess_u",
                                                         description="",
                                                         default=200.0,
                                                         min=0.0,
                                                         max=1000.0,
                                                         update=refresh_preview)

    #
    # Blinn BRDF.
    #

    blinn_brdf_exponent = bpy.props.FloatProperty(name="blinn_brdf_exponent",
                                                  description="Blinn exponent",
                                                  default=0.8,
                                                  min=0.0,
                                                  update=refresh_preview)

    blinn_brdf_exponent_use_tex = bpy.props.BoolProperty(name="blinn_brdf_exponent_use_tex",
                                                         description="Use a texture to influence exponent color",
                                                         default=False,
                                                         update=refresh_preview)

    blinn_brdf_exponent_tex = bpy.props.StringProperty(name="blinn_brdf_exponent_tex",
                                                       description="Exponent color texture",
                                                       default="",
                                                       update=refresh_preview)

    blinn_brdf_ior = bpy.props.FloatProperty(name="blinn_brdf_ior",
                                             description="Index of refraction",
                                             default=1.5,
                                             min=1,
                                             max=2.5,
                                             update=refresh_preview)

    #
    # Diffuse BTDF.
    #

    diffuse_btdf_transmittance_multiplier = bpy.props.FloatProperty(name="diffuse_btdf_transmittance_multiplier",
                                                                    description="Multiplier for material transmittance",
                                                                    default=1.0,
                                                                    min=0.0,
                                                                    max=2.0,
                                                                    update=refresh_preview)

    diffuse_btdf_transmittance_use_mult_tex = bpy.props.BoolProperty(name="diffuse_btdf_transmittance_use_mult_tex",
                                                                     description="Use texture to influence transmittance",
                                                                     default=False,
                                                                     update=refresh_preview)

    diffuse_btdf_transmittance_mult_tex = bpy.props.StringProperty(name="diffuse_btdf_transmittance_mult_tex",
                                                                   description="Texture to influence transmittance",
                                                                   default="",
                                                                   update=refresh_preview)

    diffuse_btdf_transmittance_color = bpy.props.FloatVectorProperty(name="diffuse_btdf_transmittance_color",
                                                                     description="Transmittance color",
                                                                     default=(0.8, 0.8, 0.8),
                                                                     subtype='COLOR',
                                                                     min=0.0,
                                                                     max=1.0,
                                                                     update=refresh_preview)

    diffuse_btdf_use_diffuse_tex = bpy.props.BoolProperty(name="diffuse_btdf_use_diffuse_tex",
                                                          description="Use texture to influence diffuse color",
                                                          default=False,
                                                          update=refresh_preview)

    diffuse_btdf_diffuse_tex = bpy.props.StringProperty(name="diffuse_btdf_diffuse_tex",
                                                        description="Texture to influence diffuse color",
                                                        default="",
                                                        update=refresh_preview)

    #
    # Disney BRDF.
    #

    disney_brdf_base = bpy.props.FloatVectorProperty(name="disney_brdf_base",
                                                     description="Base coat color",
                                                     default=(0.8, 0.8, 0.8),
                                                     subtype='COLOR',
                                                     min=0.0,
                                                     max=1.0,
                                                     update=refresh_preview)

    disney_brdf_use_base_tex = bpy.props.BoolProperty(name="disney_brdf_use_base_tex",
                                                      description="Use a texture to influence base coat color",
                                                      default=False,
                                                      update=refresh_preview)

    disney_brdf_base_tex = bpy.props.StringProperty(name="disney_brdf_base_tex",
                                                    description="Texture to influence base coat color",
                                                    default="",
                                                    update=refresh_preview)

    disney_brdf_anisotropy = bpy.props.FloatProperty(name="disney_brdf_anisotropy",
                                                     description="Anisotropic",
                                                     default=0,
                                                     min=0,
                                                     soft_max=1.0,
                                                     update=refresh_preview)

    disney_brdf_use_anisotropy_tex = bpy.props.BoolProperty(name="disney_brdf_use_anisotropy_tex",
                                                            description="Use a texture to influence anisotropy",
                                                            default=False,
                                                            update=refresh_preview)

    disney_brdf_anisotropy_tex = bpy.props.StringProperty(name="disney_brdf_anisotropy_tex",
                                                          description="Texture to influence anisotropy",
                                                          default="",
                                                          update=refresh_preview)

    disney_brdf_clearcoat = bpy.props.FloatProperty(name="disney_brdf_clearcoat",
                                                    description="Clear coat",
                                                    default=0,
                                                    min=0,
                                                    soft_max=10.0,
                                                    update=refresh_preview)

    disney_brdf_use_clearcoat_tex = bpy.props.BoolProperty(name="disney_brdf_use_clearcoat_tex",
                                                           description="Use a texture to influence clear coat",
                                                           default=False,
                                                           update=refresh_preview)

    disney_brdf_clearcoat_tex = bpy.props.StringProperty(name="disney_brdf_clearcoat_tex",
                                                         description="Texture to influence clear coat",
                                                         default="",
                                                         update=refresh_preview)

    disney_brdf_clearcoat_gloss = bpy.props.FloatProperty(name="disney_brdf_clearcoat_gloss",
                                                          description="Clear coat gloss",
                                                          default=1,
                                                          min=0,
                                                          soft_max=1.0,
                                                          update=refresh_preview)

    disney_brdf_use_clearcoat_glossy_tex = bpy.props.BoolProperty(name="disney_brdf_use_clearcoat_glossy_tex",
                                                                  description="Use a texture to influence clear coat gloss",
                                                                  default=False,
                                                                  update=refresh_preview)

    disney_brdf_clearcoat_glossy_tex = bpy.props.StringProperty(name="disney_brdf_clearcoat_glossy_tex",
                                                                description="Texture to influence clear coat gloss",
                                                                default="",
                                                                update=refresh_preview)

    disney_brdf_metallic = bpy.props.FloatProperty(name="disney_brdf_metallic",
                                                   description="Metalness",
                                                   default=0,
                                                   min=0,
                                                   soft_max=1.0,
                                                   update=refresh_preview)

    disney_brdf_use_metallic_tex = bpy.props.BoolProperty(name="disney_brdf_use_metallic_tex",
                                                          description="Use a texture to influence metalness",
                                                          default=False,
                                                          update=refresh_preview)

    disney_brdf_metallic_tex = bpy.props.StringProperty(name="disney_brdf_metallic_tex",
                                                        description="Texture to influence metalness",
                                                        default="",
                                                        update=refresh_preview)

    disney_brdf_roughness = bpy.props.FloatProperty(name="disney_brdf_roughness",
                                                    description="Specular / metallic roughness",
                                                    default=0.5,
                                                    min=0,
                                                    soft_max=1.0,
                                                    update=refresh_preview)

    disney_brdf_use_roughness_tex = bpy.props.BoolProperty(name="disney_brdf_use_roughness_tex",
                                                           description="Use a texture to influence roughness",
                                                           default=False,
                                                           update=refresh_preview)

    disney_brdf_roughness_tex = bpy.props.StringProperty(name="disney_brdf_roughness_tex",
                                                         description="Texture to influence roughness",
                                                         default="",
                                                         update=refresh_preview)

    disney_brdf_sheen = bpy.props.FloatProperty(name="disney_brdf_sheen",
                                                description="Sheen",
                                                default=0,
                                                min=0,
                                                soft_max=1.0,
                                                update=refresh_preview)

    disney_brdf_use_sheen_brdf_tex = bpy.props.BoolProperty(name="disney_brdf_use_sheen_brdf_tex",
                                                            description="Use a texture to influence sheen",
                                                            default=False,
                                                            update=refresh_preview)

    disney_brdf_sheen_brdf_tex = bpy.props.StringProperty(name="disney_brdf_sheen_brdf_tex",
                                                          description="Texture to influence sheen",
                                                          default="",
                                                          update=refresh_preview)

    disney_brdf_sheen_brdf_tint = bpy.props.FloatProperty(name="disney_brdf_sheen_brdf_tint",
                                                          description="Sheen tint",
                                                          default=0.5,
                                                          min=0,
                                                          soft_max=1.0,
                                                          update=refresh_preview)

    disney_brdf_use_sheen_brdf_tint_tex = bpy.props.BoolProperty(name="disney_brdf_use_sheen_brdf_tint_tex",
                                                                 description="Use a texture to influence sheen tint",
                                                                 default=False,
                                                                 update=refresh_preview)

    disney_brdf_sheen_brdf_tint_tex = bpy.props.StringProperty(name="disney_brdf_sheen_brdf_tint_tex",
                                                               description="Texture to influence sheen tint",
                                                               default="",
                                                               update=refresh_preview)

    disney_brdf_spec = bpy.props.FloatProperty(name="disney_brdf_spec",
                                               description="Specular",
                                               default=0.5,
                                               min=0,
                                               soft_max=1.0,
                                               update=refresh_preview)

    disney_brdf_use_specular_tex = bpy.props.BoolProperty(name="disney_brdf_use_specular_tex",
                                                          description="Use a texture to influence specular",
                                                          default=False,
                                                          update=refresh_preview)

    disney_brdf_specular_tex = bpy.props.StringProperty(name="disney_brdf_specular_tex",
                                                        description="Texture to influence specular",
                                                        default="",
                                                        update=refresh_preview)

    disney_brdf_specular_tint = bpy.props.FloatProperty(name="disney_brdf_specular_tint",
                                                        description="Specular tint",
                                                        default=0,
                                                        min=0,
                                                        soft_max=1.0,
                                                        update=refresh_preview)

    disney_brdf_use_specular_tint_tex = bpy.props.BoolProperty(name="disney_brdf_use_specular_tint_tex",
                                                               description="Use a texture to influence specular tint",
                                                               default=False,
                                                               update=refresh_preview)

    disney_brdf_specular_tint_tex = bpy.props.StringProperty(name="disney_brdf_specular_tint_tex",
                                                             description="Texture to influence specular tint",
                                                             default="",
                                                             update=refresh_preview)

    disney_brdf_subsurface = bpy.props.FloatProperty(name="disney_brdf_subsurface",
                                                     description="Subsurface",
                                                     default=0,
                                                     min=0,
                                                     soft_max=1.0,
                                                     update=refresh_preview)

    disney_brdf_use_subsurface_tex = bpy.props.BoolProperty(name="disney_brdf_use_subsurface_tex",
                                                            description="Use a texture to influence subsurface",
                                                            default=False,
                                                            update=refresh_preview)

    disney_brdf_subsurface_tex = bpy.props.StringProperty(name="disney_brdf_subsurface_tex",
                                                          description="Texture to influence subsurface",
                                                          default="",
                                                          update=refresh_preview)

    #
    # Glass BSDF.
    #

    glass_bsdf_mdf = bpy.props.EnumProperty(name="Microfacet Type",
                                            description="Microfacet distribution",
                                            items=[('beckmann', "Beckmann", ""),
                                                   ('ggx', "GGX", ""),
                                                   ('std', "STD", "")],
                                            default='ggx',
                                            update=refresh_preview)

    glass_bsdf_surface_transmittance = bpy.props.FloatVectorProperty(name="glass_bsdf_surface_transmittance",
                                                                     description="Glass transmittance",
                                                                     default=(0.8, 0.8, 0.8),
                                                                     subtype="COLOR",
                                                                     min=0.0,
                                                                     max=1.0,
                                                                     update=refresh_preview)

    glass_bsdf_surface_transmittance_use_tex = bpy.props.BoolProperty(name="glass_bsdf_surface_transmittance_use_tex",
                                                                      description="Use a texture to influence surface transmittance",
                                                                      default=False,
                                                                      update=refresh_preview)

    glass_bsdf_surface_transmittance_tex = bpy.props.StringProperty(name="glass_bsdf_surface_transmittance_tex",
                                                                    description="Transmittance texture",
                                                                    default="",
                                                                    update=refresh_preview)

    glass_bsdf_surface_transmittance_multiplier = bpy.props.FloatProperty(name="glass_bsdf_surface_transmittance_multiplier",
                                                                          description="Glass surface transmittance multiplier",
                                                                          default=1.0,
                                                                          min=0.0,
                                                                          max=1.0,
                                                                          update=refresh_preview)

    glass_bsdf_surface_transmittance_multiplier_use_tex = bpy.props.BoolProperty(name="glass_bsdf_surface_transmittance_multiplier_use_tex",
                                                                                 description="Use a texture to influence the surface transmittance multiplier",
                                                                                 default=False,
                                                                                 update=refresh_preview)

    glass_bsdf_surface_transmittance_multiplier_tex = bpy.props.StringProperty(name="glass_bsdf_surface_transmittance_multiplier_tex",
                                                                               description="Transmittance multiplier texture",
                                                                               default="",
                                                                               update=refresh_preview)

    glass_bsdf_reflection_tint = bpy.props.FloatVectorProperty(name="glass_bsdf_reflection_tint",
                                                               description="Glass reflection tint",
                                                               default=(0.8, 0.8, 0.8),
                                                               subtype="COLOR",
                                                               min=0.0,
                                                               max=1.0,
                                                               update=refresh_preview)

    glass_bsdf_reflection_tint_use_tex = bpy.props.BoolProperty(name="glass_bsdf_reflection_tint_use_tex",
                                                                description="Use a texture to influence the reflection tint",
                                                                default=False,
                                                                update=refresh_preview)

    glass_bsdf_reflection_tint_tex = bpy.props.StringProperty(name="glass_bsdf_reflection_tint_tex",
                                                              description="Reflection tint texture",
                                                              default="",
                                                              update=refresh_preview)

    glass_bsdf_refraction_tint = bpy.props.FloatVectorProperty(name="glass_bsdf_refraction_tint",
                                                               description="Glass refraction tint",
                                                               default=(0.8, 0.8, 0.8),
                                                               subtype="COLOR",
                                                               min=0.0,
                                                               max=1.0,
                                                               update=refresh_preview)

    glass_bsdf_refraction_tint_use_tex = bpy.props.BoolProperty(name="glass_bsdf_refraction_tint_use_tex",
                                                                description="Use a texture to influence the refraction tint",
                                                                default=False,
                                                                update=refresh_preview)

    glass_bsdf_refraction_tint_tex = bpy.props.StringProperty(name="glass_bsdf_refraction_tint_tex",
                                                              description="Refraction tint texture",
                                                              default="",
                                                              update=refresh_preview)

    glass_bsdf_ior = bpy.props.FloatProperty(name="glass_bsdf_ior",
                                             description="Glass index of refraction",
                                             default=1.5,
                                             min=1.0,
                                             max=2.5,
                                             update=refresh_preview)

    glass_bsdf_roughness = bpy.props.FloatProperty(name="glass_bsdf_roughness",
                                                   description="Glass roughness",
                                                   default=0.15,
                                                   min=0.0,
                                                   max=1.0,
                                                   update=refresh_preview)

    glass_bsdf_roughness_use_tex = bpy.props.BoolProperty(name="glass_bsdf_roughness_use_tex",
                                                          description="Use a texture to influence the roughness",
                                                          default=False,
                                                          update=refresh_preview)

    glass_bsdf_roughness_tex = bpy.props.StringProperty(name="glass_bsdf_roughness_tex",
                                                        description="Roughness texture",
                                                        default="",
                                                        update=refresh_preview)

    glass_bsdf_highlight_falloff = bpy.props.FloatProperty(name="glass_bsdf_highlight_falloff",
                                                           description="Glass highlight falloff",
                                                           default=0.4,
                                                           min=0.0,
                                                           max=1.0,
                                                           update=refresh_preview)

    glass_bsdf_anisotropy = bpy.props.FloatProperty(name="glass_bsdf_anisotropy",
                                                    description="Glass anisotropy",
                                                    default=0.0, min=-1.0, max=1.0,
                                                    update=refresh_preview)

    glass_bsdf_anisotropy_use_tex = bpy.props.BoolProperty(name="glass_bsdf_anisotropy_use_tex",
                                                           description="Use a texture to influence the anisotropy",
                                                           default=False,
                                                           update=refresh_preview)

    glass_bsdf_anisotropy_tex = bpy.props.StringProperty(name="glass_bsdf_anisotropy_tex",
                                                         description="Anisotropy texture",
                                                         default="",
                                                         update=refresh_preview)

    glass_bsdf_volume_parameterization = bpy.props.EnumProperty(name="Volume Type",
                                                                items=[('absorption', "Absorption", ""),
                                                                       ('transmittance', "Transmittance", "")],
                                                                default='transmittance',
                                                                update=refresh_preview)

    glass_bsdf_volume_transmittance = bpy.props.FloatVectorProperty(name="glass_bsdf_volume_transmittance",
                                                                    description="Glass volume transmittance",
                                                                    default=(1.0, 1.0, 1.0),
                                                                    subtype="COLOR",
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    update=refresh_preview)

    glass_bsdf_volume_transmittance_use_tex = bpy.props.BoolProperty(name="glass_bsdf_volume_transmittance_use_tex",
                                                                     description="Use a texture to influence the volume transmittance",
                                                                     default=False,
                                                                     update=refresh_preview)

    glass_bsdf_volume_transmittance_tex = bpy.props.StringProperty(name="glass_bsdf_volume_transmittance_tex",
                                                                   description="Volume transmittance texture",
                                                                   default="",
                                                                   update=refresh_preview)

    glass_bsdf_volume_transmittance_distance = bpy.props.FloatProperty(name="glass_bsdf_volume_transmittance_distance",
                                                                       description="Glass volume transmittance distance",
                                                                       default=0.0,
                                                                       min=0.0,
                                                                       max=10.0,
                                                                       update=refresh_preview)

    glass_bsdf_volume_transmittance_distance_use_tex = bpy.props.BoolProperty(name="glass_bsdf_volume_transmittance_distance_use_tex",
                                                                              description="Use a texture to influence the volume transmittance distance",
                                                                              default=False,
                                                                              update=refresh_preview)

    glass_bsdf_volume_transmittance_distance_tex = bpy.props.StringProperty(name="glass_bsdf_volume_transmittance_distance_tex",
                                                                            description="Volume transmittance distance texture",
                                                                            default="",
                                                                            update=refresh_preview)

    glass_bsdf_volume_absorption = bpy.props.FloatVectorProperty(name="glass_bsdf_volume_absorption",
                                                                 description="Glass volume absorption",
                                                                 default=(0.0, 0.0, 0.0),
                                                                 subtype="COLOR",
                                                                 min=0.0,
                                                                 max=1.0,
                                                                 update=refresh_preview)

    glass_bsdf_volume_absorption_use_tex = bpy.props.BoolProperty(name="glass_bsdf_volume_absorption_use_tex",
                                                                  description="Use a texture to influence the volume absorption",
                                                                  default=False,
                                                                  update=refresh_preview)

    glass_bsdf_volume_absorption_tex = bpy.props.StringProperty(name="glass_bsdf_volume_absorption_tex",
                                                                description="Volume absorption texture",
                                                                default="",
                                                                update=refresh_preview)

    glass_bsdf_volume_density = bpy.props.FloatProperty(name="glass_bsdf_volume_density",
                                                        description="Glass volume density",
                                                        default=0.0,
                                                        min=0.0,
                                                        soft_max=10.0,
                                                        update=refresh_preview)

    glass_bsdf_volume_density_use_tex = bpy.props.BoolProperty(name="glass_bsdf_volume_density_use_tex",
                                                               description="Use a texture to influence the volume density",
                                                               default=False,
                                                               update=refresh_preview)

    glass_bsdf_volume_density_tex = bpy.props.StringProperty(name="glass_bsdf_volume_density_tex",
                                                             description="Volume density texture",
                                                             default="",
                                                             update=refresh_preview)

    glass_bsdf_volume_scale = bpy.props.FloatProperty(name="glass_bsdf_volume_scale",
                                                      description="Scale of the glass volume",
                                                      default=1.0,
                                                      min=0.0,
                                                      soft_max=10.0,
                                                      update=refresh_preview)

    #
    # Glossy BRDF.
    #

    glossy_brdf_mdf = bpy.props.EnumProperty(name="Microfacet Type",
                                             description="",
                                             items=[('beckmann', "Beckmann", ""),
                                                    ('ggx', "GGX", ""),
                                                    ('std', "STD", "")],
                                             default='ggx',
                                             update=refresh_preview)

    glossy_brdf_reflectance = bpy.props.FloatVectorProperty(name="glossy_brdf_reflectance",
                                                            description="Reflection",
                                                            subtype='COLOR',
                                                            min=0.0,
                                                            max=1.0,
                                                            default=(0.75, 0.75, 0.75),
                                                            update=refresh_preview)

    glossy_brdf_reflectance_use_tex = bpy.props.BoolProperty(name="glossy_brdf_reflectance_use_tex",
                                                             description="Use a texture to influence the reflectance",
                                                             default=False,
                                                             update=refresh_preview)

    glossy_brdf_reflectance_tex = bpy.props.StringProperty(name="glossy_brdf_reflectance_tex",
                                                           description="Reflectance texture",
                                                           default="",
                                                           update=refresh_preview)

    glossy_brdf_reflectance_multiplier = bpy.props.FloatProperty(name="glossy_brdf_reflectance_multiplier",
                                                                 description="Reflection multiplier",
                                                                 min=0.0,
                                                                 max=1.0,
                                                                 default=1.0,
                                                                 update=refresh_preview)

    glossy_brdf_reflectance_multiplier_use_tex = bpy.props.BoolProperty(name="glossy_brdf_reflectance_multiplier_use_tex",
                                                                        description="Use a texture to influence the reflectance multiplier",
                                                                        default=False,
                                                                        update=refresh_preview)

    glossy_brdf_reflectance_multiplier_tex = bpy.props.StringProperty(name="glossy_brdf_reflectance_multiplier_tex",
                                                                      description="Reflectance multiplier texture",
                                                                      default="",
                                                                      update=refresh_preview)

    glossy_brdf_roughness = bpy.props.FloatProperty(name="glossy_brdf_roughness",
                                                    description="Roughness",
                                                    min=0.0,
                                                    max=1.0,
                                                    default=0.15,
                                                    update=refresh_preview)

    glossy_brdf_roughness_use_tex = bpy.props.BoolProperty(name="glossy_brdf_roughness_use_tex",
                                                           description="Use a texture to influence the roughness",
                                                           default=False,
                                                           update=refresh_preview)

    glossy_brdf_roughness_tex = bpy.props.StringProperty(name="glossy_brdf_roughness_tex",
                                                         description="Roughness texture",
                                                         default="",
                                                         update=refresh_preview)

    glossy_brdf_highlight_falloff = bpy.props.FloatProperty(name="glossy_brdf_highlight_falloff",
                                                            description="",
                                                            default=0.4,
                                                            min=0.0,
                                                            max=1.0,
                                                            update=refresh_preview)

    glossy_brdf_anisotropy = bpy.props.FloatProperty(name="glossy_brdf_anisotropy",
                                                     description="Anisotropy",
                                                     min=-1.0,
                                                     max=1.0,
                                                     default=0.0,
                                                     update=refresh_preview)

    glossy_brdf_anisotropy_use_tex = bpy.props.BoolProperty(name="glossy_brdf_anisotropy_use_tex",
                                                            description="Use a texture to influence the anisotropy",
                                                            default=False,
                                                            update=refresh_preview)

    glossy_brdf_anisotropy_tex = bpy.props.StringProperty(name="glossy_brdf_anisotropy_tex",
                                                          description="Anisotropy texture",
                                                          default="",
                                                          update=refresh_preview)

    glossy_brdf_ior = bpy.props.FloatProperty(name="glossy_brdf_ior",
                                              description="Glossy index of refraction",
                                              default=1.5,
                                              min=1.0,
                                              max=2.5,
                                              update=refresh_preview)

    #
    # Kelemen BRDF.
    #

    kelemen_brdf_matte_reflectance = bpy.props.FloatVectorProperty(name="kelemen_brdf_matte_reflectance",
                                                                   description="Kelemen matte reflectance",
                                                                   default=(0.8, 0.8, 0.8),
                                                                   subtype='COLOR',
                                                                   min=0.0,
                                                                   max=1.0,
                                                                   update=refresh_preview)

    kelemen_brdf_use_diffuse_tex = bpy.props.BoolProperty(name="kelemen_brdf_use_diffuse_tex",
                                                          description="Use texture to influence matte reflectance",
                                                          default=False,
                                                          update=refresh_preview)

    kelemen_brdf_diffuse_tex = bpy.props.StringProperty(name="kelemen_brdf_diffuse_tex",
                                                        description="Texture to influence matte reflectance",
                                                        default="",
                                                        update=refresh_preview)

    kelemen_brdf_matte_multiplier = bpy.props.FloatProperty(name="kelemen_brdf_matte_multiplier",
                                                            description="Kelemen matte reflectance multiplier",
                                                            default=1.0,
                                                            min=0.0,
                                                            max=1.0,
                                                            update=refresh_preview)

    kelemen_brdf_roughness = bpy.props.FloatProperty(name="kelemen_brdf_roughness",
                                                     description="Kelemen roughness",
                                                     default=0.0,
                                                     min=0.0,
                                                     max=1.0,
                                                     update=refresh_preview)

    kelemen_brdf_specular_reflectance = bpy.props.FloatProperty(name="kelemen_brdf_specular_reflectance",
                                                                description="Kelemen specular reflectance",
                                                                default=0.8,
                                                                min=0.0,
                                                                max=1.0,
                                                                update=refresh_preview)

    kelemen_brdf_specular_multiplier = bpy.props.FloatProperty(name="kelemen_brdf_specular_multiplier",
                                                               description="Kelemen specular reflectance multiplier",
                                                               default=1.0,
                                                               min=0.0,
                                                               max=1.0,
                                                               update=refresh_preview)

    #
    # Lambertian BRDF.
    #

    lambertian_brdf_reflectance = bpy.props.FloatVectorProperty(name="lambertian_brdf_reflectance",
                                                                description="Lambertian diffuse reflectance",
                                                                default=(0.8, 0.8, 0.8),
                                                                subtype="COLOR",
                                                                min=0.0,
                                                                max=1.0,
                                                                update=refresh_preview)

    lambertian_brdf_multiplier = bpy.props.FloatProperty(name="lambertian_brdf_multiplier",
                                                         description="Lambertian reflectance multiplier",
                                                         default=1.0,
                                                         min=0.0,
                                                         max=2.0,
                                                         update=refresh_preview)

    lambertian_brdf_use_diffuse_tex = bpy.props.BoolProperty(name="lambertian_brdf_use_diffuse_tex",
                                                             description="Use a texture to influence diffuse color",
                                                             default=False,
                                                             update=refresh_preview)

    lambertian_brdf_diffuse_tex = bpy.props.StringProperty(name="lambertian_brdf_diffuse_tex",
                                                           description="Diffuse color texture",
                                                           default="",
                                                           update=refresh_preview)

    #
    # Metal BRDF.
    #

    metal_brdf_mdf = bpy.props.EnumProperty(name="Microfacet Type",
                                            description="",
                                            items=[('beckmann', "Beckmann", ""),
                                                   ('ggx', "GGX", ""),
                                                   ('std', "STD", "")],
                                            default='ggx',
                                            update=refresh_preview)

    metal_brdf_normal_reflectance = bpy.props.FloatVectorProperty(name="metal_brdf_normal_reflectance",
                                                                  description="Reflectance facing the camera",
                                                                  subtype='COLOR',
                                                                  min=0.0,
                                                                  max=1.0,
                                                                  default=(0.92, 0.92, 0.92),
                                                                  update=refresh_preview)

    metal_brdf_normal_reflectance_use_tex = bpy.props.BoolProperty(name="metal_brdf_normal_reflectance_use_tex",
                                                                   description="Use a texture to influence the normal reflectance",
                                                                   default=False,
                                                                   update=refresh_preview)

    metal_brdf_normal_reflectance_tex = bpy.props.StringProperty(name="metal_brdf_normal_reflectance_tex",
                                                                 description="Normal reflectance texture",
                                                                 default="",
                                                                 update=refresh_preview)

    metal_brdf_edge_tint = bpy.props.FloatVectorProperty(name="metal_brdf_edge_tint",
                                                         description="Tint at glancing angle",
                                                         subtype='COLOR',
                                                         min=0.0,
                                                         max=1.0,
                                                         default=(0.98, 0.98, 0.98),
                                                         update=refresh_preview)

    metal_brdf_edge_tint_use_tex = bpy.props.BoolProperty(name="metal_brdf_edge_tint_use_tex",
                                                          description="Use a texture to influence the edge tint",
                                                          default=False,
                                                          update=refresh_preview)

    metal_brdf_edge_tint_tex = bpy.props.StringProperty(name="metal_brdf_edge_tint_tex",
                                                        description="Edge tint texture",
                                                        default="",
                                                        update=refresh_preview)

    metal_brdf_reflectance_multiplier = bpy.props.FloatProperty(name="metal_brdf_reflectance_multiplier",
                                                                description="",
                                                                min=0.0,
                                                                max=1.0,
                                                                default=1.0,
                                                                update=refresh_preview)

    metal_brdf_reflectance_multiplier_use_tex = bpy.props.BoolProperty(name="metal_brdf_reflectance_multiplier_use_tex",
                                                                       description="Use a texture to influence the reflectance multiplier",
                                                                       default=False,
                                                                       update=refresh_preview)

    metal_brdf_reflectance_multiplier_tex = bpy.props.StringProperty(name="metal_brdf_reflectance_multiplier_tex",
                                                                     description="Reflectance multiplier texture",
                                                                     default="",
                                                                     update=refresh_preview)

    metal_brdf_roughness = bpy.props.FloatProperty(name="metal_brdf_roughness",
                                                   description="Roughness",
                                                   min=0.0,
                                                   max=1.0,
                                                   default=0.15,
                                                   update=refresh_preview)

    metal_brdf_roughness_use_tex = bpy.props.BoolProperty(name="metal_brdf_roughness_use_tex",
                                                          description="Use a texture to influence the roughness",
                                                          default=False,
                                                          update=refresh_preview)

    metal_brdf_roughness_tex = bpy.props.StringProperty(name="metal_brdf_roughness_tex",
                                                        description="Roughness texture",
                                                        default="",
                                                        update=refresh_preview)

    metal_brdf_highlight_falloff = bpy.props.FloatProperty(name="metal_brdf_highlight_falloff",
                                                           description="",
                                                           default=0.4,
                                                           min=0.0,
                                                           max=1.0,
                                                           update=refresh_preview)

    metal_brdf_anisotropy = bpy.props.FloatProperty(name="metal_brdf_anisotropy",
                                                    description="",
                                                    default=0.0,
                                                    min=-1.0,
                                                    max=1.0,
                                                    update=refresh_preview)

    metal_brdf_anisotropy_use_tex = bpy.props.BoolProperty(name="metal_brdf_anisotropy_use_tex",
                                                           description="Use a texture to influence the anisotropy",
                                                           default=False,
                                                           update=refresh_preview)

    metal_brdf_anisotropy_tex = bpy.props.StringProperty(name="metal_brdf_anisotropy_tex",
                                                         description="Anisotropy texture",
                                                         default="",
                                                         update=refresh_preview)

    #
    # Oren-Nayar BRDF.
    #

    orennayar_brdf_use_diffuse_tex = bpy.props.BoolProperty(name="orennayar_brdf_use_diffuse_tex",
                                                            description="Use a texture to influence diffuse color",
                                                            default=False,
                                                            update=refresh_preview)

    orennayar_brdf_reflectance = bpy.props.FloatVectorProperty(name="orennayar_brdf_reflectance",
                                                               description="Oren-Nayar diffuse reflectance",
                                                               default=(0.8, 0.8, 0.8),
                                                               subtype="COLOR",
                                                               min=0.0,
                                                               max=1.0,
                                                               update=refresh_preview)

    orennayar_brdf_diffuse_tex = bpy.props.StringProperty(name="orennayar_brdf_diffuse_tex",
                                                          description="Diffuse color texture",
                                                          default="",
                                                          update=refresh_preview)

    orennayar_brdf_reflectance_multiplier = bpy.props.FloatProperty(name="orennayar_brdf_reflectance_multiplier",
                                                                    description="Reflectance multiplier",
                                                                    default=1.0,
                                                                    min=0.0,
                                                                    max=1.0,
                                                                    update=refresh_preview)

    orennayar_brdf_use_reflect_multiplier_tex = bpy.props.BoolProperty(name="orennayar_brdf_use_rough_tex",
                                                                       description="Use a texture to influence roughness",
                                                                       default=False,
                                                                       update=refresh_preview)

    orennayar_brdf_reflect_multiplier_tex = bpy.props.StringProperty(name="orennayar_brdf_rough_tex",
                                                                     description="Roughness texture",
                                                                     default="",
                                                                     update=refresh_preview)

    orennayar_brdf_roughness = bpy.props.FloatProperty(name="orennayar_brdf_roughness",
                                                       description="Oren-Nayar roughness",
                                                       default=0.5,
                                                       min=0.0,
                                                       max=1.0,
                                                       update=refresh_preview)

    orennayar_brdf_use_rough_tex = bpy.props.BoolProperty(name="orennayar_brdf_use_rough_tex",
                                                          description="Use a texture to influence roughness",
                                                          default=False,
                                                          update=refresh_preview)

    orennayar_brdf_rough_tex = bpy.props.StringProperty(name="orennayar_brdf_rough_tex",
                                                        description="Roughness texture",
                                                        default="",
                                                        update=refresh_preview)

    #
    # Plastic BRDF.
    #

    plastic_brdf_mdf = bpy.props.EnumProperty(name="Microfacet Type",
                                              description="",
                                              items=[('beckmann', "Beckmann", ""),
                                                     ('ggx', "GGX", ""),
                                                     ('std', "STD", ""),
                                                     ('gtr1', "GTR1", "")],
                                              default='ggx',
                                              update=refresh_preview)

    plastic_brdf_specular_reflectance = bpy.props.FloatVectorProperty(name="plastic_brdf_specular_reflectance",
                                                                      description="Specular reflection",
                                                                      subtype='COLOR',
                                                                      min=0.0,
                                                                      max=1.0,
                                                                      default=(0.8, 0.8, 0.8),
                                                                      update=refresh_preview)

    plastic_brdf_specular_reflectance_use_tex = bpy.props.BoolProperty(name="plastic_brdf_specular_reflectance_use_tex",
                                                                       description="Use a texture to influence the specular reflectance",
                                                                       default=False,
                                                                       update=refresh_preview)

    plastic_brdf_specular_reflectance_tex = bpy.props.StringProperty(name="plastic_brdf_specular_reflectance_tex",
                                                                     description="Specular reflectance texture",
                                                                     default="",
                                                                     update=refresh_preview)

    plastic_brdf_specular_reflectance_multiplier = bpy.props.FloatProperty(name="plastic_brdf_specular_reflectance_multiplier",
                                                                           description="Specular reflection multiplier",
                                                                           min=0.0,
                                                                           max=1.0,
                                                                           default=1.0,
                                                                           update=refresh_preview)

    plastic_brdf_specular_reflectance_multiplier_use_tex = bpy.props.BoolProperty(name="plastic_brdf_specular_reflectance_multiplier_use_tex",
                                                                                  description="Use a texture to influence the specular reflectance multiplier",
                                                                                  default=False,
                                                                                  update=refresh_preview)

    plastic_brdf_specular_reflectance_multiplier_tex = bpy.props.StringProperty(name="plastic_brdf_specular_reflectance_multiplier_tex",
                                                                                description="Specular reflectance multiplier texture",
                                                                                default="",
                                                                                update=refresh_preview)

    plastic_brdf_roughness = bpy.props.FloatProperty(name="plastic_brdf_roughness",
                                                     description="Roughness",
                                                     min=0.0,
                                                     max=1.0,
                                                     default=0.15,
                                                     update=refresh_preview)

    plastic_brdf_roughness_use_tex = bpy.props.BoolProperty(name="plastic_brdf_roughness_use_tex",
                                                            description="Use a texture to influence the roughness",
                                                            default=False,
                                                            update=refresh_preview)

    plastic_brdf_roughness_tex = bpy.props.StringProperty(name="plastic_brdf_roughness_tex",
                                                          description="Roughness texture",
                                                          default="",
                                                          update=refresh_preview)

    plastic_brdf_highlight_falloff = bpy.props.FloatProperty(name="plastic_brdf_highlight_falloff",
                                                             description="",
                                                             default=0.4,
                                                             min=0.0,
                                                             max=1.0,
                                                             update=refresh_preview)

    plastic_brdf_ior = bpy.props.FloatProperty(name="plastic_brdf_ior",
                                               description="Plastic index of refraction",
                                               default=1.5,
                                               min=1.0,
                                               max=2.5,
                                               update=refresh_preview)

    plastic_brdf_diffuse_reflectance = bpy.props.FloatVectorProperty(name="plastic_brdf_diffuse_reflectance",
                                                                     description="Diffuse reflection", subtype='COLOR',
                                                                     min=0.0,
                                                                     max=1.0,
                                                                     default=(0.8, 0.8, 0.8),
                                                                     update=refresh_preview)

    plastic_brdf_diffuse_reflectance_use_tex = bpy.props.BoolProperty(name="plastic_brdf_diffuse_reflectance_use_tex",
                                                                      description="Use a texture to influence the diffuse reflectance",
                                                                      default=False,
                                                                      update=refresh_preview)

    plastic_brdf_diffuse_reflectance_tex = bpy.props.StringProperty(name="plastic_brdf_diffuse_reflectance_tex",
                                                                    description="Diffuse reflectance texture",
                                                                    default="",
                                                                    update=refresh_preview)

    plastic_brdf_diffuse_reflectance_multiplier = bpy.props.FloatProperty(name="plastic_brdf_diffuse_reflectance_multiplier",
                                                                          description="Diffuse reflection multiplier",
                                                                          min=0.0,
                                                                          max=1.0,
                                                                          default=1.0,
                                                                          update=refresh_preview)

    plastic_brdf_diffuse_reflectance_multiplier_use_tex = bpy.props.BoolProperty(name="plastic_brdf_diffuse_reflectance_multiplier_use_tex",
                                                                                 description="Use a texture to influence the diffuse reflectance multiplier",
                                                                                 default=False,
                                                                                 update=refresh_preview)

    plastic_brdf_diffuse_reflectance_multiplier_tex = bpy.props.StringProperty(name="plastic_brdf_diffuse_reflectance_multiplier_tex",
                                                                               description="Diffuse reflectance multiplier texture",
                                                                               default="",
                                                                               update=refresh_preview)

    plastic_brdf_internal_scattering = bpy.props.FloatProperty(name="plastic_brdf_internal_scattering",
                                                               description="",
                                                               default=1.0,
                                                               min=0.0,
                                                               max=1.0,
                                                               update=refresh_preview)

    #
    # Sheen BRDF.
    #

    sheen_brdf_reflectance = bpy.props.FloatVectorProperty(name="sheen_brdf_reflectance",
                                                           description="Reflectance",
                                                           subtype='COLOR',
                                                           default=(0.5, 0.5, 0.5),
                                                           min=0.0,
                                                           max=1.0,
                                                           update=refresh_preview)

    sheen_brdf_reflectance_use_tex = bpy.props.BoolProperty(name="sheen_brdf_reflectance_use_tex",
                                                            description="Use a texture to influence sheen reflectance",
                                                            default=False,
                                                            update=refresh_preview)

    sheen_brdf_reflectance_tex = bpy.props.StringProperty(name="sheen_brdf_reflectance_tex",
                                                          description="Texture to influence sheen reflectance",
                                                          default="",
                                                          update=refresh_preview)

    sheen_brdf_reflectance_multiplier = bpy.props.FloatProperty(name="sheen_brdf_reflectance_multiplier",
                                                                description="Reflectance multiplier",
                                                                default=1.0,
                                                                min=0.0,
                                                                max=1.0,
                                                                update=refresh_preview)

    sheen_brdf_reflectance_multiplier_use_tex = bpy.props.BoolProperty(name="sheen_brdf_reflectance_multiplier_use_tex",
                                                                       description="Use a texture to influence sheen reflectance multiplier",
                                                                       default=False,
                                                                       update=refresh_preview)

    sheen_brdf_reflectance_multiplier_tex = bpy.props.StringProperty(name="sheen_brdf_reflectance_multiplier_tex",
                                                                     description="Texture to influence sheen reflectance multiplier",
                                                                     default="",
                                                                     update=refresh_preview)

    #
    # Specular BRDF.
    #

    specular_brdf_reflectance = bpy.props.FloatVectorProperty(name="specular_brdf_reflectance",
                                                              description="Specular BRDF reflectance",
                                                              default=(0.8, 0.8, 0.8),
                                                              subtype="COLOR",
                                                              min=0.0,
                                                              max=1.0,
                                                              update=refresh_preview)

    specular_brdf_use_glossy_tex = bpy.props.BoolProperty(name="specular_brdf_use_glossy_tex",
                                                          description="Use a texture to influence specular reflectance",
                                                          default=False,
                                                          update=refresh_preview)

    specular_brdf_glossy_tex = bpy.props.StringProperty(name="specular_brdf_glossy_tex",
                                                        description="Texture to influence specular reflectance",
                                                        default="",
                                                        update=refresh_preview)

    specular_brdf_multiplier = bpy.props.FloatProperty(name="specular_brdf_multiplier",
                                                       description="Specular BRDF reflectance multiplier",
                                                       default=1.0,
                                                       min=0.0,
                                                       max=1.0,
                                                       update=refresh_preview)

    #
    # Specular BTDF.
    #

    specular_btdf_reflectance = bpy.props.FloatVectorProperty(name="specular_btdf_reflectance",
                                                              description="Specular BTDF reflectance",
                                                              default=(0.8, 0.8, 0.8),
                                                              subtype='COLOR',
                                                              min=0.0,
                                                              max=1.0,
                                                              update=refresh_preview)

    specular_btdf_use_specular_tex = bpy.props.BoolProperty(name="specular_btdf_use_specular_tex",
                                                            description="Use a texture to influence specular reflectance",
                                                            default=False,
                                                            update=refresh_preview)

    specular_btdf_specular_tex = bpy.props.StringProperty(name="specular_btdf_specular_tex",
                                                          description="Texture to influence specular reflectance",
                                                          default="",
                                                          update=refresh_preview)

    specular_btdf_refl_mult = bpy.props.FloatProperty(name="specular_btdf_refl_mult",
                                                      description="Specular BTDF reflectance multiplier",
                                                      default=1.0,
                                                      min=0.0,
                                                      max=1.0,
                                                      update=refresh_preview)

    specular_btdf_transmittance = bpy.props.FloatVectorProperty(name="specular_btdf_transmittance",
                                                                description="Specular BTDF transmittance",
                                                                default=(0.8, 0.8, 0.8),
                                                                subtype="COLOR",
                                                                min=0.0,
                                                                max=1.0,
                                                                update=refresh_preview)

    specular_btdf_use_trans_tex = bpy.props.BoolProperty(name="specular_btdf_use_trans_tex",
                                                         description="Use a texture to influence specular transmittance",
                                                         default=False,
                                                         update=refresh_preview)

    specular_btdf_trans_tex = bpy.props.StringProperty(name="specular_btdf_trans_tex",
                                                       description="Texture to influence specular transmittance",
                                                       default="",
                                                       update=refresh_preview)

    specular_btdf_trans_mult = bpy.props.FloatProperty(name="specular_btdf_trans_mult",
                                                       description="Specular BTDF transmittance multiplier",
                                                       default=1.0,
                                                       min=0.0,
                                                       max=1.0,
                                                       update=refresh_preview)

    specular_btdf_fresnel_multiplier = bpy.props.FloatProperty(name="specular_btdf_fresnel_multiplier",
                                                               description="Fresnel multiplier",
                                                               default=1.0,
                                                               min=0.0,
                                                               max=1.0,
                                                               update=refresh_preview)

    specular_btdf_fresnel_multiplier_use_tex = bpy.props.BoolProperty(name="specular_btdf_fresnel_multiplier_use_tex",
                                                                      description="Use a texture to influence fresnel multiplier",
                                                                      default=False,
                                                                      update=refresh_preview)

    specular_btdf_fresnel_multiplier_tex = bpy.props.StringProperty(name="specular_btdf_fresnel_multiplier_tex",
                                                                    description="Texture to influence fresnel_multiplier",
                                                                    default="",
                                                                    update=refresh_preview)

    specular_btdf_ior = bpy.props.FloatProperty(name="specular_btdf_ior",
                                                description="Index of refraction",
                                                default=1.33,
                                                min=1.0,
                                                max=2.5,
                                                update=refresh_preview)

    specular_btdf_volume_density = bpy.props.FloatProperty(name="specular_btdf_volume_density",
                                                           description="Volume density",
                                                           default=0.0,
                                                           min=0.0,
                                                           max=10.0,
                                                           update=refresh_preview)

    specular_btdf_volume_scale = bpy.props.FloatProperty(name="specular_btdf_volume_scale",
                                                         description="Volume scale",
                                                         default=0.0,
                                                         min=0.0,
                                                         max=10.0,
                                                         update=refresh_preview)

    #
    # BSSRDF
    #

    bssrdf_model = bpy.props.EnumProperty(name="BSSRDF Model",
                                          description="BSSRDF model",
                                          items=[('none', "None", ""),
                                                 ('normalized_diffusion_bssrdf', "Normalized Diffusion", ""),
                                                 ('better_dipole_bssrdf', "Dipole", ""),
                                                 ('gaussian_bssrdf', "Gaussian", ""),
                                                 ('randomwalk', "Random Walk", "")],
                                          default="none",
                                          update=refresh_preview)

    bssrdf_weight = bpy.props.FloatProperty(name="bssrdf_weight",
                                            description="Weight of the BSSRDF",
                                            default=1.0,
                                            min=0.0,
                                            max=1.0,
                                            update=refresh_preview)

    bssrdf_weight_use_texture = bpy.props.BoolProperty(name="bssrdf_weight_use_texture",
                                                       description="Use a texture for the BSSRDF weight",
                                                       default=False,
                                                       update=refresh_preview)

    bssrdf_weight_texture = bpy.props.StringProperty(name="bssrdf_weight_texture",
                                                     description="Texture to influence BSSRDF weight",
                                                     default="",
                                                     update=refresh_preview)

    bssrdf_reflectance = bpy.props.FloatVectorProperty(name="bssrdf_reflectance",
                                                       description="Diffuse Surface Reflectance",
                                                       default=(0.5, 0.5, 0.5),
                                                       subtype='COLOR',
                                                       min=0.0,
                                                       max=1.0,
                                                       update=refresh_preview)

    bssrdf_reflectance_use_texture = bpy.props.BoolProperty(name="bssrdf_reflectance_use_texture",
                                                            description="Use a texture for the BSSRDF reflectance",
                                                            default=False,
                                                            update=refresh_preview)

    bssrdf_reflectance_texture = bpy.props.StringProperty(name="bssrdf_reflectance_texture",
                                                          description="Texture to influence BSSRDF reflectance",
                                                          default="",
                                                          update=refresh_preview)

    bssrdf_reflectance_multiplier = bpy.props.FloatProperty(name="bssrdf_reflectance_multiplier",
                                                            description="Diffuse Surface Reflectance Multiplier",
                                                            default=1.0,
                                                            min=0.0,
                                                            max=1.0,
                                                            update=refresh_preview)

    bssrdf_reflectance_multiplier_use_texture = bpy.props.BoolProperty(name="bssrdf_reflectance_multiplier_use_texture",
                                                                       description="Use a texture for the BSSRDF reflectance multiplier",
                                                                       default=False,
                                                                       update=refresh_preview)

    bssrdf_reflectance_multiplier_texture = bpy.props.StringProperty(name="bssrdf_reflectance_multiplier_texture",
                                                                     description="Texture to influence BSSRDF reflectance multiplier",
                                                                     default="",
                                                                     update=refresh_preview)

    bssrdf_mfp = bpy.props.FloatVectorProperty(name="bssrdf_mfp",
                                               description="Mean Free Path",
                                               default=(0.5, 0.5, 0.5),
                                               subtype='COLOR',
                                               min=0.0,
                                               max=1.0,
                                               update=refresh_preview)

    bssrdf_mfp_use_texture = bpy.props.BoolProperty(name="bssrdf_mfp_use_texture",
                                                    description="Use a texture for the Mean Free Path",
                                                    default=False,
                                                    update=refresh_preview)

    bssrdf_mfp_texture = bpy.props.StringProperty(name="bssrdf_mfp_texture",
                                                  description="Texture to influence the Mean Free Path",
                                                  default="",
                                                  update=refresh_preview)

    bssrdf_mfp_multiplier = bpy.props.FloatProperty(name="bssrdf_mfp_multiplier",
                                                    description="Mean Free Path Multiplier",
                                                    default=1.0,
                                                    min=0.0,
                                                    max=1.0,
                                                    update=refresh_preview)

    bssrdf_mfp_multiplier_use_texture = bpy.props.BoolProperty(name="bssrdf_mfp_multiplier_use_texture",
                                                               description="Use a texture for the Mean Free Path multiplier",
                                                               default=False,
                                                               update=refresh_preview)

    bssrdf_mfp_multiplier_texture = bpy.props.StringProperty(name="bssrdf_mfp_multiplier_texture",
                                                             description="Texture to influence the Mean Free Path multiplier",
                                                             default="",
                                                             update=refresh_preview)

    bssrdf_ior = bpy.props.FloatProperty(name="bssrdf_ior",
                                         description="Index of Refraction",
                                         default=1.3,
                                         min=1.0,
                                         max=2.5,
                                         update=refresh_preview)

    bssrdf_fresnel_weight = bpy.props.FloatProperty(name="bssrdf_fresnel_weight",
                                                    description="Fresnel Weight",
                                                    default=1.0,
                                                    min=0.0,
                                                    max=1.0,
                                                    update=refresh_preview)

    #
    # Volume
    #

    volume_phase_function_model = bpy.props.EnumProperty(name="Volumetric Model",
                                                         description="Volume phase function model",
                                                         items=[('none', "None", ""),
                                                                ('henyey', "Henyey-Greenstein", ""),
                                                                ('isotropic', "Isotropic", "")],
                                                         default="none",
                                                         update=refresh_preview)

    volume_absorption = bpy.props.FloatVectorProperty(name="volume_absorption",
                                                      description="Volume absorption",
                                                      default=(0.5, 0.5, 0.5),
                                                      subtype='COLOR',
                                                      min=0.0,
                                                      max=1.0,
                                                      update=refresh_preview)

    volume_absorption_multiplier = bpy.props.FloatProperty(name="volume_absorption_multiplier",
                                                           description="Volume absorption multiplier",
                                                           default=1.0,
                                                           min=0.0,
                                                           max=200.0,
                                                           update=refresh_preview)

    volume_scattering = bpy.props.FloatVectorProperty(name="volume_scattering",
                                                      description="Volume scattering",
                                                      default=(0.5, 0.5, 0.5),
                                                      subtype='COLOR',
                                                      min=0.0,
                                                      max=1.0,
                                                      update=refresh_preview)

    volume_scattering_multiplier = bpy.props.FloatProperty(name="volume_scattering_multiplier",
                                                           description="Volume absorption multiplier",
                                                           default=1.0,
                                                           min=0.0,
                                                           max=200.0,
                                                           update=refresh_preview)

    volume_average_cosine = bpy.props.FloatProperty(name="volume_average_cosine",
                                                    description="Volume average cosine",
                                                    default=0.0,
                                                    min=-1.0,
                                                    max=1.0,
                                                    update=refresh_preview)

    #
    # EDF
    #

    use_light_emission = bpy.props.BoolProperty(name="use_light_emission",
                                                description="Enable material light emission",
                                                default=False,
                                                update=refresh_preview)

    light_emission_profile = bpy.props.EnumProperty(name="Profile",
                                                    description="Profile for emission",
                                                    items=[('diffuse_edf', "Diffuse EDF", ""),
                                                           ('cone_edf', "Cone EDF", "")],
                                                    default='diffuse_edf',
                                                    update=refresh_preview)

    light_cone_edf_angle = bpy.props.FloatProperty(name="light_cone_edf_angle",
                                                   description="Angle of spread for cone EDF",
                                                   default=90.0,
                                                   min=0.0,
                                                   max=180.0,
                                                   update=refresh_preview)

    light_emission = bpy.props.FloatProperty(name="light_emission",
                                             description="Light radiance multiplier",
                                             default=1.0,
                                             min=0.0,
                                             max=10000.0,
                                             update=refresh_preview)

    light_exposure = bpy.props.FloatProperty(name="light_exposure",
                                             description="Light exposure",
                                             default=0.0,
                                             min=-64.0,
                                             max=64.0,
                                             update=refresh_preview)

    light_color = bpy.props.FloatVectorProperty(name="light_color",
                                                description="Light emission color",
                                                default=(0.8, 0.8, 0.8),
                                                subtype="COLOR",
                                                min=0.0,
                                                max=1.0,
                                                update=refresh_preview)

    importance_multiplier = bpy.props.FloatProperty(name="importance_multiplier",
                                                    description="Multiple importance sampling multiplier",
                                                    default=1,
                                                    min=0,
                                                    soft_max=10,
                                                    max=100,
                                                    update=refresh_preview)

    cast_indirect = bpy.props.BoolProperty(name="cast_indirect",
                                           description="Emissive material casts indirect light",
                                           default=True,
                                           update=refresh_preview)

    light_near_start = bpy.props.FloatProperty(name="light_near_start",
                                               description="Amount by which to extend the start of light's influence away from the emissive material",
                                               default=0.0,
                                               min=0,
                                               max=10,
                                               update=refresh_preview)

    #
    # Bump/Normal
    #

    material_use_bump_tex = bpy.props.BoolProperty(name="material_use_bump_tex",
                                                   description="Use a texture to influence bump / normal",
                                                   default=False,
                                                   update=refresh_preview)

    material_bump_tex = bpy.props.StringProperty(name="material_bump_tex",
                                                 description="Bump / normal texture",
                                                 default="",
                                                 update=refresh_preview)

    material_use_normalmap = bpy.props.BoolProperty(name="material_use_normalmap",
                                                    description="Use texture as normal map",
                                                    default=False,
                                                    update=refresh_preview)

    material_bump_amplitude = bpy.props.FloatProperty(name="material_bump_amplitude",
                                                      description="Maximum height influence of bump / normal map",
                                                      default=1.0,
                                                      min=0.0,
                                                      max=1.0,
                                                      update=refresh_preview)

    material_bump_offset = bpy.props.FloatProperty(name="material_bump_offset",
                                                   description="Offset value to elevate or reduce bump mapping",
                                                   default=0.5,
                                                   min=0.01,
                                                   max=10,
                                                   precision=4,
                                                   update=refresh_preview)

    #
    # Alpha
    #

    material_alpha_map = bpy.props.StringProperty(name="material_alpha_map",
                                                  description="Alpha texture",
                                                  default="",
                                                  update=refresh_preview)

    material_use_alpha = bpy.props.BoolProperty(name="material_use_alpha",
                                                description="Use a texture to influence alpha",
                                                default=False,
                                                update=refresh_preview)

    material_alpha = bpy.props.FloatProperty(name="material_alpha",
                                             description="Alpha",
                                             default=1.0,
                                             min=0.0,
                                             max=1.0,
                                             update=refresh_preview)

    preview_quality = bpy.props.IntProperty(name="preview_quality",
                                            description="Number of samples used for preview rendering",
                                            default=2,
                                            min=1,
                                            max=16,
                                            update=refresh_preview)

    # Nodes
    osl_node_tree = bpy.props.PointerProperty(name="OSL Node Tree", type=bpy.types.NodeTree)


def register():
    util.safe_register_class(AppleseedMatProps)
    bpy.types.Material.appleseed = bpy.props.PointerProperty(type=AppleseedMatProps)


def unregister():
    del bpy.types.Material.appleseed
    util.safe_unregister_class(AppleseedMatProps)
