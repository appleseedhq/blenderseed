#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
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

import os

import appleseed as asr
from ..translator import Translator
from ..utilites import ProjectExportMode
from ...logger import get_logger
from ...utils.util import is_object_deforming, Timer

logger = get_logger()


class MeshTranslator(Translator):
    def __init__(self, bl_obj, export_mode, asset_handler):
        logger.debug(f"appleseed: Creating mesh translator for {bl_obj.name_full}")
        super().__init__(bl_obj, asset_handler)

        self.__export_mode = export_mode

        self.__mesh_params = str()

        self.__instance_lib = asr.BlTransformLibrary()

        self.__as_mesh = None
        self.__as_mesh_inst = None
        self.__as_mesh_inst_params = dict()
        self.__front_materials = dict()
        self.__back_materials = dict()

        self.__obj_inst_name = None
        self.__ass_name = str()
        self.__ass = None

        self.__geom_dir = self._asset_handler.geometry_dir if export_mode == ProjectExportMode.PROJECT_EXPORT else None

        self.__mesh_filenames = list()

        self.__is_deforming = bl_obj.appleseed.use_deformation_blur and is_object_deforming(bl_obj)

        self._bl_obj.appleseed.obj_name = self._bl_obj.name_full
    
    @property
    def mesh_obj(self):
        return self._bl_obj

    @property
    def orig_name(self):
        return self._bl_obj.appleseed.obj_name

    @property
    def instances_size(self):
        return len(self.__instance_lib)

    def create_entities(self, depsgraph, num_def_times):
        logger.debug(f"appleseed: Creating mesh entity for {self.orig_name}")
        self.__mesh_params = self.__get_mesh_params()

        self.__as_mesh = asr.MeshObject(self.orig_name, self.__mesh_params)

        self.__as_mesh_inst_params = self.__get_mesh_inst_params()

        self.__front_materials, self.__back_materials = self.__get_material_mappings()

        eval_object = self._bl_obj.evaluated_get(depsgraph)

        me = eval_object.to_mesh()

        self.__convert_mesh(me)

        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            logger.debug(f"appleseed: Writing mesh file object {self.orig_name}, time = 0")
            self.__write_mesh(self.orig_name)

        eval_object.to_mesh_clear()

        if self.__is_deforming:
            self.__as_mesh.set_motion_segment_count(num_def_times - 1)

    def add_instance_step(self, time, instance_id, bl_matrix):
        self.__instance_lib.add_xform_step(time, instance_id, self._convert_matrix(bl_matrix))

    def set_deform_key(self, time, depsgraph, index):
        eval_object = self._bl_obj.evaluated_get(depsgraph)

        me = eval_object.to_mesh()

        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            logger.debug(f"appleseed: Writing mesh file object {self.orig_name}, time = {time}")

            self.__convert_mesh(me)
            self.__write_mesh(self.orig_name)
        else:
            self.__set_mesh_key(me, index)

        eval_object.to_mesh_clear()

    def flush_entities(self, as_scene, as_main_assembly, as_project):
        logger.debug("appleseed: Flusing mesh entity for {self.orig_name} into project")

        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            # Replace the MeshObject by an empty one referencing
            # the binarymesh files we saved before.

            params = {}

            if len(self.__mesh_filenames) == 1:
                # No motion blur. Write a single filename.
                params['filename'] = f"_geometry/{self.__mesh_filenames[0]}"
            else:
                # Motion blur. Write one filename per motion pose.

                params['filename'] = dict()

                for i, f in enumerate(self.__mesh_filenames):
                    params['filename'][str(i)] = f"_geometry/{f}"

            self.__as_mesh = asr.MeshObject(self.orig_name, params)

        mesh_name = self.__object_instance_mesh_name(self.orig_name)

        self.__obj_inst_name = f"{self.orig_name}_inst"

        self.__instance_lib.optimize_xforms()
        
        needs_assembly = self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER or self.__instance_lib.needs_assembly()

        if needs_assembly:
            self.__ass_name = f"{self.orig_name}_ass"
            self.__ass = asr.Assembly(self.__ass_name)

            self.__as_mesh_inst = asr.ObjectInstance(self.__obj_inst_name,
                                                     self.__as_mesh_inst_params,
                                                     mesh_name,
                                                     asr.Transformd(asr.Matrix4d().identity()),
                                                     self.__front_materials,
                                                     self.__back_materials)

            self.__ass.objects().insert(self.__as_mesh)
            self.__as_mesh = self.__ass.objects().get_by_name(mesh_name)

            self.__ass.object_instances().insert(self.__as_mesh_inst)
            self.__as_mesh_inst = self.__ass.object_instances().get_by_name(self.__obj_inst_name)

            as_main_assembly.assemblies().insert(self.__ass)
            self.__ass = as_main_assembly.assemblies().get_by_name(self.__ass_name)

            self.flush_instances(as_main_assembly)

        else:
            self.__as_mesh_inst = asr.ObjectInstance(self.__obj_inst_name,
                                                     self.__as_mesh_inst_params,
                                                     mesh_name,
                                                     self.__instance_lib.get_single_transform(),
                                                     self.__front_materials,
                                                     self.__back_materials)

            as_main_assembly.objects().insert(self.__as_mesh)
            self.__as_mesh = as_main_assembly.objects().get_by_name(mesh_name)

            as_main_assembly.object_instances().insert(self.__as_mesh_inst)
            self.__as_mesh_inst = as_main_assembly.object_instances().get_by_name(self.__obj_inst_name)

    def flush_instances(self, as_main_assembly):
        logger.debug(f"appleseed: Flushing instances for mesh entity {self.orig_name} into project.  Number of instances = {self.__instance_lib.size()}")
        self.__instance_lib.flush_instances(as_main_assembly, self.__ass_name)

    def update_obj_instance(self):
        self.__ass.object_instances().remove(self.__as_mesh_inst)

        self.__as_mesh_inst_params = self.__get_mesh_inst_params()

        self.__front_materials, self.__back_materials = self.__get_material_mappings()

        mesh_name = self.__object_instance_mesh_name(self.orig_name)

        self.__as_mesh_inst = asr.ObjectInstance(self.__obj_inst_name,
                                                 self.__as_mesh_inst_params,
                                                 mesh_name,
                                                 asr.Transformd(
                                                     asr.Matrix4d().identity()),
                                                 self.__front_materials,
                                                 self.__back_materials)

        self.__ass.object_instances().insert(self.__as_mesh_inst)
        self.__as_mesh_inst = self.__ass.object_instances().get_by_name(self.__obj_inst_name)

    def clear_instances(self, as_main_assembly):
        self.__instance_lib.clear_instances(as_main_assembly)

    def delete_object(self, as_main_assembly):
        logger.debug(f"appleseed: Deleting mesh entity for {self.orig_name}")
        self.clear_instances(as_main_assembly)

        self.__ass.objects().remove(self.__as_mesh)
        self.__ass.object_instances().remove(self.__as_mesh_inst)

        as_main_assembly.assemblies().remove(self.__ass)

        self.__as_mesh = None
        self.__as_mesh_inst = None
        self.__ass = None

    def __get_mesh_inst_params(self):
        asr_obj_props = self._bl_obj.appleseed
        object_instance_params = {'visibility': {'camera': asr_obj_props.camera_visible,
                                                 'light': asr_obj_props.light_visible,
                                                 'shadow': asr_obj_props.shadow_visible,
                                                 'diffuse': asr_obj_props.diffuse_visible,
                                                 'glossy': asr_obj_props.glossy_visible,
                                                 'specular': asr_obj_props.specular_visible,
                                                 'transparency': asr_obj_props.transparency_visible},
                                  'medium_priority': asr_obj_props.medium_priority,
                                  'shadow_terminator_correction': asr_obj_props.shadow_terminator_correction,
                                  'photon_target': asr_obj_props.photon_target}

        if asr_obj_props.object_sss_set != "":
            object_instance_params['sss_set_id'] = asr_obj_props.object_sss_set

        return object_instance_params

    def __get_material_mappings(self):

        material_slots = self._bl_obj.material_slots

        front_mats = dict()
        rear_mats = dict()

        if len(material_slots) > 1:
            for i, m in enumerate(material_slots):
                if m.material is not None and m.material.use_nodes:
                    mat_key = f"{m.material.original.appleseed.obj_name}"
                else:
                    mat_key = "__default_material"
                front_mats[f"slot-{i}"] = mat_key
        else:
            if len(material_slots) == 1:
                if material_slots[0].material is not None and material_slots[0].material.use_nodes:
                    mat_key = f"{material_slots[0].material.original.appleseed.obj_name}"
                else:
                    mat_key = "__default_material"
                front_mats["default"] = mat_key
            else:
                mesh_name = f"{self.obj_name}_obj"
                logger.debug("appleseed: Mesh %s has no materials, assigning default material instead", mesh_name)
                front_mats["default"] = "__default_material"

        double_sided_materials = False if self._bl_obj.appleseed.double_sided is False else True

        if double_sided_materials:
            rear_mats = front_mats

        return front_mats, rear_mats

    def __get_mesh_params(self):
        params = dict()

        if self._bl_obj.appleseed.object_alpha_texture is not None:
            params['alpha_map'] = f"{self._bl_obj.appleseed.object_alpha_texture.appleseed.obj_name}_inst"

        return params

    def __convert_mesh(self, me):
        main_timer = Timer()
        material_slots = self._bl_obj.material_slots
        active_uv = None

        self.__as_mesh.reserve_material_slots(len(material_slots))

        if len(material_slots) > 1:
            for i, m in enumerate(material_slots):
                self.__as_mesh.push_material_slot(f"slot-{i}")
        else:
            self.__as_mesh.push_material_slot("default")

        do_normals = self._bl_obj.data.appleseed.export_normals

        normal_timer = Timer()

        if do_normals is True and not self._bl_obj.data.has_custom_normals:
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

        if self._bl_obj.data.appleseed.export_uvs and len(me.uv_layers) > 0:
            do_uvs = True
            uv_textures = me.uv_layers

            for uv in uv_textures:
                if uv.active_render:
                    active_uv = uv
                    break

            uv_layer_pointer = active_uv.data[0].as_pointer()

        convert_timer = Timer()

        asr.export_mesh_blender80(self.__as_mesh,
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

        logger.debug("\nappleseed: Mesh %s converted in: %s", self.obj_name, main_timer.elapsed())
        logger.debug("             Number of triangles:    %s", len(me.loop_triangles))
        logger.debug("             Normals converted in:   %s", normal_timer.elapsed())
        logger.debug("             Looptris converted in:  %s", looptri_timer.elapsed())
        logger.debug("             C++ conversion in:      %s", convert_timer.elapsed())

    def __set_mesh_key(self, me, key_index):
        do_normals = self._bl_obj.data.appleseed.export_normals

        if do_normals is True and not self._bl_obj.data.has_custom_normals:
            me.calc_normals()
            me.split_faces()

        vertex_pointer = me.vertices[0].as_pointer()

        loop_length = len(me.loops)
        loops_pointer = me.loops[0].as_pointer()

        asr.export_mesh_blender80_pose(self.__as_mesh,
                                       key_index,
                                       loops_pointer,
                                       loop_length,
                                       vertex_pointer,
                                       do_normals)

    def __write_mesh(self, mesh_name):
        # Compute tangents if needed.
        if self._bl_obj.data.appleseed.smooth_tangents and self._bl_obj.data.appleseed.export_uvs:
            asr.compute_smooth_vertex_tangents(self.__as_mesh)

        # Compute the mesh signature and the mesh filename.
        bl_hash = asr.MurmurHash()
        asr.compute_signature(bl_hash, self.__as_mesh)

        logger.debug("Mesh info:")
        logger.debug("   get_triangle_count       %s", self.__as_mesh.get_triangle_count())
        logger.debug("   get_material_slot_count  %s", self.__as_mesh.get_material_slot_count())
        logger.debug("   get_vertex_count         %s", self.__as_mesh.get_vertex_count())
        logger.debug("   get_tex_coords_count     %s", self.__as_mesh.get_tex_coords_count())
        logger.debug("   get_vertex_normal_count  %s", self.__as_mesh.get_vertex_normal_count())
        logger.debug("   get_vertex_tangent_count %s", self.__as_mesh.get_vertex_tangent_count())
        logger.debug("   get_motion_segment_count %s", self.__as_mesh.get_motion_segment_count())

        logger.debug("appleseed: Computed mesh signature for object %s, hash: %s", self.orig_name, bl_hash)

        # Save the mesh filename for later use.
        mesh_filename = f"{bl_hash}.binarymesh"
        self.__mesh_filenames.append(mesh_filename)

        # Write the binarymesh file.
        mesh_abs_path = os.path.join(self.__geom_dir, mesh_filename)

        if not os.path.exists(mesh_abs_path):
            logger.debug("appleseed: Writing mesh for object %s to %s", mesh_name, mesh_abs_path)
            asr.MeshObjectWriter.write(self.__as_mesh, "mesh", mesh_abs_path)
        else:
            logger.debug("appleseed: Skipping already saved mesh file for mesh %s", mesh_name)

    def __object_instance_mesh_name(self, mesh_name):
        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            return f"{mesh_name}.mesh"

        return mesh_name
