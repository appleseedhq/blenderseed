
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

from enum import Enum

from ..logger import get_logger
logger = get_logger()


class ProjectExportMode(Enum):
    FINAL_RENDER = 1
    INTERACTIVE_RENDER = 2
    PROJECT_EXPORT = 3


class ObjectKey(object):
    '''
    Class used to uniquely identify blender objects.
    '''

    def __init__(self, obj):
        self.__name = obj.name
        self.__library_name = None

        if obj.library:
            self.__library_name = obj.library.name

    def __hash__(self):
        return hash((self.__name, self.__library_name))

    def __eq__(self, other):
        return (self.__name, self.__library_name) == (other.__name, other.__library_name)

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        if self.__library_name:
            return self.__library_name + "|" + self.__name

        return self.__name


class Translator(object):
    """
    Base class for translators that convert Blender objects to appleseed Entities.
    """

    #
    # Constructor.
    #

    def __init__(self, obj, asset_handler):
        self._bl_obj = obj
        if self._bl_obj is not None:
            self._obj_key = ObjectKey(obj)
        self._asset_handler = asset_handler

    #
    # Properties.
    #

    @property
    def appleseed_name(self):
        return str(self._obj_key)

    @property
    def asset_handler(self):
        return self._asset_handler

    #
    # Entity translation.
    #

    def create_entities(self, scene):
        """todo: document me..."""

        raise NotImplementedError()

    def flush_entities(self, project, assembly):
        """todo: document me..."""

        raise NotImplementedError()

    #
    # Utility methods.
    #

    def _reset(self, obj):
        """
        This exists in order to reset the basic data on the translator when doing an interactive render update.
        This is necessary when the name of an object or material changes.
        """

        self._bl_obj = obj
        if self._bl_obj:
            self._obj_key = ObjectKey(obj)

    @staticmethod
    def _convert_matrix(m):
        """
        Converts a Blender matrix to an appleseed matrix

        We have the following conventions:

        Both Blender and appleseed use right-hand coordinate systems.
        Both Blender and appleseed use column-major matrices.
        Both Blender and appleseed use pre-multiplication.
        In Blender, given a matrix m, m[i][j] is the element at the i'th row, j'th column.

        The only difference between the coordinate systems of Blender and appleseed is the up vector:
        in Blender, up is Z+; in appleseed, up is Y+.  So we need to add a -90 degree rotation along the x
        axis to translate.
        """

        matrix = asr.Matrix4d([m[0][0], m[0][1], m[0][2], m[0][3],
                               m[1][0], m[1][1], m[1][2], m[1][3],
                               m[2][0], m[2][1], m[2][2], m[2][3],
                               m[3][0], m[3][1], m[3][2], m[3][3]])

        rotation_modify = asr.Matrix4d.make_rotation(asr.Vector3d(1.0, 0.0, 0.0), math.radians(-90.0))

        matrix = rotation_modify * matrix

        return asr.Transformd(matrix)

    @staticmethod
    def _convert_color(color):
        """Convert a Blender color to a Python list."""

        return [color[0], color[1], color[2]]

    @staticmethod
    def _insert_entity_with_unique_name(container, entity, name):
        """
        Insert an appleseed entity into a container with an unique name.
        Returns the new entity name.
        """

        if container.get_by_name(name) == None:
            entity.set_name(name)
            container.insert(entity)
            return name

        i = 2
        fmt = name + "_%d"

        while True:
            new_name = fmt % i
            i += 1

            if container.get_by_name(new_name) == None:
                entity.set_name(new_name)
                container.insert(entity)
                return new_name
