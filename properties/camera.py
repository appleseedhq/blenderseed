
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2013 Franz Beaune, Joel Daniels, Esteban Tovagliari.
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

def get_shutter_min(self, context):
    return context.scene.camera.appleseed.shutter_open

def get_shutter_max(self, context):
    return context.scene.camera.appleseed.shutter_close

class AppleseedCameraSettings( bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        bpy.types.Camera.appleseed = bpy.props.PointerProperty(
                name = "Appleseed Camera Settings",
                description = "Appleseed camera settings",
                type = cls)

        cls.camera_type = bpy.props.EnumProperty( items = [('pinhole', 'Pinhole', 'Pinhole camera - no DoF'),
                                                           ('thinlens', 'Thin lens', 'Thin lens - enables DoF')],
                                            name = "Camera type",
                                            description = "Camera lens model",
                                            default = 'pinhole')
                                            
        cls.camera_dof = bpy.props.FloatProperty( name = "F-stop", 
                                            description = "Thin lens camera f-stop value", 
                                            default = 32.0, 
                                            min = 0.0, 
                                            max = 32.0, 
                                            step = 3, 
                                            precision = 1)

    @classmethod
    def unregister( cls):
        del bpy.types.Camera.appleseed

def register():
    pass

def unregister():
    pass
