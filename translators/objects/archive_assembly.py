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

import math

import mathutils

import appleseed as asr

from ..translator import Translator
from ..assethandlers import AssetType


class ArchiveAssemblyTranslator(Translator):

    def __init__(self, archive_obj, asset_handler):
        super().__init__(archive_obj, asset_handler=asset_handler)

        self.__xform_seq = asr.TransformSequence()

        self.__as_ass = None
        self.__as_ass_inst = None

    def create_entities(self, bl_scene):
        ass_name = f"{self._bl_obj.name_full}_ass"
        ass_inst_name = f"{ass_name}_ass_inst"

        file_path = self.asset_handler.process_path(self._bl_obj.appleseed.archive_path, AssetType.ARCHIVE_ASSET)

        as_ass_params = {'filename': file_path}

        self.__as_ass = asr.Assembly("archive_assembly", ass_name, as_ass_params)

        self.__as_ass_inst = asr.AssemblyInstance(ass_inst_name,
                                                  {},
                                                  ass_name)

    def flush_entities(self, as_assembly, as_project):
        self.__xform_seq.optimize()

        self.__as_ass_inst.set_transform_sequence(self.__xform_seq)

        as_assembly.assemblies().insert(self.__as_ass)
        as_assembly.assembly_instances().insert(self.__as_ass_inst)

    def set_xform_step(self, time):
        self.__xform_seq.set_transform(time, self._convert_matrix(self._bl_obj.matrix_world))

    def set_deform_key(self, time, depsgraph, all_times):
        pass
