#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
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

import datetime
import multiprocessing
import os

import bpy
from bpy.app.handlers import persistent
import bpy_extras

from . import path_util
from ..logger import get_logger

logger = get_logger()

image_extensions = ('jpg', 'png', 'tif', 'exr', 'bmp', 'tga', 'hdr', 'dpx', 'psd', 'gif', 'jp2')


def safe_register_class(cls):
    try:
        logger.debug("[appleseed] Registering class {0}...".format(cls))
        bpy.utils.register_class(cls)
    except Exception as e:
        logger.error("[appleseed] ERROR: Failed to register class {0}: {1}".format(cls, e))


def safe_unregister_class(cls):
    try:
        logger.debug("[appleseed] Unregistering class {0}...".format(cls))
        bpy.utils.unregister_class(cls)
    except Exception as e:
        logger.error("[appleseed] ERROR: Failed to unregister class {0}: {1}".format(cls, e))


def read_osl_shaders():
    '''
    Reads parameters from OSL .oso files using the ShaderQuery function that is built
    into the Python bindings for appleseed.  These parameters are used to create a dictionary
    of the shader parameters that is then added to a list.  This shader list is passed
    on to the oslnode.generate_node function.
    '''

    nodes = []

    if not path_util.get_appleseed_bin_dir_path():
        logger.warning("[appleseed] WARNING: Path to appleseed's binary directory not set: rendering and OSL features will not be available.")
        return nodes

    shader_directories = path_util.get_osl_search_paths()

    import appleseed as asr

    q = asr.ShaderQuery()

    logger.debug("[appleseed] Parsing OSL shaders...")

    for shader_dir in shader_directories:
        if os.path.isdir(shader_dir):
            logger.debug("[appleseed] Searching {0} for OSO files...".format(shader_dir))
            for file in os.listdir(shader_dir):
                if file.endswith(".oso"):
                    logger.debug("[appleseed] Reading {0}...".format(file))
                    d = {}
                    filename = os.path.join(shader_dir, file)
                    q.open(filename)
                    d['inputs'] = []
                    d['outputs'] = []
                    shader_meta = q.get_metadata()
                    if 'as_node_name' in shader_meta:
                        d['name'] = shader_meta['as_node_name']['value']
                    else:
                        d['name'] = q.get_shader_name()
                    d['filename'] = filename
                    if 'URL' in shader_meta:
                        d['url'] = shader_meta['URL']['value']
                    else:
                        d['url'] = ''
                    if 'as_category' in shader_meta:
                        d['category'] = shader_meta['as_category']['value']
                    else:
                        d['category'] = 'other'
                    num_of_params = q.get_num_params()
                    for x in range(0, num_of_params):
                        metadata = {}
                        param = q.get_param_info(x)
                        if 'metadata' in param:
                            metadata = param['metadata']
                        param_data = {}
                        param_data['name'] = param['name']
                        param_data['type'] = param['type']
                        param_data['connectable'] = True
                        param_data['hide_ui'] = param['validdefault'] is False
                        if 'default' in param:
                            param_data['default'] = param['default']
                        if 'label' in metadata:
                            param_data['label'] = metadata['label']['value']
                        if 'widget' in metadata:
                            param_data['widget'] = metadata['widget']['value']
                            if param_data['widget'] == 'null':
                                param_data['hide_ui'] = True
                        if 'page' in metadata:
                            param_data['section'] = metadata['page']['value']
                        if 'min' in metadata:
                            param_data['min'] = metadata['min']['value']
                        if 'max' in metadata:
                            param_data['max'] = metadata['max']['value']
                        if 'softmin' in metadata:
                            param_data['softmin'] = metadata['softmin']['value']
                        if 'softmax' in metadata:
                            param_data['softmax'] = metadata['softmax']['value']
                        if 'help' in metadata:
                            param_data['help'] = metadata['help']['value']
                        if 'options' in metadata:
                            param_data['options'] = metadata['options']['value'].split(" = ")[-1].replace("\"", "").split("|")
                        if 'as_blender_input_socket' in metadata:
                            param_data['connectable'] = False if metadata['as_blender_input_socket']['value'] == 0.0 else True

                        if param['isoutput'] is True:
                            d['outputs'].append(param_data)
                        else:
                            d['inputs'].append(param_data)

                    nodes.append(d)

    logger.debug("[appleseed] OSL parsing complete.")

    return nodes


# ------------------------------------
# Generic utilities and settings.
# ------------------------------------

sep = os.sep

