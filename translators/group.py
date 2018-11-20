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
from .dupli import DupliTranslator
from .lamps import LampTranslator, AreaLampTranslator
from .materials import MaterialTranslator
from .mesh import MeshTranslator
from .object import ProjectExportMode, InstanceTranslator, ArchiveTranslator
from .translator import Translator, ObjectKey
from ..logger import get_logger
from ..util import inscenelayer

logger = get_logger()


class GroupTranslator(Translator):

    #
    # Constants and settings.
    #

    OBJECT_TYPES_TO_IGNORE = {'ARMATURE', 'CAMERA'}
    MESH_OBJECTS = {'MESH'}

    #
    # Constructor.
    #

    def __init__(self, group, export_mode, selected_only, asset_handler):
        super(GroupTranslator, self).__init__(group, asset_handler)

        self._export_mode = export_mode

        self._selected_only = selected_only

        # Translators.
        self._osl_translators = {}
        self._material_translators = {}

        self._lamp_translators = {}
        self._lamp_material_translators = {}
        self._object_translators = {}
        self._dupli_translators = {}

        # Map from datablocks to translators for instancing.
        self._datablock_to_translator = {}

    #
    # Properties.
    #

    @property
    def bl_group(self):
        return self._bl_obj

    @property
    def export_mode(self):
        return self._export_mode

    @property
    def selected_only(self):
        return self._selected_only

    @property
    def assembly_name(self):
        return self.appleseed_name + "_group"

    @property
    def all_translators(self):
        return [
            self._dupli_translators,
            self._material_translators,
            self._lamp_translators,
            self._lamp_material_translators,
            self._object_translators]

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        logger.debug("Creating assembly for group %s", self.bl_group.name)

        self.__assembly = asr.Assembly(self.assembly_name)

        self._create_translators(scene)
        self._do_create_entities(scene)

    def flush_entities(self, assembly):
        logger.debug("Flushing entities for group %s", self.bl_group.name)

        self._do_flush_entities(self.__assembly)

        assembly.assemblies().insert(self.__assembly)

    def set_transform_key(self, scene, time, key_times):
        for x in self._object_translators.values():
            x.set_transform_key(scene, time, key_times)

        for x in self._dupli_translators.values():
            x.set_transform_key(scene, time, key_times)

    def set_deform_key(self, scene, time, key_times):
        for x in self._object_translators.values():
            x.set_deform_key(scene, time, key_times)

        for x in self._dupli_translators.values():
            x.set_deform_key(scene, time, key_times)

    #
    # Internal methods.
    #

    def _create_translators(self, scene):
        logger.debug("Creating translators for group %s contents", self.bl_group.name)

        for obj in self.bl_group.objects:

            # Skip object types that are not renderable.
            if obj.type in GroupTranslator.OBJECT_TYPES_TO_IGNORE:
                logger.debug("Ignoring object %s of type %s", obj.name, obj.type)
                continue

            if self.export_mode != ProjectExportMode.INTERACTIVE_RENDER and obj.hide_render:
                logger.debug("skipping hidden object %s", obj.name)
                continue

            if self.export_mode == ProjectExportMode.INTERACTIVE_RENDER and obj.hide:
                logger.debug("skipping hidden object %s", obj.name)
                continue

            if not inscenelayer(obj, self.bl_group):
                logger.debug("skipping invisible object %s", obj.name)
                continue

            if self.selected_only and not obj.select:
                logger.debug("skipping non-selected object %s", obj.name)
                continue

            obj_key = ObjectKey(obj)

            if obj.type == 'LAMP':
                logger.debug("Creating lamp translator for object %s of type %s", obj_key, obj.data.type)

                if obj.data.type == 'AREA':
                    self._lamp_translators[obj_key] = AreaLampTranslator(obj, self.export_mode, self.asset_handler)
                else:
                    self._lamp_translators[obj_key] = LampTranslator(obj, self.asset_handler)
                if obj.data.appleseed.osl_node_tree is not None:
                    lamp = obj.data
                    lamp_key = ObjectKey(lamp)
                    translator = MaterialTranslator(lamp, self.asset_handler)
                    self._lamp_material_translators[lamp_key] = translator

            elif self.__is_dupli_source(obj):
                self.__create_material_translators(obj)

                # Sources of duplicated objects are not shown in renders.
                logger.debug("Skipping dupli-source object %s", obj_key)
                continue

            elif obj.type in GroupTranslator.MESH_OBJECTS:
                mesh_key = ObjectKey(obj.data)

                if obj.is_duplicator:
                    logger.debug("Creating dupli translator for object %s", obj_key)
                    self._dupli_translators[obj_key] = DupliTranslator(obj, self.export_mode, self.asset_handler)

                elif obj.appleseed.object_export != 'normal':
                    logger.debug("Creating archive translator for object %s", obj_key)
                    archive_path = obj.appleseed.archive_path
                    self._object_translators[obj_key] = ArchiveTranslator(obj, archive_path, self._asset_handler)
                else:
                    is_modified = obj.is_modified(scene, 'RENDER')

                    if is_modified == False and mesh_key in self._datablock_to_translator:
                        logger.debug("Creating instance translator for object %s, master obj: %s", obj_key, mesh_key)

                        master_translator = self._datablock_to_translator[mesh_key]
                        self._object_translators[obj_key] = InstanceTranslator(obj, master_translator, self.asset_handler)
                        master_translator.add_instance()
                    else:
                        logger.debug("Creating mesh translator for object %s", obj_key)

                        translator = MeshTranslator(obj, self.export_mode, self.asset_handler)
                        self._object_translators[obj_key] = translator

                        if not is_modified:
                            logger.debug("Saving translator for object %s in instance map", obj_key)
                            self._datablock_to_translator[mesh_key] = translator

                        self.__create_material_translators(obj)

            else:
                pass  # log here unknown object found...

    def _do_create_entities(self, scene):
        for t in self.all_translators:
            for x in t.values():
                x.create_entities(scene)

    def _do_flush_entities(self, assembly):
        for t in self.all_translators:
            for x in t.values():
                x.flush_entities(assembly)

    def __create_material_translators(self, obj):
        for slot in obj.material_slots:
            mat = slot.material
            mat_key = ObjectKey(mat)

            if mat_key not in self._material_translators:
                logger.debug("Creating material translator for material %s", mat_key)
                translator = MaterialTranslator(mat, self.asset_handler)
                self._material_translators[mat_key] = translator

    def __is_dupli_source(self, obj):
        '''
        Return True if any parent of the object is a duplicator.
        '''
        o = obj.parent

        while o != None:
            if o.is_duplicator:
                return True

            o = o.parent
