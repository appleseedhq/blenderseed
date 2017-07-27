
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
import os
from . import util

#--------------------------------------------------------------------------------------------------
# Write a mesh object to disk in Wavefront OBJ format.
#--------------------------------------------------------------------------------------------------


def get_array2_key(v):
    a = int(v[0] * 1000000)
    b = int(v[1] * 1000000)
    return a, b


def get_vector2_key(v):
    w = v * 1000000
    return int(w.x), int(w.y)


def get_vector3_key(v):
    w = v * 1000000
    return w.x, w.y, w.z


def write_mesh_to_disk(ob, scene, mesh, filepath):
    mesh_parts = []
    verts = []
    verts_n = []
    verts_t = []
    faces_w = []

    try:
        obj_file = open(filepath, "w", encoding="utf8")
        fw = obj_file.write
    except:
        util.asUpdate("Cannot create file %s. Check directory permissions." % filepath)
        return

    vertices = mesh.vertices
    faces = mesh.tessfaces
    uvtex = mesh.tessface_uv_textures
    uvset = uvtex.active.data if uvtex else None

    # Sort the faces by material.
    sorted_faces = [(index, face) for index, face in enumerate(faces)]
    sorted_faces.sort(key=lambda item: item[1].material_index)

    # Write vertices.
    for vertex in vertices:
        v = vertex.co
        verts.append("v %.15f %.15f %.15f\n" % (v.x, v.y, v.z))

    fw(('').join(verts))

    # Deduplicate and write normals.
    normal_indices = {}
    vertex_normal_indices = {}
    face_normal_indices = {}
    current_normal_index = 0
    for face_index, face in sorted_faces:
        if face.use_smooth:
            for vertex_index in face.vertices:
                vn = vertices[vertex_index].normal
                vn_key = (vn.x, vn.y, vn.z)
                if vn_key in normal_indices:
                    vertex_normal_indices[vertex_index] = normal_indices[vn_key]
                else:
                    verts_n.append("vn %.15f %.15f %.15f\n" % (vn.x, vn.y, vn.z))
                    normal_indices[vn_key] = current_normal_index
                    vertex_normal_indices[vertex_index] = current_normal_index
                    current_normal_index += 1
        else:
            vn = face.normal
            vn_key = (vn.x, vn.y, vn.z)
            if vn_key in normal_indices:
                face_normal_indices[face_index] = normal_indices[vn_key]
            else:
                verts_n.append("vn %.15f %.15f %.15f\n" % (vn.x, vn.y, vn.z))
                normal_indices[vn_key] = current_normal_index
                face_normal_indices[face_index] = current_normal_index
                current_normal_index += 1

    fw(('').join(verts_n))

    # Deduplicate and write texture coordinates.
    if uvset:
        vt_indices = {}
        vertex_texcoord_indices = {}
        current_vt_index = 0
        for face_index, face in sorted_faces:
            assert len(uvset[face_index].uv) == len(face.vertices)
            for vt_index, vt in enumerate(uvset[face_index].uv):
                vertex_index = face.vertices[vt_index]
                vt_key = get_array2_key(vt)
                if vt_key in vt_indices:
                    vertex_texcoord_indices[face_index, vertex_index] = vt_indices[vt_key]
                else:
                    verts_t.append("vt %.15f %.15f\n" % (vt[0], vt[1]))
                    vt_indices[vt_key] = current_vt_index
                    vertex_texcoord_indices[face_index, vertex_index] = current_vt_index
                    current_vt_index += 1

    fw(('').join(verts_t))

    # Write faces.
    current_material_index = -1
    for face_index, face in sorted_faces:
        if current_material_index != face.material_index:
            current_material_index = face.material_index
            mesh_name = "part_%d" % current_material_index
            mesh_parts.append((current_material_index, mesh_name))
            faces_w.append("o {0}\n".format(mesh_name))
        line = "f"
        if uvset and len(uvset[face_index].uv) > 0:
            if face.use_smooth:
                for vertex_index in face.vertices:
                    texcoord_index = vertex_texcoord_indices[face_index, vertex_index]
                    normal_index = vertex_normal_indices[vertex_index]
                    line += " %d/%d/%d" % (vertex_index + 1, texcoord_index + 1, normal_index + 1)
            else:
                normal_index = face_normal_indices[face_index]
                for vertex_index in face.vertices:
                    texcoord_index = vertex_texcoord_indices[face_index, vertex_index]
                    line += " %d/%d/%d" % (vertex_index + 1, texcoord_index + 1, normal_index + 1)
        else:
            if face.use_smooth:
                for vertex_index in face.vertices:
                    normal_index = vertex_normal_indices[vertex_index]
                    line += " %d//%d" % (vertex_index + 1, normal_index + 1)
            else:
                normal_index = face_normal_indices[face_index]
                for vertex_index in face.vertices:
                    line += " %d//%d" % (vertex_index + 1, normal_index + 1)
        faces_w.append(line + "\n")

    fw(('').join(faces_w))

    obj_file.close()

    return mesh_parts
    # End with block


def write_curves_to_disk(ob, scene, psys, filepath):
    """
    Write curves object to file.
    """
    with open(filepath, "w") as curves_file:
        fw = curves_file.write

        psys.set_resolution(scene, ob, 'RENDER')
        steps = 2 ** psys.settings.render_step

        # Write the number of hairs to the file
        num_curves = len(psys.particles) if len(psys.child_particles) == 0 else len(psys.child_particles)
        fw("%d\n" % num_curves)

        # Write the number of points per hair to the file
        fw("%d\n" % steps)

        root_size = psys.settings.appleseed.root_size * psys.settings.appleseed.scaling
        tip_size = psys.settings.appleseed.tip_size * psys.settings.appleseed.scaling
        radius_decrement = util.calc_decrement(root_size, tip_size, steps)
        for p in range(0, num_curves):
            p_radius = root_size
            for step in range(0, steps):
                # A hack for now, to keep the points at max of 4
                if step == 4:
                    break
                co = psys.co_hair(ob, p, step)
                radius = p_radius
                fw("%.6f %.6f %.6f %.4f " % (co.x, co.y, co.z, radius))
                p_radius -= radius_decrement
            fw("\n")
        psys.set_resolution(scene, ob, 'PREVIEW')
    return
