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
from ...logger import get_logger

logger = get_logger()


class ArchiveAssemblyTranslator(Translator):

    def __init__(self, archive_obj, asset_handler):
        super().__init__(archive_obj, asset_handler=asset_handler)

        self.__instances = {}

        self.__ass = None

    @property
    def instances(self):
        return self.__instances

    def create_entities(self, bl_scene):
        ass_name = f"{self.appleseed_name}_ass"

        file_path = self.asset_handler.process_path(self._bl_obj.appleseed.archive_path, AssetType.ARCHIVE_ASSET)

        ass_options = {'filename': file_path}

        self.__ass = asr.Assembly("archive_assembly", ass_name, ass_options)

    def flush_entities(self, as_assembly, as_project):
        for instance in self.__instances.values():
            instance.optimize()

        ass_name = f"{self.appleseed_name}_ass"

        as_assembly.assemblies().insert(self.__ass)
        self.__ass = as_assembly.assemblies().get_by_name(ass_name)

        for key, transform_matrix in self.__instances.items():
            ass_inst_name = f"{key}_ass_inst"
            ass_inst = asr.AssemblyInstance(ass_inst_name,
                                            {},
                                            ass_name)
            ass_inst.set_transform_sequence(transform_matrix)
            as_assembly.assembly_instances().insert(ass_inst)
            self.__instances[key] = as_assembly.assembly_instances().get_by_name(ass_inst_name)

    def set_xform_step(self, time, inst_key, bl_matrix):
        self.__instances[inst_key].set_transform(time, self._convert_matrix(bl_matrix))

    def delete_instances(self, as_assembly, as_scene):
        for ass_inst in self.__instances.values():
            as_assembly.assembly_instances().remove(ass_inst)

        self.__instances.clear()

    def xform_update(self, inst_key, bl_matrix, as_assembly, as_scene):
        xform_seq = asr.TransformSequence()
        xform_seq.set_transform(0.0, self._convert_matrix(bl_matrix))
        ass_name = f"{self.appleseed_name}_ass"
        ass_inst_name = f"{inst_key}_ass_inst"
        ass_inst = asr.AssemblyInstance(ass_inst_name,
                                        {},
                                        ass_name)
        ass_inst.set_transform_sequence(xform_seq)
        as_assembly.assembly_instances().insert(ass_inst)
        self.__instances[inst_key] = as_assembly.assembly_instances().get_by_name(ass_inst_name)

    def delete_object(self, as_assembly):
        for ass_inst in self.__instances.values():
            as_assembly.assembly_instances().remove(ass_inst)

    def add_instance(self, inst_key):
        self.__instances[inst_key] = asr.TransformSequence()

    def set_deform_key(self, time, depsgraph, all_times):
        pass
