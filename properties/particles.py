
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

import bpy
from ..utils import util


class AppleseedPsysProps(bpy.types.PropertyGroup):
    shape = bpy.props.EnumProperty(name="shape",
                                   description="Strand shape to use for rendering",
                                   items=[('thick', 'Thick', 'Use thick strands for rendering'),
                                          ('ribbon', 'Ribbon', 'Use ribbon strands for rendering - ignore thickness of strand')],
                                   default='thick')

    resolution = bpy.props.IntProperty(name="resolution",
                                       description="Cylindrical resolution of strand. Default of 0 should be sufficient in the majority of cases. Higher values require longer export times",
                                       default=0,
                                       min=0,
                                       max=2)

    root_size = bpy.props.FloatProperty(name="root",
                                        description="Thickness of strand root",
                                        default=1.0,
                                        min=0.0,
                                        max=100)

    tip_size = bpy.props.FloatProperty(name="tip",
                                       description="Thickness of strand tip",
                                       default=0.0,
                                       min=0.0,
                                       max=100)

    scaling = bpy.props.FloatProperty(name="scaling",
                                      description="Multiplier of width properties",
                                      default=0.01,
                                      min=0.0,
                                      max=1000)


def register():
    util.safe_register_class(AppleseedPsysProps)
    bpy.types.ParticleSettings.appleseed = bpy.props.PointerProperty(type=AppleseedPsysProps)


def unregister():
    del bpy.types.ParticleSettings.appleseed
    util.safe_unregister_class(AppleseedPsysProps)
