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
    def __init__(self, bl_obj, export_mode, asset_handler, xform_times):
        super().__init__(bl_obj, asset_handler)

        self.__xform_times = xform_times

        self.__export_mode = export_mode

        self.__mesh_name = str()
        self.__mesh_params = str()

        self.__instance_lib = asr.BlTransformLibrary(xform_times)

        self.__as_mesh = None
        self.__as_mesh_inst = None
        self.__as_mesh_inst_params = dict()
        self.__front_materials = dict()
        self.__back_materials = dict()

        self.__geom_dir = self._asset_handler.geometry_dir if export_mode == ProjectExportMode.PROJECT_EXPORT else None

        self.__has_assembly = False
        self.__ass = None

        self.__mesh_filenames = list()

        self.__deforming = bl_obj.appleseed.use_deformation_blur and is_object_deforming(bl_obj)
    
    @property
    def mesh_obj(self):
        return self._bl_obj

    @property
    def instances_size(self):
        return self.__instance_lib.get_size()   

    def add_instance_step(self, instance_id, bl_matrix):
        inst_id = f"{self.obj_name}|{instance_id}"
        self.__instance_lib.add_xform_step(inst_id, self._convert_matrix(bl_matrix))

    def create_entities(self, bl_scene, context=None):
        self.__mesh_name = f"{self.obj_name}_obj"

        self.__mesh_params = self.__get_mesh_params()

        self.__as_mesh = asr.MeshObject(self.__mesh_name, self.__mesh_params)

        self.__as_mesh_inst_params = self.__get_mesh_inst_params()

        self.__front_materials, self.__back_materials = self.__get_material_mappings()

        me = self._bl_obj.to_mesh()

        if self.__deforming:
            self.__as_mesh.set_motion_segment_count(len(self.__xform_times) - 1)

        self.__convert_mesh(me)

        self._bl_obj.to_mesh_clear()

    def flush_entities(self, as_main_assembly, as_project):
        pass

    def set_deform_key(self, time, depsgraph, index):
        me = self._bl_obj.to_mesh()

        self.__set_mesh_key(me, index)

        self._bl_obj.to_mesh_clear()

    def __convert_mesh(self, me):
        main_timer = Timer()
        material_slots = self._bl_obj.material_slots
        active_uv = None

        self.__as_mesh.reserve_material_slots(len(material_slots))

        if len(material_slots) > 1:
            for i, m in enumerate(material_slots):
                self.__as_mesh.push_material_slot("slot-%s" % i)
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

        asr.export_mesh_blender80(
            self.__as_mesh,
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

        logger.debug("\nMesh %s converted in: %s", self.obj_name, main_timer.elapsed())
        logger.debug("  Number of triangles:    %s", len(me.loop_triangles))
        logger.debug("  Normals converted in:   %s", normal_timer.elapsed())
        logger.debug("  Looptris converted in:  %s", looptri_timer.elapsed())
        logger.debug("  C++ conversion in:      %s", convert_timer.elapsed())

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