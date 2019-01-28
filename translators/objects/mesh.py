#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 The appleseedhq Organization
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

import os

import bpy
import bmesh

import appleseed as asr
from ..translator import Translator
from ..utilites import ProjectExportMode
from ...logger import get_logger
from ...utils.util import is_object_deforming, Timer


logger = get_logger()


class MeshTranslator(Translator):
    def __init__(self, obj, export_mode, asset_handler, is_inst_source=False):
        super().__init__(obj, asset_handler=asset_handler)
        self.__export_mode = export_mode
        self.__xform_seq = asr.TransformSequence()
        self.__instance_count = 1
        self.__is_inst_source = is_inst_source

        self.__bl_temp_mesh = None
        self.__as_mesh = None
        self.__as_mesh_inst = None
        self.__as_mesh_inst_params = {}
        self.__front_materials = {}
        self.__back_materials = {}

        self.__geom_dir = self.asset_handler.geometry_dir if export_mode == ProjectExportMode.PROJECT_EXPORT else None

        self.__has_assembly = False
        self.__as_ass = None
        self.__as_ass_inst = None

        self.__mesh_filenames = []

        # Motion blur
        self.__key_index = 0
        self.__deforming = obj.appleseed.use_deformation_blur and is_object_deforming(obj)

    @property
    def bl_obj(self):
        return self._bl_obj

    def create_entities(self, bl_scene):
        logger.debug("Creating translator for mesh %s", self.appleseed_name)
        
        mesh_name = f"{self.appleseed_name}_obj"

        mesh_params = self.__get_mesh_params()

        self.__as_mesh = asr.MeshObject(mesh_name, mesh_params)

        self.__as_mesh_inst_params = self.__get_mesh_inst_params()
        self.__front_materials, self.__back_materials = self.__get_material_mappings()

    def set_xform_step(self, time):

        self.__xform_seq.set_transform(time, self._convert_matrix(self.bl_obj.matrix_world))

    def set_deform_key(self, time, depsgraph, key_times):
        if not self.__deforming and self.__key_index > 0:
            logger.debug("Skipping mesh key for non deforming object %s", self.bl_obj.name)
            return

        mesh_name = f"{self.appleseed_name}_obj"

        me = self.__create_bl_render_mesh(depsgraph)

        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            # Write a mesh file for the mesh key.
            logger.debug("Writing mesh file object %s, time = %s", self.bl_obj.name, time)

            self.__convert_mesh(me)
            self.__write_mesh(mesh_name)

        else:
            if self.__key_index == 0:
                # First key, convert the mesh and reserve keys.
                logger.debug("Converting mesh object %s", self.bl_obj.name)
                self.__convert_mesh(me)

                if self.__deforming:
                    self.__as_mesh.set_motion_segment_count(len(key_times) - 1)
            else:
                # Set vertex and normal poses.
                logger.debug("Setting mesh key for object %s, time = %s", self.bl_obj.name, time)
                self.__set_mesh_key(me, self.__key_index)

        bpy.data.meshes.remove(me)
        self.__key_index += 1

    def flush_entities(self, as_assembly, as_project):
        self.__xform_seq.optimize()

        mesh_name = f"{self.appleseed_name}_obj"

        logger.debug("Flushing mesh %s, number of xform steps: %s", mesh_name, self.__xform_seq.size())

        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            # Replace the MeshObject by an empty one referencing
            # the binarymesh files we saved before.

            params = {}

            if len(self.__mesh_filenames) == 1:
                # No motion blur. Write a single filename.
                params['filename'] = "_geometry/" + self.__mesh_filenames[0]
            else:
                # Motion blur. Write one filename per motion pose.

                params['filename'] = {}

                for i, f in enumerate(self.__mesh_filenames):
                    params['filename'][str(i)] = "_geometry/" + f

            self.__as_mesh = asr.MeshObject(mesh_name, params)

        mesh_name = self.__object_instance_mesh_name(f"{self.appleseed_name}_obj")

        as_assembly.objects().insert(self.__as_mesh)
        self.__as_mesh = as_assembly.objects().get_by_name(mesh_name)

        # Check if mesh needs separate assembly
        self.__has_assembly = self.__instance_count > 1 or self.__xform_seq.size() > 1 or \
            self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER or self.__is_inst_source

        if self.__has_assembly:
            self.__as_mesh_inst = asr.ObjectInstance(self.appleseed_name,
                                                     self.__as_mesh_inst_params,
                                                     mesh_name,
                                                     asr.Transformd(asr.Matrix4d().identity()),
                                                     self.__front_materials,
                                                     self.__back_materials)

            ass_name = f"{self.appleseed_name}_ass"
            ass_inst_name = f"{self.appleseed_name}_ass_inst"

            self.__as_ass = asr.Assembly(ass_name)
            self.__as_ass_inst = asr.AssemblyInstance(ass_inst_name,
                                                      {},
                                                      ass_name)

            self.__as_ass.object_instances().insert(self.__as_mesh_inst)
            self.__as_mesh_inst = self.__as_ass.object_instances().get_by_name(self.appleseed_name)

            as_assembly.assemblies().insert(self.__as_ass)
            self.__as_ass = as_assembly.assemblies().get_by_name(ass_name)

            if not self.__is_inst_source:
                self.__as_ass_inst.set_transform_sequence(self.__xform_seq)
                as_assembly.assembly_instances().insert(self.__as_ass_inst)
                self.__as_ass_inst = as_assembly.assembly_instances().get_by_name(ass_inst_name)

        else:
            self.__as_mesh_inst = asr.ObjectInstance(self.appleseed_name,
                                                     self.__as_mesh_inst_params,
                                                     mesh_name,
                                                     self.__xform_seq.get_earliest_transform(),
                                                     self.__front_materials,
                                                     self.__back_materials)

            as_assembly.object_instances().insert(self.__as_mesh_inst)
            self.__as_mesh_inst = as_assembly.object_instances().get_by_name(self.appleseed_name)

    def add_instance(self):
        self.__instance_count += 1

    def __get_mesh_inst_params(self):
        asr_obj_props = self.bl_obj.appleseed
        object_instance_params = {'visibility': {'camera': asr_obj_props.camera_visible,
                                                 'light': asr_obj_props.light_visible,
                                                 'shadow': asr_obj_props.shadow_visible,
                                                 'diffuse': asr_obj_props.diffuse_visible,
                                                 'glossy': asr_obj_props.glossy_visible,
                                                 'specular': asr_obj_props.specular_visible,
                                                 'transparency': asr_obj_props.transparency_visible},
                                  'medium_priority': asr_obj_props.medium_priority,
                                  'photon_target': asr_obj_props.photon_target,
                                  'ray_bias_method': asr_obj_props.object_ray_bias_method,
                                  'ray_bias_distance': asr_obj_props.object_ray_bias_distance}

        if asr_obj_props.object_sss_set != "":
            object_instance_params['sss_set_id'] = asr_obj_props.object_sss_set

        return object_instance_params

    def __get_material_mappings(self):

        material_slots = self.bl_obj.material_slots

        front_mats = {}
        rear_mats = {}

        if len(material_slots) > 1:
            for i, m in enumerate(material_slots):
                if m.material.appleseed.osl_node_tree is not None:
                    mat_key = m.material.name_full + "_mat"
                    front_mats[f"slot-{i}"] = mat_key
                else:
                    front_mats[f"slot-{i}"] = "__default_material"
        else:
            if len(material_slots) == 1:
                if material_slots[0].material.appleseed.osl_node_tree is not None:
                    mat_key = material_slots[0].material.name_full + "_mat"
                    front_mats["default"] = mat_key
                else:
                    front_mats["default"] = "__default_material"
            else:
                mesh_name = f"{self.appleseed_name}_obj"
                logger.debug("Mesh %s has no materials, assigning default material instead", mesh_name)
                front_mats["default"] = "__default_material"

        double_sided_materials = False if self.bl_obj.appleseed.double_sided is False else True

        if double_sided_materials:
            rear_mats = front_mats

        return front_mats, rear_mats

    def __get_mesh_params(self):
        params = {}
        if self.bl_obj.appleseed.object_alpha_texture is not None:
            params['alpha_map'] = self.bl_obj.appleseed.object_alpha_texture.name_full + "_inst"

        return params

    def __create_bl_render_mesh(self, depsgraph):
        me = self._bl_obj.to_mesh(depsgraph,
                                  apply_modifiers=True)

        return me

    def __convert_mesh(self, me):
        main_timer = Timer()
        material_slots = self.bl_obj.material_slots

        self.__as_mesh.reserve_material_slots(len(material_slots))

        if len(material_slots) > 1:
            for i, m in enumerate(material_slots):
                self.__as_mesh.push_material_slot("slot-%s" % i)
        else:
            self.__as_mesh.push_material_slot("default")

        do_normals = self.bl_obj.data.appleseed.export_normals

        normal_timer = Timer()

        if do_normals is True and not self.bl_obj.data.has_custom_normals:
            me.calc_normals()
            me.split_faces()

        normal_timer.stop()

        looptri_timer = Timer()
        me.calc_loop_triangles()
        looptri_timer.stop()

        vert_pointer = me.vertices[0].as_pointer()

        loop_tris_pointer = me.loop_triangles[0].as_pointer()
        loop_tris_length = len(me.loop_triangles)

        loops_pointer = me.loops[0].as_pointer()
        loops_length = len(me.loops)

        polygons_pointer = me.polygons[0].as_pointer()

        do_uvs = False
        uv_layer_pointer = 0

        if self.bl_obj.data.appleseed.export_uvs and len(me.uv_layers) > 0:
            do_uvs = True
            uv_textures = me.uv_layers

            for uv in uv_textures:
                if uv.active_render:
                    active_uv = uv
                    break

            uv_layer_pointer = active_uv.data[0].as_pointer()

        convert_timer = Timer()

        asr.convert_bl_mesh(self.__as_mesh,
                            loop_tris_length,
                            loop_tris_pointer,
                            loops_length,
                            loops_pointer,
                            polygons_pointer,
                            vert_pointer,
                            uv_layer_pointer,
                            do_normals,
                            do_uvs)

        convert_timer.stop()
        main_timer.stop()

        logger.debug("\nMesh %s converted in: %s", self.appleseed_name, main_timer.elapsed())
        logger.debug("  Number of triangles:    %s", len(me.loop_triangles))
        logger.debug("  Normals converted in:   %s", normal_timer.elapsed())
        logger.debug("  Looptris converted in:  %s", looptri_timer.elapsed())
        logger.debug("  C++ conversion in:      %s", convert_timer.elapsed())

    def __set_mesh_key(self, me, key_index):
        pose = key_index - 1

        do_normals = self.bl_obj.data.appleseed.export_normals

        if do_normals is True and not self.bl_obj.data.has_custom_normals:
            me.calc_normals()
            me.split_faces()

        vertex_pointer = me.vertices[0].as_pointer()

        loop_length = len(me.loops)
        loops_pointer = me.loops[0].as_pointer()

        asr.convert_bl_vertex_pose(
            self.__as_mesh,
            pose,
            loops_pointer,
            loop_length,
            vertex_pointer,
            do_normals)

    def __write_mesh(self, mesh_name):
            # Compute tangents if needed.
        if self.bl_obj.data.appleseed.smooth_tangents and self.bl_obj.data.appleseed.export_uvs:
            asr.compute_smooth_vertex_tangents(self.__as_mesh)

        # Compute the mesh signature and the mesh filename.
        hash = asr.MurmurHash()
        asr.compute_signature(hash, self.__as_mesh)

        logger.debug("Mesh info:")
        logger.debug("   get_triangle_count       %s", self.__as_mesh.get_triangle_count())
        logger.debug("   get_material_slot_count  %s", self.__as_mesh.get_material_slot_count())
        logger.debug("   get_vertex_count         %s", self.__as_mesh.get_vertex_count())
        logger.debug("   get_tex_coords_count     %s", self.__as_mesh.get_tex_coords_count())
        logger.debug("   get_vertex_normal_count  %s", self.__as_mesh.get_vertex_normal_count())
        logger.debug("   get_vertex_tangent_count %s", self.__as_mesh.get_vertex_tangent_count())
        logger.debug("   get_motion_segment_count %s", self.__as_mesh.get_motion_segment_count())

        logger.debug("Computed mesh signature for object %s, hash: %s", self.appleseed_name, hash)

        # Save the mesh filename for later use.
        mesh_filename = str(hash) + ".binarymesh"
        self.__mesh_filenames.append(mesh_filename)

        # Write the binarymesh file.
        mesh_abs_path = os.path.join(self.__geom_dir, mesh_filename)

        if not os.path.exists(mesh_abs_path):
            logger.debug("Writing mesh for object %s to %s", mesh_name, mesh_abs_path)
            asr.MeshObjectWriter.write(self.__as_mesh, "mesh", mesh_abs_path)
        else:
            logger.debug("Skipping already saved mesh file for mesh %s", mesh_name)

    def __object_instance_mesh_name(self, mesh_name):
        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            return f"{mesh_name}.mesh"

        return mesh_name
