
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

class AppleseedRenderLayers( bpy.types.PropertyGroup):
    pass

class AppleseedRenderLayerProps( bpy.types.PropertyGroup):
    layers = bpy.props.CollectionProperty( type = AppleseedRenderLayers, 
                                           name = "Appleseed Render Layers", 
                                           description = "")

    layer_index = bpy.props.IntProperty( name = "Layer Index", 
                                         description = "", 
                                         default = 0, 
                                         min = 0, 
                                         max = 32)

def register():
    bpy.utils.register_class( AppleseedRenderLayers)
    bpy.utils.register_class( AppleseedRenderLayerProps)

def unregister():
    bpy.utils.unregister_class( AppleseedRenderLayers)
    bpy.utils.unregister_class( AppleseedRenderLayerProps)
