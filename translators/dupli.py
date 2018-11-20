
#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2018 The appleseedhq Organization
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

import bpy
from mathutils import Matrix

import appleseed as asr
from .assethandlers import AssetType
from .mesh import MeshTranslator
from .object import InstanceTranslator, ObjectKey
from .translator import Translator, ProjectExportMode
from ..logger import get_logger

logger = get_logger()


class DupliListBuilder(object):
    '''
    Helper class to make sure that the dupli list is cleared,
    even in the presence of exceptions.
    '''

    def __init__(self, obj, scene, settings):
        self.__obj = obj
        self.__scene = scene
        self.__settings = settings

    def __enter__(self):
        self.__obj.dupli_list_create(self.__scene, self.__settings)

    def __exit__(self, type, value, traceback):
        self.__obj.dupli_list_clear()


class DupliTranslator(Translator):

    #
    # Constructor.
    #

    def __init__(self, dupli, export_mode, asset_handler):
        super(DupliTranslator, self).__init__(dupli, asset_handler)

        self.__export_mode = export_mode
        self.__settings = 'VIEWPORT' if self.__export_mode == ProjectExportMode.INTERACTIVE_RENDER else 'RENDER'

        self.__object_translators = []
        self.__datablock_to_translator = {}

    #
    # Properties.
    #

    @property
    def bl_dupli(self):
        return self._bl_obj

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        logger.debug("Creating dupli assembly for dupli: %s" % self.appleseed_name)

        self.__ass = asr.Assembly(self.appleseed_name, {})
        self.__create_dupli_instances(self._bl_obj, scene, self.__settings)

    def flush_entities(self, assembly):
        logger.debug("Flushing dupli entities for dupli: %s" % self.bl_dupli.name)

        for translator in self.__object_translators:
            translator.flush_entities(self.__ass)

        ass_name = self._insert_entity_with_unique_name(
            assembly.assemblies(),
            self.__ass,
            self.__ass.get_name())
        self.__ass = assembly.assemblies().get_by_name(ass_name)

        self.__ass_inst = asr.AssemblyInstance(ass_name + "_inst", {}, ass_name)
        ass_inst_name = self._insert_entity_with_unique_name(
            assembly.assembly_instances(),
            self.__ass_inst,
            self.__ass_inst.get_name())

    def set_transform_key(self, scene, time, key_times):
        self.__set_instance_transforms(self.bl_dupli, scene, time)

    def set_deform_key(self, scene, time, key_times):
        self.__set_instance_transforms(self.bl_dupli, scene, time)

    def update(self, obj, scene):
        if obj.is_updated_data:
            logger.debug("Updating dupli instances")

            # Recreate all the instances.
            self.__clear_dupli_instances()
            self.__create_dupli_instances(obj, scene, self.__settings)

            current_frame = scene.frame_current + scene.frame_subframe
            self.__set_instance_transforms(obj, scene, current_frame)

            for translator in self.__object_translators:
                translator.flush_entities(self.__ass)
        else:
            logger.debug("Updating dupli xforms")

            # Update the transform of all the instances.
            self.__update_instance_transforms(obj, scene, 0.0)

    #
    # Internal methods.
    #

    def __create_dupli_instances(self, obj, scene, settings):
        with DupliListBuilder(obj, scene, settings):
            for dupli in obj.dupli_list:
                # Create translators for dupli instances.
                if dupli.object.type == 'MESH':
                    obj_key = ObjectKey (dupli.object)
                    mesh_key = ObjectKey(dupli.object.data)

                    is_modified = dupli.object.is_modified(scene, 'RENDER')

                    if is_modified == False and mesh_key in self.__datablock_to_translator:
                        logger.debug("Creating instance translator for object %s, master obj: %s", obj_key, mesh_key)

                        master_translator = self.__datablock_to_translator[mesh_key]
                        self.__object_translators.append(InstanceTranslator(dupli.object, master_translator, self.asset_handler))
                        master_translator.add_instance()
                    else:
                        logger.debug("Creating mesh translator for object %s", obj_key)

                        translator = MeshTranslator(dupli.object,
                                                    self.__export_mode,
                                                    self.asset_handler)

                        self.__object_translators.append(translator)

                        if not is_modified:
                            logger.debug("Saving translator for object %s in instance map", obj_key)
                            self.__datablock_to_translator[mesh_key] = translator
                else:
                    logger.debug("Skipping unsupported dupli source object of type %s", dupli.object.type)

            # Create dupli instances entities.
            for translator in self.__object_translators:
                translator.create_entities(scene)

            current_frame = scene.frame_current + scene.frame_subframe
            for translator in self.__object_translators:
                translator.set_deform_key(scene, current_frame, {current_frame})

    def __set_instance_transforms(self, obj, scene, time):
        with DupliListBuilder(obj, scene, self.__settings):
            for i, mesh in enumerate(self.__object_translators):
                mesh.set_transform(time, obj.dupli_list[i].matrix)

    def __update_instance_transforms(self, obj, scene, time):
        with DupliListBuilder(obj, scene, self.__settings):
            for i, mesh in enumerate(self.__object_translators):
                mesh.update_transform(time, obj.dupli_list[i].matrix)

    def __clear_dupli_instances(self):
        self.__ass.clear()

        self.__datablock_to_translator = {}
        self.__object_translators = []
