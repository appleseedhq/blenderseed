#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 Jonathan Dent, The appleseedhq Organization
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

import appleseed as asr

from .assethandlers import AssetType
from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class TextureTranslator(Translator):
    """
    Stores the parameters and appleseed entities needed to hold a texture from Blender's internal texture system for rendering.
    OSL shaders do not store anything here
    """

    def __init__(self, bl_texture, asset_handler=None):
        logger.debug(f"appleseed: Creating texture translator for {bl_texture.name_full}")
        super().__init__(bl_texture, asset_handler)

        self.__as_tex = None
        self.__as_tex_inst = None

        self.__as_tex_params = None
        self.__as_tex_inst_params = None

        self._bl_obj.appleseed.obj_name = self._bl_obj.name_full

    @property
    def bl_tex(self):
        return self._bl_obj

    @property
    def orig_name(self):
        return self._bl_obj.appleseed.obj_name

    def create_entities(self, depsgraph):
        logger.debug(f"appleseed: Creating texture entity for {self.orig_name}")
        self.__as_tex_params = self.__get_tex_params()
        self.__as_tex = asr.Texture('disk_texture_2d', self.orig_name, self.__as_tex_params, [])

        self.__as_tex_inst_params = self.__get_tex_inst_params()

        self.__as_tex_inst = asr.TextureInstance(f"{self.orig_name}_inst",
                                                 self.__as_tex_inst_params,
                                                 self.obj_name,
                                                 asr.Transformf(asr.Matrix4f.identity()))

    def flush_entities(self, as_scene, as_main_assembly, as_project):
        logger.debug(f"appleseed: Flushing texture entity for {self.orig_name} to project")
        scene = as_project.get_scene()
        tex_name = self.__as_tex.get_name()
        scene.textures().insert(self.__as_tex)
        self.__as_tex = scene.textures().get_by_name(tex_name)

        tex_inst_name = self.__as_tex_inst.get_name()
        scene.texture_instances().insert(self.__as_tex_inst)
        self.__as_tex_inst = scene.texture_instances().get_by_name(tex_inst_name)

    def __get_tex_params(self):
        as_tex_params = self.bl_tex.appleseed
        filepath = self._asset_handler.process_path(self.bl_tex.filepath, AssetType.TEXTURE_ASSET)
        tex_params = {'filename': filepath, 'color_space': as_tex_params.as_color_space}

        return tex_params

    def __get_tex_inst_params(self):
        as_tex_params = self.bl_tex.appleseed
        tex_inst_params = {'addressing_mode': as_tex_params.as_wrap_mode,
                           'filtering_mode': 'bilinear',
                           'alpha_mode': as_tex_params.as_alpha_mode}

        return tex_inst_params
