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

        for instance in self.__instances.values():
            instance.create_entities(bl_scene)

    def flush_entities(self, as_assembly, as_project):
        for instance in self.__instances.values():
            instance.xform_seq.optimize()

        ass_name = f"{self.appleseed_name}_ass"

        as_assembly.assemblies().insert(self.__ass)
        self.__ass = as_assembly.assemblies().get_by_name(ass_name)

        for instance in self.__instances.values():
            instance.flush_entities(as_assembly)

    def set_xform_step(self, time, inst_key, bl_matrix):
        self.__instances[inst_key].set_xform_step(time, bl_matrix)

    def add_instance(self, inst_key, instance):
        self.__instances[inst_key] = instance

    def set_deform_key(self, time, depsgraph, all_times):
        pass
