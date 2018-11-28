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

import os
import shutil
from enum import Enum

import bpy


class AssetType(Enum):
    TEXTURE_ASSET = 1
    SHADER_ASSET = 2
    ARCHIVE_ASSET = 3


class AssetHandler(object):

    def __init__(self):
        self._searchpaths = []

    @property
    def searchpaths(self):
        return self._searchpaths

    def set_searchpath(self, path):
        self._searchpaths.append(path)

    def process_path(self, filename, asset_type, sub_texture=False):
        file = bpy.path.abspath(filename)
        if asset_type == AssetType.SHADER_ASSET:
            dir_name, file_name = os.path.split(file)
            self._searchpaths.append(dir_name)
            file = os.path.splitext(file_name)[0]
        if asset_type == AssetType.TEXTURE_ASSET and sub_texture:
            base_filename = os.path.splitext(file)[0]
            file = "{0}.tx".format(base_filename)
        if asset_type == AssetType.ARCHIVE_ASSET:
            archive_dir, archive = os.path.split(file)
            self._searchpaths.append(archive_dir)
            file = archive

        return file


class CopyAssetsAssetHandler(AssetHandler):

    def __init__(self, export_dir, geometry_dir, textures_dir):
        super(CopyAssetsAssetHandler, self).__init__()
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
        original_dir, filename = os.path.split(original_path)

        if asset_type == AssetType.TEXTURE_ASSET:
            if sub_texture:
                base_filename = os.path.splitext(filename)[0]
                filename = "{0}.tx".format(base_filename)

            dest_dir = self.textures_dir
            dest_file = os.path.join(dest_dir, filename)
            if not os.path.exists(dest_file):
                shutil.copy(os.path.join(original_dir, filename), os.path.join(dest_dir, filename))
            return "_textures/" + filename

        else:
            self._searchpaths.append(original_dir)
            return os.path.splitext(filename)[0]
