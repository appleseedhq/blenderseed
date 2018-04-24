
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


def osl_node_tree_selector_draw(layout, mat):
    try:
        layout.prop_search(mat.appleseed, "osl_node_tree", bpy.data, "node_groups", text="OSL Node Tree")
    except:
        return False

    if mat.appleseed.osl_node_tree == None:
        layout.operator('appleseed.add_osl_nodetree', text="Add appleseed Material Node", icon='NODETREE')
        return False

    return True


class AppleseedMaterialPreview(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "material"
    bl_label = "Preview"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine in cls.COMPAT_ENGINES and context.object is not None and context.object.active_material is not None

    def draw(self, context):
        layout = self.layout
        obj = context.object
        material = obj.active_material
        asr_mat = material.appleseed

        layout.template_preview(context.material, show_buttons=False)
        layout.prop(asr_mat, "preview_quality", text="Preview Quality")


class AppleseedMaterialShading(bpy.types.Panel):
    bl_label = 'Surface Shader'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type == 'MESH' and context.object.active_material is not None

    def draw(self, context):
        layout = self.layout
        object = context.object
        material = object.active_material
        asr_mat = material.appleseed

        osl_node_tree_selector_draw(layout, material)

        if asr_mat.osl_node_tree == None:
            layout.prop(asr_mat, "bsdf_type", text="BSDF Model")
            layout.separator()

            #
            # Ashikhmin-Shirley BRDF.
            #

            if asr_mat.bsdf_type == "ashikhmin_brdf":
                # reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Diffuse Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "ashikhmin_brdf_reflectance", text="")

                if asr_mat.ashikhmin_brdf_use_diffuse_tex:
                    layout.prop_search(asr_mat, "ashikhmin_brdf_diffuse_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "ashikhmin_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.ashikhmin_brdf_diffuse_tex != '' and asr_mat.ashikhmin_brdf_use_diffuse_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.ashikhmin_brdf_diffuse_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                row = layout.row()
                row.prop(asr_mat, "ashikhmin_brdf_multiplier", text="Diffuse Reflectance Multiplier")

                # glossiness
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Glossy Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "ashikhmin_brdf_glossy", text="")

                if asr_mat.ashikhmin_brdf_use_glossy_tex:
                    layout.prop_search(asr_mat, "ashikhmin_brdf_glossy_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "ashikhmin_brdf_use_glossy_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.ashikhmin_brdf_glossy_tex != '' and asr_mat.ashikhmin_brdf_use_glossy_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.ashikhmin_brdf_glossy_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                row = layout.row()
                row.prop(asr_mat, "ashikhmin_brdf_glossy_multiplier", text="Glossy Reflectance Multiplier")

                # fresnel
                col = layout.column()
                col.prop(asr_mat, "ashikhmin_brdf_fresnel", text="Fresnel Multiplier")
                layout.prop(asr_mat, "ashikhmin_brdf_shininess_u", text="Shininess U")
                layout.prop(asr_mat, "ashikhmin_brdf_shininess_v", text="Shininess V")

            #
            # Blinn BRDF.
            #

            elif asr_mat.bsdf_type == "blinn_brdf":
                # exponent
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "blinn_brdf_exponent", text="Exponent")

                if asr_mat.blinn_brdf_exponent_use_tex:
                    layout.prop_search(asr_mat, "blinn_brdf_exponent_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "blinn_brdf_exponent_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.blinn_brdf_exponent_tex != '' and asr_mat.blinn_brdf_exponent_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.blinn_brdf_exponent_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # ior
                col = layout.column()
                col.prop(asr_mat, "blinn_brdf_ior", text="Index of Refraction")

            #
            # Diffuse BTDF.
            #

            elif asr_mat.bsdf_type == "diffuse_btdf":
                # reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Transmittance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "diffuse_btdf_transmittance_color", text="")
                if asr_mat.diffuse_btdf_use_diffuse_tex:
                    layout.prop_search(asr_mat, "diffuse_btdf_diffuse_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "diffuse_btdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.diffuse_btdf_diffuse_tex != '' and asr_mat.diffuse_btdf_use_diffuse_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.diffuse_btdf_diffuse_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # transmittance
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "diffuse_btdf_transmittance_multiplier", text="Transmittance Multiplier:")
                if asr_mat.diffuse_btdf_transmittance_use_mult_tex:
                    layout.prop_search(asr_mat, "diffuse_btdf_transmittance_mult_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "diffuse_btdf_transmittance_use_mult_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.diffuse_btdf_transmittance_mult_tex != '' and asr_mat.diffuse_btdf_transmittance_use_mult_tex:
                    mult_tex = bpy.data.textures[asr_mat.diffuse_btdf_transmittance_mult_tex]
                    layout.prop(mult_tex.image.colorspace_settings, "name", text="Color Space")

            #
            # Disney BRDF.
            #

            elif asr_mat.bsdf_type == "disney_brdf":
                # base color
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Base Color:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_base", text="")

                if asr_mat.disney_brdf_use_base_tex:
                    layout.prop_search(asr_mat, "disney_brdf_base_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_base_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_base_tex != '' and asr_mat.disney_brdf_use_base_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.disney_brdf_base_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # subsurface
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_subsurface", text="Subsurface")
                if asr_mat.disney_brdf_use_subsurface_tex:
                    layout.prop_search(asr_mat, "disney_brdf_subsurface_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_subsurface_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_subsurface_tex != '' and asr_mat.disney_brdf_use_subsurface_tex:
                    subsurface_tex = bpy.data.textures[asr_mat.disney_brdf_subsurface_tex]
                    layout.prop(subsurface_tex.image.colorspace_settings, "name", text="Color Space")

                # metallic
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_metallic", text="Metallic")
                if asr_mat.disney_brdf_use_metallic_tex:
                    layout.prop_search(asr_mat, "disney_brdf_metallic_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_metallic_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_metallic_tex != '' and asr_mat.disney_brdf_use_metallic_tex:
                    metal_brdf_tex = bpy.data.textures[asr_mat.disney_brdf_metallic_tex]
                    layout.prop(metal_brdf_tex.image.colorspace_settings, "name", text="Color Space")

                # specular
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_spec", text="Specular")
                if asr_mat.disney_brdf_use_specular_tex:
                    layout.prop_search(asr_mat, "disney_brdf_specular_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_specular_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_specular_tex != '' and asr_mat.disney_brdf_use_specular_tex:
                    specular_tex = bpy.data.textures[asr_mat.disney_brdf_specular_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # specular tint
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_specular_tint", text="Specular Tint")
                if asr_mat.disney_brdf_use_specular_tint_tex:
                    layout.prop_search(asr_mat, "disney_brdf_specular_tint_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_specular_tint_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_specular_tint_tex != '' and asr_mat.disney_brdf_use_specular_tint_tex:
                    specular_tint_tex = bpy.data.textures[asr_mat.disney_brdf_specular_tint_tex]
                    layout.prop(specular_tint_tex.image.colorspace_settings, "name", text="Color Space")

                # anisotropy
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_anisotropy", text="Anisotropy")
                if asr_mat.disney_brdf_use_anisotropy_tex:
                    layout.prop_search(asr_mat, "disney_brdf_anisotropy_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_anisotropy_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_anisotropy_tex != '' and asr_mat.disney_brdf_use_anisotropy_tex:
                    anisotropy_tex = bpy.data.textures[asr_mat.disney_brdf_anisotropy_tex]
                    layout.prop(anisotropy_tex.image.colorspace_settings, "name", text="Color Space")

                # roughness
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_roughness", text="Roughness")
                if asr_mat.disney_brdf_use_roughness_tex:
                    layout.prop_search(asr_mat, "disney_brdf_roughness_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_roughness_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_roughness_tex != '' and asr_mat.disney_brdf_use_roughness_tex:
                    rough_tex = bpy.data.textures[asr_mat.disney_brdf_roughness_tex]
                    layout.prop(rough_tex.image.colorspace_settings, "name", text="Color Space")

                # sheen
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_sheen", text="Sheen")
                if asr_mat.disney_brdf_use_sheen_brdf_tex:
                    layout.prop_search(asr_mat, "disney_brdf_sheen_brdf_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_sheen_brdf_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_sheen_brdf_tex != '' and asr_mat.disney_brdf_use_sheen_brdf_tex:
                    sheen_brdf_tex = bpy.data.textures[asr_mat.disney_brdf_sheen_brdf_tex]
                    layout.prop(sheen_brdf_tex.image.colorspace_settings, "name", text="Color Space")

                # sheen tint
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_sheen_brdf_tint", text="Sheen Tint")
                if asr_mat.disney_brdf_use_sheen_brdf_tint_tex:
                    layout.prop_search(asr_mat, "disney_brdf_sheen_brdf_tint_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_sheen_brdf_tint_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_sheen_brdf_tint_tex != '' and asr_mat.disney_brdf_use_sheen_brdf_tint_tex:
                    sheen_brdf_tint_tex = bpy.data.textures[asr_mat.disney_brdf_sheen_brdf_tint_tex]
                    layout.prop(sheen_brdf_tint_tex.image.colorspace_settings, "name", text="Color Space")

                # clear coat
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_clearcoat", text="Clear Coat")
                if asr_mat.disney_brdf_use_clearcoat_tex:
                    layout.prop_search(asr_mat, "disney_brdf_clearcoat_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_clearcoat_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_clearcoat_tex != '' and asr_mat.disney_brdf_use_clearcoat_tex:
                    clearcoat_tex = bpy.data.textures[asr_mat.disney_brdf_clearcoat_tex]
                    layout.prop(clearcoat_tex.image.colorspace_settings, "name", text="Color Space")

                # clear coat gloss
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "disney_brdf_clearcoat_gloss", text="Clear Coat Gloss")
                if asr_mat.disney_brdf_use_clearcoat_glossy_tex:
                    layout.prop_search(asr_mat, "disney_brdf_clearcoat_glossy_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "disney_brdf_use_clearcoat_glossy_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.disney_brdf_clearcoat_glossy_tex != '' and asr_mat.disney_brdf_use_clearcoat_glossy_tex:
                    clearcoat_glossy_tex = bpy.data.textures[asr_mat.disney_brdf_clearcoat_glossy_tex]
                    layout.prop(clearcoat_glossy_tex.image.colorspace_settings, "name", text="Color Space")

            #
            # Glass BSDF.
            #

            elif asr_mat.bsdf_type == "glass_bsdf":
                # mdf
                col = layout.column()
                col.prop(asr_mat, "glass_bsdf_mdf", text="Microfacet Distribution Function")

                # surface transmittance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Surface Transmittance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_surface_transmittance", text="")

                if asr_mat.glass_bsdf_surface_transmittance_use_tex:
                    layout.prop_search(asr_mat, "glass_bsdf_surface_transmittance_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_surface_transmittance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glass_bsdf_surface_transmittance_tex != '' and asr_mat.glass_bsdf_surface_transmittance_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.glass_bsdf_surface_transmittance_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # surface transmittance multiplier
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_surface_transmittance_multiplier", text="Surface Transmittance Multiplier")

                if asr_mat.glass_bsdf_surface_transmittance_multiplier_use_tex:
                    layout.prop_search(asr_mat, "glass_bsdf_surface_transmittance_multiplier_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "glass_bsdf_surface_transmittance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glass_bsdf_surface_transmittance_multiplier_tex != '' and asr_mat.glass_bsdf_surface_transmittance_multiplier_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.glass_bsdf_surface_transmittance_multiplier_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # reflection tint
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Reflection Tint:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_reflection_tint", text="")

                if asr_mat.glass_bsdf_reflection_tint_use_tex:
                    layout.prop_search(asr_mat, "glass_bsdf_reflection_tint_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_reflection_tint_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glass_bsdf_reflection_tint_tex != '' and asr_mat.glass_bsdf_reflection_tint_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.glass_bsdf_reflection_tint_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # refraction tint
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Refraction Tint:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_refraction_tint", text="")

                if asr_mat.glass_bsdf_refraction_tint_use_tex:
                    layout.prop_search(asr_mat, "glass_bsdf_refraction_tint_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_refraction_tint_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glass_bsdf_refraction_tint_tex != '' and asr_mat.glass_bsdf_refraction_tint_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.glass_bsdf_refraction_tint_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # ior
                col = layout.column()
                col.prop(asr_mat, "glass_bsdf_ior", text="Index of Refraction")

                # roughness
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_roughness", text="Roughness")

                if asr_mat.glass_bsdf_roughness_use_tex:
                    layout.prop_search(asr_mat, "glass_bsdf_roughness_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "glass_bsdf_roughness_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glass_bsdf_roughness_tex != '' and asr_mat.glass_bsdf_roughness_use_tex:
                    glass_bsdf_roughness = bpy.data.textures[asr_mat.glass_bsdf_roughness_tex]
                    layout.prop(glass_bsdf_roughness.image.colorspace_settings, "name", text="Color Space")

                # highlight falloff
                col = layout.column()
                col.prop(asr_mat, "glass_bsdf_highlight_falloff", text="Highlight Falloff")

                # anisotropy
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "glass_bsdf_anisotropy", text="Anisotropy")

                if asr_mat.glass_bsdf_anisotropy_use_tex:
                    layout.prop_search(asr_mat, "glass_bsdf_anisotropy_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "glass_bsdf_anisotropy_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glass_bsdf_anisotropy_tex != '' and asr_mat.glass_bsdf_anisotropy_use_tex:
                    glass_bsdf_anisotropy = bpy.data.textures[asr_mat.glass_bsdf_anisotropy_tex]
                    layout.prop(glass_bsdf_anisotropy.image.colorspace_settings, "name", text="Color Space")

                # volume parameterization
                col = layout.column()
                col.prop(asr_mat, "glass_bsdf_volume_parameterization", text="Volume Absorption Parameterization")

                if asr_mat.glass_bsdf_volume_parameterization == 'transmittance':
                    # normal reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Volume Transmittance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(asr_mat, "glass_bsdf_volume_transmittance", text="")

                    if asr_mat.glass_bsdf_volume_transmittance_use_tex:
                        layout.prop_search(asr_mat, "glass_bsdf_volume_transmittance_tex", material, "texture_slots", text="")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(asr_mat, "glass_bsdf_volume_transmittance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if asr_mat.glass_bsdf_volume_transmittance_tex != '' and asr_mat.glass_bsdf_volume_transmittance_use_tex:
                        specular_tex = bpy.data.textures[asr_mat.glass_bsdf_volume_transmittance_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # glass volume transmittance distance
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(asr_mat, "glass_bsdf_volume_transmittance_distance", text="Volume Transmittance Distance")

                    if asr_mat.glass_bsdf_volume_transmittance_distance_use_tex:
                        layout.prop_search(asr_mat, "glass_bsdf_volume_transmittance_distance_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(asr_mat, "glass_bsdf_volume_transmittance_distance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if asr_mat.glass_bsdf_volume_transmittance_distance_tex != '' and asr_mat.glass_bsdf_volume_transmittance_distance_use_tex:
                        glass_bsdf_volume_transmittance_distance = bpy.data.textures[asr_mat.glass_bsdf_volume_transmittance_distance_tex]
                        layout.prop(glass_bsdf_volume_transmittance_distance.image.colorspace_settings, "name", text="Color Space")

                else:
                    # glass volume density
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(asr_mat, "glass_bsdf_volume_density", text="Volume Density")

                    if asr_mat.glass_bsdf_volume_density_use_tex:
                        layout.prop_search(asr_mat, "glass_bsdf_volume_density_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(asr_mat, "glass_bsdf_volume_density_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if asr_mat.glass_bsdf_volume_density_tex != '' and asr_mat.glass_bsdf_volume_density_use_tex:
                        glass_bsdf_volume_density = bpy.data.textures[asr_mat.glass_bsdf_volume_density_tex]
                        layout.prop(glass_bsdf_volume_density.image.colorspace_settings, "name", text="Color Space")

                    # glass absorption
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Volume Absorption:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(asr_mat, "glass_bsdf_volume_absorption", text="")

                    if asr_mat.glass_bsdf_volume_absorption_use_tex:
                        layout.prop_search(asr_mat, "glass_bsdf_volume_absorption_tex", material, "texture_slots", text="")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(asr_mat, "glass_bsdf_volume_absorption_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if asr_mat.glass_bsdf_volume_absorption_tex != '' and asr_mat.glass_bsdf_volume_absorption_use_tex:
                        specular_tex = bpy.data.textures[asr_mat.glass_bsdf_volume_absorption_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # scale
                col = layout.column()
                col.prop(asr_mat, "glass_bsdf_volume_scale", text="Volume Scale")

            #
            # Glossy BRDF.
            #

            elif asr_mat.bsdf_type == "glossy_brdf":
                # mdf
                col = layout.column()
                col.prop(asr_mat, "glossy_brdf_mdf", text="Microfacet Distribution Function")

                # reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "glossy_brdf_reflectance", text="")

                if asr_mat.glossy_brdf_reflectance_use_tex:
                    layout.prop_search(asr_mat, "glossy_brdf_reflectance_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "glossy_brdf_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glossy_brdf_reflectance_tex != '' and asr_mat.glossy_brdf_reflectance_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.glossy_brdf_reflectance_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # reflectance multiplier
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "glossy_brdf_reflectance_multiplier", text="Reflectance Multiplier")

                if asr_mat.glossy_brdf_reflectance_multiplier_use_tex:
                    layout.prop_search(asr_mat, "glossy_brdf_reflectance_multiplier_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "glossy_brdf_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glossy_brdf_reflectance_multiplier_tex != '' and asr_mat.glossy_brdf_reflectance_multiplier_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.glossy_brdf_reflectance_multiplier_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # roughness
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "glossy_brdf_roughness", text="Roughness")

                if asr_mat.glossy_brdf_roughness_use_tex:
                    layout.prop_search(asr_mat, "glossy_brdf_roughness_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "glossy_brdf_roughness_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glossy_brdf_roughness_tex != '' and asr_mat.glossy_brdf_roughness_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.glossy_brdf_roughness_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # highlight falloff
                col = layout.column()
                col.prop(asr_mat, "glossy_brdf_highlight_falloff", text="Highlight Falloff")

                # anisotropy
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "glossy_brdf_anisotropy", text="Anisotropy")

                if asr_mat.glossy_brdf_anisotropy_use_tex:
                    layout.prop_search(asr_mat, "glossy_brdf_anisotropy_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "glossy_brdf_anisotropy_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.glossy_brdf_anisotropy_tex != '' and asr_mat.glossy_brdf_anisotropy_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.glossy_brdf_anisotropy_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # ior
                col = layout.column()
                col.prop(asr_mat, "glossy_brdf_ior", text="Index of Refraction")

            #
            # Kelemen BRDF.
            #

            elif asr_mat.bsdf_type == "kelemen_brdf":
                # reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Matte Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "kelemen_brdf_matte_reflectance", text="")

                if asr_mat.kelemen_brdf_use_diffuse_tex:
                    layout.prop_search(asr_mat, "kelemen_brdf_diffuse_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "kelemen_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.kelemen_brdf_diffuse_tex != '' and asr_mat.kelemen_brdf_use_diffuse_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.kelemen_brdf_diffuse_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")
                row = layout.row()
                row.prop(asr_mat, "kelemen_brdf_matte_multiplier", text="Matte Reflectance Multiplier")

                layout.prop(asr_mat, "kelemen_brdf_specular_reflectance", text="Specular Reflectance")
                layout.prop(asr_mat, "kelemen_brdf_specular_multiplier", text="Specular Reflectance Multiplier")
                layout.prop(asr_mat, "kelemen_brdf_roughness", text="Roughness")

            #
            # Lambertian BRDF.
            #

            elif asr_mat.bsdf_type == "lambertian_brdf":
                # reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "lambertian_brdf_reflectance", text="")

                if asr_mat.lambertian_brdf_use_diffuse_tex:
                    layout.prop_search(asr_mat, "lambertian_brdf_diffuse_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "lambertian_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.lambertian_brdf_diffuse_tex != '' and asr_mat.lambertian_brdf_use_diffuse_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.lambertian_brdf_diffuse_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")
                layout.prop(asr_mat, "lambertian_brdf_multiplier", text="Reflectance Multiplier")

            #
            # Metal BRDF.
            #

            elif asr_mat.bsdf_type == "metal_brdf":
                # mdf
                col = layout.column()
                col.prop(asr_mat, "metal_brdf_mdf", text="Microfacet Distribution Function")

                # normal reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Normal Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "metal_brdf_normal_reflectance", text="")

                if asr_mat.metal_brdf_normal_reflectance_use_tex:
                    layout.prop_search(asr_mat, "metal_brdf_normal_reflectance_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "metal_brdf_normal_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.metal_brdf_normal_reflectance_tex != '' and asr_mat.metal_brdf_normal_reflectance_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.metal_brdf_normal_reflectance_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # edge tint
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Edge Tint:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "metal_brdf_edge_tint", text="")

                if asr_mat.metal_brdf_edge_tint_use_tex:
                    layout.prop_search(asr_mat, "metal_brdf_edge_tint_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "metal_brdf_edge_tint_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.metal_brdf_edge_tint_tex != '' and asr_mat.metal_brdf_edge_tint_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.metal_brdf_edge_tint_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # reflectance multiplier
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "metal_brdf_reflectance_multiplier", text="Reflectance Multiplier")

                if asr_mat.metal_brdf_reflectance_multiplier_use_tex:
                    layout.prop_search(asr_mat, "metal_brdf_reflectance_multiplier_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "metal_brdf_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.metal_brdf_reflectance_multiplier_tex != '' and asr_mat.metal_brdf_reflectance_multiplier_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.metal_brdf_reflectance_multiplier_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # roughness
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "metal_brdf_roughness", text="Roughness")

                if asr_mat.metal_brdf_roughness_use_tex:
                    layout.prop_search(asr_mat, "metal_brdf_roughness_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "metal_brdf_roughness_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.metal_brdf_roughness_tex != '' and asr_mat.metal_brdf_roughness_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.metal_brdf_roughness_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                col = layout.column()
                col.prop(asr_mat, "metal_brdf_highlight_falloff", text="Highlight Falloff")

                # anisotropy
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "metal_brdf_anisotropy", text="Anisotropy")

                if asr_mat.metal_brdf_anisotropy_use_tex:
                    layout.prop_search(asr_mat, "metal_brdf_anisotropy_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "metal_brdf_anisotropy_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.metal_brdf_anisotropy_tex != '' and asr_mat.metal_brdf_anisotropy_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.metal_brdf_anisotropy_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

            #
            # Oren-Nayar BRDF.
            #

            elif asr_mat.bsdf_type == "orennayar_brdf":
                # reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "orennayar_brdf_reflectance", text="")

                if asr_mat.orennayar_brdf_use_diffuse_tex:
                    layout.prop_search(asr_mat, "orennayar_brdf_diffuse_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "orennayar_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.orennayar_brdf_diffuse_tex != '' and asr_mat.orennayar_brdf_use_diffuse_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.orennayar_brdf_diffuse_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # reflectance multiplier
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "orennayar_brdf_reflectance_multiplier", text="Reflectance Multiplier")
                if asr_mat.orennayar_brdf_use_reflect_multiplier_tex:
                    layout.prop_search(asr_mat, "orennayar_brdf_reflect_multiplier_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "orennayar_brdf_use_reflect_multiplier_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.orennayar_brdf_reflect_multiplier_tex != '' and asr_mat.orennayar_brdf_use_reflect_multiplier_tex:
                    reflect_multiplier_tex = bpy.data.textures[asr_mat.orennayar_brdf_reflect_multiplier_tex]
                    layout.prop(reflect_multiplier_tex.image.colorspace_settings, "name", text="Color Space")

                # roughness
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "orennayar_brdf_roughness", text="Roughness")
                if asr_mat.orennayar_brdf_use_rough_tex:
                    layout.prop_search(asr_mat, "orennayar_brdf_rough_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "orennayar_brdf_use_rough_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.orennayar_brdf_rough_tex != '' and asr_mat.orennayar_brdf_use_rough_tex:
                    rough_tex = bpy.data.textures[asr_mat.orennayar_brdf_rough_tex]
                    layout.prop(rough_tex.image.colorspace_settings, "name", text="Color Space")

            #
            # Plastic BRDF.
            #

            elif asr_mat.bsdf_type == "plastic_brdf":
                # mdf
                col = layout.column()
                col.prop(asr_mat, "plastic_brdf_mdf", text="Microfacet Distribution Function")

                # specular reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Specular Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_specular_reflectance", text="")

                if asr_mat.plastic_brdf_specular_reflectance_use_tex:
                    layout.prop_search(asr_mat, "plastic_brdf_specular_reflectance_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_specular_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.plastic_brdf_specular_reflectance_tex != '' and asr_mat.plastic_brdf_specular_reflectance_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.plastic_brdf_specular_reflectance_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # specular reflectance multiplier
                split = layout.split(percentage=0.9)
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_specular_reflectance_multiplier", text="Specular Reflectance Multiplier")

                if asr_mat.plastic_brdf_specular_reflectance_multiplier_use_tex:
                    layout.prop_search(asr_mat, "plastic_brdf_specular_reflectance_multiplier_tex", material, "texture_slots", text="")

                split = split.split()
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_specular_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.plastic_brdf_specular_reflectance_multiplier_tex != '' and asr_mat.plastic_brdf_specular_reflectance_multiplier_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.plastic_brdf_specular_reflectance_multiplier_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # roughness
                split = layout.split(percentage=0.9)
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_roughness", text="Roughness")

                if asr_mat.plastic_brdf_roughness_use_tex:
                    layout.prop_search(asr_mat, "plastic_brdf_roughness_tex", material, "texture_slots", text="")

                split = split.split()
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_roughness_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.plastic_brdf_roughness_tex != '' and asr_mat.plastic_brdf_roughness_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.plastic_brdf_roughness_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                col = layout.column()
                col.prop(asr_mat, "plastic_brdf_highlight_falloff", text="Highlight Falloff")
                col.prop(asr_mat, "plastic_brdf_ior", text="Index of Refraction")

                # diffuse reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Diffuse Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_diffuse_reflectance", text="")

                if asr_mat.plastic_brdf_diffuse_reflectance_use_tex:
                    layout.prop_search(asr_mat, "plastic_brdf_diffuse_reflectance_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_diffuse_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.plastic_brdf_diffuse_reflectance_tex != '' and asr_mat.plastic_brdf_diffuse_reflectance_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.plastic_brdf_diffuse_reflectance_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # diffuse reflectance multiplier
                split = layout.split(percentage=0.9)
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_diffuse_reflectance_multiplier", text="Diffuse Reflectance Multiplier")

                if asr_mat.plastic_brdf_diffuse_reflectance_multiplier_use_tex:
                    layout.prop_search(asr_mat, "plastic_brdf_diffuse_reflectance_multiplier_tex", material, "texture_slots", text="")

                split = split.split()
                col = split.column()
                col.prop(asr_mat, "plastic_brdf_diffuse_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.plastic_brdf_diffuse_reflectance_multiplier_tex != '' and asr_mat.plastic_brdf_diffuse_reflectance_multiplier_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.plastic_brdf_diffuse_reflectance_multiplier_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                col = layout.column()
                col.prop(asr_mat, "plastic_brdf_internal_scattering", text="Internal Scattering")

            #
            # Sheen BRDF.
            #

            elif asr_mat.bsdf_type == "sheen_brdf":
                # reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "sheen_brdf_reflectance", text="")

                if asr_mat.sheen_brdf_reflectance_use_tex:
                    layout.prop_search(asr_mat, "sheen_brdf_reflectance_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "sheen_brdf_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.sheen_brdf_reflectance_tex != '' and asr_mat.sheen_brdf_reflectance_use_tex:
                    specular_tex = bpy.data.textures[asr_mat.sheen_brdf_reflectance_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                # reflectance multiplier
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "sheen_brdf_reflectance_multiplier", text="Reflectance Multiplier")

                if asr_mat.sheen_brdf_reflectance_multiplier_use_tex:
                    layout.prop_search(asr_mat, "sheen_brdf_reflectance_multiplier_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "sheen_brdf_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.sheen_brdf_reflectance_multiplier_tex != '' and asr_mat.sheen_brdf_reflectance_multiplier_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.sheen_brdf_reflectance_multiplier_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

            #
            # Specular BRDF.
            #

            elif asr_mat.bsdf_type == "specular_brdf":
                # glossiness
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Specular Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "specular_brdf_reflectance", text="")

                if asr_mat.specular_brdf_use_glossy_tex:
                    layout.prop_search(asr_mat, "specular_brdf_glossy_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "specular_brdf_use_glossy_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.specular_brdf_glossy_tex != '' and asr_mat.specular_brdf_use_glossy_tex:
                    specular_tex = bpy.data.textures[asr_mat.specular_brdf_glossy_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                layout.prop(asr_mat, "specular_brdf_multiplier", text="Specular Reflectance Multiplier")

            #
            # Specular BTDF.
            #

            elif asr_mat.bsdf_type == "specular_btdf":
                # specular reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Specular Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "specular_btdf_reflectance", text="")

                if asr_mat.specular_btdf_use_specular_tex:
                    layout.prop_search(asr_mat, "specular_btdf_specular_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "specular_btdf_use_specular_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.specular_btdf_specular_tex != '' and asr_mat.specular_btdf_use_specular_tex:
                    specular_tex = bpy.data.textures[asr_mat.specular_btdf_specular_tex]
                    layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                layout.prop(asr_mat, "specular_btdf_refl_mult", text="Specular Reflectance Multiplier")

                # transmittance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Specular Transmittance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "specular_btdf_transmittance", text="")

                if asr_mat.specular_btdf_use_trans_tex:
                    layout.prop_search(asr_mat, "specular_btdf_trans_tex", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "specular_btdf_use_trans_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.specular_btdf_trans_tex != '' and asr_mat.specular_btdf_use_trans_tex:
                    trans_tex = bpy.data.textures[asr_mat.specular_btdf_trans_tex]
                    layout.prop(trans_tex.image.colorspace_settings, "name", text="Color Space")

                layout.prop(asr_mat, "specular_btdf_trans_mult", text="Specular Transmittance Multiplier")

                # Fresnel multiplier
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "specular_btdf_fresnel_multiplier", text="Fresnel Multiplier")

                if asr_mat.specular_btdf_fresnel_multiplier_use_tex:
                    layout.prop_search(asr_mat, "specular_btdf_fresnel_multiplier_tex", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "specular_btdf_fresnel_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.specular_btdf_fresnel_multiplier_tex != '' and asr_mat.specular_btdf_fresnel_multiplier_use_tex:
                    diffuse_tex = bpy.data.textures[asr_mat.specular_btdf_fresnel_multiplier_tex]
                    layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                # IOR
                layout.prop(asr_mat, "specular_btdf_ior", text="Index of Refraction")

                # volume
                layout.prop(asr_mat, "specular_btdf_volume_density", text="Volume Density")

                # volume density
                layout.prop(asr_mat, "specular_btdf_volume_scale", text="Volume Scale")

            layout.separator()

            #
            # BSSRDF
            #

            # Model
            layout.prop(asr_mat, "bssrdf_model")
            if asr_mat.bssrdf_model != 'none':
                # Weight
                layout.prop(asr_mat, "bssrdf_weight", text="Weight")

                # Reflectance
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Reflectance:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "bssrdf_reflectance", text="")

                if asr_mat.bssrdf_reflectance_use_texture:
                    layout.prop_search(asr_mat, "bssrdf_reflectance_texture", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "bssrdf_reflectance_use_texture", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.bssrdf_reflectance_texture != '' and asr_mat.bssrdf_reflectance_use_texture:
                    specular_texture = bpy.data.textures[asr_mat.bssrdf_reflectance_texture]
                    layout.prop(specular_texture.image.colorspace_settings, "name", text="Color Space")

                # Reflectance multiplier
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "bssrdf_reflectance_multiplier", text="Reflectance Multiplier")

                if asr_mat.bssrdf_reflectance_multiplier_use_texture:
                    layout.prop_search(asr_mat, "bssrdf_reflectance_multiplier_texture", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "bssrdf_reflectance_multiplier_use_texture", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.bssrdf_reflectance_multiplier_texture != '' and asr_mat.bssrdf_reflectance_multiplier_use_texture:
                    reflect_mult_tex = bpy.data.textures[asr_mat.bssrdf_reflectance_multiplier_texture]
                    layout.prop(reflect_mult_tex.image.colorspace_settings, "name", text="Color Space")

                # MFP
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Mean Free Path:")
                split = split.split(percentage=0.83)
                col = split.column()
                col.prop(asr_mat, "bssrdf_mfp", text="")

                if asr_mat.bssrdf_mfp_use_texture:
                    layout.prop_search(asr_mat, "bssrdf_mfp_texture", material, "texture_slots", text="")

                split = split.split(percentage=1.0)
                col = split.column()
                col.prop(asr_mat, "bssrdf_mfp_use_texture", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.bssrdf_mfp_texture != '' and asr_mat.bssrdf_mfp_use_texture:
                    meanfp_texture = bpy.data.textures[asr_mat.bssrdf_mfp_texture]
                    layout.prop(meanfp_texture.image.colorspace_settings, "name", text="Color Space")

                # MFP multiplier
                split = layout.split(percentage=0.90)
                col = split.column()
                col.prop(asr_mat, "bssrdf_mfp_multiplier", text="Mean Free Path Multiplier")

                if asr_mat.bssrdf_mfp_multiplier_use_texture:
                    layout.prop_search(asr_mat, "bssrdf_mfp_multiplier_texture", material, "texture_slots", text="")

                col = split.column()
                col.prop(asr_mat, "bssrdf_mfp_multiplier_use_texture", text="", icon="TEXTURE_SHADED", toggle=True)
                if asr_mat.bssrdf_mfp_multiplier_texture != '' and asr_mat.bssrdf_mfp_multiplier_use_texture:
                    mfp_mult_tex = bpy.data.textures[asr_mat.bssrdf_mfp_multiplier_texture]
                    layout.prop(mfp_mult_tex.image.colorspace_settings, "name", text="Color Space")

                # IOR
                layout.prop(asr_mat, "bssrdf_ior", text="Index of Refraction")

                # Fresnel weight
                layout.prop(asr_mat, "bssrdf_fresnel_weight", text="Fresnel Weight")

            layout.separator()

            #
            # Volume
            #
            col = layout.column()
            col.prop(asr_mat, "volume_phase_function_model")
            if asr_mat.volume_phase_function_model != 'none':
                # Absorption
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Absorption:")
                col = split.column()
                col.prop(asr_mat, "volume_absorption", text="")

                # Absorption Multiplier
                col = layout.column()
                col.prop(asr_mat, "volume_absorption_multiplier", text="Absorption Multiplier")

                # Volume Scattering
                split = layout.split(percentage=0.40)
                col = split.column()
                col.label("Scattering:")
                col = split.column()
                col.prop(asr_mat, "volume_scattering", text="")

                # Scattering Multiplier
                col = layout.column()
                col.prop(asr_mat, "volume_scattering_multiplier", text="Scattering Multiplier")

                if asr_mat.volume_phase_function_model == 'henyey':
                    col.prop(asr_mat, "volume_average_cosine", text="Average Cosine")

            #
            # Alpha mapping.
            #

            layout.separator()

            split = layout.split(percentage=0.90)
            col = split.column()
            col.prop(asr_mat, "material_alpha", text="Alpha")

            if asr_mat.material_use_alpha:
                layout.prop_search(asr_mat, "material_alpha_map",
                                   material, "texture_slots", text="")

            col = split.column()
            col.prop(asr_mat, "material_use_alpha", text="", icon="TEXTURE_SHADED", toggle=True)
            if asr_mat.material_alpha_map != '' and asr_mat.material_use_alpha:
                alpha_tex = bpy.data.textures[asr_mat.material_alpha_map]
                layout.prop(alpha_tex.image.colorspace_settings,
                            "name", text="Color Space")

            #
            # Bump/normal mapping.
            #

            split = layout.split(percentage=0.50)
            col = split.column()
            col.prop(asr_mat, "material_use_bump_tex", text="Bump Map", icon="POTATO", toggle=True)
            col = split.column()
            if asr_mat.material_use_bump_tex:
                col.prop(asr_mat, "material_use_normalmap", text="Normal Map", toggle=True)
                layout.prop_search(asr_mat, "material_bump_tex", material, "texture_slots", text="")

                if asr_mat.material_bump_tex != '':
                    bump_tex = bpy.data.textures[asr_mat.material_bump_tex]
                    layout.prop(bump_tex.image.colorspace_settings, "name", text="Color Space")
                if not asr_mat.material_use_normalmap:
                    layout.prop(asr_mat, "material_bump_amplitude", text="Bump Amplitude")
                    layout.prop(asr_mat, "material_bump_offset", text="Bump Offset")


class AppleseedMatEmissionPanel(bpy.types.Panel):
    bl_label = "Light Material"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render.engine == 'APPLESEED_RENDER'
        obj = context.object is not None
        obj_type = context.object.type == 'MESH'
        material = context.object.active_material is not None
        if material:
            is_not_nodemat = context.object.active_material.appleseed.osl_node_tree == None
            return renderer and obj and obj_type and material and is_not_nodemat
        return False

    def draw_header(self, context):
        header = self.layout
        asr_mat = context.object.active_material.appleseed
        header.prop(asr_mat, "use_light_emission", text="")

    def draw(self, context):
        layout = self.layout
        material = context.object.active_material
        asr_mat = material.appleseed

        layout.active = asr_mat.use_light_emission
        col = layout.column()
        col.active = asr_mat.use_light_emission
        split = layout.split(percentage=0.40)
        col = split.column()
        col.label("Radiance:")
        col = split.column()
        col.prop(asr_mat, "light_color", text="")
        col = layout.column()
        col.prop(asr_mat, "light_emission_profile")
        if asr_mat.light_emission_profile == 'cone_edf':
            col.prop(asr_mat, "light_cone_edf_angle", text="Cone EDF Angle")
        col.prop(asr_mat, "light_emission", text="Radiance Multiplier")
        col.prop(asr_mat, "light_exposure", text="Exposure")
        layout.prop(asr_mat, "cast_indirect", text="Cast Indirect Light")
        layout.prop(asr_mat, "importance_multiplier", text="Importance Multiplier")
        layout.prop(asr_mat, "light_near_start", text="Light Near Start")


class TextureConvertSlots(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        texture = item.name
        if 'DEFAULT' in self.layout_type:
            layout.label(text=texture, translate=False, icon_value=icon)


class AppleseedTextureConverterPanel(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    bl_context = "material"
    bl_label = "Texture Converter"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine in cls.COMPAT_ENGINES and context.object is not None and context.object.active_material.appleseed.osl_node_tree is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        asr_scene_props = scene.appleseed
        textures = asr_scene_props.textures

        row = layout.row()
        row.template_list("TextureConvertSlots", "", asr_scene_props,
                          "textures", asr_scene_props, "textures_index", rows=1, maxrows=16, type="DEFAULT")

        col = layout.column(align=True)

        col.prop(asr_scene_props, "sub_textures", text="Use Converted Textures", toggle=True)
        row = col.row(align=True)
        row.operator("appleseed.add_texture", text="Add Texture", icon="ZOOMIN")
        row.operator("appleseed.remove_texture", text="Remove Texture", icon="ZOOMOUT")
        row = col.row(align=True)
        row.operator("appleseed.refresh_textures", text="Refresh Textures", icon='FILE_REFRESH')
        row.operator("appleseed.convert_textures", text="Convert Textures", icon='PLAY')

        if textures:
            current_set = textures[asr_scene_props.textures_index]
            layout.prop(current_set, "name", text="Texture")
            layout.prop(current_set, "input_space")
            layout.prop(current_set, "output_depth")
            layout.prop(current_set, "command_string", text="Additional Commands")


def register():
    bpy.types.MATERIAL_PT_context_material.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.MATERIAL_PT_custom_props.COMPAT_ENGINES.add('APPLESEED_RENDER')
    util.safe_register_class(AppleseedMaterialPreview)
    util.safe_register_class(AppleseedMaterialShading)
    util.safe_register_class(AppleseedMatEmissionPanel)
    util.safe_register_class(TextureConvertSlots)
    util.safe_register_class(AppleseedTextureConverterPanel)


def unregister():
    util.safe_unregister_class(AppleseedTextureConverterPanel)
    util.safe_unregister_class(TextureConvertSlots)
    util.safe_unregister_class(AppleseedMatEmissionPanel)
    util.safe_unregister_class(AppleseedMaterialShading)
    util.safe_unregister_class(AppleseedMaterialPreview)
    bpy.types.MATERIAL_PT_context_material.COMPAT_ENGINES.remove('APPLESEED_RENDER')
    bpy.types.MATERIAL_PT_custom_props.COMPAT_ENGINES.remove('APPLESEED_RENDER')
