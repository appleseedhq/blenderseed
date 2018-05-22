
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

from enum import Enum


class ProjectExportMode(Enum):
    FINAL_RENDER = 1
    INTERACTIVE_RENDER = 2
    PROJECT_EXPORT = 3


class Translator(object):
    """
    Base class for translators that convert Blender objects to appleseed Entities.
    """

    def create_entities(self):

        raise NotImplementedError()

    def flush_entities(self, project):

        raise NotImplementedError()

    def _convert_matrix(self, m, area=False):
        """
        Converts a Blender matrix to an appleseed matrix

         We have the following conventions:

           Both Blender and appleseed use right-hand coordinate systems.
           Both Blender and appleseed use column-major matrices.
           Both Blender and appleseed use pre-multiplication.
           In Blender, given a matrix m, m[i][j] is the element at the i'th row, j'th column.

         The only difference between the coordinate systems of Blender and appleseed is the up vector:
         in Blender, up is Z+; in appleseed, up is Y+. We can go from Blender's coordinate system to
         appleseed's one by rotating by +90 degrees around the X axis. That means that Blender
         objects must be rotated by -90 degrees around X before being exported to appleseed.
        """

        rot = mathutils.Matrix.Rotation(math.radians(-90), 4, 'X')

        if area:
            m = rot * m * rot
        else:
            m = rot * m

        matrix = asr.Matrix4d([m[0][0], m[0][1], m[0][2], m[0][3],
                               m[1][0], m[1][1], m[1][2], m[1][3],
                               m[2][0], m[2][1], m[2][2], m[2][3],
                               m[3][0], m[3][1], m[3][2], m[3][3]])

        return asr.Transformd(matrix)

    @staticmethod
    def _convert_color(color):

        return [color[0], color[1], color[2]]
