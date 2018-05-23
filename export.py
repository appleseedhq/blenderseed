
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
from bpy_extras.io_utils import ExportHelper
import os
import subprocess
import shutil

from . import projectwriter
from . import util


class ExportAppleseedScene(bpy.types.Operator, ExportHelper):
    """
    Export the scene to an appleseed project on disk.
    """

    bl_idname = "appleseed.export_scene"
    bl_label = "Export appleseed Scene"

    filename_ext = ".appleseed"
    filter_glob = bpy.props.StringProperty(default="*.appleseed", options={'HIDDEN'})

    compress_export = bpy.props.BoolProperty(name="Create compressed archive",
                                             description="Compress export (including all textures) into archive file",
                                             default=False)

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

    def execute(self, context):
        export_path = util.realpath(self.filepath)
        writer = projectwriter.Writer()
        writer.write(context.scene, export_path)

        if self.compress_export:
            appleseed_bin_dir = util.get_appleseed_bin_dir()
            projecttool_path = os.path.join(appleseed_bin_dir, "projecttool")
            cmd = (projecttool_path, 'pack', export_path)
            try:
                process = subprocess.Popen(cmd, cwd=appleseed_bin_dir, env=os.environ.copy(), stdout=subprocess.PIPE)
                process.wait()
            except OSError as e:
                self.report({'ERROR'}, "Failed to run {0} with project {1}: {2}.".format(projecttool_path, export_path, e))
                return
            dir_path = os.path.dirname(export_path)
            shutil.rmtree(os.path.join(dir_path, "meshes"))
            os.remove(export_path)

        return {'FINISHED'}


class ExportAppleseedAnimationScene(bpy.types.Operator, ExportHelper):
    """
    Export the scene to an appleseed project on disk.
    """

    bl_idname = "appleseed.export_anim_scene"
    bl_label = "Export appleseed Animation Scene"

    filename_ext = ".appleseed"
    filter_glob = bpy.props.StringProperty(default="*.appleseed", options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'

    def execute(self, context):
        scene = context.scene
        frame_start = scene.frame_start
        frame_end = scene.frame_end

        for frame in range(frame_start, frame_end + 1):
            scene.frame_set(frame)
            file_split = os.path.splitext(self.filepath)
            export_path = util.realpath(os.path.join('{0}_{1}.{2}'.format(file_split[0], frame, file_split[1])))
            writer = projectwriter.Writer()
            writer.write(context.scene, export_path, animation=True)

        return {'FINISHED'}


def menu_func_export_scene(self, context):
    self.layout.operator(ExportAppleseedScene.bl_idname, text="appleseed (.appleseed)")
    self.layout.operator(ExportAppleseedAnimationScene.bl_idname, text="appleseed animation (.appleseed)")


def register():
    util.safe_register_class(ExportAppleseedScene)
    util.safe_register_class(ExportAppleseedAnimationScene)
    bpy.types.INFO_MT_file_export.append(menu_func_export_scene)


def unregister():
    bpy.types.INFO_MT_file_export.remove(menu_func_export_scene)
    util.safe_unregister_class(ExportAppleseedAnimationScene)
    util.safe_unregister_class(ExportAppleseedScene)
