#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2018 Jonathan Dent, The appleseedhq Organization
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
import platform
import sys


def find_python_path():

    if 'APPLESEED_PYTHON_PATH' in os.environ:
        python_path = os.environ['APPLESEED_PYTHON_PATH']
    else:
        python_path = os.path.join(get_appleseed_parent_dir_path(), 'lib')

    return python_path


def load_appleseed_python_paths():
    python_path = find_python_path()
    if python_path != "":
        sys.path.append(python_path)
        print("[appleseed] Python path set to: {0}".format(python_path))

        if platform.system() == 'Windows':
            bin_dir = get_appleseed_bin_dir_path()
            os.environ['PATH'] += os.pathsep + bin_dir
            print("[appleseed] Path to appleseed.dll is set to: {0}".format(bin_dir))


def get_appleseed_bin_dir_path():
    if "APPLESEED_BIN_DIR" in os.environ:
        appleseed_bin_dir = os.environ['APPLESEED_BIN_DIR']
    else:
        appleseed_bin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "appleseed", "bin")
    if appleseed_bin_dir:
        appleseed_bin_dir = os.path.realpath(appleseed_bin_dir)
    return appleseed_bin_dir


def get_appleseed_parent_dir_path():
    appleseed_parent_dir = get_appleseed_bin_dir_path()
    while os.path.basename(appleseed_parent_dir) != 'bin':
        appleseed_parent_dir = os.path.dirname(appleseed_parent_dir)
    appleseed_parent_dir = os.path.dirname(appleseed_parent_dir)

    return appleseed_parent_dir


def get_appleseed_tool_dir():
    return os.path.join(get_appleseed_parent_dir_path(), 'bin')


def get_osl_search_paths():
    appleseed_parent_dir = get_appleseed_parent_dir_path()

    if "APPLESEED_BIN_DIR" in os.environ:
        shader_directories = [os.path.join(appleseed_parent_dir, 'shaders', 'appleseed'), os.path.join(appleseed_parent_dir, 'shaders', 'blenderseed')]
    else:
        shader_directories = [os.path.join(appleseed_parent_dir, 'shaders')]

    # Add environment paths.
    if "APPLESEED_SEARCHPATH" in os.environ:
        shader_directories.extend(os.environ["APPLESEED_SEARCHPATH"].split(os.path.pathsep))

    # Remove duplicated paths.
    tmp = set(shader_directories)
    shader_directories = list(tmp)

    return shader_directories
