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

import appleseed as asr
from ..translator import Translator
from ..utilities import ProjectExportMode
from ..utilities.mesh_converter import create_bl_render_mesh
from ...logger import get_logger
from ...utils.util import is_object_deforming


logger = get_logger()


class MeshTranslator(Translator):
    def __init__(self, obj, export_mode, asset_handler):
        super().__init__(obj, asset_handler=asset_handler)
        self.__export_mode = export_mode
        self.__xform_seq = asr.TransformSequence()
        self.__instance_count = 1

        self.__as_mesh = None
        self.__as_mesh_inst = None
        self.__as_mesh_inst_params = {}
        self.__front_materials = {}
        self.__back_materials = {}

        self.__has_assembly = False
        self.__as_ass = None
        self.__as_ass_inst = None

        # Motion blur
        self.__key_index = 0
        self.__deforming = obj.appleseed.use_deformation_blur and is_object_deforming(obj)

    @property
    def bl_obj(self):
        return self._bl_obj

    def create_entities(self, bl_scene):
        mesh_name = f"{self.appleseed_name}_mesh"

        mesh_params = self.__get_mesh_params()

        self.__as_mesh = asr.MeshObject(mesh_name, mesh_params)

        self.__as_mesh_inst_params = self.__get_mesh_inst_params()
        self.__front_materials, self.__back_materials = self.__get_material_mappings()

        self.__xform_seq.set_transform(0.0, self._convert_matrix(self.bl_obj.matrix_world))

        # bl_mesh = create_bl_render_mesh(self.__as_mesh, self._bl_obj, bl_scene, self.export_mode)

    def set_xform_step(self, time):
        self.__xform_seq.set_transform(time, self._convert_matrix(self.bl_obj.matrix_world))

    def flush_entities(self, as_assembly):
        self.__xform_seq.optimize()

        mesh_name = f"{self.appleseed_name}_mesh"
        as_assembly.objects().insert(self.__as_mesh)
        self.__as_mesh = as_assembly.objects().get_by_name(mesh_name)

        # Check if mesh needs separate assembly
        self.__has_assembly = self.__instance_count > 1 or self.__xform_seq.size() > 1 or \
            self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER

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

            self.__as_ass_inst.set_transform_sequence(self._xform_seq)
            as_assembly.assembly_instances().insert(self.__as_ass_inst)
            self.__as_ass_inst = as_assembly.assembly_instances().get_by_name(ass_inst_name)

        else:
            mesh_name = f"{self.appleseed_name}_mesh"
            self.__as_mesh_inst = asr.ObjectInstance(self.appleseed_name,
                                                     self.__as_mesh_inst_params,
                                                     mesh_name,
                                                     self._xform_seq.get_earliest_transform(),
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
                    self.__front_materials[f"slot-{i}"] = mat_key
                else:
                    self.__front_materials[f"slot-{i}"] = "__default_material"
        else:
            if len(material_slots) == 1:
                if material_slots[0].material.appleseed.osl_node_tree is not None:
                    mat_key = material_slots[0].material.name_full + "_mat"
                    self.__front_materials["default"] = mat_key
                else:
                    self.__front_materials["default"] = "__default_material"
            else:
                mesh_name = f"{self.appleseed_name}_mesh"
                logger.debug("Mesh %s has no materials, assigning default material instead", mesh_name)
                self.__front_materials["default"] = "__default_material"

        double_sided_materials = False if self.bl_obj.appleseed.double_sided is False else True

        if double_sided_materials:
            rear_mats = front_mats

        return front_mats, rear_mats

    def __get_mesh_params(self):
        params = {}
        if self.bl_obj.appleseed.object_alpha_texture is not None:
            params['alpha_map'] = self.bl_obj.appleseed.object_alpha_texture.name_full + "_inst"

        return params
