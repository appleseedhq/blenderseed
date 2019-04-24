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

import appleseed as asr

from ..translator import Translator


class ObjectInstanceTranslator(Translator):
    def __init__(self, inst_key, source_key):
        self.__inst_key = inst_key
        self.__source_key = source_key

        self.__ass_inst = None

        self.__xform_seq = asr.TransformSequence()

    @property
    def xform_seq(self):
        return self.__xform_seq

    def create_entities(self, bl_scene):
        ass_name = f"{self.__source_key}_ass"
        ass_inst_name = f"{self.__inst_key}_ass_inst"
        self.__ass_inst = asr.AssemblyInstance(ass_inst_name,
                                               {},
                                               ass_name)

    def set_xform_step(self, time, bl_matrix):
        self.__xform_seq.set_transform(time, self._convert_matrix(bl_matrix))

    def flush_entities(self, as_assembly):
        self.__ass_inst.set_transform_sequence(self.__xform_seq)

        ass_inst_name = self.__ass_inst.get_name()
        as_assembly.assembly_instances().insert(self.__ass_inst)
        self.__ass_inst = as_assembly.assembly_instances().get_by_name(ass_inst_name)
