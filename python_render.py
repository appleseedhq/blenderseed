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

import bpy
import tempfile
import os
import threading

from .util import safe_register_class, safe_unregister_class



class RenderAppleseed(bpy.types.RenderEngine):
    bl_idname = 'APPLESEED_RENDER'
    bl_label = 'appleseed'
    # bl_use_preview = True

    # This lock allows to serialize renders.
    render_lock = threading.Lock()

    def __init__(self):
        print("Engine created")

    def __del__(self):
        print("Engine deleted")

    def update(self, data, scene):
        if self.is_preview:
            pass
        else:
            print("Render update!")
            from .translators.scene import SceneTranslator
            project_dir = os.path.join(tempfile.gettempdir(), "blenderseed", "render")
            project_filepath = os.path.join(project_dir, "render.appleseed")
            scene_translator = SceneTranslator.create_project_export_translator(scene, project_filepath)
            scene_translator.translate_scene()
            scene_translator.write_project(project_filepath)

    def render(self, scene):
        pass


def register():
    safe_register_class(RenderAppleseed)


def unregister():
    safe_unregister_class(RenderAppleseed)
