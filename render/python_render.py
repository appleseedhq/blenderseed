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
import threading

from ..util import safe_register_class, safe_unregister_class

from ..logger import get_logger

logger = get_logger()


class RenderThread(threading.Thread):
    def __init__(self, renderer):
        super(RenderThread, self).__init__()
        self.__renderer = renderer

    def run(self):
        self.__renderer.render()


class RenderAppleseed(bpy.types.RenderEngine):
    bl_idname = 'APPLESEED_RENDER'
    bl_label = 'appleseed'
    # bl_use_preview = True

    # This lock allows to serialize renders.
    render_lock = threading.Lock()

    def __init__(self):
        logger.debug("Render Engine Created")
        self.__scene_translator = None
        self.__proj = None

    def __del__(self):
        logger.debug("Render Engine Deleted")

    def update(self, data, scene):
        if self.is_preview:
            pass
        else:
            logger.debug("Create Scene Translator")
            from ..translators.scene import SceneTranslator
            self.__scene_translator = SceneTranslator.create_final_render_translator(scene)
            self.__scene_translator.translate_scene()

    def render(self, scene):
        if self.is_preview:
            pass
        else:
            import appleseed as asr
            from .renderercontroller import RendererController
            from .tilecallbacks import FinalTileCallback
            logger.debug("Loading appleseed Project")
            self.__proj = self.__scene_translator.as_project

            renderer_controller = RendererController(self)
            tile_callback = FinalTileCallback(self)

            logger.debug("Starting Render")
            renderer = asr.MasterRenderer(self.__proj,
                                          self.__proj.configurations()['final'].get_inherited_parameters(),
                                          renderer_controller,
                                          tile_callback)

            render_thread = RenderThread(renderer)
            render_thread.start()

            logger.debug("Rendering")

            while render_thread.isAlive():
                render_thread.join(0.5)  # seconds


def register():
    safe_register_class(RenderAppleseed)


def unregister():
    safe_unregister_class(RenderAppleseed)
