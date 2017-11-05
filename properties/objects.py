
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


class AppleseedObjSettings(bpy.types.PropertyGroup):

    @classmethod
    def register(cls):
        bpy.types.Object.appleseed = bpy.props.PointerProperty(
            name="appleseed Object Settings",
            description="appleseed object settings",
            type=cls)

        cls.mblur_enable = bpy.props.BoolProperty(name="",
                                                  description="Enable rendering of motion blur",
                                                  default=False)

        cls.mblur_type = bpy.props.EnumProperty(name="Type",
                                                items=[('object', 'Object', 'Object motion blur'),
                                                       ('deformation', 'Deformation', 'Deformation motion blur. Warning - this will increase export time')],
                                                description="Type of motion blur to render",
                                                default='object')

    @classmethod
    def unregister(cls):
        del bpy.types.Object.appleseed


def register():
    pass


def unregister():
    pass
