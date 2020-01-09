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
from ..assethandlers import AssetType
from ..translator import Translator
from ...logger import get_logger

logger = get_logger()


class ArchiveAssemblyTranslator(Translator):
    def __init__(self, archive_obj, asset_handler):
        super().__init__(archive_obj, asset_handler)

        self.__instance_lib = asr.BlTransformLibrary()

        self.__ass_name = None

        self._bl_obj.appleseed.obj_name = self._bl_obj.name_full

    @property
    def orig_name(self):
        return self._bl_obj.appleseed.obj_name

    @property
    def instances_size(self):
        return self.__instance_lib.get_size()

    def add_instance_step(self, time, instance_id, bl_matrix):
        self.__instance_lib.add_xform_step(time, instance_id, self._convert_matrix(bl_matrix))

    def set_deform_key(self, time, depsgraph, index):
        pass

    def create_entities(self, bl_scene, context=None):
        self.__ass_name = f"{self.orig_name}_ass"

        file_path = self._asset_handler.process_path(self._bl_obj.appleseed.archive_path,
                                                    AssetType.ARCHIVE_ASSET)

        ass_options = {'filename': file_path}

        self.__ass = asr.Assembly("archive_assembly", self.__ass_name, ass_options)

    def flush_entities(self, as_scene, as_main_assembly, as_project):
        as_main_assembly.assemblies().insert(self.__ass)
        self.__ass = as_main_assembly.assemblies().get_by_name(self.__ass_name)

        self.flush_instances(as_main_assembly)

    def flush_instances(self, as_main_assembly):
        self.__instance_lib.flush_instances(as_main_assembly, self.__ass_name)

    def update_archive_ass(self, depsgraph):
        file_path = self._asset_handler.process_path(self._bl_obj.appleseed.archive_path,
                                                    AssetType.ARCHIVE_ASSET)

        ass_options = {'filename': file_path}

        self.__ass.set_parameters(ass_options)

    def clear_instances(self, as_main_assembly):
        self.__instance_lib.clear_instances(as_main_assembly)

    def delete_object(self, as_main_assembly):
        self.clear_instances(as_main_assembly)

        as_main_assembly.assemblies().remove(self.__ass)

        self.__ass = None
