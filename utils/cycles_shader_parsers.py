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

from .util import mapping_to_array


def parse_cycles_shader(shader):

    if shader.bl_idname == "ShaderNodeRGBCurve":
        return parse_ShaderNodeRGBCurve(shader)

def parse_ShaderNodeRGBCurve(shader):
    params = dict()
    outputs = ["ColorOut"]

    # Color input.
    color_input = list(shader.inputs[1].default_value)
    params['ColorIn'] = f"color {color_input[0]} {color_input[1]} {color_input[2]}"

    # Fac input.
    params['Fac'] = f"float {shader.inputs[0].default_value}"

    # Curve mapping.
    mapping = shader.mapping
    mapping.update()
    float_array = mapping_to_array(mapping)
    float_string = " ".join(map(str, float_array))
    value_string = f"color[] {float_string}"
    params['ramp'] = value_string

    return params, outputs
