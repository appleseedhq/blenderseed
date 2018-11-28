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
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ExportHelper

from .utils import util
from .translators import SceneTranslator


class ExportAppleseedScene(bpy.types.Operator, ExportHelper):
    """
    Export the scene to an appleseed project on disk.
    """

    bl_idname = "appleseed.export_scene"
    bl_label = "Export appleseed Scene"
    bl_options = {'PRESET'}

    filename_ext = ".appleseed"
    filter_glob = StringProperty(default="*.appleseed", options={'HIDDEN'})

    # Properties.

    animation = BoolProperty(name="Animation", description="Write out an appleseed project for each frame", default=False)

    # selected_only = BoolProperty(name="Selection Only", description="Export selected objects only", default=False)
    # packed = BoolProperty(name="Pack Project", description="Export packed projects", default=False)

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

    def execute(self, context):
        export_path = util.realpath(self.filepath)

        scene = context.scene

        if self.animation:

            if not '#' in export_path:
                self.report(
                    {'ERROR'},
                    'Exporting animation but project filename has no # frame placeholders.')
                return {'CANCELLED'}

            replacements = [
                ('######', "%06d"),
                ('#####', "%05d"),
                ('####', "%04d"),
                ('###', "%03d"),
                ('##', "%02d"),
                ('#', "%d")
            ]

            for i in replacements:
                if i[0] in export_path:
                    export_path = export_path.replace(i[0], i[1])
                    break

            frame_start = scene.frame_start
            frame_end = scene.frame_end

            for frame in range(frame_start, frame_end + 1):
                scene.frame_set(frame)
                proj_filename = export_path % frame
                self.__export_project(context, proj_filename)

        else:
            self.__export_project(context, export_path)

        return {'FINISHED'}

    def __export_project(self, context, export_path):
        scene_translator = SceneTranslator.create_project_export_translator(context.scene, export_path)
        scene_translator.translate_scene()
        scene_translator.write_project(export_path)


def menu_func_export_scene(self, context):
    self.layout.operator(ExportAppleseedScene.bl_idname, text="appleseed (.appleseed)")


def register():
    util.safe_register_class(ExportAppleseedScene)
    bpy.types.INFO_MT_file_export.append(menu_func_export_scene)


def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export_scene)
    util.safe_unregister_class(ExportAppleseedScene)
