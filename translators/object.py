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

import appleseed as asr
import math
import mathutils
import os

from .assethandlers import AssetType
from .translator import Translator, ProjectExportMode, ObjectKey
from ..logger import get_logger

logger = get_logger()


class ObjectTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, obj, asset_handler):
        super(ObjectTranslator, self).__init__(obj, asset_handler)

        self._xform_seq = asr.TransformSequence()
        self._num_instances = 1

    #
    # Properties.
    #

    @property
    def bl_obj(self):
        return self._bl_obj

    @property
    def assembly_name(self):
        return self.appleseed_name + "_ass"

    #
    # Instancing.
    #

    def add_instance(self):
        self._num_instances += 1

    #
    # Entity translation.
    #

    def set_transform_key(self, scene, time, key_times):
        self._xform_seq.set_transform(time, self._convert_matrix(self.bl_obj.matrix_world))

    def set_transform(self, time, matrix):
        self._xform_seq.set_transform(time, self._convert_matrix(matrix))

    def set_deform_key(self, scene, time, key_times):
        pass

    def update(self, obj):
        self.update_transform(0.0, obj.matrix_world)

class InstanceTranslator(ObjectTranslator):

    #
    # Constructor.
    #

    def __init__(self, obj, master_translator, asset_handler):
        super(InstanceTranslator, self).__init__(obj, asset_handler)
        self.__master = master_translator

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        pass

    def flush_entities(self, assembly):
        logger.debug("Creating assembly instance for object %s", self.appleseed_name)

        assembly_instance_name = self.appleseed_name + "_ass_inst"
        self.__ass_inst = asr.AssemblyInstance(assembly_instance_name, {}, self.__master.assembly_name)

        self._xform_seq.optimize()
        self.__ass_inst.set_transform_sequence(self._xform_seq)

        assembly_instance_name = self._insert_entity_with_unique_name(
            assembly.assembly_instances(),
            self.__ass_inst,
            self.__ass_inst.get_name())

        self.__ass_inst = assembly.assembly_instances().get_by_name(assembly_instance_name)

    def update_transform(self, time, matrix):
        self.__ass_inst.transform_sequence().set_transform(time, self._convert_matrix(matrix))

    def _convert_matrix(self, m):
        if self.bl_obj.is_duplicator and self.bl_obj.dupli_type == 'GROUP':
            rot_comp = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
            m = m * rot_comp
        return super(InstanceTranslator, self)._convert_matrix(m)


class ArchiveTranslator(ObjectTranslator):

    #
    # Constructor.
    #

    def __init__(self, obj, archive_path, asset_handler):
        super(ArchiveTranslator, self).__init__(obj, asset_handler)

        self.__archive_path = archive_path

    #
    # Properties.
    #

    @property
    def bl_obj(self):
        return self._bl_obj

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        self._xform_seq.set_transform(0.0, self._convert_matrix(self.bl_obj.matrix_world))

    def flush_entities(self, assembly):
        assembly_name = self.appleseed_name + "_ass"
        file_path = self.asset_handler.process_path(self.__archive_path, AssetType.ARCHIVE_ASSET)

        params = {'filename': file_path}

        self.__ass = asr.Assembly("archive_assembly", assembly_name, params)

        ass_inst_name = self.appleseed_name + "_ass_inst"
        self.__ass_inst = asr.AssemblyInstance(ass_inst_name, {}, assembly_name)
        self.__ass_inst.set_transform_sequence(self._xform_seq)

        assembly.assemblies().insert(self.__ass)
        assembly.assembly_instances().insert(self.__ass_inst)

    def update_transform(self, time, matrix):
        self.__ass_inst.transform_sequence().set_transform(time, self._convert_matrix(matrix))

    def _convert_matrix(self, m):
        # undo export rotation
        rotation = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
        m = rotation * m
        return super(ArchiveTranslator, self)._convert_matrix(m)
