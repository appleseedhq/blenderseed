#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 The appleseedhq Organization
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

import appleseed as asr

from .assethandlers import AssetType
from .translator import Translator


class TextureTranslator(Translator):

    def __init__(self, bl_texture, color_space, asset_handler):
        super().__init__(bl_texture, asset_handler=asset_handler)

        self.__as_color_space = color_space
        self.__as_tex = None
        self.__as_tex_inst = None

    # Properties
    @property
    def bl_tex(self):
        return self._bl_obj

    def create_entities(self):
        filepath = self.asset_handler.process_path(self.bl_tex.filepath, AssetType.TEXTURE_ASSET)

        tex_params = {'filename': filepath,
                      'color_space': self.__as_color_space}
        self.__as_tex = asr.Texture('disk_texture_2d',
                                    self.appleseed_name,
                                    tex_params,
                                    [])

        tex_inst_params = {'addressing_mode': 'wrap',
                           'filtering_mode': 'bilinear'}
        self.__as_tex_inst = asr.TextureInstance(f"{self.appleseed_name}_inst",
                                                 tex_inst_params,
                                                 self.appleseed_name,
                                                 asr.Transformf(asr.Matrix4f.identity()))

    def flush_entities(self, as_assembly):
        tex_name = self.__as_tex.get_name()
        as_assembly.textures().insert(self.__as_tex)
        self.__as_tex = as_assembly.textures().get_by_name(tex_name)

        tex_inst_name = self.__as_tex_inst.get_name()
        as_assembly.texture_instances().insert(self.__as_tex_inst)
        self.__as_tex_inst = as_assembly.texture_instances().get_by_name(tex_inst_name)
