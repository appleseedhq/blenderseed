
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

from .translator import Translator, ObjectKey, ProjectExportMode

from .lamps import LampTranslator, AreaLampTranslator
from .materials import MaterialTranslator
from .object import InstanceTranslator
from .mesh import MeshTranslator
from ..util import inscenelayer

import appleseed as asr

from ..logger import get_logger
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

    def __init__(self, group, export_mode, geometry_dir, textures_dir):
        super(GroupTranslator, self).__init__(group)

        self._export_mode = export_mode

        self._geometry_dir = geometry_dir
        self._textures_dir = textures_dir

        # Translators.
        self._osl_translators = {}
        self._material_translators = {}

        self._lamp_translators = {}
        self._object_translators = {}

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
    def geometry_dir(self):
        return self._geometry_dir

    @property
    def textures_dir(self):
        return self._textures_dir

    @property
    def assembly_name(self):
        return self.appleseed_name + "_group"

    @property
    def all_translators(self):
        return [
            self._material_translators,
            self._lamp_translators,
            self._object_translators
        ]

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        logger.debug("Creating assembly for group %s", self.bl_group.name)

        self.__assembly = asr.Assembly(self.assembly_name)

        self._create_translators()
        self._do_create_entities(scene)

    def flush_entities(self, assembly):
        logger.debug("Flushing entities for group %s", self.bl_group.name)

        self._do_flush_entities(self.__assembly)

        assembly.assemblies().insert(self.__assembly)

    #
    # Internal methods.
    #

    def _create_translators(self):
        logger.debug("Creating translators for group %s contents", self.bl_group.name)

        for obj in self.bl_group.objects:

            # Skip object types that are not renderable.
            if obj.type in GroupTranslator.OBJECT_TYPES_TO_IGNORE:
                logger.debug("Ignoring object %s of type %s", obj.name, obj.type)
                continue

            if obj.hide_render:
                continue

            if not inscenelayer(obj, self.bl_group):
                logger.debug("skipping invisible object %s", obj.name)
                continue

            obj_key = ObjectKey(obj)

            if obj.type == 'LAMP':
                logger.debug("Creating lamp translator for object %s of type %s", obj_key, obj.data.type)

                if obj.data.type == 'AREA':
                    self._lamp_translators[obj_key] = AreaLampTranslator(obj, self.export_mode)
                else:
                    self._lamp_translators[obj_key] = LampTranslator(obj)
                if obj.data.appleseed.osl_node_tree is not None:
                    lamp = obj.data
                    lamp_key = ObjectKey(lamp)
                    translator = MaterialTranslator(lamp)
                    self._material_translators[lamp_key] = translator

            elif obj.type in GroupTranslator.MESH_OBJECTS:
                mesh = obj.data
                mesh_key = ObjectKey(mesh)

                if mesh_key in self._datablock_to_translator:
                    logger.debug("Creating instance translator for object %s, master obj: %s", obj_key, mesh_key)

                    master_translator = self._datablock_to_translator[mesh_key]
                    self._object_translators[obj_key] = InstanceTranslator(obj, master_translator)
                    master_translator.add_instance()
                else:
                    logger.debug("Creating mesh translator for object %s", obj_key)

                    translator = MeshTranslator(obj, self.export_mode, self.geometry_dir)
                    self._object_translators[obj_key] = translator
                    self._datablock_to_translator[mesh_key] = translator

                    self.__create_material_translators(obj)

                if obj.is_duplicator:
                    # todo: handle dupli - objects here...
                    pass

            else:
                pass # log here unknown object found...

    def _do_create_entities(self, scene):
        for t in self.all_translators:
            for x in t.values():
                x.create_entities(scene)

    def set_transform_key(self, time, key_times):
        for x in self._object_translators.values():
            x.set_transform_key(time, key_times)

    def set_deform_key(self, scene, time, key_times):
        for x in self._object_translators.values():
            x.set_deform_key(scene, time, key_times)

    def _do_flush_entities(self, assembly):
        for t in self.all_translators:
            for x in t.values():
                x.flush_entities(assembly)

    def __create_material_translators(self, obj):
        for slot in obj.material_slots:
            mat = slot.material
            mat_key = ObjectKey(mat)
            print(str(mat_key))

            if mat_key not in self._material_translators:
                translator = MaterialTranslator(mat)
                self._material_translators[mat_key] = translator
