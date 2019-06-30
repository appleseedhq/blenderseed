#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 Jonathan Dent, The appleseedhq Organization
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

import os
import shutil
from enum import Enum

import bpy

from ..utils.path_util import get_osl_search_paths


class AssetType(Enum):
    TEXTURE_ASSET = 1
    SHADER_ASSET = 2
    ARCHIVE_ASSET = 3


class AssetHandler(object):
    """
    This class holds methods that are used to translate Blender textures and OSL shader asset filepaths into the correct
    format for rendering
    """

    def __init__(self, depsgraph):
        self._searchpaths = get_osl_search_paths()
        self._depsgraph = depsgraph

        self._searchpaths.extend(x.name for x in bpy.context.preferences.addons['blenderseed'].preferences.search_paths)

    @property
    def searchpaths(self):
        return self._searchpaths

    def set_searchpath(self, path):
        self._searchpaths.append(path)

    def process_path(self, filename, asset_type, sub_texture=False):
        file = bpy.path.abspath(filename)

        if '%' in file:
            file = self._convert_frame_number(file)

        if asset_type == AssetType.SHADER_ASSET:
            dir_name, file_name = os.path.split(file)
            self._searchpaths.append(dir_name)
            file = os.path.splitext(file_name)[0]

        if asset_type == AssetType.TEXTURE_ASSET and sub_texture:
            base_filename = os.path.splitext(file)[0]
            file = f"{base_filename}.tx"

        if asset_type == AssetType.ARCHIVE_ASSET:
            archive_dir, archive = os.path.split(file)
            self._searchpaths.append(archive_dir)
            file = archive

        return file

    def _convert_frame_number(self, file):
        base_filename, ext = os.path.splitext(file)
        index_1 = base_filename.find("%")
        pre_string = base_filename[:index_1]
        post_string = base_filename[index_1 + 1:]
        number_of_zeroes = int(post_string[:-1])
        current_frame = str(self._depsgraph.scene_eval.frame_current)
        for zero in range(number_of_zeroes - len(current_frame)):
            current_frame = f"0{current_frame}"

        return f"{pre_string}{current_frame}{ext}"


class CopyAssetsAssetHandler(AssetHandler):
    """
    This class holds methods that are used to translate Blender textures and OSL shader asset filepaths into the correct
    format for exported scene files.  It also copies texture assets into the correct output folder
    """

    def __init__(self, export_dir, geometry_dir, textures_dir, depsgraph):
        super(CopyAssetsAssetHandler, self).__init__(depsgraph)
        self.__export_dir = export_dir
        self.__geometry_dir = geometry_dir
        self.__textures_dir = textures_dir

    @property
    def export_dir(self):
        return self.__export_dir

    @property
    def geometry_dir(self):
        return self.__geometry_dir

    @property
    def textures_dir(self):
        return self.__textures_dir

    def process_path(self, blend_path, asset_type, sub_texture=False):
        original_path = bpy.path.abspath(blend_path)
        if '%' in original_path:
            original_path = self._convert_frame_number(original_path)
        original_dir, filename = os.path.split(original_path)

        if asset_type == AssetType.TEXTURE_ASSET:
            if sub_texture:
                base_filename = os.path.splitext(filename)[0]
                filename = f"{base_filename}.tx"

            dest_dir = self.textures_dir
            dest_file = os.path.join(dest_dir, filename)
            if not os.path.exists(dest_file):
                shutil.copy(os.path.join(original_dir, filename), os.path.join(dest_dir, filename))
            return "_textures/" + filename

        else:
            self._searchpaths.append(original_dir)
            return os.path.splitext(filename)[0]
