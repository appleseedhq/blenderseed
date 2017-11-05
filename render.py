
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2014-2017 The appleseedhq Organization
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
import struct
import subprocess
import sys
import threading
from shutil import copyfile

import bpy
from extensions_framework import util as efutil

from . import project_file_writer
from . import util


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

    def render(self, scene):
        with RenderAppleseed.render_lock:
            if self.is_preview:
                if not bpy.app.background:
                    self.__render_material_preview(scene)
            elif self.is_animation:
                frame_current = scene.frame_start
                while frame_current <= scene.frame_end:
                    scene.frame_set(frame_current)
                    self.__render_scene(scene)
                    frame_current += scene.frame_step
            else:
                self.__render_scene(scene)

    def __render_scene(self, scene):
        """
        Export and render the scene.
        """

        # Write project file and export meshes.
        bpy.ops.appleseed.export()

        if scene.appleseed.project_path == '':
            self.report({'INFO'}, "Please first specify a project path in the appleseed render settings.")
            return

        # Make sure the project directory exists.
        project_dir = util.realpath(scene.appleseed.project_path)
        if not os.path.exists(project_dir):
            try:
                os.makedirs(project_dir)
            except os.error:
                self.report({"ERROR"}, "The project directory could not be created. Check directory permissions.")
                return

        # Build the file path for the appleseed project.
        project_filepath = scene.name
        if not project_filepath.endswith(".appleseed"):
            project_filepath += ".appleseed"
        project_filepath = os.path.join(project_dir, project_filepath)

        # Render the project.
        self.__render_project_file(scene, project_filepath)

    def __render_material_preview(self, scene):
        """
        Export and render the material preview scene.
        """

        # Don't render material thumbnails.
        (width, height) = util.get_render_resolution(scene)
        if width <= 96:
            return

        # Collect objects and their materials in a object -> [materials] dictionary.
        objects_materials = {}
        for obj in (obj for obj in scene.objects if obj.is_visible(scene) and not obj.hide_render):
            for mat in util.get_instance_materials(obj):
                if mat is not None:
                    if obj.name not in objects_materials.keys():
                        objects_materials[obj] = []
                    objects_materials[obj].append(mat)

        # Find objects that are likely to be the preview objects.
        preview_objects = [o for o in objects_materials.keys() if o.name.startswith('preview')]
        if not preview_objects:
            return

        # Find the materials attached to the likely preview object.
        likely_materials = objects_materials[preview_objects[0]]
        if not likely_materials:
            return

        # Build the path to the template preview project in the add-on directory.
        preview_template_dir = os.path.join(os.sep.join(util.realpath(__file__).split(os.sep)[:-1]), "mat_preview")

        # Build the path to the output preview project.
        preview_output_dir = os.path.join(efutil.temp_directory(), "mat_preview")
        preview_project_filepath = os.path.join(preview_output_dir, "mat_preview.appleseed")

        # Copy preview scene assets.
        if not os.path.isdir(preview_output_dir):
            os.mkdir(preview_output_dir)
        existing_files = os.listdir(preview_output_dir)
        for item in os.listdir(preview_template_dir):
            if item not in existing_files:
                copyfile(os.path.join(preview_template_dir, item), os.path.join(preview_output_dir, item))

        prev_mat = likely_materials[0]
        prev_type = prev_mat.preview_render_type.lower()

        # Export the project.
        exporter = project_file_writer.Exporter()
        file_written = exporter.export_preview(scene,
                                               preview_project_filepath,
                                               prev_mat,
                                               prev_type,
                                               width,
                                               height)
        if not file_written:
            print('Error while exporting. Check the console for details.')
            return

        # Render the project.
        self.__render_project_file(scene, preview_project_filepath)

    def __render_project_file(self, scene, project_filepath):
        # Get the absolute path to the executable directory.
        as_bin_path = util.realpath(bpy.context.user_preferences.addons['blenderseed'].preferences.appleseed_bin_path)
        if as_bin_path == '':
            self.report({'ERROR'}, "The path to appleseed.cli executable has not been specified. Set the path in the add-on user preferences.")
            return
        appleseed_exe = os.path.join(as_bin_path, "appleseed.cli")

        # If running Linux/macOS, add the binary path to environment.
        if sys.platform != "win32":
            os.environ['LD_LIBRARY_PATH'] = as_bin_path

        # Compute render resolution.
        (width, height) = util.get_render_resolution(scene)

        # Compute render window.
        x0, y0, x1, y1 = 0, 0, width, height
        if scene.render.use_border:
            x0 = int(scene.render.border_min_x * width)
            x1 = int(scene.render.border_max_x * width)
            y0 = height - int(scene.render.border_min_y * height)
            y1 = height - int(scene.render.border_max_y * height)

        # Launch appleseed.cli.
        cmd = (appleseed_exe,
               project_filepath,
               '--to-stdout',
               '--threads', str(scene.appleseed.threads),
               '--message-verbosity', 'warning',
               '--resolution', str(width), str(height),
               '--window', str(x0), str(y0), str(x1), str(y1))
        process = subprocess.Popen(cmd, cwd=as_bin_path, env=os.environ.copy(), stdout=subprocess.PIPE)

        self.update_stats("", "appleseed: Rendering")

        # Update while rendering.
        while not self.test_break():
            # Wait for the next chunk header from the process's stdout.
            chunk_header_data = os.read(process.stdout.fileno(), 2 * 4)
            if not chunk_header_data:
                break

            # Decode chunk header.
            chunk_header = struct.unpack("II", chunk_header_data)
            chunk_type = chunk_header[0]
            chunk_size = chunk_header[1]

            # Ignore unknown chunks.
            # Known chunk types:
            #   1 = tile, protocol version 1
            if chunk_type != 1:
                os.read(process.stdout.fileno(), chunk_size)
                continue

            # Read and decode tile header.
            tile_header = struct.unpack("IIIII", os.read(process.stdout.fileno(), 5 * 4))
            tile_x = tile_header[0]
            tile_y = tile_header[1]
            tile_w = tile_header[2]
            tile_h = tile_header[3]
            tile_c = tile_header[4]

            # Read tile data.
            tile_size = 4 * tile_w * tile_h * tile_c
            tile_data = bytes()
            while len(tile_data) < tile_size and not self.test_break():
                tile_data += os.read(process.stdout.fileno(), tile_size - len(tile_data))
            if self.test_break():
                break

            # Optional debug message.
            if False:
                print("Received tile: x={0} y={1} w={2} h={3} c={4}".format(tile_x, tile_y, tile_w, tile_h, tile_c))

            # Convert tile data to the format expected by Blender.
            floats = array.array('f')
            floats.fromstring(tile_data)
            pix = []
            for y in range(tile_h - 1, -1, -1):
                stride = tile_w * 4
                start_index = y * stride
                end_index = start_index + stride
                pix.extend(floats[i:i + 4] for i in range(start_index, end_index, 4))

            # Update image.
            result = self.begin_result(tile_x, height - tile_y - tile_h, tile_w, tile_h)
            layer = result.layers[0] if bpy.app.version < (2, 74, 4) else result.layers[0].passes[0]
            layer.rect = pix
            self.end_result(result)

        # Make sure the appleseed.cli process has terminated.
        process.kill()