# Add-on directory.
for addon_path in bpy.utils.script_paths("addons"):
    if "blenderseed" in os.listdir(addon_path):
        addon_dir = os.path.join(addon_path, "blenderseed")

thread_count = multiprocessing.cpu_count()


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

@persistent
def update_project(_):
    # Update shader trees to new node ui
    for node_group in bpy.data.node_groups:
            for node in node_group.nodes:
                for socket in node.inputs:
                    if hasattr(socket, "socket_value"):
                        current_value = socket.socket_value
                        default_value = socket.socket_default_value
                        if current_value != default_value:
                            logger.debug("Updating shader tree %s, Node: %s, Parameter: %s", node_group.name, node.name, socket.socket_osl_id)
                            setattr(node, socket.socket_osl_id, current_value)
                            setattr(socket, "socket_value", default_value)

# ------------------------------------
# Scene export utilities.
# ------------------------------------

def inscenelayer(obj, scene):
    for i in range(len(obj.layers)):
        if obj.layers[i] and scene.layers[i]:
            return True


def get_render_resolution(scene):
    scale = scene.render.resolution_percentage / 100.0
    width = int(scene.render.resolution_x * scale)
    height = int(scene.render.resolution_y * scale)
    return width, height


def get_frame_aspect_ratio(scene):
    render = scene.render
    scale = render.resolution_percentage / 100.0
    width = int(render.resolution_x * scale)
    height = int(render.resolution_y * scale)
    xratio = width * render.pixel_aspect_x
    yratio = height * render.pixel_aspect_y
    return xratio / yratio


def calc_film_dimensions(aspect_ratio, camera, zoom):
    """
    Fit types:
    Horizontal = Horizontal size manually set.  Vertical size derived from aspect ratio.

    Vertical = Vertical size manually set.  Horizontal size derived from aspect ratio.

    Auto = sensor_width bpy property sets the horizontal size when the aspect ratio is over 1 and
    the vertical size when it is below 1.  Other dimension is derived from aspect ratio.

    Much thanks to the Radeon ProRender plugin for clarifying this behavior
    """

    horizontal_fit = camera.sensor_fit == 'HORIZONTAL' or \
                     (camera.sensor_fit == 'AUTO' and aspect_ratio > 1)

    if camera.sensor_fit == 'VERTICAL':
        film_height = camera.sensor_height / 1000 * zoom
        film_width = film_height * aspect_ratio
    elif horizontal_fit:
        film_width = camera.sensor_width / 1000 * zoom
        film_height = film_width / aspect_ratio
    else:
        film_height = camera.sensor_width / 1000 * zoom
        film_width = film_height * aspect_ratio

    return film_width, film_height


def find_autofocus_point(scene):
    cam = scene.camera
    co = scene.cursor_location
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, co)
    y = 1 - co_2d.y

    return co_2d.x, y

def get_focal_distance(camera):
    if camera.data.dof_object is not None:
        cam_location = camera.matrix_world.to_translation()
        cam_target_location = bpy.data.objects[camera.data.dof_object.name].matrix_world.to_translation()
        focal_distance = (cam_target_location - cam_location).magnitude
    else:
        focal_distance = camera.data.dof_distance

    return focal_distance


# ------------------------------------
# Object / instance utilities.
# ------------------------------------


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


def is_object_deforming(ob):
    deforming_mods = {'ARMATURE', 'MESH_SEQUENCE_CACHE', 'CAST', 'CLOTH', 'CURVE', 'DISPLACE',
                      'HOOK', 'LATTICE', 'MESH_DEFORM', 'SHRINKWRAP', 'EXPLODE',
                      'SIMPLE_DEFORM', 'SMOOTH', 'WAVE', 'SOFT_BODY',
                      'SURFACE', 'MESH_CACHE', 'FLUID_SIMULATION',
                      'DYNAMIC_PAINT'}
    if ob.modifiers:
        for mod in ob.modifiers:
            if mod.type in deforming_mods:
                return True

    if ob.data and hasattr(ob.data, 'shape_keys') and ob.data.shape_keys:
        return True

    return False


# ------------------------------------
# Simple timer for profiling.
# ------------------------------------

class Timer(object):
    '''
    Simple timer for profiling operations.
    '''

    def __init__(self):
        self.start()

    def start(self):
        self.__start = datetime.datetime.now()

    def stop(self):
        self.__end = datetime.datetime.now()

    def elapsed(self):
        delta = self.__end - self.__start
        return delta.total_seconds()


# ------------------------------------
# Blender addon.
# ------------------------------------

def register():
    pass


def unregister():
    pass
