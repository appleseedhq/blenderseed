
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

from .. import util
from ..logger import get_logger

logger = get_logger()

class FinalTileCallback(asr.ITileCallback):
    def __init__(self, engine, scene):
        super(FinalTileCallback, self).__init__()

        self.__engine = engine
        self.__scene = scene

    def on_tiled_frame_begin(self, frame):
        # Compute render resolution.
        (width, height) = util.get_render_resolution(self.__scene)

        # Compute render window.
        if self.__scene.render.use_border:
            self.__min_x = int(self.__scene.render.border_min_x * width)
            self.__min_y = height - int(self.__scene.render.border_max_y * height)
            self.__max_x = int(self.__scene.render.border_max_x * width) - 1
            self.__max_y = height - int(self.__scene.render.border_min_y * height) - 1
        else:
            self.__min_x = 0
            self.__min_y = 0
            self.__max_x = width - 1
            self.__max_y = height - 1

        pass

    def on_tiled_frame_end(self, frame):
        pass

    def on_tile_begin(self, frame, tile_x, tile_y):
        pass

    def on_tile_end(self, frame, tile_x, tile_y):
        logger.debug("Finished tile %s %s", tile_x, tile_y)

        image = frame.image()
        properties = image.properties()

        x = tile_x * properties.m_tile_width
        y = tile_y * properties.m_tile_height

        tile = image.tile(tile_x, tile_y)

        tile_w = tile.get_width()
        tile_h = tile.get_height()
        tile_c = tile.get_channel_count()

        # Ignore tiles completely outside the render window.
        if tile_x > self.__max_x or tile_x + tile_w - 1 < self.__min_x:
            logger.debug("Skipping invisible tile")
            return
        if tile_y > self.__max_y or tile_y + tile_h - 1 < self.__min_y:
            logger.debug("Skipping invisible tile")
            return

        # Image-space coordinates of the intersection between the tile and the render window.
        ix0 = max(x, self.__min_x)
        iy0 = max(y, self.__min_y)
        ix1 = min(x + tile_w - 1, self.__max_x)
        iy1 = min(y + tile_h - 1, self.__max_y)

        # Number of rows and columns to skip in the input tile.
        skip_x = ix0 - x
        skip_y = iy0 - y
        take_x = ix1 - ix0 + 1
        take_y = iy1 - iy0 + 1

        # Extract relevant tile data and convert them to the format expected by Blender.
        floats = tile.get_storage()

        pix = []
        for y in range(take_y - 1, -1, -1):
            start_pix = (skip_y + y) * tile_w + skip_x
            end_pix = start_pix + take_x
            pix.extend(floats[p * 4:p * 4 + 4] for p in range(start_pix, end_pix))

        # Window-space coordinates of the intersection between the tile and the render window.
        x0 = ix0 - self.__min_x  # left
        y0 = self.__max_y - iy1  # bottom

        # Update image.
        result = self.__engine.begin_result(x0, y0, take_x, take_y)
        layer = result.layers[0].passes[0]
        layer.rect = pix
        self.__engine.end_result(result)
