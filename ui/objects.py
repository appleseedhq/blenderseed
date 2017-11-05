
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
import bl_ui


class AppleseedObjMBlurPanel(bpy.types.Panel):
    bl_label = "Motion Blur"
    COMPAT_ENGINES = {'APPLESEED_RENDER'}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER' and context.object is not None and context.object.type in {'MESH', 'CURVE', 'SURFACE'}

    def draw_header(self, context):
        header = self.layout
        asr_obj = context.object.appleseed
        header.prop(asr_obj, "mblur_enable")

    def draw(self, context):
        layout = self.layout
        asr_obj = context.object.appleseed
        layout.active = asr_obj.mblur_enable

        layout.prop(asr_obj, "mblur_type")


def register():
    import bl_ui.properties_object as properties_object
    for member in dir(properties_object):
        subclass = getattr(properties_object, member)
        try:
            subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
        except:
            pass
    del properties_object


def unregister():
    import bl_ui.properties_object as properties_object
    for member in dir(properties_object):
        subclass = getattr(properties_object, member)
        try:
            subclass.COMPAT_ENGINES.remove('APPLESEED_RENDER')
        except:
            pass
    del properties_object
