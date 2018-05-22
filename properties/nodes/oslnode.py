
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
from bpy.types import NodeSocket, Node
from . import AppleseedNode, AppleseedSocket
from ... import util


class AppleseedOSLInSocket(NodeSocket, AppleseedSocket):
    """appleseed OSL base socket"""

    bl_idname = "AppleseedOSLInSocket"
    bl_label = "OSL Socket"

    socket_value = ''

    socket_osl_id = ''

    hide_ui = False

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked or self.hide_ui:
            layout.label(text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        pass


class AppleseedOSLOutSocket(NodeSocket, AppleseedSocket):
    """appleseed OSL base socket"""

    bl_idname = "AppleseedOSLOutSocket"
    bl_label = "OSL Socket"

    socket_osl_id = ''

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return 1.0, 1.0, 1.0, 1.0


class AppleseedOSLNode(Node, AppleseedNode):
    """appleseed OSL base node"""
    bl_idname = "AppleseedOSLNode"
    bl_label = "OSL Material"
    bl_icon = 'SMOOTH'

    node_type = 'osl'

    def traverse_tree(self, material_node):
        """Iterate inputs and traverse the tree backward if any inputs are connected.

        Nodes are added to a list attribute of the material output node.
        """
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                if linked_node.node_type != 'osl':
                    print("ERROR: {0} cannot be used with OSL nodes.  All nodes upstream of {0} will be skipped".format(linked_node.name))
                else:
                    linked_node.traverse_tree(material_node)
        material_node.tree.append(self)


def generate_node(node):
    """
    Generates a node based on the provided node data

    input format is {name, input properties, output properties, non-connectable properties, filename}
    properties consist of [name, type, default value, min value, max value].
    Enum properties have item list in place of min/max
    """

    def draw_color_float(self, context, node):
        return 0.5, 0.5, 0.5, 1.0

    def draw_color_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0

    def draw_closure_color(self, context, node):
        return 0.0, 0.8, 0.0, 1.0

    def draw_vector_color(self, context, node):
        return 0.67, 0.45, 1.0, 1.0

    def draw_point_color(self, context, node):
        return 0.0, 0.0, 1.0, 1.0

    def draw_uv_color(self, context, node):
        return 0.6, 0.1, 0.0, 1.0

    def draw_matrix_color(self, context, node):
        return 1.0, 0.5, 1.0, 1.0

    parameter_types = {}
    filepaths = []
    name = node['name']
    category = node['category']
    input_sockets = node['inputs']
    output_sockets = node['outputs']
    non_connected_props = []

    socket_input_names = []
    socket_output_names = []

    # create socket classes
    for in_socket in input_sockets:
        if not in_socket['connectable'] and in_socket['hide_ui']:
            continue
        if not in_socket['connectable']:
            non_connected_props.append(in_socket)
        else:
            socket_name = 'Appleseed{0}{1}'.format(node['name'], in_socket['name'].capitalize())
            keys = in_socket.keys()
            helper = ""
            minimum = None
            maximum = None
            soft_minimum = None
            soft_maximum = None
            hide_ui = False
            if 'default' in keys:
                default = in_socket['default']
            if 'label' in keys:
                socket_label = "{0}".format(in_socket['label'])
            else:
                socket_label = "{0}".format(in_socket['name'])
            if 'help' in keys:
                helper = in_socket['help']
            if 'min' in keys:
                minimum = in_socket['min']
            if 'max' in keys:
                maximum = in_socket['max']
            if 'softmin' in keys:
                soft_minimum = in_socket['softmin']
            if 'softmax' in keys:
                soft_maximum = in_socket['softmax']
            hide_ui = in_socket['hide_ui']

            stype = type(socket_name, (AppleseedOSLInSocket,), {})
            stype.bl_idname = socket_name
            stype.bl_label = socket_label
            stype.socket_osl_id = in_socket['name']
            socket_type = in_socket['type']
            if socket_type == 'float':
                stype.draw_color = draw_color_float

                kwargs = {'name': in_socket['name'], 'description': helper, 'default': float(default)}
                if minimum:
                    kwargs['min'] = float(minimum)
                if maximum:
                    kwargs['max'] = float(maximum)
                if soft_minimum:
                    kwargs['soft_min'] = float(soft_minimum)
                if soft_maximum:
                    kwargs['soft_max'] = float(soft_maximum)

                stype.socket_value = bpy.props.FloatProperty(**kwargs)

            elif socket_type == 'color':
                stype.draw_color = draw_color_color
                stype.socket_value = bpy.props.FloatVectorProperty(name=in_socket['name'],
                                                                   description=helper,
                                                                   subtype='COLOR',
                                                                   default=(float(default[0]),
                                                                            float(default[1]),
                                                                            float(default[2])),
                                                                   min=0.0,
                                                                   max=1.0)

            elif socket_type == 'pointer':
                stype.draw_color = draw_closure_color

            elif socket_type == 'vector':
                stype.draw_color = draw_vector_color
                kwargs = {'name': in_socket['name'], 'description': helper}
                if 'default' in keys:
                    kwargs['default'] = (float(default[0]),
                                         float(default[1]),
                                         float(default[2]))

                stype.socket_value = bpy.props.FloatVectorProperty(**kwargs)

            elif socket_type == 'int':
                stype.draw_color = draw_color_float
                stype.socket_value = bpy.props.IntProperty(name=in_socket['name'],
                                                           description=helper,
                                                           default=int(default))

            elif socket_type == 'float[2]':
                stype.draw_color = draw_uv_color
                kwargs = {'name': in_socket['name'], 'description': helper, 'size': 2}
                if in_socket['hide_ui'] is False:
                    if 'default' in keys:
                        kwargs['default'] = (float(default[0]),
                                             float(default[1]))

                    stype.socket_value = bpy.props.FloatVectorProperty(**kwargs)

            elif socket_type == 'normal':
                stype.draw_color = draw_vector_color

            elif socket_type == 'matrix':
                stype.draw_color = draw_matrix_color

            elif socket_type in ('point', 'point[4]'):
                stype.draw_color = draw_point_color

            parameter_types[in_socket['name']] = in_socket['type']
            stype.hide_ui = hide_ui
            util.safe_register_class(stype)

            socket_input_names.append([socket_name, socket_label])

    # create output socket classes
    for out_socket in output_sockets:
        socket_name = "Appleseed{0}{1}".format(node['name'], out_socket['name'].capitalize())
        if 'label' in out_socket.keys():
            socket_label = "{0}".format(out_socket['label'])
        else:
            socket_label = "{0}".format(out_socket['name'].strip("out_"))

        stype = type(socket_name, (AppleseedOSLOutSocket,), {})
        stype.bl_idname = socket_name
        stype.bl_label = socket_label
        stype.socket_osl_id = out_socket['name']
        socket_type = out_socket['type']
        if socket_type in ('float[4]', 'float'):
            stype.draw_color = draw_color_float
        elif socket_type in ('color', 'color[4]'):
            stype.draw_color = draw_color_color
        elif socket_type in ('normal'):
            stype.draw_color = draw_vector_color
        elif socket_type in ('pointer'):
            stype.draw_color = draw_closure_color
        elif socket_type in ('vector'):
            stype.draw_color = draw_vector_color
        elif socket_type == 'matrix':
            stype.draw_color = draw_matrix_color
        elif socket_type in ('point', 'point[4]'):
            stype.draw_color = draw_point_color
        elif socket_type in ('float[2]'):
            stype.draw_color = draw_uv_color
        else:
            pass

        util.safe_register_class(stype)

        socket_output_names.append([socket_name, socket_label])

    # create node class
    def init(self, context):
        if socket_input_names:
            for x in socket_input_names:
                self.inputs.new(x[0], x[1])
        if socket_output_names:
            for x in socket_output_names:
                self.outputs.new(x[0], x[1])
        else:
            pass

    def draw_buttons_ext(self, context, layout):
        pass

    def copy(self, node):
        pass

    def free(self):
        pass

    def draw_label(self):
        return self.bl_label

    def traverse_tree(self):
        """Iterate inputs and traverse the tree backward if any inputs are connected.

        Nodes are added to a list attribute of the material output node.
        Return the tree as a list of all the nodes.
        """
        self.tree.clear()
        for socket in self.inputs:
            if socket.is_linked:
                linked_node = socket.links[0].from_node
                linked_node.traverse_tree(self)
        return util.filter_params(self.tree)

    node_name = "Appleseed{0}Node".format(name)
    node_label = "{0}".format(name)

    ntype = type(node_name, (AppleseedOSLNode,), {})
    ntype.bl_idname = node_name
    ntype.bl_label = node_label
    setattr(ntype, 'file_name', node['filename'])

    def draw_buttons(self, context, layout):
        for prop in non_connected_props:
            layout.prop(self, prop['name'], text=prop['label'])

    for prop in non_connected_props:
        keys = prop.keys()
        widget = ""
        minimum = None
        maximum = None
        soft_minimum = None
        soft_maximum = None

        if 'default' in keys:
            default = prop['default']
        if 'widget' in keys:
            widget = prop['widget']
        prop_name = prop['name']
        if 'label' not in keys:
            prop['label'] = prop_name
        if 'help' in keys:
            helper = prop['help']
        else:
            helper = ""
        if 'min' in keys:
            minimum = prop['min']
        if 'max' in keys:
            maximum = prop['max']
        if 'softmin' in keys:
            soft_minimum = prop['softmin']
        if 'softmax' in keys:
            soft_maximum = prop['softmax']

        if prop['type'] == 'string':
            kwargs = {'name': prop['name'], 'description': helper}
            if widget == 'filename':
                kwargs['subtype'] = 'FILE_PATH'
                setattr(ntype, prop_name, bpy.props.StringProperty(**kwargs))
                filepaths.append(prop_name)

            elif widget in ('mapper', 'popup'):
                items = []
                for enum_item in prop['options']:
                    items.append((enum_item, enum_item.capitalize(), ""))
                setattr(ntype, prop_name, bpy.props.EnumProperty(name=prop['label'],
                                                                 description=helper,
                                                                 default=str(default),
                                                                 items=items))

            else:
                setattr(ntype, prop_name, bpy.props.StringProperty(**kwargs))

            parameter_types[prop['name']] = "string"

        elif prop['type'] == 'int' and widget in ('mapper', 'popup'):
            items = []
            for enum_item in prop['options']:
                items.append((enum_item.split(":")[1], enum_item.split(":")[0], ""))
                parameter_types[prop_name] = "int"

            setattr(ntype, prop_name, bpy.props.EnumProperty(name=prop['label'],
                                                             description=helper,
                                                             default=str(int(default)),
                                                             items=items))

        elif prop['type'] == 'int':
            if widget == 'checkBox':
                kwargs = {'name': prop['name'], 'description': helper, 'default': bool(int(default))}
                setattr(ntype, prop_name, bpy.props.BoolProperty(**kwargs))
                parameter_types[prop['name']] = "int checkbox"

            else:
                kwargs = {'name': prop['name'], 'description': helper, 'default': int(default)
                          }
                if minimum:
                    kwargs['min'] = int(minimum)
                if maximum:
                    kwargs['max'] = int(maximum)
                if soft_minimum:
                    kwargs['soft_min'] = int(soft_minimum)
                if soft_maximum:
                    kwargs['soft_max'] = int(soft_maximum)

                setattr(ntype, prop_name, bpy.props.IntProperty(**kwargs))

                parameter_types[prop['name']] = "int"

        elif prop['type'] == 'float':

            kwargs = {'name': prop['name'], 'description': helper, 'default': float(default)}
            if minimum:
                kwargs['min'] = float(minimum)
            if maximum:
                kwargs['max'] = float(maximum)
            if soft_minimum:
                kwargs['soft_min'] = float(soft_minimum)
            if soft_maximum:
                kwargs['soft_max'] = float(soft_maximum)

            setattr(ntype, prop_name, bpy.props.FloatProperty(**kwargs))

            parameter_types[prop['name']] = "float"

        elif prop['type'] == 'color':
            setattr(ntype, prop_name, bpy.props.FloatVectorProperty(name=prop['name'],
                                                                    description=helper,
                                                                    subtype='COLOR',
                                                                    default=(float(default[0]),
                                                                             float(default[1]),
                                                                             float(default[2])),
                                                                    min=0.0,
                                                                    max=1.0))

            parameter_types[prop['name']] = "color"

        elif prop['type'] == 'vector':
            setattr(ntype, prop_name, bpy.props.FloatVectorProperty(name=prop['name'],
                                                                    description=helper,
                                                                    default=(float(default[0]),
                                                                             float(default[1]),
                                                                             float(default[2]))))

            parameter_types[prop['name']] = "vector"

    ntype.parameter_types = parameter_types
    ntype.init = init
    ntype.draw_buttons = draw_buttons
    ntype.draw_buttons_ext = draw_buttons_ext
    ntype.copy = copy
    ntype.filepaths = filepaths
    ntype.free = free
    ntype.draw_label = draw_label
    if category == 'surface':
        ntype.traverse_tree = traverse_tree
        ntype.tree = []
        ntype.node_type = 'osl_surface'

    util.safe_register_class(ntype)

    return ntype.bl_idname, category


def register():
    pass


def unregister():
    pass
