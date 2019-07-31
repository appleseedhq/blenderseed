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

path_added = False


def updated_path(self, context):
    global path_added

    path_added = True

class AppleseedSearchPath(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(name="name",
                                   subtype="DIR_PATH",
                                   update=updated_path)


class ASS_UL_SearchPathList(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        search_path = item.name
        if 'DEFAULT' in self.layout_type:
            layout.label(text=search_path, translate=False, icon_value=icon)


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

    search_paths = bpy.props.CollectionProperty(type=AppleseedSearchPath,
                                               name="search_paths")

    path_index = bpy.props.IntProperty(name="path_index",
                                      description="",
                                      default=0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "log_level", text="Log Level")
        layout.separator()

        layout.label(text="Resource Search Paths")
        row = layout.row()
        row.template_list("ASS_UL_SearchPathList", "", self,
                          "search_paths", self, "path_index", rows=1, maxrows=16, type="DEFAULT")

        row = layout.row(align=True)
        row.operator("appleseed.add_search_path", text="Add Search Path", icon="ZOOMIN")
        row.operator("appleseed.remove_search_path", text="Remove Search Path", icon="ZOOMOUT")

        if self.search_paths:
            current_set = self.search_paths[self.path_index]
            layout.prop(current_set, "name", text="Filepath")

        global path_added

        if path_added is True:
            layout.label(text="Changes to search paths will take effect upon restarting Blender", icon="ERROR")

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
    bpy.utils.register_class(AppleseedSearchPath)
    bpy.utils.register_class(ASS_UL_SearchPathList)
    bpy.utils.register_class(AppleseedPreferencesPanel)


def unregister():
    bpy.utils.unregister_class(AppleseedPreferencesPanel)
    bpy.utils.unregister_class(ASS_UL_SearchPathList)
    bpy.utils.unregister_class(AppleseedSearchPath)
