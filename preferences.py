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


class AppleseedPreferencesPanel(bpy.types.AddonPreferences):
    bl_idname = __package__

    def update_logger(self, context):
        from .logger import set_logger_level

        set_logger_level(self.log_level)

    log_level = bpy.props.EnumProperty(name="log_level",
                                       items=[('debug', "Debug", ""),
                                              ('warning', "Warning", ""),
                                              ('error', "Error", ""),
                                              ('critical', "Critical", "")],
                                       default='error',
                                       update=update_logger)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "log_level", text="Log Level")
        layout.separator()
        layout.label(text="appleseed Library Versions:")
        import appleseed as asr
        box = layout.box()
        box.label(text=asr.get_synthetic_version_string())

        lib_info = asr.get_third_parties_versions()
        for key in lib_info:
            box = layout.box()
            box.label(text="%s: %s" % (key, lib_info [key]))


def register():
    bpy.utils.register_class(AppleseedPreferencesPanel)


def unregister():
    bpy.utils.unregister_class(AppleseedPreferencesPanel)
