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

import bmesh
import bpy

import appleseed as asr
from .assethandlers import AssetType
from .object import ObjectTranslator
from .translator import ObjectKey, ProjectExportMode
from ..logger import get_logger
from ..util import is_object_deforming

logger = get_logger()


class MeshTranslator(ObjectTranslator):

    #
    # Constructor.
    #

    def __init__(self, obj, export_mode, asset_handler, use_cpp_export, skip_triangulation):
        super(MeshTranslator, self).__init__(obj, asset_handler)

        self.__export_mode = export_mode
        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            self.__geom_dir = self.asset_handler.geometry_dir

        self.__mesh_filenames = []

        # Motion blur
        self.__key_index = 0
        self.__deforming = obj.appleseed.use_deformation_blur and is_object_deforming(obj)

        # Materials
        self.__front_materials = {}
        self.__back_materials = {}

        self.__alpha_tex = None
        self.__alpha_tex_inst = None

        self.__use_cpp_export = use_cpp_export
        self.__skip_triangulation = skip_triangulation

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        logger.debug("Creating mesh entities for object %s", self.bl_obj.name)

        # Materials
        mesh_key = str(ObjectKey(self.bl_obj.data)) + "_obj"
        mesh_name = mesh_key

        asr_obj_props = self.bl_obj.appleseed

        self.__obj_params = {'alpha_map': asr_obj_props.object_alpha}
        if self.bl_obj.appleseed.object_alpha_texture is not None:
            filename = self.asset_handler.process_path(asr_obj_props.object_alpha_texture.filepath, AssetType.TEXTURE_ASSET)
            tex_inst_params = {'addressing_mode': asr_obj_props.object_alpha_texture_wrap_mode,
                               'filtering_mode': 'bilinear',
                               'alpha_mode': asr_obj_props.object_alpha_mode}
            self.__alpha_tex = asr.Texture('disk_texture_2d', mesh_name + "_tex",
                                           {'filename': filename,
                                            'color_space': asr_obj_props.object_alpha_texture_colorspace}, [])
            self.__alpha_tex_inst = asr.TextureInstance(mesh_name + "_tex_inst", tex_inst_params, mesh_name + "_tex",
                                                        asr.Transformf(asr.Matrix4f.identity()))

            self.__obj_params['alpha_map'] = mesh_name + "_tex_inst"

        material_slots = self.bl_obj.material_slots

        if len(material_slots) > 1:
            for i, m in enumerate(material_slots):
                if m.material.appleseed.osl_node_tree is not None:
                    mat_key = str(ObjectKey(m.material)) + "_mat"
                    self.__front_materials["slot-%s" % i] = mat_key
                else:
                    self.__front_materials["slot-%s" % i] = "__default_material"
        else:
            if len(material_slots) == 1:
                if material_slots[0].material.appleseed.osl_node_tree is not None:
                    mat_key = str(ObjectKey(material_slots[0].material)) + "_mat"
                    self.__front_materials["default"] = mat_key
                else:
                    self.__front_materials["default"] = "__default_material"
            else:
                logger.debug("Mesh %s has no materials, assigning default material instead", mesh_name)
                self.__front_materials["default"] = "__default_material"

        double_sided_materials = False if self.bl_obj.appleseed.double_sided is False else True

        if double_sided_materials:
            self.__back_materials = self.__front_materials

    def set_deform_key(self, scene, time, key_times):
        # Don't save keys for non deforming meshes.
        if not self.__deforming and self.__key_index > 0:
            logger.debug("Skipping mesh key for non deforming object %s", self.bl_obj.name)
            return

        mesh_key = str(ObjectKey(self.bl_obj.data)) + "_obj"
        mesh_name = mesh_key

        me = self.__get_blender_mesh(scene, triangulate=not self.__skip_triangulation)

        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            # Write a mesh file for the mesh key.
            logger.debug("Writing mesh file object %s, time = %s", self.bl_obj.name, time)
            self.__mesh_object = asr.MeshObject(mesh_name, self.__obj_params)
            self.__convert_mesh(me)
            self.__write_mesh(mesh_key)
        else:
            if self.__key_index == 0:
                # First key, convert the mesh and reserve keys.
                logger.debug("Converting mesh object %s", self.bl_obj.name)
                self.__mesh_object = asr.MeshObject(mesh_name, self.__obj_params)
                self.__convert_mesh(me)

                if self.__deforming:
                    self.__mesh_object.set_motion_segment_count(len(key_times) - 1)
            else:
                # Set vertex and normal poses.
                logger.debug("Setting mesh key for object %s, time = %s", self.bl_obj.name, time)
                self.__set_mesh_key(me, self.__key_index)

        bpy.data.meshes.remove(me)
        self.__key_index += 1

    def flush_entities(self, assembly):
        # Compute tangents if needed.
        if self.__export_mode != ProjectExportMode.PROJECT_EXPORT:
            if self.bl_obj.data.appleseed.smooth_tangents and self.bl_obj.data.appleseed.export_uvs:
                asr.compute_smooth_vertex_tangents(self.__mesh_object)

        asr_obj_props = self.bl_obj.appleseed

        mesh_name = self.__mesh_object.get_name()
        object_instance_params = {'visibility': {'camera': asr_obj_props.camera_visible,
                                                 'light': asr_obj_props.light_visible,
                                                 'shadow': asr_obj_props.shadow_visible,
                                                 'diffuse': asr_obj_props.diffuse_visible,
                                                 'glossy': asr_obj_props.glossy_visible,
                                                 'specular': asr_obj_props.specular_visible,
                                                 'transparency': asr_obj_props.transparency_visible},
                                  'medium_priority': asr_obj_props.medium_priority,
                                  'ray_bias_method': asr_obj_props.object_ray_bias_method,
                                  'ray_bias_distance': asr_obj_props.object_ray_bias_distance}

        if asr_obj_props.object_sss_set != "":
            object_instance_params['sss_set_id'] = asr_obj_props.object_sss_set

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

        self._xform_seq.optimize()

        logger.debug(
            "Flushing object %s, num instances = %s, num xform keys = %s",
            self.appleseed_name,
            self._num_instances,
            self._xform_seq.size())

        if self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER:
            # We always create assemblies when doing IPR to allow quick xform edits.
            needs_assembly = True
        else:
            # Only create an assembly if the object is instanced or has xform motion blur.
            needs_assembly = self._num_instances > 1 or self._xform_seq.size() > 1

        if needs_assembly:
            logger.debug("Creating assembly for object %s, name: %s", mesh_name, self.assembly_name)

            ass = asr.Assembly(self.assembly_name)

            logger.debug("Creating object instance for object %s, name: %s", mesh_name, self.appleseed_name)

            obj_inst = asr.ObjectInstance(
                self.appleseed_name,
                object_instance_params,
                self.__object_instance_mesh_name(mesh_name),
                asr.Transformd(asr.Matrix4d().identity()),
                self.__front_materials,
                self.__back_materials)

            ass.objects().insert(self.__mesh_object)
            self.__mesh_object = ass.objects().get_by_name(mesh_name)

            obj_inst_name = obj_inst.get_name()
            ass.object_instances().insert(obj_inst)
            self.__obj_inst = ass.object_instances().get_by_name(obj_inst_name)

            assembly_instance_name = self.assembly_name + "_inst"

            logger.debug("Creating assembly instance for object %s, name: %s", mesh_name, assembly_instance_name)

            ass_name = self._insert_entity_with_unique_name(assembly.assemblies(), ass, ass.get_name())
            self.__ass = assembly.assemblies().get_by_name(ass_name)

            ass_inst = asr.AssemblyInstance(
                assembly_instance_name,
                {},
                ass_name)
            ass_inst.set_transform_sequence(self._xform_seq)

            ass_inst_name = self._insert_entity_with_unique_name(assembly.assembly_instances(), ass_inst, ass_inst.get_name())
            self.__ass_inst = assembly.assembly_instances().get_by_name(ass_inst_name)

            if self.__alpha_tex is not None:
                self.__ass.textures().insert(self.__alpha_tex)
            if self.__alpha_tex_inst is not None:
                self.__ass.texture_instances().insert(self.__alpha_tex_inst)

        else:
            logger.debug("Creating object instance for object %s, name: %s", mesh_name, self.appleseed_name)

            mesh_name = self._insert_entity_with_unique_name(assembly.objects(), self.__mesh_object, mesh_name)
            self.__mesh_object = assembly.objects().get_by_name(mesh_name)

            obj_inst = asr.ObjectInstance(
                self.appleseed_name,
                object_instance_params,
                self.__object_instance_mesh_name(mesh_name),
                self._xform_seq.get_earliest_transform(),
                self.__front_materials,
                self.__back_materials)

            obj_inst_name = self._insert_entity_with_unique_name(assembly.object_instances(), obj_inst, obj_inst.get_name())
            self.__obj_inst = assembly.object_instances().get_by_name(obj_inst_name)

            if self.__alpha_tex is not None:
                assembly.textures().insert(self.__alpha_tex)
            if self.__alpha_tex_inst is not None:
                assembly.texture_instances().insert(self.__alpha_tex_inst)

    def update_transform(self, time, matrix):
        self.__ass_inst.transform_sequence().set_transform(time, self._convert_matrix(matrix))

    #
    # Internal methods.
    #

    def __get_blender_mesh(self, scene, triangulate=True):
        settings = 'RENDER' if self.__export_mode != ProjectExportMode.INTERACTIVE_RENDER else 'PREVIEW'
        me = self.bl_obj.to_mesh(
            scene,
            apply_modifiers=True,
            settings=settings,
            calc_tessface=True)

        if triangulate:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            bm.to_mesh(me)
            bm.free()

        return me

    def __convert_mesh(self, me):
        if not self.__use_cpp_export:
            # Python export

            # Material slots.
            material_slots = self.bl_obj.material_slots

            self.__mesh_object.reserve_material_slots(len(material_slots))

            if len(material_slots) > 1:
                for i, m in enumerate(material_slots):
                    self.__mesh_object.push_material_slot("slot-%s" % i)
            else:
                self.__mesh_object.push_material_slot("default")

            # Vertices
            self.__mesh_object.reserve_vertices(len(me.vertices))

            for v in me.vertices:
                self.__mesh_object.push_vertex(asr.Vector3f(v.co[0], v.co[1], v.co[2]))

            # Faces.
            self.__mesh_object.reserve_triangles(len(me.polygons))

            for f in me.polygons:
                assert (len(f.vertices) == 3)
                tri = asr.Triangle(
                    f.vertices[0],
                    f.vertices[1],
                    f.vertices[2],
                    f.material_index)

                self.__mesh_object.push_triangle(tri)

            loops = me.loops

            # UVs.
            if self.bl_obj.data.appleseed.export_uvs and len(me.uv_textures) > 0:
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
            if self.bl_obj.data.appleseed.export_normals:
                me.calc_normals_split()

                self.__mesh_object.reserve_vertex_normals(len(me.polygons) * 3)

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
        else:
            # C++ export
            do_uvs = False

            do_normals = False

            material_slots = self.bl_obj.material_slots

            self.__mesh_object.reserve_material_slots(len(material_slots))

            if len(material_slots) > 1:
                for i, m in enumerate(material_slots):
                    self.__mesh_object.push_material_slot("slot-%s" % i)
            else:
                self.__mesh_object.push_material_slot("default")

            if self.bl_obj.data.appleseed.export_normals:
                me.calc_normals()
                me.split_faces()
                do_normals = True

            me.calc_tessface()

            vertex_pointer = me.vertices[0].as_pointer()
            tessface_pointer = me.tessfaces[0].as_pointer()
            vertices_length = len(me.vertices)
            tessface_length = len(me.tessfaces)

            if self.bl_obj.data.appleseed.export_uvs and len(me.uv_textures) > 0:
                uv_textures = me.tessface_uv_textures

                for uv in uv_textures:
                    if uv.active_render:
                        active_uv = uv

                uv_layer_pointer = active_uv.data[0].as_pointer()
                do_uvs = True
            else:
                uv_layer_pointer = 0

            asr.convert_bl_mesh(self.__mesh_object,
                                vertices_length,
                                vertex_pointer,
                                tessface_length,
                                tessface_pointer,
                                uv_layer_pointer,
                                do_normals,
                                do_uvs)

    def __set_mesh_key(self, me, key_index):
        pose = key_index - 1

        do_normals = True if self.bl_obj.data.appleseed.export_normals else False

        if not self.__use_cpp_export:
            # Vertices.
            for i, v in enumerate(me.vertices):
                self.__mesh_object.set_vertex_pose(i, pose, asr.Vector3f(v.co[0], v.co[1], v.co[2]))

            # Normals.
            if do_normals:
                me.calc_normals_split()
                loops = me.loops

                normal_index = 0

                for f in me.polygons:
                    loop = f.loop_indices

                    for i in range(0, 3):
                        n = loops[f.loop_indices[i]].normal
                        self.__mesh_object.set_vertex_normal_pose(normal_index, pose, asr.Vector3f(n[0], n[1], n[2]))
                        normal_index += 1
        else:
            if do_normals:
                me.calc_normals()
                me.split_faces()

            me.calc_tessface()

            vertex_pointer = me.vertices[0].as_pointer()
            tessface_pointer = me.tessfaces[0].as_pointer()
            vertices_length = len(me.vertices)
            tessface_length = len(me.polygons)

            asr.convert_bl_vertex_pose(self.__mesh_object,
                                       pose,
                                       vertices_length,
                                       vertex_pointer,
                                       tessface_length,
                                       tessface_pointer,
                                       do_normals)

    def __write_mesh(self, mesh_name):
        # Compute tangents if needed.
        if self.bl_obj.data.appleseed.smooth_tangents and self.bl_obj.data.appleseed.export_uvs:
            asr.compute_smooth_vertex_tangents(self.__mesh_object)

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

    def __object_instance_mesh_name(self, mesh_name):
        if self.__export_mode == ProjectExportMode.PROJECT_EXPORT:
            return mesh_name + ".mesh"

        return mesh_name
