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

from .translator import Translator
from ..logger import get_logger

logger = get_logger()


class ObjectTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, obj):
        super(ObjectTranslator, self).__init__(obj)

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

    def set_transform_key(self, time, key_times):
        self._xform_seq.set_transform(time, self._convert_matrix(self.bl_obj.matrix_world))

    def set_deform_key(self, scene, time, key_times):
        pass


class InstanceTranslator(ObjectTranslator):

    #
    # Constructor.
    #

    def __init__(self, obj, master_translator):
        super(InstanceTranslator, self).__init__(obj)
        self.__master = master_translator

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        self._xform_seq.set_transform(0.0, self._convert_matrix(self.bl_obj.matrix_world))

    def flush_entities(self, assembly):
        logger.debug("Creating assembly instance for object %s", self.appleseed_name)

        self._xform_seq.optimize()

        assembly_instance_name = self.appleseed_name + "_ass_inst"

        self.__ass_inst = asr.AssemblyInstance(
            assembly_instance_name,
            {},
            self.__master.assembly_name)

        self.__ass_inst.set_transform_sequence(self._xform_seq)
        ass_name = self.__ass_inst.get_name()
        assembly.assembly_instances().insert(self.__ass_inst)
        self.__ass_inst = assembly.assembly_instances().get_by_name(ass_name)

    def update(self, obj):
        self.__ass_inst.transform_sequence().set_transform(0.0, self._convert_matrix(obj.matrix_world))
