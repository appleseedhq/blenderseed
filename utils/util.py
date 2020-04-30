#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2014-2019 The appleseedhq Organization
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
import os

import bpy
import bpy_extras
from bpy.app.handlers import persistent
import numpy as np

import appleseed as asr
from . import path_util, osl_utils
from ..logger import get_logger
from ..properties.nodes import AppleseedOSLScriptNode

logger = get_logger()

image_extensions = ('jpg', 'png', 'tif', 'exr', 'bmp',
                    'tga', 'hdr', 'dpx', 'psd', 'gif', 'jp2')

cycles_nodes = {"ShaderNodeRGBCurve": "node_rgb_curves.oso"}


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


# ------------------------------------
# Generic utilities and settings.
# ------------------------------------

def clamp_value(n, smallest, largest):
    return max(smallest, min(n, largest))


def filter_params(params):
    filter_list = list()
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

def appleseed_popup_info(message="", title="appleseed Info", icon='INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

def mapping_to_array(mapping):
    curve_resolution = bpy.context.preferences.addons['blenderseed'].preferences.curve_resolution
    rgb_floats = np.empty(curve_resolution * 3, dtype=float)

    map_r = mapping.curves[0]
    map_g = mapping.curves[1]
    map_b = mapping.curves[2]
    map_i = mapping.curves[3]

    for i in range(curve_resolution):
        start_index = i * 3
        t = i / (curve_resolution - 1)
        rgb_floats[start_index] = mapping.evaluate(map_r, mapping.evaluate(map_i, t))
        rgb_floats[start_index + 1] = mapping.evaluate(map_g, mapping.evaluate(map_i, t))
        rgb_floats[start_index + 2] = mapping.evaluate(map_b, mapping.evaluate(map_i, t))

    return rgb_floats

@persistent
def update_project(_):
    """
    This function automatically runs when a .blend file is opened.
    :param _:
    :return:
    """

    # Compile all OSL Script nodes
    stdosl_path = path_util.get_stdosl_paths()
    compiler = asr.ShaderCompiler(stdosl_path)
    q = asr.ShaderQuery()
    for script in bpy.data.texts:
        osl_bytecode = osl_utils.compile_osl_bytecode(compiler,
                                                      script)
        if osl_bytecode is not None:
            q.open_bytecode(osl_bytecode)

            node_data = osl_utils.parse_shader(q)

            node_name, node_category, node_classes = osl_utils.generate_node(node_data,
                                                                             AppleseedOSLScriptNode)

            for cls in node_classes:
                safe_register_class(cls)

        else:
            logger.debug(f"appleseed: Shader {script.name} did not compile")


# ------------------------------------
# Scene export utilities.
# ------------------------------------


def get_render_resolution(scene):
    scale = scene.render.resolution_percentage / 100.0
    width = int(scene.render.resolution_x * scale)
    height = int(scene.render.resolution_y * scale)
    return width, height


def calc_film_aspect_ratio(scene):
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
    :param aspect_ratio:
    :param camera:
    :param zoom:
    :return:
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
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene,
                                                         cam,
                                                         co)
    y = 1 - co_2d.y

    return co_2d.x, y


def get_focal_distance(camera):
    if camera.data.dof.focus_object is not None:
        cam_location = camera.matrix_world.to_translation()
        cam_target_location = bpy.data.objects[camera.data.dof.focus_object.name].matrix_world.to_translation()
        focal_distance = (cam_target_location - cam_location).magnitude
    else:
        focal_distance = camera.data.dof.focus_distance

    return focal_distance


# ------------------------------------
# Object / instance utilities.
# ------------------------------------


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
    """
    Simple timer for profiling operations.
    """

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
