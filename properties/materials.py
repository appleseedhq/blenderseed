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

from .. import util


def refresh_preview(self, context):
    """
    Triggers a refresh of the material preview.
    """

    if hasattr(context, "material"):
        if context.material is not None:
            context.material.preview_render_type = context.material.preview_render_type

    if hasattr(context, "texture"):
        if context.texture is not None:
            context.texture.type = context.texture.type


class AppleseedMatProps(bpy.types.PropertyGroup):
    shader_lighting_samples = bpy.props.IntProperty(name="lighting_samples",
                                                    description="",
                                                    min=1,
                                                    soft_max=1000,
                                                    default=1,
                                                    update=refresh_preview)

    preview_quality = bpy.props.IntProperty(name="preview_quality",
                                            description="Number of samples used for preview rendering",
                                            default=3,
                                            min=1,
                                            max=16,
                                            update=refresh_preview)

    # Nodes
    osl_node_tree = bpy.props.PointerProperty(name="OSL Node Tree",
                                              type=bpy.types.NodeTree)


def register():
    util.safe_register_class(AppleseedMatProps)
    bpy.types.Material.appleseed = bpy.props.PointerProperty(type=AppleseedMatProps)


def unregister():
    del bpy.types.Material.appleseed
    util.safe_unregister_class(AppleseedMatProps)
