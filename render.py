
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

from . import projectwriter
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

        # Name and location of the exported project.
        project_dir = os.path.join(efutil.temp_directory(), "blenderseed", "render")
        project_filepath = os.path.join(project_dir, "render.appleseed")

        # Create target directories if necessary.
        if not os.path.exists(project_dir):
            try:
                os.makedirs(project_dir)
            except os.error:
                self.report({"ERROR"}, "The directory {0} could not be created. Check directory permissions.".format(project_dir))
                return

        # Generate project on disk.
        writer = projectwriter.Writer()
        writer.write(scene, project_filepath)

        # Render project.
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

        # Build the path to the output preview project.
        preview_output_dir = os.path.join(efutil.temp_directory(), "blenderseed", "material_preview")
        preview_project_filepath = os.path.join(preview_output_dir, "material_preview.appleseed")

        # Create target directories if necessary.
        if not os.path.exists(preview_output_dir):
            try:
                os.makedirs(preview_output_dir)
            except os.error:
                self.report({"ERROR"}, "The directory {0} could not be created. Check directory permissions.".format(preview_output_dir))
                return

        # Copy assets from template project to output directory.
        preview_template_dir = os.path.join(os.sep.join(util.realpath(__file__).split(os.sep)[:-1]), "mat_preview")
        existing_files = os.listdir(preview_output_dir)
        for item in os.listdir(preview_template_dir):
            if item not in existing_files:
                copyfile(os.path.join(preview_template_dir, item), os.path.join(preview_output_dir, item))

        prev_mat = likely_materials[0]
        prev_type = prev_mat.preview_render_type.lower()

        # Export the project.
        writer = projectwriter.Writer()
        file_written = writer.export_preview(scene,
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
        # Check that the path to the bin folder is set.
        appleseed_bin_dir = bpy.context.user_preferences.addons['blenderseed'].preferences.appleseed_binary_directory
        if not appleseed_bin_dir:
            self.report({'ERROR'}, "The path to the folder containing the appleseed.cli executable has not been specified. Set the path in the add-on user preferences.")
            return

        # Check that the path to the bin folder indeed points to a folder.
        if not os.path.isdir(appleseed_bin_dir):
            self.report({'ERROR'}, "The path to the folder containing the appleseed.cli executable was set to {0} but this does not appear to be a valid folder.".format(appleseed_bin_dir))
            return

        # Compute the path to the appleseed.cli executable.
        appleseed_bin_path = os.path.join(appleseed_bin_dir, "appleseed.cli")

        # Compute render resolution.
        (width, height) = util.get_render_resolution(scene)

        # Compute render window.
        if scene.render.use_border:
            min_x = int(scene.render.border_min_x * width)
            min_y = height - int(scene.render.border_max_y * height)
            max_x = int(scene.render.border_max_x * width) - 1
            max_y = height - int(scene.render.border_min_y * height) - 1
        else:
            min_x = 0
            min_y = 0
            max_x = width - 1
            max_y = height - 1

        # Launch appleseed.cli.
        threads = 'auto' if scene.appleseed.threads_auto else str(scene.appleseed.threads)
        cmd = (appleseed_bin_path,
               project_filepath,
               '--to-stdout',
               '--threads', threads,
               '--message-verbosity', 'warning',
               '--resolution', str(width), str(height),
               '--window', str(min_x), str(min_y), str(max_x), str(max_y))
        try:
            process = subprocess.Popen(cmd, cwd=appleseed_bin_dir, env=os.environ.copy(), stdout=subprocess.PIPE)
        except OSError as e:
            self.report({'ERROR'}, "Failed to run {0} with project {1}: {2}.".format(appleseed_bin_path, project_filepath, e))
            return

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

            # Ignore tiles completely outside the render window.
            if tile_x > max_x or tile_x + tile_w - 1 < min_x:
                continue
            if tile_y > max_y or tile_y + tile_h - 1 < min_y:
                continue

            # Image-space coordinates of the intersection between the tile and the render window.
            x0 = max(tile_x, min_x)
            y0 = max(tile_y, min_y)
            x1 = min(tile_x + tile_w - 1, max_x)
            y1 = min(tile_y + tile_h - 1, max_y)

            # Number of rows and columns to skip in the input tile.
            skip_x = x0 - tile_x
            skip_y = y0 - tile_y
            take_x = x1 - x0 + 1
            take_y = y1 - y0 + 1

            # Extract relevant tile data and convert them to the format expected by Blender.
            floats = array.array('f')
            floats.fromstring(tile_data)
            pix = []
            for y in range(take_y - 1, -1, -1):
                start_pix = (skip_y + y) * tile_w + skip_x
                end_pix = start_pix + take_x
                pix.extend(floats[p*4:p*4+4] for p in range(start_pix, end_pix))

            # Update image.
            result = self.begin_result(x0 - min_x, max_y - (y0 + take_y - 1), take_x, take_y)
            layer = result.layers[0].passes[0]
            layer.rect = pix
            self.end_result(result)

        # Make sure the appleseed.cli process has terminated.
        process.kill()
