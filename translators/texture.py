
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
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

from .translator import Translator

import appleseed as asr
import os


class TextureTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, tex):
        super(TextureTranslator, self).__init__(tex)
        self.__tex_dir, self.__tex_name = os.path.split(tex.image.filepath)

    #
    # Properties.
    #

    @property
    def bl_tex(self):
        return self._bl_obj

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        color_space_mapping = {'sRGB': 'srgb',
                               'Linear': 'linear_rgb'}

        tex_params = {'filename': self.__tex_name, 'color_space': color_space_mapping[self.bl_tex.image.colorspace_settings.name]}
        self.__as_tex = asr.Texture("disk_texture_2d", self.bl_tex.name, tex_params, [self.__tex_dir])

        tex_inst_params = {'addressing_mode': "wrap", 'filtering_mode': "bilinear"}
        self.__as_tex_inst = asr.TextureInstance("{0}_inst".format(self.bl_tex.name), tex_inst_params, self.bl_tex.name, asr.Transformf(asr.Matrix4f.identity()))

    def flush_entities(self, assembly):
        assembly.textures().insert(self.__as_tex)
        assembly.texture_instances().insert(self.__as_tex_inst)

        # todo: move this somewhere else...
        '''
        paths = project.get_search_paths()
        if self.__tex_dir not in paths:
            paths.append(self.__tex_dir)
        project.set_search_paths(paths)
        '''
