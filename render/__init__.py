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

import array
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
from math import ceil

import appleseed as asr
import bpy

from .renderercontroller import RendererController
from .tilecallbacks import FinalTileCallback
from .. import util
from ..logger import get_logger
from ..translators.preview import PreviewRenderer
from ..translators.scene import SceneTranslator

logger = get_logger()

_preview_renderer = None


class RenderThread(threading.Thread):

    def __init__(self, renderer):
        super(RenderThread, self).__init__()
        self.__renderer = renderer

    def run(self):
        self.__renderer.render()


class RenderAppleseed(bpy.types.RenderEngine):
    bl_idname = 'APPLESEED_RENDER'
    bl_label = 'appleseed'
    bl_use_preview = True

    # This lock allows to serialize renders.
    render_lock = threading.Lock()

    def __init__(self):
        pass

    def update(self, data, scene):
        pass

    def update_render_passes(self, scene=None, renderlayer=None):
        asr_scene_props = scene.appleseed

        if not self.is_preview:
            self.register_pass(scene, renderlayer, "Combined", 4, "RGBA", 'COLOR')
            if asr_scene_props.enable_aovs:
                if asr_scene_props.diffuse_aov:
                    self.register_pass(scene, renderlayer, "Diffuse", 4, "RGBA", 'COLOR')
                if asr_scene_props.direct_diffuse_aov:
                    self.register_pass(scene, renderlayer, "Direct Diffuse", 4, "RGBA", 'COLOR')
                if asr_scene_props.indirect_diffuse_aov:
                    self.register_pass(scene, renderlayer, "Indirect Diffuse", 4, "RGBA", 'COLOR')
                if asr_scene_props.glossy_aov:
                    self.register_pass(scene, renderlayer, "Glossy", 4, "RGBA", 'COLOR')
                if asr_scene_props.direct_glossy_aov:
                    self.register_pass(scene, renderlayer, "Direct Glossy", 4, "RGBA", 'COLOR')
                if asr_scene_props.indirect_glossy_aov:
                    self.register_pass(scene, renderlayer, "Indirect Glossy", 4, "RGBA", 'COLOR')
                if asr_scene_props.normal_aov:
                    self.register_pass(scene, renderlayer, "Normal", 3, "RGB", 'VECTOR')
                if asr_scene_props.uv_aov:
                    self.register_pass(scene, renderlayer, "UV", 3, "RGB", 'VECTOR')
                if asr_scene_props.depth_aov:
                    self.register_pass(scene, renderlayer, "Z Depth", 1, "Z", 'VALUE')
                if asr_scene_props.pixel_time_aov:
                    self.register_pass(scene, renderlayer, "Pixel Time", 1, "X", "VALUE")

    def render(self, scene):
        asr_scene_props = scene.appleseed

        if not self.is_preview:
            if asr_scene_props.enable_aovs:
                if asr_scene_props.diffuse_aov:
                    self.add_pass("Diffuse", 4, "RGBA")
                if asr_scene_props.direct_diffuse_aov:
                    self.add_pass("Direct Diffuse", 4, "RGBA")
                if asr_scene_props.indirect_diffuse_aov:
                    self.add_pass("Indirect Diffuse", 4, "RGBA")
                if asr_scene_props.glossy_aov:
                    self.add_pass("Glossy", 4, "RGBA")
                if asr_scene_props.direct_glossy_aov:
                    self.add_pass("Direct Glossy", 4, "RGBA")
                if asr_scene_props.indirect_glossy_aov:
                    self.add_pass("Indirect Glossy", 4, "RGBA")
                if asr_scene_props.normal_aov:
                    self.add_pass("Normal", 3, "RGB")
                if asr_scene_props.uv_aov:
                    self.add_pass("UV", 3, "RGB")
                if asr_scene_props.depth_aov:
                    self.add_pass("Z Depth", 1, "Z")
                if asr_scene_props.pixel_time_aov:
                    self.add_pass("Pixel Time", 1, "X")

        with RenderAppleseed.render_lock:
            if self.is_preview:
                if not bpy.app.background:
                    self.__render_material_preview(scene)
            else:
                self.__render_scene(scene)

    def __render_material_preview(self, scene):
        global _preview_renderer

        if not _preview_renderer:
            _preview_renderer = PreviewRenderer()

        _preview_renderer.translate_preview(scene)

        # else:
        #     _preview_renderer.update_preview(scene)

        project = _preview_renderer.as_project

        self.__render_final(project, scene)

    def __render_scene(self, scene):
        """
        Export and render the scene.
        """

        # if scene.appleseed.scene_export_mode == "export_render":
            # export_path = scene.appleseed.export_path
            # scene_translator = SceneTranslator.create_project_export_translator(scene, export_path)
            # scene_translator.translate_scene()
            # scene_translator.write_project(export_path)
            #
            # appleseed_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "appleseed", "schemas")
            # schema_path = os.path.join(appleseed_dir, "project.xsd")
            # project = asr.ProjectFileReader.read(export_path, schema_path, asr.ProjectFileReaderOptions.Defaults)

        scene_translator = SceneTranslator.create_final_render_translator(scene)
        scene_translator.translate_scene()

        project = scene_translator.as_project

        self.__render_final(project, scene)

    def __render_final(self, project, scene):
        renderer_controller = RendererController(self)

        tile_callback = FinalTileCallback(self, scene)

        renderer = asr.MasterRenderer(project,
                                      project.configurations()['final'].get_inherited_parameters(),
                                      renderer_controller,
                                      tile_callback)

        render_thread = RenderThread(renderer)

        # While debugging, log to the console. This should be configurable.
        log_target = asr.ConsoleLogTarget(sys.stderr)
        asr.global_logger().add_target(log_target)

        render_thread.start()

        while render_thread.isAlive():
            render_thread.join(0.5)  # seconds

        asr.global_logger().remove_target(log_target)
