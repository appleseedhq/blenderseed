
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

#---------------------------------------------
# node tree selector ui
#---------------------------------------------


def node_tree_selector_draw(layout, mat, output_type):
    try:
        layout.prop_search(mat.appleseed, "node_tree", bpy.data, "node_groups", text="Node Tree")
    except:
        return False

    node = find_node(mat, output_type)
    if not node:
        if mat.appleseed.node_tree == '':
            layout.operator('appleseed.add_material_nodetree', text="appleseed Node", icon='NODETREE')
            return False
    return True


def find_node(material, nodetype):
    if not (material and material.appleseed and material.appleseed.node_tree):
        return None

    node_tree = material.appleseed.node_tree

    if node_tree == '':
        return None

    ntree = bpy.data.node_groups[node_tree]

    for node in ntree.nodes:
        nt = getattr(node, "bl_idname", None)
        if nt == nodetype:
            return node
    return None

#---------------------------------------------
# material preview panel
#---------------------------------------------


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

#---------------------------------------------
# material bsdf slot
#---------------------------------------------


class MATERIAL_UL_BSDF_slots(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        BSDF = item
        bsdf_type = BSDF.bsdf_type
        bsdf_type_name = bsdf_type[0].upper() + bsdf_type[1:-5] + " " + bsdf_type[-4:].upper()
        if 'DEFAULT' in self.layout_type:
            layout.label(text=BSDF.name + "  |  " + bsdf_type_name, translate=False, icon_value=icon)

#---------------------------------------------
# material shading panel
#---------------------------------------------


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

        node_tree_selector_draw(layout, material, 'AppleseedMaterialNode')
        if asr_mat.node_tree != '':
            node_tree = bpy.data.node_groups[asr_mat.node_tree]
            layout.prop_search(asr_mat, "node_output", node_tree, "nodes", text="Node Output")

        if asr_mat.node_tree == '':
            row = layout.row()
            row.template_list("MATERIAL_UL_BSDF_slots", "appleseed_material_layers", asr_mat,
                              "layers", asr_mat, "layer_index", rows=1, maxrows=16, type="DEFAULT")

            row = layout.row(align=True)
            row.operator("appleseed.add_matlayer", text="Add Layer", icon="ZOOMIN")
            row.operator("appleseed.remove_matlayer", text="Remove", icon="ZOOMOUT")

            if asr_mat.layers:
                current_layer = asr_mat.layers[asr_mat.layer_index]
                layout.prop(current_layer, "bsdf_name", text="BSDF Name")
                layout.prop(current_layer, "bsdf_type", text="BSDF Model")
                layout.separator()

                # Lambertian brdf layout
                if current_layer.bsdf_type == "lambertian_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "lambertian_brdf_weight", text="Layer Weight")
                    if current_layer.lambertian_brdf_use_tex:
                        layout.prop_search(current_layer, "lambertian_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "lambertian_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.lambertian_brdf_mix_tex != '' and current_layer.lambertian_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.lambertian_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "lambertian_brdf_reflectance", text="")

                    if current_layer.lambertian_brdf_use_diffuse_tex:
                        layout.prop_search(current_layer, "lambertian_brdf_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "lambertian_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.lambertian_brdf_diffuse_tex != '' and current_layer.lambertian_brdf_use_diffuse_tex:
                        diffuse_tex = bpy.data.textures[current_layer.lambertian_brdf_diffuse_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")
                    layout.prop(current_layer, "lambertian_brdf_multiplier", text="Reflectance Multiplier")

                #-------------------------------------------------

                # sheen brdf layout
                if current_layer.bsdf_type == "sheen_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "sheen_brdf_weight", text="Layer Weight")
                    if current_layer.sheen_brdf_use_tex:
                        layout.prop_search(current_layer, "sheen_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "sheen_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.sheen_brdf_mix_tex != '' and current_layer.sheen_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.sheen_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "sheen_brdf_reflectance", text="")

                    if current_layer.sheen_brdf_reflectance_use_tex:
                        layout.prop_search(current_layer, "sheen_brdf_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "sheen_brdf_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.sheen_brdf_reflectance_tex != '' and current_layer.sheen_brdf_reflectance_use_tex:
                        specular_tex = bpy.data.textures[current_layer.sheen_brdf_reflectance_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "sheen_brdf_reflectance_multiplier", text="Reflectance Multiplier")

                    if current_layer.sheen_brdf_reflectance_multiplier_use_tex:
                        layout.prop_search(current_layer, "sheen_brdf_reflectance_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "sheen_brdf_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.sheen_brdf_reflectance_multiplier_tex != '' and current_layer.sheen_brdf_reflectance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.sheen_brdf_reflectance_multiplier_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                #-------------------------------------------------

                # glossy brdf layout
                if current_layer.bsdf_type == "glossy_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_weight", text="Layer Weight")
                    if current_layer.glossy_brdf_use_tex:
                        layout.prop_search(current_layer, "glossy_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_brdf_mix_tex != '' and current_layer.glossy_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.glossy_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # mdf
                    col = layout.column()
                    col.prop(current_layer, "glossy_brdf_mdf", text="Microfacet Distribution Function")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_reflectance", text="")

                    if current_layer.glossy_brdf_reflectance_use_tex:
                        layout.prop_search(current_layer, "glossy_brdf_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_brdf_reflectance_tex != '' and current_layer.glossy_brdf_reflectance_use_tex:
                        specular_tex = bpy.data.textures[current_layer.glossy_brdf_reflectance_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_reflectance_multiplier", text="Reflectance Multiplier")

                    if current_layer.glossy_brdf_reflectance_multiplier_use_tex:
                        layout.prop_search(current_layer, "glossy_brdf_reflectance_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_brdf_reflectance_multiplier_tex != '' and current_layer.glossy_brdf_reflectance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.glossy_brdf_reflectance_multiplier_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_roughness", text="Roughness")

                    if current_layer.glossy_brdf_roughness_use_tex:
                        layout.prop_search(current_layer, "glossy_brdf_roughness_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_roughness_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_brdf_roughness_tex != '' and current_layer.glossy_brdf_roughness_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.glossy_brdf_roughness_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # highlight falloff
                    col = layout.column()
                    col.prop(current_layer, "glossy_brdf_highlight_falloff", text="Highlight Falloff")

                    # anisotropy
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_anisotropy", text="Anisotropy")

                    if current_layer.glossy_brdf_anisotropy_use_tex:
                        layout.prop_search(current_layer, "glossy_brdf_anisotropy_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glossy_brdf_anisotropy_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_brdf_anisotropy_tex != '' and current_layer.glossy_brdf_anisotropy_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.glossy_brdf_anisotropy_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # ior
                    col = layout.column()
                    col.prop(current_layer, "glossy_brdf_ior", text="Index of Refraction")

                #--------------------------------------------------

                # glass bsdf layout
                if current_layer.bsdf_type == "glass_bsdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_weight", text="Layer Weight")
                    if current_layer.glass_bsdf_use_tex:
                        layout.prop_search(current_layer, "glass_bsdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_bsdf_mix_tex != '' and current_layer.glass_bsdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.glass_bsdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # mdf
                    col = layout.column()
                    col.prop(current_layer, "glass_bsdf_mdf", text="Microfacet Distribution Function")

                    # surface transmittance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Surface Transmittance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_surface_transmittance", text="")

                    if current_layer.glass_bsdf_surface_transmittance_use_tex:
                        layout.prop_search(current_layer, "glass_bsdf_surface_transmittance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_surface_transmittance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_bsdf_surface_transmittance_tex != '' and current_layer.glass_bsdf_surface_transmittance_use_tex:
                        specular_tex = bpy.data.textures[current_layer.glass_bsdf_surface_transmittance_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # surface transmittance multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_surface_transmittance_multiplier", text="Surface Transmittance Multiplier")

                    if current_layer.glass_bsdf_surface_transmittance_multiplier_use_tex:
                        layout.prop_search(current_layer, "glass_bsdf_surface_transmittance_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_surface_transmittance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_bsdf_surface_transmittance_multiplier_tex != '' and current_layer.glass_bsdf_surface_transmittance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.glass_bsdf_surface_transmittance_multiplier_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflection tint
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflection Tint:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_reflection_tint", text="")

                    if current_layer.glass_bsdf_reflection_tint_use_tex:
                        layout.prop_search(current_layer, "glass_bsdf_reflection_tint_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_reflection_tint_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_bsdf_reflection_tint_tex != '' and current_layer.glass_bsdf_reflection_tint_use_tex:
                        specular_tex = bpy.data.textures[current_layer.glass_bsdf_reflection_tint_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # refraction tint
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Refraction Tint:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_refraction_tint", text="")

                    if current_layer.glass_bsdf_refraction_tint_use_tex:
                        layout.prop_search(current_layer, "glass_bsdf_refraction_tint_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_refraction_tint_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_bsdf_refraction_tint_tex != '' and current_layer.glass_bsdf_refraction_tint_use_tex:
                        specular_tex = bpy.data.textures[current_layer.glass_bsdf_refraction_tint_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # ior
                    col = layout.column()
                    col.prop(current_layer, "glass_bsdf_ior", text="Index of Refraction")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_roughness", text="Roughness")

                    if current_layer.glass_bsdf_roughness_use_tex:
                        layout.prop_search(current_layer, "glass_bsdf_roughness_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_roughness_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_bsdf_roughness_tex != '' and current_layer.glass_bsdf_roughness_use_tex:
                        glass_bsdf_roughness = bpy.data.textures[current_layer.glass_bsdf_roughness_tint_tex]
                        layout.prop(glass_bsdf_roughness.image.colorspace_settings, "name", text="Color Space")

                    # highlight falloff
                    col = layout.column()
                    col.prop(current_layer, "glass_bsdf_highlight_falloff", text="Highlight Falloff")

                    # anisotropy
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_anisotropy", text="Anisotropy")

                    if current_layer.glass_bsdf_anisotropy_use_tex:
                        layout.prop_search(current_layer, "glass_bsdf_anisotropy_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glass_bsdf_anisotropy_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_bsdf_anisotropy_tex != '' and current_layer.glass_bsdf_anisotropy_use_tex:
                        glass_bsdf_anisotropy = bpy.data.textures[current_layer.glass_bsdf_anisotropy_tex]
                        layout.prop(glass_bsdf_anisotropy.image.colorspace_settings, "name", text="Color Space")

                    # volume parameterization
                    col = layout.column()
                    col.prop(current_layer, "glass_bsdf_volume_parameterization", text="Volume Absorption Parameterization")

                    if current_layer.glass_bsdf_volume_parameterization == 'transmittance':
                        # normal reflectance
                        split = layout.split(percentage=0.40)
                        col = split.column()
                        col.label("Volume Transmittance:")
                        split = split.split(percentage=0.83)
                        col = split.column()
                        col.prop(current_layer, "glass_bsdf_volume_transmittance", text="")

                        if current_layer.glass_bsdf_volume_transmittance_use_tex:
                            layout.prop_search(current_layer, "glass_bsdf_volume_transmittance_tex", material, "texture_slots")

                        split = split.split(percentage=1.0)
                        col = split.column()
                        col.prop(current_layer, "glass_bsdf_volume_transmittance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                        if current_layer.glass_bsdf_volume_transmittance_tex != '' and current_layer.glass_bsdf_volume_transmittance_use_tex:
                            specular_tex = bpy.data.textures[current_layer.glass_bsdf_volume_transmittance_tex]
                            layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                        # glass volume transmittance distance
                        split = layout.split(percentage=0.90)
                        col = split.column()
                        col.prop(current_layer, "glass_bsdf_volume_transmittance_distance", text="Volume Transmittance Distance")

                        if current_layer.glass_bsdf_volume_transmittance_distance_use_tex:
                            layout.prop_search(current_layer, "glass_bsdf_volume_transmittance_distance_tex", material, "texture_slots")

                        col = split.column()
                        col.prop(current_layer, "glass_bsdf_volume_transmittance_distance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                        if current_layer.glass_bsdf_volume_transmittance_distance_tex != '' and current_layer.glass_bsdf_volume_transmittance_distance_use_tex:
                            glass_bsdf_volume_transmittance_distance = bpy.data.textures[current_layer.glass_bsdf_volume_transmittance_distance_tex]
                            layout.prop(glass_bsdf_volume_transmittance_distance.image.colorspace_settings, "name", text="Color Space")

                    else:
                        # glass volume density
                        split = layout.split(percentage=0.90)
                        col = split.column()
                        col.prop(current_layer, "glass_bsdf_volume_density", text="Volume Density")

                        if current_layer.glass_bsdf_volume_density_use_tex:
                            layout.prop_search(current_layer, "glass_bsdf_volume_density_tex", material, "texture_slots")

                        col = split.column()
                        col.prop(current_layer, "glass_bsdf_volume_density_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                        if current_layer.glass_bsdf_volume_density_tex != '' and current_layer.glass_bsdf_volume_density_use_tex:
                            glass_bsdf_volume_density = bpy.data.textures[current_layer.glass_bsdf_volume_density_tex]
                            layout.prop(glass_bsdf_volume_density.image.colorspace_settings, "name", text="Color Space")

                        # glass absorption
                        split = layout.split(percentage=0.40)
                        col = split.column()
                        col.label("Volume Absorption:")
                        split = split.split(percentage=0.83)
                        col = split.column()
                        col.prop(current_layer, "glass_bsdf_volume_absorption", text="")

                        if current_layer.glass_bsdf_volume_absorption_use_tex:
                            layout.prop_search(current_layer, "glass_bsdf_volume_absorption_tex", material, "texture_slots")

                        split = split.split(percentage=1.0)
                        col = split.column()
                        col.prop(current_layer, "glass_bsdf_volume_absorption_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                        if current_layer.glass_bsdf_volume_absorption_tex != '' and current_layer.glass_bsdf_volume_absorption_use_tex:
                            specular_tex = bpy.data.textures[current_layer.glass_bsdf_volume_absorption_tex]
                            layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # scale
                    col = layout.column()
                    col.prop(current_layer, "glass_bsdf_volume_scale", text="Volume Scale")

                #------------------------------------------------

                # metal brdf layout
                if current_layer.bsdf_type == "metal_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "metal_brdf_weight", text="Layer Weight")
                    if current_layer.metal_brdf_use_tex:
                        layout.prop_search(current_layer, "metal_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "metal_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_brdf_mix_tex != '' and current_layer.metal_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.metal_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # mdf
                    col = layout.column()
                    col.prop(current_layer, "metal_brdf_mdf", text="Microfacet Distribution Function")

                    # normal reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Normal Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "metal_brdf_normal_reflectance", text="")

                    if current_layer.metal_brdf_normal_reflectance_use_tex:
                        layout.prop_search(current_layer, "metal_brdf_normal_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "metal_brdf_normal_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_brdf_normal_reflectance_tex != '' and current_layer.metal_brdf_normal_reflectance_use_tex:
                        specular_tex = bpy.data.textures[current_layer.metal_brdf_normal_reflectance_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # edge tint
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Edge Tint:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "metal_brdf_edge_tint", text="")

                    if current_layer.metal_brdf_edge_tint_use_tex:
                        layout.prop_search(current_layer, "metal_brdf_edge_tint_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "metal_brdf_edge_tint_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_brdf_edge_tint_tex != '' and current_layer.metal_brdf_edge_tint_use_tex:
                        specular_tex = bpy.data.textures[current_layer.metal_brdf_edge_tint_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "metal_brdf_reflectance_multiplier", text="Reflectance Multiplier")

                    if current_layer.metal_brdf_reflectance_multiplier_use_tex:
                        layout.prop_search(current_layer, "metal_brdf_reflectance_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "metal_brdf_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_brdf_reflectance_multiplier_tex != '' and current_layer.metal_brdf_reflectance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.metal_brdf_reflectance_multiplier_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "metal_brdf_roughness", text="Roughness")

                    if current_layer.metal_brdf_roughness_use_tex:
                        layout.prop_search(current_layer, "metal_brdf_roughness_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "metal_brdf_roughness_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_brdf_roughness_tex != '' and current_layer.metal_brdf_roughness_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.metal_brdf_roughness_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    col = layout.column()
                    col.prop(current_layer, "metal_brdf_highlight_falloff", text="Highlight Falloff")

                    # anisotropy
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "metal_brdf_anisotropy", text="Anisotropy")

                    if current_layer.metal_brdf_anisotropy_use_tex:
                        layout.prop_search(current_layer, "metal_brdf_anisotropy_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "metal_brdf_anisotropy_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_brdf_anisotropy_tex != '' and current_layer.metal_brdf_anisotropy_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.metal_brdf_anisotropy_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                #-------------------------------------------------

                # plastic brdf layout
                if current_layer.bsdf_type == "plastic_brdf":
                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_weight", text="Layer Weight")
                    if current_layer.plastic_brdf_use_tex:
                        layout.prop_search(current_layer, "plastic_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_brdf_mix_tex != '' and current_layer.plastic_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.plastic_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # mdf
                    col = layout.column()
                    col.prop(current_layer, "plastic_brdf_mdf", text="Microfacet Distribution Function")

                    # specular reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_specular_reflectance", text="")

                    if current_layer.plastic_brdf_specular_reflectance_use_tex:
                        layout.prop_search(current_layer, "plastic_brdf_specular_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_specular_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_brdf_specular_reflectance_tex != '' and current_layer.plastic_brdf_specular_reflectance_use_tex:
                        specular_tex = bpy.data.textures[current_layer.plastic_brdf_specular_reflectance_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # specular reflectance multiplier
                    split = layout.split(percentage=0.9)
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_specular_reflectance_multiplier", text="Specular Reflectance Multiplier")

                    if current_layer.plastic_brdf_specular_reflectance_multiplier_use_tex:
                        layout.prop_search(current_layer, "plastic_brdf_specular_reflectance_multiplier_tex", material, "texture_slots")

                    split = split.split()
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_specular_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_brdf_specular_reflectance_multiplier_tex != '' and current_layer.plastic_brdf_specular_reflectance_multiplier_use_tex:
                        specular_tex = bpy.data.textures[current_layer.plastic_brdf_specular_reflectance_multiplier_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.9)
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_roughness", text="Roughness")

                    if current_layer.plastic_brdf_roughness_use_tex:
                        layout.prop_search(current_layer, "plastic_brdf_roughness_tex", material, "texture_slots")

                    split = split.split()
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_roughness_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_brdf_roughness_tex != '' and current_layer.plastic_brdf_roughness_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.plastic_brdf_roughness_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    col = layout.column()
                    col.prop(current_layer, "plastic_brdf_highlight_falloff", text="Highlight Falloff")
                    col.prop(current_layer, "plastic_brdf_ior", text="Index of Refraction")

                    # diffuse reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Diffuse Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_diffuse_reflectance", text="")

                    if current_layer.plastic_brdf_diffuse_reflectance_use_tex:
                        layout.prop_search(current_layer, "plastic_brdf_diffuse_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_diffuse_reflectance_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_brdf_diffuse_reflectance_tex != '' and current_layer.plastic_brdf_diffuse_reflectance_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.plastic_brdf_diffuse_reflectance_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # diffuse reflectance multiplier
                    split = layout.split(percentage=0.9)
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_diffuse_reflectance_multiplier", text="Diffuse Reflectance Multiplier")

                    if current_layer.plastic_brdf_diffuse_reflectance_multiplier_use_tex:
                        layout.prop_search(current_layer, "plastic_brdf_diffuse_reflectance_multiplier_tex", material, "texture_slots")

                    split = split.split()
                    col = split.column()
                    col.prop(current_layer, "plastic_brdf_diffuse_reflectance_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_brdf_diffuse_reflectance_multiplier_tex != '' and current_layer.plastic_brdf_diffuse_reflectance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.plastic_brdf_diffuse_reflectance_multiplier_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    col = layout.column()
                    col.prop(current_layer, "plastic_brdf_internal_scattering", text="Internal Scattering")

                #-------------------------------------------------

                # blinn brdf layout
                if current_layer.bsdf_type == "blinn_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "blinn_brdf_weight", text="Layer Weight")
                    if current_layer.blinn_brdf_use_tex:
                        layout.prop_search(current_layer, "blinn_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "blinn_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.blinn_brdf_mix_tex != '' and current_layer.blinn_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.blinn_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # exponent
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "blinn_brdf_exponent", text="Exponent")

                    if current_layer.blinn_brdf_exponent_use_tex:
                        layout.prop_search(current_layer, "blinn_brdf_exponent_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "blinn_brdf_exponent_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.blinn_brdf_exponent_tex != '' and current_layer.blinn_brdf_exponent_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.blinn_brdf_exponent_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # ior
                    col = layout.column()
                    col.prop(current_layer, "blinn_brdf_ior", text="Index of Refraction")

                #-------------------------------------------------

                # oren-nayar brdf layout
                if current_layer.bsdf_type == "orennayar_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "orennayar_brdf_weight", text="Layer Weight")
                    if current_layer.orennayar_brdf_use_tex:
                        layout.prop_search(current_layer, "orennayar_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "orennayar_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.orennayar_brdf_mix_tex != '' and current_layer.orennayar_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.orennayar_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "orennayar_brdf_reflectance", text="")

                    if current_layer.orennayar_brdf_use_diffuse_tex:
                        layout.prop_search(current_layer, "orennayar_brdf_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "orennayar_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.orennayar_brdf_diffuse_tex != '' and current_layer.orennayar_brdf_use_diffuse_tex:
                        diffuse_tex = bpy.data.textures[current_layer.orennayar_brdf_diffuse_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "orennayar_brdf_roughness", text="Roughness")
                    if current_layer.orennayar_brdf_use_rough_tex:
                        layout.prop_search(current_layer, "orennayar_brdf_rough_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "orennayar_brdf_use_rough_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.orennayar_brdf_rough_tex != '' and current_layer.orennayar_brdf_use_rough_tex:
                        rough_tex = bpy.data.textures[current_layer.orennayar_brdf_diffuse_tex]
                        layout.prop(rough_tex.image.colorspace_settings, "name", text="Color Space")

                #-------------------------------------------------

                # ashikhmin-shirley brdf layout
                elif current_layer.bsdf_type == "ashikhmin_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_brdf_weight", text="Layer Weight")
                    if current_layer.ashikhmin_brdf_use_tex:
                        layout.prop_search(current_layer, "ashikhmin_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "ashikhmin_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.ashikhmin_brdf_mix_tex != '' and current_layer.ashikhmin_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.ashikhmin_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Diffuse Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_brdf_reflectance", text="")

                    if current_layer.ashikhmin_brdf_use_diffuse_tex:
                        layout.prop_search(current_layer, "ashikhmin_brdf_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.ashikhmin_brdf_diffuse_tex != '' and current_layer.ashikhmin_brdf_use_diffuse_tex:
                        diffuse_tex = bpy.data.textures[current_layer.ashikhmin_brdf_diffuse_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    row = layout.row()
                    row.prop(current_layer, "ashikhmin_brdf_multiplier", text="Diffuse Reflectance Multiplier")

                    # glossiness
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Glossy Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_brdf_glossy", text="")

                    if current_layer.ashikhmin_brdf_use_glossy_tex:
                        layout.prop_search(current_layer, "ashikhmin_brdf_glossy_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.ashikhmin_brdf_glossy_tex != '' and current_layer.ashikhmin_brdf_use_glossy_tex:
                        diffuse_tex = bpy.data.textures[current_layer.ashikhmin_brdf_glossy_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    row = layout.row()
                    row.prop(current_layer, "ashikhmin_brdf_glossy_multiplier", text="Glossy Reflectance Multiplier")

                    # fresnel
                    col = layout.column()
                    col.prop(current_layer, "ashikhmin_brdf_fresnel", text="Fresnel Multiplier")
                    layout.prop(current_layer, "ashikhmin_brdf_shininess_u", text="Shininess U")
                    layout.prop(current_layer, "ashikhmin_brdf_shininess_v", text="Shininess V")

                #-------------------------------------------------

                # diffuse btdf layout
                elif current_layer.bsdf_type == "diffuse_btdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "diffuse_btdf_weight", text="Layer Weight")
                    if current_layer.diffuse_btdf_transmittance_use_mult_tex:
                        layout.prop_search(current_layer, "diffuse_btdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "diffuse_btdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.diffuse_btdf_mix_tex != '' and current_layer.diffuse_btdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.diffuse_btdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Transmittance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "diffuse_btdf_transmittance_color", text="Transmittance Color")

                    if current_layer.diffuse_btdf_use_diffuse_tex:
                        layout.prop_search(current_layer, "diffuse_btdf_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "diffuse_btdf_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.diffuse_btdf_diffuse_tex != '' and current_layer.diffuse_btdf_use_diffuse_tex:
                        diffuse_tex = bpy.data.textures[current_layer.diffuse_btdf_diffuse_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # transmittance
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "diffuse_btdf_transmittance_multiplier", text="Transmittance Multiplier:")
                    if current_layer.diffuse_btdf_transmittance_use_mult_tex:
                        layout.prop_search(current_layer, "diffuse_btdf_transmittance_mult_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "diffuse_btdf_transmittance_use_mult_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.diffuse_btdf_transmittance_mult_tex != '' and current_layer.diffuse_btdf_transmittance_use_mult_tex:
                        mult_tex = bpy.data.textures[current_layer.diffuse_btdf_transmittance_mult_tex]
                        layout.prop(mult_tex.image.colorspace_settings, "name", text="Color Space")

                #-------------------------------------------------

                # disney brdf layout
                elif current_layer.bsdf_type == "disney_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_weight", text="Layer Weight")
                    if current_layer.disney_brdf_use_tex:
                        layout.prop_search(current_layer, "disney_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_mix_tex != '' and current_layer.disney_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.disney_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # base color
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Base Color:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_base", text="")

                    if current_layer.disney_brdf_use_base_tex:
                        layout.prop_search(current_layer, "disney_brdf_base_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_base_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_base_tex != '' and current_layer.disney_brdf_use_base_tex:
                        diffuse_tex = bpy.data.textures[current_layer.disney_brdf_base_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # subsurface
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_subsurface", text="Subsurface")
                    if current_layer.disney_brdf_use_subsurface_tex:
                        layout.prop_search(current_layer, "disney_brdf_subsurface_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_subsurface_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_subsurface_tex != '' and current_layer.disney_brdf_use_subsurface_tex:
                        subsurface_tex = bpy.data.textures[current_layer.disney_brdf_subsurface_tex]
                        layout.prop(subsurface_tex.image.colorspace_settings, "name", text="Color Space")

                    # metallic
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_metallic", text="Metallic")
                    if current_layer.disney_brdf_use_metallic_tex:
                        layout.prop_search(current_layer, "disney_brdf_metallic_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_metallic_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_metallic_tex != '' and current_layer.disney_brdf_use_metallic_tex:
                        metal_brdf_tex = bpy.data.textures[current_layer.disney_brdf_metallic_tex]
                        layout.prop(metal_brdf_tex.image.colorspace_settings, "name", text="Color Space")

                    # specular
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_spec", text="Specular")
                    if current_layer.disney_brdf_use_specular_tex:
                        layout.prop_search(current_layer, "disney_brdf_specular_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_specular_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_specular_tex != '' and current_layer.disney_brdf_use_specular_tex:
                        specular_tex = bpy.data.textures[current_layer.disney_brdf_specular_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # specular tint
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_specular_tint", text="Specular Tint")
                    if current_layer.disney_brdf_use_specular_tint_tex:
                        layout.prop_search(current_layer, "disney_brdf_specular_tint_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_specular_tint_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_specular_tint_tex != '' and current_layer.disney_brdf_use_specular_tint_tex:
                        specular_tint_tex = bpy.data.textures[current_layer.disney_brdf_specular_tint_tex]
                        layout.prop(specular_tint_tex.image.colorspace_settings, "name", text="Color Space")

                    # anisotropy
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_anisotropy", text="Anisotropy")
                    if current_layer.disney_brdf_use_anisotropy_tex:
                        layout.prop_search(current_layer, "disney_brdf_anisotropy_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_anisotropy_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_anisotropy_tex != '' and current_layer.disney_brdf_use_anisotropy_tex:
                        anisotropy_tex = bpy.data.textures[current_layer.disney_brdf_anisotropy_tex]
                        layout.prop(anisotropy_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_roughness", text="Roughness")
                    if current_layer.disney_brdf_use_roughness_tex:
                        layout.prop_search(current_layer, "disney_brdf_roughness_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_roughness_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_roughness_tex != '' and current_layer.disney_brdf_use_roughness_tex:
                        rough_tex = bpy.data.textures[current_layer.disney_brdf_roughness_tex]
                        layout.prop(rough_tex.image.colorspace_settings, "name", text="Color Space")

                    # sheen
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_sheen", text="Sheen")
                    if current_layer.disney_brdf_use_sheen_brdf_tex:
                        layout.prop_search(current_layer, "disney_brdf_sheen_brdf_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_sheen_brdf_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_sheen_brdf_tex != '' and current_layer.disney_brdf_use_sheen_brdf_tex:
                        sheen_brdf_tex = bpy.data.textures[current_layer.disney_brdf_sheen_brdf_tex]
                        layout.prop(sheen_brdf_tex.image.colorspace_settings, "name", text="Color Space")

                    # sheen tint
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_sheen_brdf_tint", text="Sheen Tint")
                    if current_layer.disney_brdf_use_sheen_brdf_tint_tex:
                        layout.prop_search(current_layer, "disney_brdf_sheen_brdf_tint_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_sheen_brdf_tint_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_sheen_brdf_tint_tex != '' and current_layer.disney_brdf_use_sheen_brdf_tint_tex:
                        sheen_brdf_tint_tex = bpy.data.textures[current_layer.disney_brdf_sheen_brdf_tint_tex]
                        layout.prop(sheen_brdf_tint_tex.image.colorspace_settings, "name", text="Color Space")

                    # clear coat
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_clearcoat", text="Clear Coat")
                    if current_layer.disney_brdf_use_clearcoat_tex:
                        layout.prop_search(current_layer, "disney_brdf_clearcoat_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_clearcoat_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_clearcoat_tex != '' and current_layer.disney_brdf_use_clearcoat_tex:
                        clearcoat_tex = bpy.data.textures[current_layer.disney_brdf_clearcoat_tex]
                        layout.prop(clearcoat_tex.image.colorspace_settings, "name", text="Color Space")

                    # clear coat gloss
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_brdf_clearcoat_gloss", text="Clear Coat Gloss")
                    if current_layer.disney_brdf_use_clearcoat_glossy_tex:
                        layout.prop_search(current_layer, "disney_brdf_clearcoat_glossy_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_brdf_use_clearcoat_glossy_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_brdf_clearcoat_glossy_tex != '' and current_layer.disney_brdf_use_clearcoat_glossy_tex:
                        clearcoat_glossy_tex = bpy.data.textures[current_layer.disney_brdf_clearcoat_glossy_tex]
                        layout.prop(clearcoat_glossy_tex.image.colorspace_settings, "name", text="Color Space")

                #-------------------------------------------------

                # kelemen brdf layout
                elif current_layer.bsdf_type == "kelemen_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "kelemen_brdf_weight", text="Layer Weight")
                    if current_layer.kelemen_brdf_use_tex:
                        layout.prop_search(current_layer, "kelemen_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "kelemen_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.kelemen_brdf_mix_tex != '' and current_layer.kelemen_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.kelemen_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Matte Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "kelemen_brdf_matte_reflectance", text="Matte Reflectance")

                    if current_layer.kelemen_brdf_use_diffuse_tex:
                        layout.prop_search(current_layer, "kelemen_brdf_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "kelemen_brdf_use_diffuse_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.kelemen_brdf_diffuse_tex != '' and current_layer.kelemen_brdf_use_diffuse_tex:
                        diffuse_tex = bpy.data.textures[current_layer.kelemen_brdf_diffuse_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")
                    row = layout.row()
                    row.prop(current_layer, "kelemen_brdf_matte_multiplier", text="Matte Reflectance Multiplier")

                    # spec reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "kelemen_brdf_specular_reflectance", text="Specular Reflectance")

                    if current_layer.kelemen_brdf_use_specular_tex:
                        layout.prop_search(current_layer, "kelemen_brdf_specular_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "kelemen_brdf_use_specular_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.kelemen_brdf_specular_tex != '' and current_layer.kelemen_brdf_use_specular_tex:
                        diffuse_tex = bpy.data.textures[current_layer.kelemen_brdf_specular_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    layout.prop(current_layer, "kelemen_brdf_specular_multiplier", text="Specular Reflectance Multiplier")
                    layout.prop(current_layer, "kelemen_brdf_roughness", text="Roughness")

                #-------------------------------------------------

                # specular brdf layout
                elif current_layer.bsdf_type == "specular_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "specular_brdf_weight", text="Layer Weight")
                    if current_layer.specular_brdf_use_tex:
                        layout.prop_search(current_layer, "specular_brdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "specular_brdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.specular_brdf_mix_tex != '' and current_layer.specular_brdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.specular_brdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # glossiness
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "specular_brdf_reflectance", text="")

                    if current_layer.specular_brdf_use_glossy_tex:
                        layout.prop_search(current_layer, "specular_brdf_glossy_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "specular_brdf_use_glossy_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.specular_brdf_glossy_tex != '' and current_layer.specular_brdf_use_glossy_tex:
                        specular_tex = bpy.data.textures[current_layer.specular_brdf_glossy_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    layout.prop(current_layer, "specular_brdf_multiplier", text="Specular Reflectance Multiplier")

                #----------------------------------------------

                # specular btdf layout
                elif current_layer.bsdf_type == "specular_btdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "specular_btdf_weight", text="Layer Weight")
                    if current_layer.specular_btdf_use_tex:
                        layout.prop_search(current_layer, "specular_btdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "specular_btdf_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.specular_btdf_mix_tex != '' and current_layer.specular_btdf_use_tex:
                        mix_tex = bpy.data.textures[current_layer.specular_btdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings, "name", text="Color Space")

                    # specular reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "specular_btdf_reflectance", text="")

                    if current_layer.specular_btdf_use_specular_tex:
                        layout.prop_search(current_layer, "specular_btdf_specular_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "specular_btdf_use_specular_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.specular_btdf_specular_tex != '' and current_layer.specular_btdf_use_specular_tex:
                        specular_tex = bpy.data.textures[current_layer.specular_btdf_specular_tex]
                        layout.prop(specular_tex.image.colorspace_settings, "name", text="Color Space")

                    layout.prop(current_layer, "specular_btdf_refl_mult", text="Specular Reflectance Multiplier")

                    # transmittance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Transmittance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "specular_btdf_transmittance", text="")

                    if current_layer.specular_btdf_use_trans_tex:
                        layout.prop_search(current_layer, "specular_btdf_trans_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "specular_btdf_use_trans_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.specular_btdf_trans_tex != '' and current_layer.specular_btdf_use_trans_tex:
                        trans_tex = bpy.data.textures[current_layer.specular_btdf_trans_tex]
                        layout.prop(trans_tex.image.colorspace_settings, "name", text="Color Space")

                    layout.prop(current_layer, "specular_btdf_trans_mult", text="Specular Transmittance Multiplier")

                    # Fresnel multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "specular_btdf_fresnel_multiplier", text="Fresnel Multiplier")

                    if current_layer.specular_btdf_fresnel_multiplier_use_tex:
                        layout.prop_search(current_layer, "specular_btdf_fresnel_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "specular_btdf_fresnel_multiplier_use_tex", text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.specular_btdf_fresnel_multiplier_tex != '' and current_layer.specular_btdf_fresnel_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[current_layer.specular_btdf_fresnel_multiplier_tex]
                        layout.prop(diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # IOR
                    layout.prop(current_layer, "specular_btdf_ior", text="Index of Refraction")

                    # volume
                    layout.prop(current_layer, "specular_btdf_volume_density", text="Volume Density")

                    # volume density
                    layout.prop(current_layer, "specular_btdf_volume_scale", text="Volume Scale")


            #----------------------------------------------

            # alpha

            layout.separator()

            layout.prop(asr_mat, "material_alpha", text="Alpha")

            # split = layout.split(percentage=0.50)
            # col = split.column()
            # col.prop(asr_mat, "material_use_alpha", text="Alpha Map", icon="POTATO", toggle=True)
            # col = split.column()
            # if asr_mat.material_use_alpha:
                # col.prop_search(asr_mat, "material_alpha_map", material, "texture_slots", text="")
                # if asr_mat.material_alpha_map != '':
                    # alpha_tex = bpy.data.textures[asr_mat.material_alpha_map]
                    # layout.prop(alpha_tex.image.colorspace_settings, "name", text="Color Space")

            #----------------------------------------------

            # bump/normal mapping

            split = layout.split(percentage=0.50)
            col = split.column()
            col.prop(asr_mat, "material_use_bump_tex", text="Bump Map", icon="POTATO", toggle=True)
            col = split.column()
            if asr_mat.material_use_bump_tex:
                col.prop(asr_mat, "material_use_normalmap", text="Normal Map", toggle=True)
                layout.prop_search(asr_mat, "material_bump_tex", material, "texture_slots", text="")

                if asr_mat.material_bump_tex != '':
                    bump_tex = bpy.data.textures[asr_mat.material_bump_tex]
                    layout.prop(bump_tex.image.colorspace_settings, "name",  text="Color Space")
                layout.prop(asr_mat, "material_bump_amplitude", text="Bump Amplitude")


#---------------------------------------------
# light material panel
#---------------------------------------------


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
            is_not_nodemat = context.object.active_material.appleseed.node_tree == ''
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

        col = layout.column()
        col.active = asr_mat.use_light_emission
        col.prop(asr_mat, "light_color", text="")
        col.prop(asr_mat, "light_emission", text="Radiance Multiplier")

        layout.active = asr_mat.use_light_emission
        row = layout.row(align=True)
        layout.prop(asr_mat, "cast_indirect", text="Cast Indirect Light")
        layout.prop(asr_mat, "importance_multiplier", text="Importance Multiplier")
        layout.prop(asr_mat, "light_near_start", text="Light Near Start")


def register():
    bpy.types.MATERIAL_PT_context_material.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.types.MATERIAL_PT_custom_props.COMPAT_ENGINES.add('APPLESEED_RENDER')
    bpy.utils.register_class(AppleseedMaterialPreview)
    bpy.utils.register_class(MATERIAL_UL_BSDF_slots)
    bpy.utils.register_class(AppleseedMaterialShading)
    bpy.utils.register_class(AppleseedMatEmissionPanel)


def unregister():
    bpy.utils.unregister_class(AppleseedMaterialPreview)
    bpy.utils.unregister_class(MATERIAL_UL_BSDF_slots)
    bpy.utils.unregister_class(AppleseedMaterialShading)
    bpy.utils.unregister_class(AppleseedMatEmissionPanel)
