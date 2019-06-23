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

import os

import bpy
from nodeitems_utils import NodeItem, unregister_node_categories, register_node_categories, _node_categories

import appleseed as asr

osl_custom_nodes = list()


def update_searchpath(self, context):
    from .properties.nodes import AppleseedOSLNode, AppleseedOSLNodeCategory
    from .utils import osl_utils, util
    from .utils.osl_utils import parse_shader

    index = context.preferences.addons['blenderseed'].preferences.path_index
    path = context.preferences.addons['blenderseed'].preferences.search_paths[index].file_path

    q = asr.ShaderQuery()

    from .logger import get_logger
    logger = get_logger()

    logger.debug("[appleseed] Parsing OSL shaders...")

    nodes = list()

    if os.path.isdir(path):
        logger.debug("[appleseed] Searching {0} for OSO files...".format(path))
        for file in os.listdir(path):
            if file.endswith(".oso"):
                logger.debug("[appleseed] Reading {0}...".format(file))
                filename = os.path.join(path, file)
                q.open(filename)
                nodes.append(parse_shader(q, filename=filename))

    for node in nodes:
        node_name, node_category, node_classes = osl_utils.generate_node(node,
                                                                         AppleseedOSLNode)

        for cls in node_classes:
            util.safe_register_class(cls)

        osl_custom_nodes.append(NodeItem(node_name))

    if "APPLESEED_CUSTOM" in _node_categories.keys():
        unregister_node_categories("APPLESEED_CUSTOM")

    custom_nodes = [AppleseedOSLNodeCategory("OSL_Custom", "appleseed-Custom", items=osl_custom_nodes)]

    register_node_categories("APPLESEED_CUSTOM", custom_nodes)


class AppleseedSearchPath(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="name")

    file_path: bpy.props.StringProperty(name="file_path",
                                        subtype="DIR_PATH",
                                        update=update_searchpath)


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

    log_level: bpy.props.EnumProperty(name="log_level",
                                      items=[('debug', "Debug", ""),
                                             ('warning', "Warning", ""),
                                             ('error', "Error", ""),
                                             ('critical', "Critical", "")],
                                      default='error',
                                      update=update_logger)

    search_paths: bpy.props.CollectionProperty(type=AppleseedSearchPath,
                                               name="search_paths")

    path_index: bpy.props.IntProperty(name="path_index",
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
        row.operator("appleseed.add_searchpath", text="Add Path", icon="ADD")
        row.operator("appleseed.remove_searchpath", text="Remove Path", icon="REMOVE")

        if self.search_paths:
            current_set = self.search_paths[self.path_index]
            layout.prop(current_set, "file_path", text="Filepath")

        layout.label(text="appleseed Library Versions:")
        box = layout.box()
        box.label(text=asr.get_synthetic_version_string())

        lib_info = asr.get_third_parties_versions()
        for key in lib_info:
            box = layout.box()
            box.label(text="%s: %s" % (key, lib_info[key]))


classes = (AppleseedSearchPath,
           ASS_UL_SearchPathList,
           AppleseedPreferencesPanel)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
