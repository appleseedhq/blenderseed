
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
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

import os

import appleseed as asr
import bmesh
import bpy

from .translator import Translator, ObjectKey, ProjectExportMode
from ..logger import get_logger

logger = get_logger()


class ObjectTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, obj):
        super(ObjectTranslator, self).__init__(obj)

        self._xform_seq = asr.TransformSequence()
        self._num_instances = 1

    #
    # Properties.
    #

    @property
    def bl_obj(self):
        return self._bl_obj

    @property
    def assembly_name(self):
        return self.appleseed_name + "_ass"

    #
    # Instancing.
    #

    def add_instance(self):
        self._num_instances += 1


class MeshTranslator(ObjectTranslator):

    #
    # Constructor.
    #

    def __init__(self, obj, export_mode, geom_directory=None):
        super(MeshTranslator, self).__init__(obj)

        self.__export_mode = export_mode
        self.__geom_dir = geom_directory
        self.__mesh_filenames = []

        # Materials
        self.__front_materials = {}
        self.__back_materials = {}

        self.__object_instance_params = {}

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        logger.debug("Creating mesh entities for object %s", self.bl_obj.name)

        # Copy the transform.
        self._xform_seq.set_transform(0.0, self._convert_matrix(self.bl_obj.matrix_world))

        # Convert the blender mesh.
        mesh_key = ObjectKey(self.bl_obj.data)
        mesh_name = str(mesh_key)

        self.__mesh_object = asr.MeshObject(mesh_name, {})
        me = self.__get_blender_mesh(scene, triangulate=True)

        # Materials & material  slots
        material_slots = self.bl_obj.material_slots
        if len(material_slots) > 1:
            for i, m in enumerate(material_slots):
                self.__mesh_object.push_material_slot("slot-%s" % i)

                if m.material.appleseed.osl_node_tree is not None:
                    mat_key = ObjectKey(m.material)
                    self.__front_materials["slot-%s" % i] = str(mat_key)
                else:
                    self.__front_materials["slot-%s" % i] = "default_material"
        else:
            self.__mesh_object.push_material_slot("default")
            if len(material_slots) == 1:
                if material_slots[0].material.appleseed.osl_node_tree is not None:
                    mat_key = ObjectKey(material_slots[0].material)
                    self.__front_materials["default"] = str(mat_key)
                else:
                    self.__front_materials["default"] = "default_material"
            else:
                logger.debug("Mesh %s has no materials, assigning default material instead", mesh_name)
                self.__front_materials["default"] = "default_material"

        double_sided_materials = False if self.bl_obj.appleseed.double_sided is False else True

        if double_sided_materials:
            self.__back_materials = self.__front_materials

        # Vertices
        self.__mesh_object.reserve_vertices(len(me.vertices))

        for v in me.vertices:
            self.__mesh_object.push_vertex(asr.Vector3f(v.co[0], v.co[1], v.co[2]))

        # Faces.
        self.__mesh_object.reserve_triangles(len(me.polygons))

        for f in me.polygons:
            assert(len(f.vertices) == 3)
            tri = asr.Triangle(
                f.vertices[0],
                f.vertices[1],
                f.vertices[2],
                f.material_index)

            self.__mesh_object.push_triangle(tri)

        loops = me.loops

        # UVs.
        export_uvs = True if self.bl_obj.data.appleseed.export_uvs else False

        if export_uvs and len(me.uv_textures) > 0:
            uv_texture = me.uv_textures.active.data[:]
            uv_layer = me.uv_layers.active.data[:]

            self.__mesh_object.reserve_tex_coords(len(me.polygons) * 3)

            uv_index = 0

            for i, f in enumerate(me.polygons):
                loop = f.loop_indices
                tri = self.__mesh_object.get_triangle(i)

                uv = uv_layer[f.loop_indices[0]].uv
                self.__mesh_object.push_tex_coords(asr.Vector2f(uv[0], uv[1]))
                tri.m_a0 = uv_index
                uv_index += 1

                uv = uv_layer[f.loop_indices[1]].uv
                self.__mesh_object.push_tex_coords(asr.Vector2f(uv[0], uv[1]))
                tri.m_a1 = uv_index
                uv_index += 1

                uv = uv_layer[f.loop_indices[2]].uv
                self.__mesh_object.push_tex_coords(asr.Vector2f(uv[0], uv[1]))
                tri.m_a2 = uv_index
                uv_index += 1

        # Normals.
        export_normals = True if self.bl_obj.data.appleseed.export_normals else False

        if export_normals:
            me.calc_normals_split()

            self.__mesh_object.reserve_tex_coords(len(me.polygons) * 3)

            normal_index = 0

            for i, f in enumerate(me.polygons):
                loop = f.loop_indices
                tri = self.__mesh_object.get_triangle(i)

                n = loops[f.loop_indices[0]].normal
                self.__mesh_object.push_vertex_normal(asr.Vector3f(n[0], n[1], n[2]))
                tri.m_n0 = normal_index
                normal_index += 1

                n = loops[f.loop_indices[1]].normal
                self.__mesh_object.push_vertex_normal(asr.Vector3f(n[0], n[1], n[2]))
                tri.m_n1 = normal_index
                normal_index += 1

                n = loops[f.loop_indices[2]].normal
                self.__mesh_object.push_vertex_normal(asr.Vector3f(n[0], n[1], n[2]))
                tri.m_n2 = normal_index
                normal_index += 1

        # Tangents.
        if self.bl_obj.data.appleseed.smooth_tangents and self.bl_obj.data.appleseed.export_uvs:
            asr.compute_smooth_vertex_tangents(self.__mesh_object)


        bpy.data.meshes.remove(me)

        # Write the appleseed mesh if needed.
        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            self.__write_mesh(mesh_key)

    def flush_entities(self, assembly):
        asr_obj_props = self.bl_obj.appleseed
        mesh_name = self.__mesh_object.get_name()
        self.__object_instance_params = {'visibility': {'camera': asr_obj_props.camera_visible,
                                                        'light': asr_obj_props.light_visible,
                                                        'shadow': asr_obj_props.shadow_visible,
                                                        'diffuse': asr_obj_props.diffuse_visible,
                                                        'glossy': asr_obj_props.glossy_visible,
                                                        'specular': asr_obj_props.specular_visible,
                                                        'transparency': asr_obj_props.transparency_visible},
                                         'medium_priority': asr_obj_props.medium_priority}

        if asr_obj_props.object_sss_set != "":
            self.__object_instance_params['sss_set_id'] = asr_obj_props.object_sss_set

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

            self.__mesh_object = asr.MeshObject(mesh_name, params)

            mesh_name += ".mesh"

        self._xform_seq.optimize()

        logger.debug(
            "Flushing object %s, num instances = %s, num xform keys = %s",
            self.appleseed_name,
            self._num_instances,
            self._xform_seq.size())

        if self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER:
            # We always create assemblies when doing IPR to allow quick scene edits.
            needs_assembly = True
        else:
            needs_assembly = self._num_instances > 1 or self._xform_seq.size() > 1

        if needs_assembly:
            logger.debug("Creating assembly for object %s, name: %s", self.appleseed_name, self.assembly_name)

            ass = asr.Assembly(self.assembly_name)

            obj_inst = asr.ObjectInstance(
                self.appleseed_name,
                self.__object_instance_params,
                mesh_name,
                asr.Transformd(asr.Matrix4d().identity()),
                self.__front_materials,
                self.__back_materials)

            ass.objects().insert(self.__mesh_object)
            ass.object_instances().insert(obj_inst)

            assembly_instance_name = self.assembly_name + "_inst"

            logger.debug("Creating assembly instance for object %s, name: %s", self.appleseed_name, assembly_instance_name)

            ass_inst = asr.AssemblyInstance(
                assembly_instance_name,
                {},
                self.assembly_name)
            ass_inst.transform_sequence = self._xform_seq

            assembly.assemblies().insert(ass)
            assembly.assembly_instances().insert(ass_inst)
        else:
            logger.debug("Creating object instance for object %s, name: %s", self.appleseed_name, self.appleseed_name)

            obj_inst = asr.ObjectInstance(
                self.appleseed_name,
                self.__object_instance_params,
                mesh_name,
                self._xform_seq.get_earliest_transform(),
                self.__front_materials,
                self.__back_materials)

            assembly.objects().insert(self.__mesh_object)
            assembly.object_instances().insert(obj_inst)

    #
    # Internal methods.
    #

    def __get_blender_mesh(self, scene, triangulate=True):
        me = self.bl_obj.to_mesh(
            scene,
            apply_modifiers=True,
            settings='RENDER',
            calc_tessface=False)

        if triangulate:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            bm.to_mesh(me)
            bm.free()

        return me

    def __write_mesh(self, mesh_name):
        # Compute the mesh signature and the mesh filename.
        hash = asr.MurmurHash()
        asr.compute_signature(hash, self.__mesh_object)

        logger.debug("Mesh info:")
        logger.debug("   get_triangle_count       %s", self.__mesh_object.get_triangle_count())
        logger.debug("   get_material_slot_count  %s", self.__mesh_object.get_material_slot_count())
        logger.debug("   get_vertex_count         %s", self.__mesh_object.get_vertex_count())
        logger.debug("   get_tex_coords_count     %s", self.__mesh_object.get_tex_coords_count())
        logger.debug("   get_vertex_normal_count  %s", self.__mesh_object.get_vertex_normal_count())
        logger.debug("   get_vertex_tangent_count %s", self.__mesh_object.get_vertex_tangent_count())
        logger.debug("   get_motion_segment_count %s", self.__mesh_object.get_motion_segment_count())

        logger.debug("Computed mesh signature for object %s, hash: %s", self.appleseed_name, hash)

        # Save the mesh filename for later use.
        mesh_filename = str(hash) + ".binarymesh"
        self.__mesh_filenames.append(mesh_filename)

        # Write the binarymesh file.
        mesh_abs_path = os.path.join(self.__geom_dir, mesh_filename)

        if not os.path.exists(mesh_abs_path):
            logger.debug("Writing mesh for object %s to %s", mesh_name, mesh_abs_path)
            asr.MeshObjectWriter.write(self.__mesh_object, "mesh", mesh_abs_path)
        else:
            logger.debug("Skipping already saved mesh file for mesh %s", mesh_name)


class InstanceTranslator(ObjectTranslator):

    #
    # Constructor.
    #

    def __init__(self, obj, master_translator):
        super(InstanceTranslator, self).__init__(obj)
        self.__master = master_translator

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        self._xform_seq.set_transform(0.0, self._convert_matrix(self.bl_obj.matrix_world))

    def flush_entities(self, assembly):
        logger.debug("Creating assembly instance for object %s", self.appleseed_name)

        self._xform_seq.optimize()

        assembly_instance_name = self.appleseed_name + "_ass_inst"

        ass_inst = asr.AssemblyInstance(
            assembly_instance_name,
            {},
            self.__master.assembly_name)

        ass_inst.set_transform_sequence(self._xform_seq)
        assembly.assembly_instances().insert(ass_inst)
