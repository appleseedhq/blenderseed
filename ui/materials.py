
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
        layout.prop_search(mat.appleseed, "node_tree", bpy.data, "node_groups")
    except:
        return False

    node = find_node(mat, output_type)
    if not node:
        if mat.appleseed.node_tree == '':
            layout.operator('appleseed.add_material_nodetree',
                            text="appleseed Node", icon='NODETREE')
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
        layout.prop(asr_mat, "preview_quality")

#---------------------------------------------
# material bsdf slot
#---------------------------------------------


class MATERIAL_UL_BSDF_slots(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        BSDF = item
        bsdf_type = BSDF.bsdf_type
        bsdf_type_name = bsdf_type[
            0].upper() + bsdf_type[1:-5] + " " + bsdf_type[-4:].upper()
        if 'DEFAULT' in self.layout_type:
            layout.label(text=BSDF.name + "  |  " + bsdf_type_name,
                         translate=False, icon_value=icon)

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
            layout.prop_search(asr_mat, "node_output", node_tree, "nodes")

        if asr_mat.node_tree == '':

            row = layout.row()
            row.template_list("MATERIAL_UL_BSDF_slots", "appleseed_material_layers", asr_mat,
                              "layers", asr_mat, "layer_index", rows=1, maxrows=16, type="DEFAULT")

            row = layout.row(align=True)
            row.operator("appleseed.add_matlayer",
                         text="Add Layer", icon="ZOOMIN")
            row.operator("appleseed.remove_matlayer",
                         text="Remove", icon="ZOOMOUT")

            if asr_mat.layers:
                current_layer = asr_mat.layers[asr_mat.layer_index]
                layout.prop(current_layer, "name")
                layout.prop(current_layer, "bsdf_type")
                layout.separator()

                # lambertian brdf layout
                if current_layer.bsdf_type == "lambertian_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "lambertian_weight",
                             text="Layer Weight")
                    if current_layer.lambertian_use_tex:
                        layout.prop_search(
                            current_layer, "lambertian_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "lambertian_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.lambertian_mix_tex != '' and current_layer.lambertian_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.lambertian_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "lambertian_reflectance", text="")

                    if current_layer.lambertian_use_diff_tex:
                        layout.prop_search(
                            current_layer, "lambertian_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "lambertian_use_diff_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.lambertian_diffuse_tex != '' and current_layer.lambertian_use_diff_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.lambertian_diffuse_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")
                    layout.prop(current_layer, "lambertian_multiplier")

                #-------------------------------------------------

                # sheen brdf layout
                if current_layer.bsdf_type == "sheen_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "sheen_weight",
                             text="Layer Weight")
                    if current_layer.sheen_use_tex:
                        layout.prop_search(
                            current_layer, "sheen_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "sheen_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.sheen_mix_tex != '' and current_layer.sheen_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.sheen_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "sheen_reflectance", text="")

                    if current_layer.sheen_reflectance_use_tex:
                        layout.prop_search(
                            current_layer, "sheen_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "sheen_reflectance_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.sheen_reflectance_tex != '' and current_layer.sheen_reflectance_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.sheen_reflectance_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "sheen_reflectance_multiplier")

                    if current_layer.sheen_reflectance_multiplier_use_tex:
                        layout.prop_search(
                            current_layer, "sheen_reflectance_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "sheen_reflectance_multiplier_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.sheen_reflectance_multiplier_tex != '' and current_layer.sheen_reflectance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.sheen_reflectance_multiplier_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                #-------------------------------------------------

                # glossy brdf layout
                if current_layer.bsdf_type == "glossy_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glossy_weight",
                             text="Layer Weight")
                    if current_layer.glossy_use_tex:
                        layout.prop_search(
                            current_layer, "glossy_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glossy_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_mix_tex != '' and current_layer.glossy_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.glossy_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # mdf
                    col = layout.column()
                    col.prop(current_layer, "glossy_mdf")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "glossy_reflectance", text="")

                    if current_layer.glossy_reflectance_use_tex:
                        layout.prop_search(
                            current_layer, "glossy_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "glossy_reflectance_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_reflectance_tex != '' and current_layer.glossy_reflectance_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.glossy_reflectance_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glossy_reflectance_multiplier")

                    if current_layer.glossy_reflectance_multiplier_use_tex:
                        layout.prop_search(
                            current_layer, "glossy_reflectance_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glossy_reflectance_multiplier_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_reflectance_multiplier_tex != '' and current_layer.glossy_reflectance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.glossy_reflectance_multiplier_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glossy_roughness")

                    if current_layer.glossy_roughness_use_tex:
                        layout.prop_search(
                            current_layer, "glossy_roughness_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glossy_roughness_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_roughness_tex != '' and current_layer.glossy_roughness_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.glossy_roughness_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # highlight falloff
                    col = layout.column()
                    col.prop(current_layer, "glossy_highlight_falloff")

                    # anisotropy
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glossy_anisotropy")

                    if current_layer.glossy_anisotropy_use_tex:
                        layout.prop_search(
                            current_layer, "glossy_anisotropy_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glossy_anisotropy_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glossy_anisotropy_tex != '' and current_layer.glossy_anisotropy_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.glossy_anisotropy_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # ior
                    col = layout.column()
                    col.prop(current_layer, "glossy_ior")

                #--------------------------------------------------

                # glass bsdf layout
                if current_layer.bsdf_type == "glass_bsdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glass_weight",
                             text="Layer Weight")
                    if current_layer.glass_use_tex:
                        layout.prop_search(
                            current_layer, "glass_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glass_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_mix_tex != '' and current_layer.glass_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.glass_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # mdf
                    col = layout.column()
                    col.prop(current_layer, "glass_mdf")

                    # surface transmittance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Surface Transmittance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer,
                             "glass_surface_transmittance", text="")

                    if current_layer.glass_surface_transmittance_use_tex:
                        layout.prop_search(
                            current_layer, "glass_surface_transmittance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "glass_surface_transmittance_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_surface_transmittance_tex != '' and current_layer.glass_surface_transmittance_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.glass_surface_transmittance_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # surface transmittance multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer,
                             "glass_surface_transmittance_multiplier")

                    if current_layer.glass_surface_transmittance_multiplier_use_tex:
                        layout.prop_search(
                            current_layer, "glass_surface_transmittance_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glass_surface_transmittance_multiplier_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_surface_transmittance_multiplier_tex != '' and current_layer.glass_surface_transmittance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.glass_surface_transmittance_multiplier_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflection tint
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflection Tint:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "glass_reflection_tint", text="")

                    if current_layer.glass_reflection_tint_use_tex:
                        layout.prop_search(
                            current_layer, "glass_reflection_tint_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "glass_reflection_tint_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_reflection_tint_tex != '' and current_layer.glass_reflection_tint_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.glass_reflection_tint_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # refraction tint
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Refraction Tint:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "glass_refraction_tint", text="")

                    if current_layer.glass_refraction_tint_use_tex:
                        layout.prop_search(
                            current_layer, "glass_refraction_tint_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "glass_refraction_tint_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_refraction_tint_tex != '' and current_layer.glass_refraction_tint_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.glass_refraction_tint_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # ior
                    col = layout.column()
                    col.prop(current_layer, "glass_ior")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glass_roughness")

                    if current_layer.glass_roughness_use_tex:
                        layout.prop_search(
                            current_layer, "glass_roughness_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glass_roughness_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_roughness_tex != '' and current_layer.glass_roughness_use_tex:
                        glass_roughness = bpy.data.textures[
                            current_layer.glass_roughness_tint_tex]
                        layout.prop(
                            glass_roughness.image.colorspace_settings, "name", text="Color Space")

                    # highlight falloff
                    col = layout.column()
                    col.prop(current_layer, "glass_highlight_falloff")

                    # anisotropy
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "glass_anisotropy")

                    if current_layer.glass_anisotropy_use_tex:
                        layout.prop_search(
                            current_layer, "glass_anisotropy_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "glass_anisotropy_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.glass_anisotropy_tex != '' and current_layer.glass_anisotropy_use_tex:
                        glass_anisotropy = bpy.data.textures[
                            current_layer.glass_anisotropy_tex]
                        layout.prop(
                            glass_anisotropy.image.colorspace_settings, "name", text="Color Space")

                    # volume parameterization
                    col = layout.column()
                    col.prop(current_layer, "glass_volume_parameterization")

                    if current_layer.glass_volume_parameterization == 'transmittance':
                        # normal reflectance
                        split = layout.split(percentage=0.40)
                        col = split.column()
                        col.label("Volume Transmittance:")
                        split = split.split(percentage=0.83)
                        col = split.column()
                        col.prop(current_layer,
                                 "glass_volume_transmittance", text="")

                        if current_layer.glass_volume_transmittance_use_tex:
                            layout.prop_search(
                                current_layer, "glass_volume_transmittance_tex", material, "texture_slots")

                        split = split.split(percentage=1.0)
                        col = split.column()
                        col.prop(current_layer, "glass_volume_transmittance_use_tex",
                                 text="", icon="TEXTURE_SHADED", toggle=True)
                        if current_layer.glass_volume_transmittance_tex != '' and current_layer.glass_volume_transmittance_use_tex:
                            specular_tex = bpy.data.textures[
                                current_layer.glass_volume_transmittance_tex]
                            layout.prop(
                                specular_tex.image.colorspace_settings, "name", text="Color Space")

                        # glass volume transmittance distance
                        split = layout.split(percentage=0.90)
                        col = split.column()
                        col.prop(current_layer,
                                 "glass_volume_transmittance_distance")

                        if current_layer.glass_volume_transmittance_distance_use_tex:
                            layout.prop_search(
                                current_layer, "glass_volume_transmittance_distance_tex", material, "texture_slots")

                        col = split.column()
                        col.prop(current_layer, "glass_volume_transmittance_distance_use_tex",
                                 text="", icon="TEXTURE_SHADED", toggle=True)
                        if current_layer.glass_volume_transmittance_distance_tex != '' and current_layer.glass_volume_transmittance_distance_use_tex:
                            glass_volume_transmittance_distance = bpy.data.textures[
                                current_layer.glass_volume_transmittance_distance_tex]
                            layout.prop(
                                glass_volume_transmittance_distance.image.colorspace_settings, "name", text="Color Space")

                    else:
                        # glass volume density
                        split = layout.split(percentage=0.90)
                        col = split.column()
                        col.prop(current_layer, "glass_volume_density")

                        if current_layer.glass_volume_density_use_tex:
                            layout.prop_search(
                                current_layer, "glass_volume_density_tex", material, "texture_slots")

                        col = split.column()
                        col.prop(current_layer, "glass_volume_density_use_tex",
                                 text="", icon="TEXTURE_SHADED", toggle=True)
                        if current_layer.glass_volume_density_tex != '' and current_layer.glass_volume_density_use_tex:
                            glass_volume_density = bpy.data.textures[
                                current_layer.glass_volume_density_tex]
                            layout.prop(
                                glass_volume_density.image.colorspace_settings, "name", text="Color Space")

                        # glass absorption
                        split = layout.split(percentage=0.40)
                        col = split.column()
                        col.label("Volume Absorption:")
                        split = split.split(percentage=0.83)
                        col = split.column()
                        col.prop(current_layer,
                                 "glass_volume_absorption", text="")

                        if current_layer.glass_volume_absorption_use_tex:
                            layout.prop_search(
                                current_layer, "glass_volume_absorption_tex", material, "texture_slots")

                        split = split.split(percentage=1.0)
                        col = split.column()
                        col.prop(current_layer, "glass_volume_absorption_use_tex",
                                 text="", icon="TEXTURE_SHADED", toggle=True)
                        if current_layer.glass_volume_absorption_tex != '' and current_layer.glass_volume_absorption_use_tex:
                            specular_tex = bpy.data.textures[
                                current_layer.glass_volume_absorption_tex]
                            layout.prop(
                                specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # scale
                    col = layout.column()
                    col.prop(current_layer, "glass_volume_scale")

                #------------------------------------------------

                # metal bsdf layout
                if current_layer.bsdf_type == "metal_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "metal_weight",
                             text="Layer Weight")
                    if current_layer.metal_use_tex:
                        layout.prop_search(
                            current_layer, "metal_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "metal_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_mix_tex != '' and current_layer.metal_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.metal_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # mdf
                    col = layout.column()
                    col.prop(current_layer, "metal_mdf")

                    # normal reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Normal Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "metal_normal_reflectance", text="")

                    if current_layer.metal_normal_reflectance_use_tex:
                        layout.prop_search(
                            current_layer, "metal_normal_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "metal_normal_reflectance_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_normal_reflectance_tex != '' and current_layer.metal_normal_reflectance_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.metal_normal_reflectance_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # edge tint
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Edge Tint:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "metal_edge_tint", text="")

                    if current_layer.metal_edge_tint_use_tex:
                        layout.prop_search(
                            current_layer, "metal_edge_tint_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "metal_edge_tint_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_edge_tint_tex != '' and current_layer.metal_edge_tint_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.metal_edge_tint_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # reflectance multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "metal_reflectance_multiplier")

                    if current_layer.metal_reflectance_multiplier_use_tex:
                        layout.prop_search(
                            current_layer, "metal_reflectance_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "metal_reflectance_multiplier_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_reflectance_multiplier_tex != '' and current_layer.metal_reflectance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.metal_reflectance_multiplier_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "metal_roughness")

                    if current_layer.metal_roughness_use_tex:
                        layout.prop_search(
                            current_layer, "metal_roughness_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "metal_roughness_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_roughness_tex != '' and current_layer.metal_roughness_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.metal_roughness_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    col = layout.column()
                    col.prop(current_layer, "highlight_falloff")

                    # anisotropy
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "metal_anisotropy")

                    if current_layer.metal_anisotropy_use_tex:
                        layout.prop_search(
                            current_layer, "metal_anisotropy_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "metal_anisotropy_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.metal_anisotropy_tex != '' and current_layer.metal_anisotropy_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.metal_anisotropy_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                #-------------------------------------------------

                # plastic brdf layout
                if current_layer.bsdf_type == "plastic_brdf":
                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "plastic_weight",
                             text="Layer Weight")
                    if current_layer.plastic_use_tex:
                        layout.prop_search(
                            current_layer, "plastic_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "plastic_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_mix_tex != '' and current_layer.plastic_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.plastic_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # mdf
                    col = layout.column()
                    col.prop(current_layer, "plastic_mdf")

                    # specular reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer,
                             "plastic_specular_reflectance", text="")

                    if current_layer.plastic_specular_reflectance_use_tex:
                        layout.prop_search(
                            current_layer, "plastic_specular_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "plastic_specular_reflectance_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_specular_reflectance_tex != '' and current_layer.plastic_specular_reflectance_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.plastic_specular_reflectance_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # specular reflectance multiplier
                    split = layout.split(percentage=0.9)
                    col = split.column()
                    col.prop(current_layer,
                             "plastic_specular_reflectance_multiplier")

                    if current_layer.plastic_specular_reflectance_multiplier_use_tex:
                        layout.prop_search(
                            current_layer, "plastic_specular_reflectance_multiplier_tex", material, "texture_slots")

                    split = split.split()
                    col = split.column()
                    col.prop(current_layer, "plastic_specular_reflectance_multiplier_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_specular_reflectance_multiplier_tex != '' and current_layer.plastic_specular_reflectance_multiplier_use_tex:
                        specular_tex = bpy.data.textures[
                            current_layer.plastic_specular_reflectance_multiplier_tex]
                        layout.prop(
                            specular_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.9)
                    col = split.column()
                    col.prop(current_layer, "plastic_roughness")

                    if current_layer.plastic_roughness_use_tex:
                        layout.prop_search(
                            current_layer, "plastic_roughness_tex", material, "texture_slots")

                    split = split.split()
                    col = split.column()
                    col.prop(current_layer, "plastic_roughness_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_roughness_tex != '' and current_layer.plastic_roughness_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.plastic_roughness_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    col = layout.column()
                    col.prop(current_layer, "plastic_highlight_falloff")
                    col.prop(current_layer, "plastic_ior")

                    # diffuse reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Diffuse Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer,
                             "plastic_diffuse_reflectance", text="")

                    if current_layer.plastic_diffuse_reflectance_use_tex:
                        layout.prop_search(
                            current_layer, "plastic_diffuse_reflectance_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "plastic_diffuse_reflectance_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_diffuse_reflectance_tex != '' and current_layer.plastic_diffuse_reflectance_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.plastic_diffuse_reflectance_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # diffuse reflectance multiplier
                    split = layout.split(percentage=0.9)
                    col = split.column()
                    col.prop(current_layer,
                             "plastic_diffuse_reflectance_multiplier")

                    if current_layer.plastic_diffuse_reflectance_multiplier_use_tex:
                        layout.prop_search(
                            current_layer, "plastic_diffuse_reflectance_multiplier_tex", material, "texture_slots")

                    split = split.split()
                    col = split.column()
                    col.prop(current_layer, "plastic_diffuse_reflectance_multiplier_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.plastic_diffuse_reflectance_multiplier_tex != '' and current_layer.plastic_diffuse_reflectance_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.plastic_diffuse_reflectance_multiplier_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    col = layout.column()
                    col.prop(current_layer, "plastic_internal_scattering")

                #-------------------------------------------------

                # blinn brdf layout
                if current_layer.bsdf_type == "blinn_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "blinn_weight",
                             text="Layer Weight")
                    if current_layer.blinn_use_tex:
                        layout.prop_search(
                            current_layer, "blinn_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "blinn_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.blinn_mix_tex != '' and current_layer.blinn_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.blinn_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # exponent
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "blinn_exponent")

                    if current_layer.blinn_exponent_use_tex:
                        layout.prop_search(
                            current_layer, "blinn_exponent_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "blinn_exponent_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.blinn_exponent_tex != '' and current_layer.blinn_exponent_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.blinn_exponent_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # ior
                    col = layout.column()
                    col.prop(current_layer, "blinn_ior")

                #-------------------------------------------------

                # oren-nayar brdf layout
                if current_layer.bsdf_type == "orennayar_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "orennayar_weight",
                             text="Layer Weight")
                    if current_layer.orennayar_use_tex:
                        layout.prop_search(
                            current_layer, "orennayar_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "orennayar_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.orennayar_mix_tex != '' and current_layer.orennayar_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.orennayar_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "orennayar_reflectance", text="")

                    if current_layer.orennayar_use_diff_tex:
                        layout.prop_search(
                            current_layer, "orennayar_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "orennayar_use_diff_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.orennayar_diffuse_tex != '' and current_layer.orennayar_use_diff_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.orennayar_diffuse_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "orennayar_roughness")
                    if current_layer.orennayar_use_rough_tex:
                        layout.prop_search(
                            current_layer, "orennayar_rough_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "orennayar_use_rough_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.orennayar_rough_tex != '' and current_layer.orennayar_use_rough_tex:
                        rough_tex = bpy.data.textures[
                            current_layer.orennayar_diffuse_tex]
                        layout.prop(rough_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                #-------------------------------------------------

                # ashikhmin-shirley brdf layout
                elif current_layer.bsdf_type == "ashikhmin_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_weight",
                             text="Layer Weight")
                    if current_layer.ashikhmin_use_tex:
                        layout.prop_search(
                            current_layer, "ashikhmin_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "ashikhmin_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.ashikhmin_mix_tex != '' and current_layer.ashikhmin_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.ashikhmin_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Diffuse Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_reflectance", text="")

                    if current_layer.ashikhmin_use_diff_tex:
                        layout.prop_search(
                            current_layer, "ashikhmin_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_use_diff_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.ashikhmin_diffuse_tex != '' and current_layer.ashikhmin_use_diff_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.ashikhmin_diffuse_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    row = layout.row()
                    row.prop(current_layer, "ashikhmin_multiplier")

                    # glossiness
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Glossy Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_glossy", text="")

                    if current_layer.ashikhmin_use_gloss_tex:
                        layout.prop_search(
                            current_layer, "ashikhmin_gloss_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "ashikhmin_use_diff_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.ashikhmin_gloss_tex != '' and current_layer.ashikhmin_use_gloss_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.ashikhmin_gloss_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    row = layout.row()
                    row.prop(current_layer, "ashikhmin_glossy_multiplier")

                    # fresnel
                    col = layout.column()
                    col.prop(current_layer, "ashikhmin_fresnel")
                    layout.prop(current_layer, "ashikhmin_shininess_u")
                    layout.prop(current_layer, "ashikhmin_shininess_v")

                #-------------------------------------------------

                # diffuse btdf layout
                elif current_layer.bsdf_type == "diffuse_btdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "transmittance_weight",
                             text="Layer Weight")
                    if current_layer.transmittance_use_tex:
                        layout.prop_search(
                            current_layer, "transmittance_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "transmittance_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.transmittance_mix_tex != '' and current_layer.transmittance_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.transmittance_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Transmittance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "transmittance_color", text="")

                    if current_layer.transmittance_use_diff_tex:
                        layout.prop_search(
                            current_layer, "transmittance_diffuse_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "transmittance_use_diff_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.transmittance_diffuse_tex != '' and current_layer.transmittance_use_diff_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.transmittance_diffuse_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # transmittance
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "transmittance_multiplier",
                             text="Transmittance")
                    if current_layer.transmittance_use_mult_tex:
                        layout.prop_search(
                            current_layer, "transmittance_mult_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "transmittance_use_mult_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.transmittance_mult_tex != '' and current_layer.transmittance_use_mult_tex:
                        mult_tex = bpy.data.textures[
                            current_layer.transmittance_mult_tex]
                        layout.prop(mult_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                #-------------------------------------------------

                # disney brdf layout
                elif current_layer.bsdf_type == "disney_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_weight",
                             text="Layer Weight")
                    if current_layer.disney_use_tex:
                        layout.prop_search(
                            current_layer, "disney_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "disney_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_mix_tex != '' and current_layer.disney_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.disney_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # base color
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Base Color:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "disney_base", text="")

                    if current_layer.disney_use_base_tex:
                        layout.prop_search(
                            current_layer, "disney_base_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "disney_use_base_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_base_tex != '' and current_layer.disney_use_base_tex:
                        diff_tex = bpy.data.textures[
                            current_layer.disney_base_tex]
                        layout.prop(diff_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # subsurface
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_subsurface")
                    if current_layer.disney_use_subsurface_tex:
                        layout.prop_search(
                            current_layer, "disney_subsurface_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_subsurface_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_subsurface_tex != '' and current_layer.disney_use_subsurface_tex:
                        subsurface_tex = bpy.data.textures[
                            current_layer.disney_subsurface_tex]
                        layout.prop(
                            subsurface_tex.image.colorspace_settings, "name", text="Color Space")

                    # metallic
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_metallic")
                    if current_layer.disney_use_metallic_tex:
                        layout.prop_search(
                            current_layer, "disney_metallic_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_metallic_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_metallic_tex != '' and current_layer.disney_use_metallic_tex:
                        metal_tex = bpy.data.textures[
                            current_layer.disney_metallic_tex]
                        layout.prop(metal_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # specular
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_spec")
                    if current_layer.disney_use_spec_tex:
                        layout.prop_search(
                            current_layer, "disney_spec_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_spec_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_spec_tex != '' and current_layer.disney_use_spec_tex:
                        spec_tex = bpy.data.textures[
                            current_layer.disney_spec_tex]
                        layout.prop(spec_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # specular tint
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_spec_tint")
                    if current_layer.disney_use_spec_tint_tex:
                        layout.prop_search(
                            current_layer, "disney_spec_tint_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_spec_tint_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_spec_tint_tex != '' and current_layer.disney_use_spec_tint_tex:
                        spec_tint_tex = bpy.data.textures[
                            current_layer.disney_spec_tint_tex]
                        layout.prop(
                            spec_tint_tex.image.colorspace_settings, "name", text="Color Space")

                    # anisotropy
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_aniso")
                    if current_layer.disney_use_aniso_tex:
                        layout.prop_search(
                            current_layer, "disney_aniso_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_aniso_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_aniso_tex != '' and current_layer.disney_use_aniso_tex:
                        aniso_tex = bpy.data.textures[
                            current_layer.disney_aniso_tex]
                        layout.prop(aniso_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # roughness
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_roughness")
                    if current_layer.disney_use_roughness_tex:
                        layout.prop_search(
                            current_layer, "disney_roughness_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_roughness_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_roughness_tex != '' and current_layer.disney_use_roughness_tex:
                        rough_tex = bpy.data.textures[
                            current_layer.disney_roughness_tex]
                        layout.prop(rough_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # sheen
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_sheen")
                    if current_layer.disney_use_sheen_tex:
                        layout.prop_search(
                            current_layer, "disney_sheen_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_sheen_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_sheen_tex != '' and current_layer.disney_use_sheen_tex:
                        sheen_tex = bpy.data.textures[
                            current_layer.disney_sheen_tex]
                        layout.prop(sheen_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # sheen tint
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_sheen_tint")
                    if current_layer.disney_use_sheen_tint_tex:
                        layout.prop_search(
                            current_layer, "disney_sheen_tint_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_sheen_tint_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_sheen_tint_tex != '' and current_layer.disney_use_sheen_tint_tex:
                        sheen_tint_tex = bpy.data.textures[
                            current_layer.disney_sheen_tint_tex]
                        layout.prop(
                            sheen_tint_tex.image.colorspace_settings, "name", text="Color Space")

                    # clear coat
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_clearcoat")
                    if current_layer.disney_use_clearcoat_tex:
                        layout.prop_search(
                            current_layer, "disney_clearcoat_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_clearcoat_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_clearcoat_tex != '' and current_layer.disney_use_clearcoat_tex:
                        clearcoat_tex = bpy.data.textures[
                            current_layer.disney_clearcoat_tex]
                        layout.prop(
                            clearcoat_tex.image.colorspace_settings, "name", text="Color Space")

                    # clear coat gloss
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "disney_clearcoat_gloss")
                    if current_layer.disney_use_clearcoat_gloss_tex:
                        layout.prop_search(
                            current_layer, "disney_clearcoat_gloss_tex", material, "texture_slots", text="")

                    col = split.column()
                    col.prop(current_layer, "disney_use_clearcoat_gloss_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.disney_clearcoat_gloss_tex != '' and current_layer.disney_use_clearcoat_gloss_tex:
                        clearcoat_gloss_tex = bpy.data.textures[
                            current_layer.disney_clearcoat_gloss_tex]
                        layout.prop(
                            clearcoat_gloss_tex.image.colorspace_settings, "name", text="Color Space")

                #-------------------------------------------------

                # kelemen brdf layout
                elif current_layer.bsdf_type == "kelemen_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "kelemen_weight",
                             text="Layer Weight")
                    if current_layer.kelemen_use_tex:
                        layout.prop_search(
                            current_layer, "kelemen_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "kelemen_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.kelemen_mix_tex != '' and current_layer.kelemen_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.kelemen_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Matte Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer,
                             "kelemen_matte_reflectance", text="")

                    if current_layer.kelemen_use_diff_tex:
                        layout.prop_search(
                            current_layer, "kelemen_diff_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "kelemen_use_diff_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.kelemen_diff_tex != '' and current_layer.kelemen_use_diff_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.kelemen_diff_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")
                    row = layout.row()
                    row.prop(current_layer, "kelemen_matte_multiplier")

                    # spec reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer,
                             "kelemen_specular_reflectance", text="")

                    if current_layer.kelemen_use_spec_tex:
                        layout.prop_search(
                            current_layer, "kelemen_spec_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "kelemen_use_spec_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.kelemen_spec_tex != '' and current_layer.kelemen_use_spec_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.kelemen_spec_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    layout.prop(current_layer, "kelemen_specular_multiplier")
                    layout.prop(current_layer, "kelemen_roughness")

                #-------------------------------------------------

                # specular brdf layout
                elif current_layer.bsdf_type == "specular_brdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "specular_weight",
                             text="Layer Weight")
                    if current_layer.specular_use_tex:
                        layout.prop_search(
                            current_layer, "specular_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "specular_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.specular_mix_tex != '' and current_layer.specular_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.specular_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # glossiness
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "specular_reflectance", text="")

                    if current_layer.specular_use_gloss_tex:
                        layout.prop_search(
                            current_layer, "specular_gloss_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "specular_use_gloss_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.specular_gloss_tex != '' and current_layer.specular_use_gloss_tex:
                        spec_tex = bpy.data.textures[
                            current_layer.specular_gloss_tex]
                        layout.prop(spec_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    layout.prop(current_layer, "specular_multiplier")

                #----------------------------------------------

                # specular btdf layout
                elif current_layer.bsdf_type == "specular_btdf":

                    # layer weight
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "spec_btdf_weight",
                             text="Layer Weight")
                    if current_layer.spec_btdf_use_tex:
                        layout.prop_search(
                            current_layer, "spec_btdf_mix_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "spec_btdf_use_tex",
                             icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.spec_btdf_mix_tex != '' and current_layer.spec_btdf_use_tex:
                        mix_tex = bpy.data.textures[
                            current_layer.spec_btdf_mix_tex]
                        layout.prop(mix_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    # specular reflectance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Reflectance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "spec_btdf_reflectance", text="")

                    if current_layer.spec_btdf_use_spec_tex:
                        layout.prop_search(
                            current_layer, "spec_btdf_spec_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "spec_btdf_use_spec_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.spec_btdf_spec_tex != '' and current_layer.spec_btdf_use_spec_tex:
                        spec_tex = bpy.data.textures[
                            current_layer.spec_btdf_spec_tex]
                        layout.prop(spec_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    layout.prop(current_layer, "spec_btdf_refl_mult")

                    # transmittance
                    split = layout.split(percentage=0.40)
                    col = split.column()
                    col.label("Specular Transmittance:")
                    split = split.split(percentage=0.83)
                    col = split.column()
                    col.prop(current_layer, "spec_btdf_transmittance", text="")

                    if current_layer.spec_btdf_use_trans_tex:
                        layout.prop_search(
                            current_layer, "spec_btdf_trans_tex", material, "texture_slots")

                    split = split.split(percentage=1.0)
                    col = split.column()
                    col.prop(current_layer, "spec_btdf_use_trans_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.spec_btdf_trans_tex != '' and current_layer.spec_btdf_use_trans_tex:
                        trans_tex = bpy.data.textures[
                            current_layer.spec_btdf_trans_tex]
                        layout.prop(trans_tex.image.colorspace_settings,
                                    "name", text="Color Space")

                    layout.prop(current_layer, "spec_btdf_trans_mult")

                    # Fresnel multiplier
                    split = layout.split(percentage=0.90)
                    col = split.column()
                    col.prop(current_layer, "spec_fresnel_multiplier")

                    if current_layer.spec_fresnel_multiplier_use_tex:
                        layout.prop_search(
                            current_layer, "spec_fresnel_multiplier_tex", material, "texture_slots")

                    col = split.column()
                    col.prop(current_layer, "spec_fresnel_multiplier_use_tex",
                             text="", icon="TEXTURE_SHADED", toggle=True)
                    if current_layer.spec_fresnel_multiplier_tex != '' and current_layer.spec_fresnel_multiplier_use_tex:
                        diffuse_tex = bpy.data.textures[
                            current_layer.spec_fresnel_multiplier_tex]
                        layout.prop(
                            diffuse_tex.image.colorspace_settings, "name", text="Color Space")

                    # IOR
                    layout.prop(current_layer, "spec_btdf_ior")

                    # volume
                    layout.prop(current_layer, "spec_volume_density")

                    # volume density
                    layout.prop(current_layer, "spec_volume_scale")

            #----------------------------------------------

            # alpha

            layout.separator()

            layout.prop(asr_mat, "material_alpha")

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
            col.prop(asr_mat, "material_use_bump_tex",
                     text="Bump Map", icon="POTATO", toggle=True)
            col = split.column()
            if asr_mat.material_use_bump_tex:
                col.prop(asr_mat, "material_use_normalmap",
                         text="Normal Map", toggle=True)
                layout.prop_search(asr_mat, "material_bump_tex",
                                   material, "texture_slots", text="")

                if asr_mat.material_bump_tex != '':
                    bump_tex = bpy.data.textures[asr_mat.material_bump_tex]
                    layout.prop(bump_tex.image.colorspace_settings,
                                "name",  text="Color Space")
                layout.prop(asr_mat, "material_bump_amplitude",
                            text="Bump Amplitude")


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
        header.prop(asr_mat, "use_light_emission")

    def draw(self, context):
        layout = self.layout
        material = context.object.active_material
        asr_mat = material.appleseed

        col = layout.column()
        col.active = asr_mat.use_light_emission
        col.prop(asr_mat, "light_color", text="")
        col.prop(asr_mat, "light_emission")

        layout.active = asr_mat.use_light_emission
        row = layout.row(align=True)
        layout.prop(asr_mat, "cast_indirect")
        layout.prop(asr_mat, "importance_multiplier")
        layout.prop(asr_mat, "light_near_start")


def register():
    bpy.types.MATERIAL_PT_context_material.COMPAT_ENGINES.add(
        'APPLESEED_RENDER')
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
