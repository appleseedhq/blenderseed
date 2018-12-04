
#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2018 Jonathan Dent, The appleseedhq Organization
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


class AppleseedTextureContext(bpy.types.Panel):
    bl_context = "texture"
    bl_label = "Texture Context"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_options = {'HIDE_HEADER'}
    COMPAT_ENGINES = {'APPLESEED_RENDER'}

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        return (context.material or context.object) and engine == 'APPLESEED_RENDER'

    def draw(self, context):
        layout = self.layout
        tex = context.texture
        space = context.space_data
        pin_id = space.pin_id
        use_pin_id = space.use_pin_id
        user = context.texture_user

        space.use_limited_texture_context = False

        if not (use_pin_id and isinstance(pin_id, bpy.types.Texture)):
            pin_id = None

        if not pin_id:
            layout.template_texture_user()

        if user or pin_id:
            layout.separator()

            split = layout.split(percentage=0.65)
            col = split.column()

            if pin_id:
                col.template_ID(space, "pin_id")
            else:
                propname = context.texture_user_property.identifier
                col.template_ID(user, propname, new="texture.new")

            if tex:
                split = layout.split(percentage=0.2)
                split.label(text="Type:")
                split.prop(tex, "type", text="")


def register():
    util.safe_register_class(AppleseedTextureContext)


def unregister():
    util.safe_unregister_class(AppleseedTextureContext)
