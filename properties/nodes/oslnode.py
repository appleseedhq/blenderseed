
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
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
from ...util import asUpdate, filter_params
from . import AppleseedNode, AppleseedSocket


class AppleseedOSLInSocket(NodeSocket, AppleseedSocket):
    """appleseed OSL base socket"""

    bl_idname = "AppleseedOSLInSocket"
    bl_label = "OSL Socket"

    is_closure = False

    socket_value = ''

    socket_default_value = None

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
    name = node['name']
    category = node['category']
    input_sockets = node['inputs']
    output_sockets = node['outputs']
    non_connected_props = []

    socket_input_names = []
    socket_output_names = []

    # create socket classes
    for in_socket in input_sockets:
        if in_socket['hidden']:
            continue
        if not in_socket['connectable']:
            non_connected_props.append(in_socket)
        else:
            helper = ""
            minimum = None
            maximum = None
            socket_name = 'Appleseed%s%s' % (node['name'], in_socket['name'].capitalize())
            if 'label' in in_socket.keys():
                socket_label = "%s" % in_socket['label']
            else:
                socket_label = "%s" % in_socket['name'].strip('in_')
            if 'help' in in_socket.keys():
                helper = in_socket['help']
            if 'min' in in_socket.keys():
                minimum = in_socket['min']
            if 'max' in in_socket.keys():
                maximum = in_socket['max']

            stype = type(socket_name, (AppleseedOSLInSocket,), {})
            stype.bl_idname = socket_name
            stype.bl_label = socket_label
            stype.socket_osl_id = in_socket['name']
            socket_type = in_socket['type']
            if socket_type == 'float':
                stype.draw_color = draw_color_float
                if minimum:
                    stype.socket_value = bpy.props.FloatProperty(name=in_socket['name'],
                                                                 description=helper,
                                                                 default=float(in_socket['default']),
                                                                 min=float(minimum))

                if maximum:
                    stype.socket_value = bpy.props.FloatProperty(name=in_socket['name'],
                                                                 description=helper,
                                                                 default=float(in_socket['default']),
                                                                 max=float(maximum))

                if minimum and maximum:
                    stype.socket_value = bpy.props.FloatProperty(name=in_socket['name'],
                                                                 description=helper,
                                                                 default=float(in_socket['default']),
                                                                 min=float(minimum),
                                                                 max=float(maximum))

                else:
                    stype.socket_value = bpy.props.FloatProperty(name=in_socket['name'],
                                                                 description=helper,
                                                                 default=float(in_socket['default']))

            elif socket_type == 'color':
                stype.draw_color = draw_color_color
                stype.socket_value = bpy.props.FloatVectorProperty(name=in_socket['name'],
                                                                   description=helper,
                                                                   subtype='COLOR',
                                                                   default=(float(in_socket['default'].split(" ")[0]),
                                                                            float(in_socket['default'].split(" ")[1]),
                                                                            float(in_socket['default'].split(" ")[2])),
                                                                   min=0.0,
                                                                   max=1.0)

            elif socket_type == 'pointer':
                stype.draw_color = draw_closure_color
                stype.hide_ui = True

            elif socket_type in ('vector', 'output vector'):
                stype.draw_color = draw_vector_color
                if 'default' in in_socket.keys():
                    stype.socket_value = bpy.props.FloatVectorProperty(name=in_socket['name'],
                                                                       description=helper,
                                                                       default=(float(in_socket['default'].split(" ")[0]),
                                                                                float(in_socket['default'].split(" ")[1]),
                                                                                float(in_socket['default'].split(" ")[2])))
                else:
                    stype.socket_value = bpy.props.FloatVectorProperty(name=in_socket['name'],
                                                                       description=helper)
                stype.hide_ui = True

            elif socket_type == 'int':
                stype.draw_color = draw_color_float
                stype.socket_value = bpy.props.IntProperty(name=in_socket['name'],
                                                           description=helper,

                                                           default=int(in_socket['default']))

            elif socket_type == 'normal':
                stype.draw_color = draw_vector_color
                stype.hide_ui = True

            elif socket_type == 'matrix':
                stype.draw_color = draw_matrix_color
                stype.hide_ui = True

            elif socket_type in ('point', 'point[4]'):
                stype.draw_color = draw_point_color
                stype.hide_ui = True

            elif socket_type in ('float[2]'):
                stype.draw_color = draw_uv_color
                stype.hide_ui = True

            parameter_types[in_socket['name']] = in_socket['type']
            if 'default' in in_socket.keys():
                stype.socket_default_value = in_socket['default']
            bpy.utils.register_class(stype)

            socket_input_names.append([socket_name, socket_label])

    # create outp-ut socket classes
    for out_socket in output_sockets:
        socket_name = 'Appleseed%s%s' % (node['name'], out_socket['name'].capitalize())
        if 'label' in out_socket.keys():
            socket_label = "%s" % out_socket['label']
        else:
            socket_label = "%s" % out_socket['name'].strip("out_out")

        stype = type(socket_name, (AppleseedOSLOutSocket,), {})
        stype.bl_idname = socket_name
        stype.bl_label = socket_label
        stype.socket_osl_id = out_socket['name']
        socket_type = out_socket['type']
        if socket_type in ('output float[4]', 'output float'):
            stype.draw_color = draw_color_float
        elif socket_type in ('output color', 'output color[4]'):
            stype.draw_color = draw_color_color
        elif socket_type in ('output normal'):
            stype.draw_color = draw_vector_color
        elif socket_type in ('output pointer'):
            stype.draw_color = draw_closure_color
        elif socket_type in ('vector', 'output vector'):
            stype.draw_color = draw_vector_color
        elif socket_type == 'output matrix':
            stype.draw_color = draw_matrix_color
        elif socket_type in ('output point', 'output point[4]'):
            stype.draw_color = draw_point_color
        elif socket_type in ('output float[2]'):
            stype.draw_color = draw_uv_color
        else:
            pass

        bpy.utils.register_class(stype)

        socket_output_names.append([socket_name, socket_label])

    # create node clas
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
        asUpdate("Removing node ", self)

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
        return filter_params(self.tree)

    node_name = "Appleseed%sNode" % name
    node_label = "%s" % name

    ntype = type(node_name, (AppleseedOSLNode,), {})
    ntype.bl_idname = node_name
    ntype.bl_label = node_label
    setattr(ntype, 'file_name', node['filename'])

    def draw_buttons(self, context, layout):
        for x in non_connected_props:
            layout.prop(self, x['name'], text=x['label'])

    for prop in non_connected_props:
        widget = ""
        minimum = None
        maximum = None

        if 'widget' in prop.keys():
            widget = prop['widget']
        prop_name = prop['name']
        if 'label' not in prop.keys():
            prop['label'] = prop_name
        if 'help' in prop.keys():
            helper = prop['help']
        else:
            helper = ""
        if 'min' in prop.keys():
            minimum = prop['min']
        if 'max' in prop.keys():
            maximum = prop['max']

        if prop['type'] == 'string':
            if prop['use_file_picker'] == True:
                setattr(ntype, prop_name, bpy.props.StringProperty(name=prop['label'],
                                                                   description=helper,
                                                                   subtype='FILE_PATH'))
            else:
                setattr(ntype, prop_name, bpy.props.StringProperty(name=prop['label'],
                                                                   description=helper))
            parameter_types[prop['name']] = "string"

        if prop['type'] == 'intenum':
            items = []
            for enum_item in prop['options']:
                if widget == 'mapper':
                    items.append((enum_item.split(":")[1], enum_item.split(":")[0], ""))
                    parameter_types[prop_name] = "int"
                else:
                    items.append((enum_item, enum_item.capitalize(), ""))
                    parameter_types[prop_name] = "string"
                setattr(ntype, prop_name, bpy.props.EnumProperty(name=prop['label'],
                                                                 description=helper,
                                                                 default=prop['default'],
                                                                 items=items))

        elif prop['type'] == 'int':
            if widget in ('checkBox', 'null'):
                setattr(ntype, prop_name, bpy.props.BoolProperty(name=prop['name'],
                                                                 description=helper,
                                                                 default=bool(int(prop['default']))))
                parameter_types[prop['name']] = "int checkbox"

            else:
                if minimum:
                    setattr(ntype, prop_name, bpy.props.IntProperty(name=prop['name'],
                                                                    description=helper,
                                                                    default=int(prop['default']),
                                                                    min=int(minimum)))

                elif minimum and maximum:
                    setattr(ntype, prop_name, bpy.props.IntProperty(name=prop['name'],
                                                                    description=helper,
                                                                    default=int(prop['default']),
                                                                    min=int(minimum),
                                                                    max=int(maximum)))

                elif maximum:
                    setattr(ntype, prop_name, bpy.props.IntProperty(name=prop['name'],
                                                                    description=helper,
                                                                    default=int(prop['default']),
                                                                    max=int(maximum)))
                else:
                    setattr(ntype, prop_name, bpy.props.IntProperty(name=prop['name'],
                                                                    description=helper,
                                                                    default=int(prop['default'])))
                parameter_types[prop['name']] = "int"

        elif prop['type'] == 'float':
            if minimum:
                setattr(ntype, prop_name, bpy.props.FloatProperty(name=prop['name'],
                                                                  description=helper,
                                                                  default=float(prop['default']),
                                                                  min=float(minimum)))
            elif minimum and maximum:
                setattr(ntype, prop_name, bpy.props.FloatProperty(name=prop['name'],
                                                                  description=helper,
                                                                  default=float(prop['default']),
                                                                  min=float(minimum),
                                                                  max=float(maximum)))

            elif maximum:
                setattr(ntype, prop_name, bpy.props.FloatProperty(name=prop['name'],
                                                                  description=helper,
                                                                  default=float(prop['default']),
                                                                  max=float(maximum)))

            else:
                setattr(ntype, prop_name, bpy.props.FloatProperty(name=prop['name'],
                                                                  description=helper,
                                                                  default=float(prop['default'])))
            parameter_types[prop['name']] = "float"

        elif prop['type'] == 'color':
            setattr(ntype, prop_name, bpy.props.FloatVectorProperty(name=prop['name'],
                                                                    description=helper,
                                                                    subtype='COLOR',
                                                                    default=(float(in_socket['default'].split(" ")[0]),
                                                                             float(in_socket['default'].split(" ")[1]),
                                                                             float(in_socket['default'].split(" ")[2])),
                                                                    min=0.0,
                                                                    max=1.0))

            parameter_types[prop['name']] = "color"

    ntype.parameter_types = parameter_types
    ntype.init = init
    ntype.draw_buttons = draw_buttons
    ntype.draw_buttons_ext = draw_buttons_ext
    ntype.copy = copy
    ntype.free = free
    ntype.draw_label = draw_label
    if category == 'surface':
        ntype.traverse_tree = traverse_tree
        ntype.tree = []
        ntype.node_type = 'osl_surface'

    bpy.utils.register_class(ntype)

    return ntype.bl_idname, category


def register():
    pass


def unregister():
    pass
