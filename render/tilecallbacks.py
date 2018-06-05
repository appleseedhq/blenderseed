
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2018 Esteban Tovagliari.
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

import bpy

import appleseed as asr

class FinalTileCallback(asr.ITileCallback):
    def __init__(self, engine):
        super(FinalTileCallback, self).__init__()
        self.__engine = engine

    def on_tile_end(self, frame, tile_x, tile_y):
        properties = frame.image().properties()

        tile = frame.image().tile(tile_x, tile_y)
        x = tile_x * properties.tile_width
        y = tile_y * properties.tile_height

        # blender image coord system is Y up
        y = properties.canvas_height - y - properties.tile_height

        # Here we write the pixel values to the RenderResult
        result = self.__engine.begin_result(x, y, tile.get_width(), tile.get_height())
        layer = result.layers[0]
        layer.passes[0].rect = tile.blender_tile_data()
        self.__engine.end_result(result)
