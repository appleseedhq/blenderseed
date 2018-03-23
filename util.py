
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

import multiprocessing
import os
import sys
from math import tan, atan, degrees

import bpy
import mathutils

from . import bl_info

import subprocess


# ------------------------------------
# OSL shader reader
# ------------------------------------

def get_osl_search_paths():
    appleseed_bin_dir = bpy.context.user_preferences.addons['blenderseed'].preferences.appleseed_binary_directory
    appleseed_parent_dir = appleseed_bin_dir
    while os.path.basename(appleseed_parent_dir) != 'bin':
        appleseed_parent_dir = os.path.dirname(appleseed_parent_dir)
    appleseed_parent_dir = os.path.dirname(appleseed_parent_dir)

    shader_directories = (os.path.join(appleseed_parent_dir, 'shaders', 'appleseed'), os.path.join(appleseed_parent_dir, 'shaders', 'blenderseed'))

    return appleseed_bin_dir, shader_directories


def read_osl_shaders():
    """Compiles any .osl files and reads all .oso parameters"""

    if bpy.context.user_preferences.addons['blenderseed'].preferences.appleseed_binary_directory == "":
        print("appleseed binary path not set.  Rendering and OSL features will not be available")
        return

    appleseed_bin_dir, shader_directories = get_osl_search_paths()

    nodes = []

    for shader_dir in shader_directories:
        if os.path.isdir(shader_dir):
            print("Searching {0} for OSL files".format(shader_dir))
            for file in os.listdir(shader_dir):
                if file.endswith(".osl"):
                    print("appleseed Compiling {0}".format(file))
                    filename = os.path.join(shader_dir, file)
                    oslc_path = os.path.join(appleseed_bin_dir, "oslc")
                    cmd = (oslc_path, '"{0}"'.format(filename))
                    try:
                        process = subprocess.Popen(" ".join(cmd), cwd=shader_dir, bufsize=1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        while True:
                            line = process.stdout.readline()
                            if not line:
                                break
                            line = line.strip().decode("utf-8")
                            if "error" in line:
                                print(line)
                                print("ERROR: Failed to compile {0}".format(file))
                                break
                        print("appleseed Compiled {0}".format(file))
                    except OSError as e:
                        print("OSError > " + e.errno)
                        print("OSError > " + e.strerror)
                        print("OSError > " + e.filename)
                    except:
                        print("ERROR: Failed to compile {0}.  Oslc did not launch: {1}".format(file, sys.exc_info()[0]))

    print("appleseed Parsing OSL shaders")
    for shader_dir in shader_directories:
        if os.path.isdir(shader_dir):
            print("Searching {0} for OSO files".format(shader_dir))
            for file in os.listdir(shader_dir):
                if file.endswith(".oso"):
                    print("appleseed Reading {0}".format(file))
                    filename = os.path.join(shader_dir, file)
                    content = []
                    cmd = ('oslinfo', '-v', '"{0}"'.format(filename))
                    try:
                        process = subprocess.Popen(" ".join(cmd), cwd=appleseed_bin_dir, bufsize=1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        while True:
                            line = process.stdout.readline()
                            if not line:
                                break
                            line = line.strip().decode("utf-8")
                            if "ERROR" in line:
                                print(line)
                                print("ERROR: Failed to read {0}".format(file))
                                break
                            content.append(line)
                        shader_params = create_osl_dict(file, content)
                        if shader_params:
                            nodes.append(shader_params)
                        else:
                            print("ERROR: No Shader Parameters")
                    except OSError as e:
                        print("OSError > " + e.errno)
                        print("OSError > " + e.strerror)
                        print("OSError > " + e.filename)
                    except:
                        print("ERROR: Failed to read {0}.  Oslinfo did not launch: {1}".format(file, sys.exc_info()[0]))

    print("appleseed OSL Parsing Complete")
    return nodes


def create_osl_dict(file, content=None):
    d = {}
    currentElement = None
    for line in content:
        if len(line) == 0:
            continue
        if line.startswith("shader") or line.startswith("surface"):
            d['inputs'] = []
            d['outputs'] = []
            d['non_connectable_props'] = []
            d['filename'] = file.replace(".oso", "")
            currentElement = d
            if line.startswith("surface"):
                currentElement['category'] = 'surface'
            else:
                currentElement['category'] = 'shader'
        else:
            if line.startswith("Default value"):
                currentElement['default'] = line.split(": ")[-1].replace("\"", "")
                if "type" in currentElement:
                    if currentElement["type"] in ["color", "vector", "output vector"]:
                        currentElement['default'] = line.split("[")[-1].split("]")[0].strip()
            elif line.startswith("metadata"):
                if 'node_name' in line:
                    currentElement['name'] = line.split(" = ")[-1].replace("\"", "")
                if "widget = " in line:
                    currentElement['widget'] = line.split(" = ")[-1].replace("\"", "")
                    if currentElement['widget'] == 'null' and currentElement['type'] not in ('vector', 'point[4]', 'point', 'normal', 'matrix', 'float[2]'):
                        currentElement['connectable'] = False
                    if currentElement['widget'] == 'filename':
                        currentElement['use_file_picker'] = True
                if "classification" in line:
                    if 'utility' in line:
                        currentElement['category'] = 'utility'
                    if 'texture/2d' in line:
                        currentElement['category'] = 'texture'
                    if 'texture/3d' in line:
                        currentElement['category'] = '3d_texture'
                if "options = " in line:
                    currentElement['type'] = 'intenum'
                    currentElement['options'] = line.split(" = ")[-1].replace("\"", "").split("|")
                    currentElement['connectable'] = False
                if "min = " in line:
                    currentElement['min'] = line.split(" ")[-1]
                if "max = " in line:
                    currentElement['max'] = line.split(" ")[-1]
                if "label = " in line:
                    currentElement['label'] = " ".join(line.split("=")[1:]).replace("\"", "").strip()
                if "connectable" in line:
                    currentElement['connectable'] = False
                if "help = " in line:
                    currentElement['help'] = line.split(" = ")[-1].replace("\"", "")
            elif line.startswith("\""):  # found a parameter
                currentElement = {}
                elementName = line.split(" ")[0].replace("\"", "")
                currentElement['name'] = reverseValidate(elementName)
                currentElement['type'] = " ".join(line.split(" ")[1:]).replace("\"", "")
                currentElement['connectable'] = True
                currentElement['hidden'] = False
                currentElement['use_file_picker'] = False
                if 'in_' not in currentElement['name']:
                    currentElement['hidden'] = True
                if 'FilePath' in elementName:
                    currentElement['use_file_picker'] = True
                if currentElement['type'] == "string":
                    currentElement['connectable'] = False

                if "out_" in line:
                    d['outputs'].append(currentElement)
                    currentElement = d['outputs'][-1]
                else:
                    d['inputs'].append(currentElement)
                    currentElement = d['inputs'][-1]
            elif line.startswith("Unknown"):
                continue
            else:
                print("ERROR: {0}".format(line))
                return {}

    return d


def reverseValidate(pname):
    if pname == "inMin":
        return "min"
    if pname == "inMax":
        return "max"
    if pname == "inVector":
        return "vector"
    if pname == "inMatrix":
        return "matrix"
    if pname == "inDiffuse":
        return "diffuse"
    if pname == "inColor":
        return "color"
    if pname == "outOutput":
        return "output"
    return pname

# ------------------------------------
# Generic utilities and settings.
# ------------------------------------
sep = os.sep

# Add-on directory.
for addon_path in bpy.utils.script_paths("addons"):
    if "blenderseed" in os.listdir(addon_path):
        addon_dir = os.path.join(addon_path, "blenderseed")

version = "{0}.{1}.{2}".format(bl_info['version'][0], bl_info['version'][1], bl_info['version'][2])

thread_count = multiprocessing.cpu_count()

EnableDebug = True


def debug(*args):
    msg = ' '.join(['%s' % a for a in args])
    global EnableDebug
    if EnableDebug:
        print("DEBUG:", msg)


def asUpdate(*args):
    msg = ' '.join(['%s' % a for a in args])
    print("appleseed:", msg)


def strip_spaces(name):
    return '_'.join(name.split(' '))


def join_names_underscore(name1, name2):
    return '_'.join((strip_spaces(name1), strip_spaces(name2)))


def filter_params(params):
    filter_list = []
    for p in params:
        if p not in filter_list:
            filter_list.append(p)
    return filter_list


def realpath(path):
    """Resolve a relative Blender path to a real filesystem path"""

    if path.startswith('//'):
        path = bpy.path.abspath(path)
    else:
        path = os.path.realpath(path)

    path = path.replace('\\', '/')
    path = os.path.realpath(path)

    return path


# ------------------------------------
# Scene export utilities.
# ------------------------------------

def inscenelayer(obj, scene):
    for i in range(len(obj.layers)):
        if obj.layers[i] and scene.layers[i]:
            return True


def do_export(obj, scene):
    return not obj.hide_render and obj.type in ('MESH', 'SURFACE', 'META', 'TEXT', 'CURVE', 'LAMP') and inscenelayer(obj, scene)


def get_render_resolution(scene):
    scale = scene.render.resolution_percentage / 100.0
    width = int(scene.render.resolution_x * scale)
    height = int(scene.render.resolution_y * scale)
    return width, height


def get_camera_matrix(camera, global_matrix):
    """
    Get the camera transformation decomposed as origin, forward, up and target.
    """
    camera_mat = global_matrix * camera.matrix_world
    origin = camera_mat.col[3]
    forward = -camera_mat.col[2]
    up = camera_mat.col[1]
    target = origin + forward
    return origin, forward, up, target


def calc_fov(camera_ob, width, height):
    """
    Calculate horizontal FOV if rendered height is greater than rendered width.

    Thanks to NOX exporter developers for this solution.
    """
    camera_angle = degrees(camera_ob.data.angle)
    if width < height:
        length = 18.0 / tan(camera_ob.data.angle / 2)
        camera_angle = 2 * atan(18.0 * width / height / length)
        camera_angle = degrees(camera_angle)
    return camera_angle


def is_uv_img(tex):
    return tex and tex.type == 'IMAGE' and tex.image


# ------------------------------------
# Object / instance utilities.
# ------------------------------------

def ob_mblur_enabled(object, scene):
    return object.appleseed.enable_motion_blur and object.appleseed.motion_blur_type == 'object' and scene.appleseed.enable_motion_blur and scene.appleseed.enable_object_blur


def def_mblur_enabled(object, scene):
    return object.appleseed.enable_motion_blur and object.appleseed.motion_blur_type == 'deformation' and scene.appleseed.enable_motion_blur and scene.appleseed.enable_deformation_blur


def get_instance_materials(ob):
    obmats = []
    # Grab materials attached to object instances ...
    if hasattr(ob, 'material_slots'):
        for ms in ob.material_slots:
            obmats.append(ms.material)
    # ... and to the object's mesh data
    if hasattr(ob.data, 'materials'):
        for m in ob.data.materials:
            obmats.append(m)
    return obmats


def is_proxy(ob, scene):
    if ob.type == 'MESH' and ob.appleseed.is_proxy:
        if ob.appleseed.use_external:
            return ob.appleseed.external_instance_mesh != ''
        else:
            return ob.appleseed.instance_mesh is not None and scene.objects[ob.appleseed.instance_mesh].type == 'MESH'


def get_instances(obj_parent, scene):
    """
    Get the instanced objects on the parent object (dupli-faces / dupli-verts).
    If motion blur is not enabled, returns list of lists [ [dupli_object.object, dupli matrix]]
    If motion blur is enabled, returns a nested list: [ [dupli_object.object, [dupli matrices]]]
    """
    dupli_list = []
    if ob_mblur_enabled(obj_parent, scene):
        dupli_list = sample_mblur(obj_parent, scene, dupli=True)
    else:
        obj_parent.dupli_list_create(scene)
        for dupli in obj_parent.dupli_list:
            dupli_matrix = dupli.matrix.copy()
            dupli_list.append([dupli.object, dupli_matrix])
        obj_parent.dupli_list_clear()
    return dupli_list


def sample_mblur(ob, scene, dupli=False):
    """
    Sample motion blur matrices for the object or duplis.
    Returns a list of matrices, if an object only.
    Returns a nested list of [ [dupli_object.object, [dupli matrix 1, dupli matrix 2]]]
    """
    matrices = []
    asr_scn = scene.appleseed
    frame_orig = scene.frame_current
    frame_set = scene.frame_set

    # Collect matrices at shutter open.
    frame_set(frame_orig, subframe=asr_scn.shutter_open)
    ob.dupli_list_create(scene)
    for dupli in ob.dupli_list:
        matrices.append([dupli.object, [dupli.matrix.copy(), ]])
    ob.dupli_list_clear()

    # Advance to shutter close, collect matrices.
    frame_set(frame_orig, subframe=asr_scn.shutter_close)
    ob.dupli_list_create(scene)
    for m in range(0, len(ob.dupli_list)):
        matrices[m][1].append(ob.dupli_list[m].matrix.copy())
    ob.dupli_list_clear()

    # Reset timeline and return.
    frame_set(frame_orig)
    return matrices


# ------------------------------------
# Particle system utilities.
# ------------------------------------
def calc_decrement(root, tip, segments):
    return ((root - tip) / (segments - 1))


def render_emitter(ob):
    render = False
    for psys in ob.particle_systems:
        if psys.settings.use_render_emitter:
            render = True
            break
    return render


def is_psys_emitter(ob):
    emitter = False
    for mod in ob.modifiers:
        if mod.type == 'PARTICLE_SYSTEM' and mod.show_render:
            psys = mod.particle_system
            if psys.settings.render_type == 'OBJECT' and psys.settings.dupli_object is not None:
                emitter = True
                break
            elif psys.settings.render_type == 'GROUP' and psys.settings.dupli_group is not None:
                emitter = True
                break
    return emitter


def has_hairsys(ob):
    has_hair = False
    for mod in ob.modifiers:
        if mod.type == 'PARTICLE_SYSTEM' and mod.show_render:
            psys = mod.particle_system
            if psys.settings.type == 'HAIR' and psys.settings.render_type == 'PATH':
                has_hair = True
                break
    return has_hair


def get_all_psysobs():
    """
    Return a set of all the objects being instanced in particle systems
    """
    obs = set()
    for settings in bpy.data.particles:
        if settings.render_type == 'OBJECT' and settings.dupli_object is not None:
            obs.add(settings.dupli_object)
        elif settings.render_type == 'GROUP' and settings.dupli_group is not None:
            obs.update({ob for ob in settings.dupli_group.objects})
    return obs


def get_psys_instances(ob, scene):
    """
    Return a dictionary of
    particle: [dupli.object, [matrices]]
    pairs. This function assumes particle systems and
    face / verts duplication aren't being used on the same object.
    """
    all_duplis = {}
    current_total = 0
    index = 0
    if not hasattr(ob, 'modifiers'):
        return {}
    if not ob_mblur_enabled(ob, scene):
        # If no motion blur
        ob.dupli_list_create(scene, settings='RENDER')
    for modifier in ob.modifiers:
        if modifier.type == 'PARTICLE_SYSTEM' and modifier.show_render:
            psys = modifier.particle_system
            if not psys.settings.render_type in {'OBJECT', 'GROUP'}:
                continue
            if psys.settings.type == 'EMITTER':
                particles = [p for p in psys.particles if p.alive_state == 'ALIVE']
            else:
                particles = [p for p in psys.particles]
            start = current_total
            current_total += len(particles)

            if not ob_mblur_enabled(ob, scene):
                # No motion blur.
                duplis = []
                for dupli_index in range(start, current_total):
                    # Store the dupli.objects for the current particle system only
                    # ob.dupli_list is created in descending order of particle systems
                    # So it should be reliable to match them this way.
                    duplis.append(ob.dupli_list[dupli_index].object)

                if psys.settings.type == 'EMITTER':
                    p_duplis_pairs = list(zip(particles, duplis))  # Match the particles to the duplis
                    dupli_dict = {p[0]: [p[1], []] for p in p_duplis_pairs}  # Create particle:[dupli.object, [matrix]] pairs
                    for particle in dupli_dict.keys():
                        size = particle.size
                        loc = particle.location
                        scale = dupli_dict[particle][0].scale * size
                        transl = mathutils.Matrix.Translation((loc))
                        scale = mathutils.Matrix.Scale(scale.x, 4, (1, 0, 0)) * mathutils.Matrix.Scale(scale.y, 4,
                                                                                                       (0, 1, 0)) * mathutils.Matrix.Scale(scale.z, 4,
                                                                                                                                           (0, 0, 1))
                        mat = transl * scale
                        dupli_dict[particle][1].append(mat)
                else:
                    dupli_mat_list = [dupli.matrix.copy() for dupli in ob.dupli_list]
                    p_duplis_pairs = list(zip(particles, duplis, dupli_mat_list))
                    dupli_dict = {p[0]: [p[1], [p[2]]] for p in p_duplis_pairs}
            else:
                # Using motion blur
                dupli_dict, index = sample_psys_mblur(ob, scene, psys, index, start, current_total)

            # Add current particle system to the collection.
            all_duplis.update(dupli_dict)

    if not ob_mblur_enabled(ob, scene):
        # If no motion blur
        ob.dupli_list_clear()
    return all_duplis


def sample_psys_mblur(ob, scene, psys, index, start, current_total):
    """
    Return a dictionary of
    particle: [dupli.object, [matrices]]
    pairs
    """
    asr_scn = scene.appleseed
    dupli_dict = {}
    frame_orig = scene.frame_current
    frame_set = scene.frame_set

    frame_set(frame_orig, subframe=asr_scn.shutter_open)
    if psys.settings.type == 'EMITTER':
        particles = [p for p in psys.particles if p.alive_state == 'ALIVE']
    else:
        particles = [p for p in psys.particles]
    if len(particles) == 0:
        return False

    if psys.settings.type == 'EMITTER':
        # Emitter particle system.
        ob.dupli_list_create(scene, 'RENDER')
        duplis = [dupli.object for dupli in ob.dupli_list]
        p_duplis_pairs = list(zip(particles, duplis))
        dupli_dict = {p[0]: [p[1], []] for p in p_duplis_pairs}
        new_index = index
        for frame in {asr_scn.shutter_open, asr_scn.shutter_close}:
            new_index = index
            frame_set(frame_orig, subframe=frame)
            for particle in dupli_dict.keys():
                size = particle.size
                transl = particle.location
                scale = dupli_dict[particle][0].scale * size
                transl = mathutils.Matrix.Translation((transl))
                scale = mathutils.Matrix.Scale(scale.x, 4, (1, 0, 0)) * mathutils.Matrix.Scale(scale.y, 4,
                                                                                               (0, 1, 0)) * mathutils.Matrix.Scale(scale.z, 4,
                                                                                                                                   (0, 0, 1))
                mat = transl * scale
                dupli_dict[particle][1].append(mat)
                new_index += 1
        index += new_index
    else:
        # Hair particle system.
        duplis = []
        ob.dupli_list_create(scene, 'RENDER')
        for dupli_index in range(start, current_total):
            duplis.append(ob.dupli_list[dupli_index].object)
        p_duplis_pairs = list(zip(particles, duplis))
        dupli_dict = {p[0]: [p[1], []] for p in p_duplis_pairs}
        ob.dupli_list_clear()
        new_index = index
        for frame in {asr_scn.shutter_open, asr_scn.shutter_close}:
            new_index = index
            frame_set(frame_orig, subframe=frame)
            ob.dupli_list_create(scene, 'RENDER')
            for particle in dupli_dict.keys():
                mat = ob.dupli_list[new_index].matrix.copy()
                dupli_dict[particle][1].append(mat)
                new_index += 1
            ob.dupli_list_clear()
        index += new_index

    # Clean up and return
    if psys.settings.type == 'EMITTER':
        del scale, transl, mat
        ob.dupli_list_clear()
    frame_set(frame_orig)
    return dupli_dict, index
