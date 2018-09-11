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

import appleseed as asr

from ..logger import get_logger

logger = get_logger()


class BaseRendererController(asr.IRendererController):
    def __init__(self):
        super(BaseRendererController, self).__init__()
        self._status = asr.IRenderControllerStatus.ContinueRendering

    def set_status(self, status):
        self._status = status

    def on_rendering_begin(self):
        pass

    def on_rendering_success(self):
        logger.debug("Render finished")

    def on_rendering_abort(self):
        pass

    def on_frame_begin(self):
        pass

    def on_frame_end(self):
        pass

    def on_progress(self):
        pass


class FinalRendererController(BaseRendererController):
    def __init__(self, engine, tile_callback):
        super(FinalRendererController, self).__init__()
        self.__engine = engine
        self.__tile_callback = tile_callback

    def get_status(self):
        if self.__engine.test_break():
            return asr.IRenderControllerStatus.AbortRendering

        render_stats = self.__tile_callback.render_stats
        self.__engine.update_stats(render_stats[0], render_stats[1])
        return self._status

    def on_rendering_begin(self):
        logger.debug("Starting Render")
        self.__engine.update_stats("appleseed Rendering: Loading scene", "Time Remaining: Unknown")


class InteractiveRendererController(BaseRendererController):
    def __init__(self, camera):
        super(InteractiveRendererController, self).__init__()

        self.__camera = camera

    def on_frame_begin(self):
        if False:
            self.__camera.set_transform(0.0)
            self._status = asr.IRenderControllerStatus.ContinueRendering
        else:
            pass

    def get_status(self):
        return self._status
