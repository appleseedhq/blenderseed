#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2020 Jonathan Dent, The appleseedhq Organization
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
import numpy as np

cycles_nodes = {"ShaderNodeRGBCurve": "node_rgb_curves.oso",
                "ShaderNodeValToRGB": "node_rgb_ramp.osl"}


def parse_cycles_shader(shader):

    if shader.bl_idname == "ShaderNodeRGBCurve":
        return parse_ShaderNodeRGBCurve(shader)
    elif shader.bl_idname == "ShaderNodeValToRGB":
        return parse_ShaderNodeValToRGB(shader)


def parse_ShaderNodeRGBCurve(shader):
    params = dict()
    outputs = ["ColorOut"]

    # Curve mapping.
    mapping = shader.mapping
    mapping.update()
    rgb_array = mapping_to_array(mapping)
    rgb_string = " ".join(map(str, rgb_array))
    params['ramp'] = "color[] " + rgb_string

    # Additional params.
    color_input = list(shader.inputs[1].default_value)
    params['ColorIn'] = f"color {color_input[0]} {color_input[1]} {color_input[2]}"
    params['Fac'] = f"float {shader.inputs[0].default_value}"

    return params, outputs


def parse_ShaderNodeValToRGB(shader):
    params = dict()
    outputs = ["Color", "Alpha"]

    # Interpret color ramp.
    ramp = shader.color_ramp
    ramp_interpolate = ramp.interpolation != 'CONSTANT'
    rgb_array, alpha_array = ramp_to_array(ramp)

    rgb_string = " ".join(map(str, rgb_array))
    params['ramp_color'] = "color[] " + rgb_string

    alpha_string = " ".join(map(str, alpha_array))
    params['ramp_alpha'] = "float[] " + alpha_string

    # Additional params.
    params['interpolate'] = f"int {int(ramp_interpolate)}"
    params['Fac'] = f"float {shader.inputs[0].default_value}"

    return params, outputs


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
        rgb_floats[start_index] = mapping.evaluate(
            map_r, mapping.evaluate(map_i, t))
        rgb_floats[start_index +
                   1] = mapping.evaluate(map_g, mapping.evaluate(map_i, t))
        rgb_floats[start_index +
                   2] = mapping.evaluate(map_b, mapping.evaluate(map_i, t))

    return rgb_floats


def ramp_to_array(ramp):
    curve_resolution = bpy.context.preferences.addons['blenderseed'].preferences.curve_resolution
    rgb_array = np.empty(curve_resolution * 3, dtype=float)
    alpha_array = np.empty(curve_resolution, dtype=float)

    for i in range(curve_resolution):
        rgb_starting_index = i * 3

        color = ramp.evaluate(i / (curve_resolution - 1))

        rgb_array[rgb_starting_index] = color[0]
        rgb_array[rgb_starting_index + 1] = color[1]
        rgb_array[rgb_starting_index + 2] = color[2]
        alpha_array[i] = color[3]

    return rgb_array, alpha_array
