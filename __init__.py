
#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
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

bl_info = {
    "name": "appleseed",
    "author": "The appleseedhq Organization",
    "version": (0, 8, 1),
    "blender": (2, 7, 9),
    "location": "Info Header (Render Engine Menu)",
    "description": "appleseed Render Engine",
    "warning": "",
    "wiki_url": "https://github.com/appleseedhq/blenderseed/wiki",
    "tracker_url": "https://github.com/appleseedhq/blenderseed/issues",
    "category": "Render"}


def find_python_path():
    python_path = ""

    if 'APPLESEED_PYTHON_PATH' in os.environ:
        python_path = os.environ['APPLESEED_PYTHON_PATH']
    else:
        python_path = os.path.join(util.get_appleseed_parent_dir(), 'lib')

    return python_path


def load_appleseed_python_paths():
    python_path = find_python_path()
    if python_path != "":
        sys.path.append(python_path)
        logger.debug("[appleseed] Python path set to: {0}".format(python_path))

        if platform.system() == 'Windows':
            bin_dir = util.get_appleseed_bin_dir()
            os.environ['PATH'] += os.pathsep + bin_dir
            logger.debug("[appleseed] Path to appleseed.dll is set to: {0}".format(bin_dir))


if "bpy" in locals():
    import imp

    imp.reload(properties)
    imp.reload(operators)
    imp.reload(export)
    imp.reload(ui)
    imp.reload(util)
    imp.reload(preferences)
    imp.reload(projectwriter)

else:
    import bpy
    import os
    import sys
    import platform
    from .logger import get_logger
    logger = get_logger()
    from . import util
    load_appleseed_python_paths()
    from . import properties
    from . import operators
    from . import ui
    from . import preferences
    from . import export
    from .render import __init__  # not superfluous

def register():
    preferences.register()
    properties.register()
    operators.register()
    export.register()
    ui.register()
    bpy.utils.register_module(__name__)


def unregister():
    ui.unregister()
    export.unregister()
    operators.unregister()
    properties.unregister()
    preferences.unregister()
    bpy.utils.unregister_module(__name__)  # Must be at the end in order to avoid unregistration errors.
