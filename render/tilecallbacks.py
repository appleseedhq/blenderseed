#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2018 Esteban Tovagliari, The appleseedhq Organization.
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

import time
from math import ceil

import appleseed as asr
from ..utils import util
from ..logger import get_logger

logger = get_logger()


class FinalTileCallback(asr.ITileCallback):
    def __init__(self, engine, scene):
        super(FinalTileCallback, self).__init__()

        self.__engine = engine
        self.__scene = scene

        self.__pass_incremented = False
        self.__render_stats = ["Starting", ""]

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

        # Compute number of tiles.
        vertical_tiles = int(ceil((self.__max_y - self.__min_y + 1) / self.__scene.appleseed.tile_size))
        horizontal_tiles = int(ceil((self.__max_x - self.__min_x + 1) / self.__scene.appleseed.tile_size))
        self.__total_tiles = vertical_tiles * horizontal_tiles

        # Compute total pixel count.
        self.__total_passes = scene.appleseed.renderer_passes
        self.__total_pixels = (self.__max_x - self.__min_x + 1) * (self.__max_y - self.__min_y + 1) * self.__total_passes

        self.__time_start = time.time()

        self.__rendered_pixels = 0

        self.__pass_number = 1

        self.__rendered_tiles = 0

    @property
    def render_stats(self):
        return self.__render_stats

    def on_tiled_frame_begin(self, frame):
        self.__pass_incremented = False
        if self.__pass_number == 1:
            self.__render_stats = ["appleseed Rendering", "Time Remaining: Unknown"]

    def on_tiled_frame_end(self, frame):
        if not self.__pass_incremented:
            self.__pass_number += 1
            self.__pass_incremented = True
        self.__rendered_tiles = 0

    def on_tile_begin(self, frame, tile_x, tile_y):
        pass

    def on_tile_end(self, frame, tile_x, tile_y):
        """
        Processes the tile data as it finished
        """
        # logger.debug("Finished tile %s %s", tile_x, tile_y)

        image = frame.image()

        properties = image.properties()

        # These are the starting pixel locations for the tile
        x = tile_x * properties.m_tile_width
        y = tile_y * properties.m_tile_height

        tile = image.tile(tile_x, tile_y)

        # Same as tile size from render settings
        tile_w = tile.get_width()
        tile_h = tile.get_height()

        # Ignore tiles completely outside the render window.
        if x > self.__max_x or x + tile_w - 1 < self.__min_x:
            logger.debug("Skipping invisible tile")
            return True
        if y > self.__max_y or y + tile_h - 1 < self.__min_y:
            logger.debug("Skipping invisible tile")
            return True

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

        # Window-space coordinates of the intersection between the tile and the render window.
        x0 = ix0 - self.__min_x  # left
        y0 = self.__max_y - iy1  # bottom

        # Update image.
        result = self.__engine.begin_result(x0, y0, take_x, take_y)
        layer = result.layers[0].passes["Combined"]
        pix = self.__get_pixels(image, tile_x, tile_y, take_x, take_y, skip_x, skip_y)
        layer.rect = pix
        if len(frame.aovs()) > 0:
            self.__engine.update_result(result)
            for aov in frame.aovs():
                image = aov.get_image()
                pix = self.__get_pixels(image, tile_x, tile_y, take_x, take_y, skip_x, skip_y)
                layer = result.layers[0].passes[self.__map_aovs(aov.get_name())]
                layer.rect = pix
                self.__engine.update_result(result)
        self.__engine.end_result(result)

        # Update progress bar.
        self.__rendered_pixels += take_x * take_y
        self.__engine.update_progress(self.__rendered_pixels / self.__total_pixels)

        # Update stats.
        seconds_per_pixel = (time.time() - self.__time_start) / self.__rendered_pixels
        remaining_seconds = (self.__total_pixels - self.__rendered_pixels) * seconds_per_pixel
        self.__rendered_tiles += 1
        self.__render_stats = ["appleseed Rendering: Pass %i of %i, Tile %i of %i completed" % (self.__pass_number, self.__total_passes, self.__rendered_tiles, self.__total_tiles), "Time Remaining: {0}".format(self.__format_seconds_to_hhmmss(remaining_seconds))]

    def __get_pixels(self, image, tile_x, tile_y, take_x, take_y, skip_x, skip_y):
        tile = image.tile(tile_x, tile_y)
        tile_w = tile.get_width()
        tile_c = tile.get_channel_count()

        floats = tile.get_storage()

        pix = []
        for y in range(take_y - 1, -1, -1):
            start_pix = (skip_y + y) * tile_w + skip_x
            end_pix = start_pix + take_x
            pix.extend(floats[p * tile_c:p * tile_c + tile_c] for p in range(start_pix, end_pix))

        return pix

    @staticmethod
    def __format_seconds_to_hhmmss(seconds):
        hours = seconds // (60 * 60)
        seconds %= (60 * 60)
        minutes = seconds // 60
        seconds %= 60
        return "%02i:%02i:%02i" % (hours, minutes, seconds)

    @staticmethod
    def __map_aovs(aov_name):

        aov_mapping = {'beauty': "Combined",
                       'diffuse': "Diffuse",
                       'screen_space_velocity': "Screen Space Velocity",
                       'direct_diffuse': "Direct Diffuse",
                       'indirect_diffuse': "Indirect Diffuse",
                       'glossy': "Glossy",
                       'direct_glossy': "Direct Glossy",
                       'indirect_glossy': "Indirect Glossy",
                       'normal': "Normal",
                       'position': "Position",
                       'uv': "UV",
                       'pixel_time': "Pixel Time",
                       'depth': "Z Depth",
                       'emission': "Emission",
                       'albedo': "Albedo",
                       'invalid_samples': "Invalid Samples",
                       'pixel_sample_count': "Pixel Sample Count",
                       'pixel_variation': "Pixel Variation",
                       'npr_shading': "NPR Shading",
                       'npr_contour': "NPR Contour"}

        return aov_mapping[aov_name]
