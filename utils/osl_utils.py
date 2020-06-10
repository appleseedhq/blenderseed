#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2019 Jonathan Dent, The appleseedhq Organization
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

import appleseed as asr
import bpy

from . import path_util, util
from ..logger import get_logger
from ..properties.nodes import AppleseedOSLSocket

logger = get_logger()


def generate_node(node, node_class):
    """
    Generates a node based on the provided node data

    Node data consists of a dictionary containing node metadata and lists of inputs and outputs
    """

    # Function templates
    def draw_color_float(self, context, node):
        return 0.5, 0.5, 0.5, 1.0

    def draw_color_color(self, context, node):
        return 0.8, 0.8, 0.5, 1.0

    def draw_closure_color(self, context, node):
        return 0.0, 0.8, 0.0, 1.0

    def draw_default_color(self, context, node):
        return 1.0, 1.0, 1.0, 1.0

    def draw_vector_color(self, context, node):
        return 0.67, 0.45, 1.0, 1.0

    def draw_point_color(self, context, node):
        return 0.0, 0.0, 1.0, 1.0

    def draw_uv_color(self, context, node):
        return 0.6, 0.1, 0.0, 1.0

    def draw_matrix_color(self, context, node):
        return 1.0, 0.5, 1.0, 1.0

    def copy(self, node):
        pass

    def free(self):
        pass

    def draw_label(self):
        return self.bl_label

    def update_sockets(self, context):
        for input_socket in self.inputs:
            if input_socket.name in self.socket_ui_props:
                input_socket.hide = not getattr(self, "%s_use_node" % input_socket.name)

    node_classes = list()
    parameter_types = dict()
    filepaths = list()
    name = node['name']
    category = node['category']
    input_params = node['inputs']
    output_sockets = node['outputs']
    url_reference = node['url']

    socket_input_names = list()
    socket_output_names = list()

    # create output socket classes
    for out_socket in output_sockets:
        socket_name = "Appleseed{0}{1}".format(node['name'], out_socket['name'].capitalize())
        if 'label' in out_socket.keys():
            socket_label = "{0}".format(out_socket['label'])
        else:
            socket_label = "{0}".format(out_socket['name'].strip("out_"))

        stype = type(socket_name, (AppleseedOSLSocket,), {})
        stype.bl_idname = socket_name
        stype.bl_label = socket_label
        stype.socket_osl_id = out_socket['name']
        socket_type = out_socket['type']
        if socket_type in ('float[4]', 'float'):
            stype.draw_color = draw_color_float
        elif socket_type in ('color', 'color[4]'):
            stype.draw_color = draw_color_color
        elif socket_type == 'normal':
            stype.draw_color = draw_vector_color
        elif socket_type == 'pointer':
            stype.draw_color = draw_closure_color
        elif socket_type == 'vector':
            stype.draw_color = draw_vector_color
        elif socket_type == 'matrix':
            stype.draw_color = draw_matrix_color
        elif socket_type in ('point', 'point[4]'):
            stype.draw_color = draw_point_color
        elif socket_type == 'float[2]':
            stype.draw_color = draw_uv_color
        else:
            stype.draw_color = draw_default_color

        node_classes.append(stype)

        socket_output_names.append([socket_name, socket_label])

    # create input socket classes
    for param in input_params:
        keys = param.keys()

        hide_ui = False

        if not param['connectable']:
            continue

        if param['hide_ui'] is True:
            hide_ui = True

        socket_name = 'Appleseed{0}{1}'.format(node['name'], param['name'].capitalize())

        if 'label' in keys:
            socket_label = "{0}".format(param['label'])
        else:
            socket_label = "{0}".format(param['name'])

        stype = type(socket_name, (AppleseedOSLSocket,), {})
        stype.bl_idname = socket_name
        stype.bl_label = socket_label
        stype.socket_osl_id = param['name']
        socket_type = param['type']

        if socket_type == "float":
            stype.draw_color = draw_color_float

        elif socket_type == "color":
            stype.draw_color = draw_color_color

        elif socket_type == "pointer":
            stype.draw_color = draw_closure_color

        elif socket_type == "vector":
            stype.draw_color = draw_vector_color

        elif socket_type == 'int':
            stype.draw_color = draw_color_float

        elif socket_type == "float[2]":
            stype.draw_color = draw_uv_color

        elif socket_type == "normal":
            stype.draw_color = draw_vector_color

        elif socket_type == "matrix":
            stype.draw_color = draw_matrix_color

        elif socket_type in ("point", "point[4]"):
            stype.draw_color = draw_point_color

        node_classes.append(stype)

        socket_input_names.append({'socket_name': socket_name, 'socket_label': socket_label, 'hide_ui': hide_ui})

    # create node class
    node_name = "Appleseed{0}Node".format(name)
    node_label = "{0}".format(name)
    ntype = type(node_name, (node_class,), {})
    ntype.bl_idname = node_name
    ntype.bl_label = node_label
    ntype.file_name = node['filename']
    ntype.input_params = input_params
    ntype.output_sockets = output_sockets
    ntype.socket_input_names = socket_input_names
    ntype.socket_output_names = socket_output_names

    ntype.__annotations__ = dict()

    socket_ui_props = list()

    param_section = str()

    for param in input_params:
        keys = param.keys()
        widget = ""
        minimum = None
        maximum = None
        soft_minimum = None
        soft_maximum = None

        if param['section'] is not None:
            if param['section'] != param_section:
                param_section = param['section']
                ntype.__annotations__[param_section] = bpy.props.BoolProperty(name=param_section,
                                                                              default=False)

        if param['connectable'] is False and param['hide_ui'] is True:
            continue

        if 'default' in keys:
            default = param['default']
        if 'widget' in keys:
            widget = param['widget']

        prop_name = param['name']
        if 'label' not in keys:
            param['label'] = prop_name

        if 'connectable' in keys and param['connectable'] is True and param['hide_ui'] is not True:
            socket_ui_props.append(param['label'])

        if 'help' in keys:
            helper = param['help']
        else:
            helper = ""
        if 'min' in keys:
            minimum = param['min']
        if 'max' in keys:
            maximum = param['max']
        if 'softmin' in keys:
            soft_minimum = param['softmin']
        if 'softmax' in keys:
            soft_maximum = param['softmax']

        if param['type'] == "string":
            if widget == "filename":
                ntype.__annotations__[prop_name] = bpy.props.PointerProperty(name=param['name'],
                                                                             description=helper,
                                                                             type=bpy.types.Image)

                filepaths.append(prop_name)

            elif widget in ("mapper", "popup"):
                items = []
                for enum_item in param['options']:
                    items.append((enum_item, enum_item.capitalize(), ""))

                ntype.__annotations__[prop_name] = bpy.props.EnumProperty(name=param['label'],
                                                                          description=helper,
                                                                          default=str(default),
                                                                          items=items)

            else:
                ntype.__annotations__[prop_name] = bpy.props.StringProperty(name=param['name'],
                                                                            description=helper,
                                                                            default=str(default))

            parameter_types[param['name']] = param['type']

        elif param['type'] == "int":
            if widget != "" and widget in ("mapper", "popup"):
                items = []
                for enum_item in param['options']:
                    items.append((enum_item.split(":")[1], enum_item.split(":")[0], ""))
                    parameter_types[prop_name] = "int"

                ntype.__annotations__[prop_name] = bpy.props.EnumProperty(name=param['label'],
                                                                          description=helper,
                                                                          default=str(int(default)),
                                                                          items=items)

            elif widget != "" and widget == 'checkBox':
                kwargs = {'name': param['name'], 'description': helper, 'default': bool(int(default))}
                ntype.__annotations__[prop_name] = bpy.props.BoolProperty(**kwargs)
                parameter_types[param['name']] = "int checkbox"

            else:
                kwargs = {'name': param['name'], 'description': helper, 'default': int(default)}
                if minimum is not None:
                    kwargs['min'] = int(minimum)
                if maximum is not None:
                    kwargs['max'] = int(maximum)
                if soft_minimum is not None:
                    kwargs['soft_min'] = int(soft_minimum)
                if soft_maximum is not None:
                    kwargs['soft_max'] = int(soft_maximum)

                ntype.__annotations__[prop_name] = bpy.props.IntProperty(**kwargs)

                parameter_types[param['name']] = param['type']

        elif param['type'] == "float":

            kwargs = {'name': param['name'], 'description': helper, 'default': float(default)} if 'default' in keys else {'name': param['name'], 'description': helper}
            if minimum is not None:
                kwargs['min'] = float(minimum)
            if maximum is not None:
                kwargs['max'] = float(maximum)
            if soft_minimum is not None:
                kwargs['soft_min'] = float(soft_minimum)
            if soft_maximum is not None:
                kwargs['soft_max'] = float(soft_maximum)

            ntype.__annotations__[prop_name] = bpy.props.FloatProperty(**kwargs)

            parameter_types[param['name']] = param['type']

        elif param['type'] == "float[2]":
            kwargs = {'name': param['name'], 'description': helper, 'size': 2}
            if 'default' in keys:
                kwargs['default'] = (float(default[0]),
                                     float(default[1]))

            ntype.__annotations__[prop_name] = bpy.props.FloatVectorProperty(**kwargs)

            parameter_types[param['name']] =  param['type']

        elif param['type'] == 'color':
            ntype.__annotations__[prop_name] = bpy.props.FloatVectorProperty(name=param['name'],
                                                                             description=helper,
                                                                             subtype='COLOR',
                                                                             default=(float(default[0]),
                                                                                      float(default[1]),
                                                                                      float(default[2])),
                                                                             min=0.0,
                                                                             max=1.0)

            parameter_types[param['name']] = param['type']

        elif param['type'] in ('vector', 'point', 'normal'):
            kwargs = {'name': param['name'], 'description': helper}

            if 'default' in keys:
                kwargs['default'] = (float(default[0]),
                                     float(default[1]),
                                     float(default[2]))

            ntype.__annotations__[prop_name] = bpy.props.FloatVectorProperty(**kwargs)

            parameter_types[param['name']] = param['type']

        elif param['type'] == 'pointer':
            pass

    for prop in socket_ui_props:
        ntype.__annotations__["%s_use_node" % prop] = bpy.props.BoolProperty(name="%s_use_node" % prop,
                                                                             description="Use node input",
                                                                             default=False,
                                                                             update=update_sockets)

    ntype.__annotations__["script"] = bpy.props.PointerProperty(name="script",
                                                                type=bpy.types.Text)

    ntype.initialized = True
    ntype.socket_ui_props = socket_ui_props
    ntype.update_sockets = update_sockets
    ntype.parameter_types = parameter_types
    ntype.url_reference = url_reference
    ntype.copy = copy
    ntype.filepaths = filepaths
    ntype.free = free
    ntype.draw_label = draw_label
    if category == 'surface':
        ntype.node_type = 'osl_surface'

    node_classes.append(ntype)

    return ntype.bl_idname, category, node_classes


def read_osl_shaders():
    """
    Reads parameters from OSL .oso files using the ShaderQuery function that is built
    into the Python bindings for appleseed.  These parameters are used to create a dictionary
    of the shader parameters that is then added to a list.  This shader list is passed
    on to the oslnode.generate_node function.
    :return: List of parsed nodes
    """

    nodes = list()

    shader_directories = path_util.get_osl_search_paths()

    q = asr.ShaderQuery()

    logger.debug("[appleseed] Parsing OSL shaders...")

    for shader_dir in shader_directories:
        if os.path.isdir(shader_dir):
            logger.debug("[appleseed] Searching {0} for OSO files...".format(shader_dir))
            for file in os.listdir(shader_dir):
                if file.endswith(".oso") and os.path.basename(file) != "as_texture2surface.oso":
                    logger.debug("[appleseed] Reading {0}...".format(file))
                    filename = os.path.join(shader_dir, file)
                    q.open(filename)
                    nodes.append(parse_shader(q, filename=filename))

    logger.debug("[appleseed] OSL parsing complete.")

    return nodes


def parse_shader(q, filename=None):
    d = {'inputs': list(),
         'outputs': list()}
    shader_meta = q.get_metadata()
    if 'as_node_name' in shader_meta:
        d['name'] = shader_meta['as_node_name']['value']
    else:
        d['name'] = q.get_shader_name()
    d['filename'] = filename
    if 'URL' in shader_meta:
        d['url'] = shader_meta['URL']['value']
    else:
        d['url'] = ''
    if 'as_category' in shader_meta:
        d['category'] = shader_meta['as_category']['value']
    else:
        d['category'] = 'other'
    num_of_params = q.get_num_params()
    for x in range(0, num_of_params):
        metadata = dict()
        param = q.get_param_info(x)
        if 'metadata' in param:
            metadata = param['metadata']
        param_data = {'name': param['name'], 'type': param['type'], 'connectable': True, 'hide_ui': param['validdefault'] is False}
        if 'default' in param:
            param_data['default'] = param['default']
        if 'label' in metadata:
            param_data['label'] = metadata['label']['value']
        if 'widget' in metadata:
            param_data['widget'] = metadata['widget']['value']
            if param_data['widget'] == 'null':
                param_data['hide_ui'] = True
        param_data['section'] = metadata['page']['value'] if 'page' in metadata else None
        if 'min' in metadata:
            param_data['min'] = metadata['min']['value']
        if 'max' in metadata:
            param_data['max'] = metadata['max']['value']
        if 'softmin' in metadata:
            param_data['softmin'] = metadata['softmin']['value']
        if 'softmax' in metadata:
            param_data['softmax'] = metadata['softmax']['value']
        if 'help' in metadata:
            param_data['help'] = metadata['help']['value']
        if 'options' in metadata:
            param_data['options'] = metadata['options']['value'].split(" = ")[-1].replace("\"", "").split("|")
        if 'as_blender_input_socket' in metadata:
            param_data['connectable'] = False if metadata['as_blender_input_socket']['value'] == 0.0 else True
        if 'as_deprecated' in metadata:
            param_data['hide_ui'] = True
            param_data['connectable'] = False

        if param['isoutput'] is True:
            d['outputs'].append(param_data)
        else:
            d['inputs'].append(param_data)

    return d


def compile_osl_bytecode(compiler, script_block):
    osl_path = bpy.path.abspath(script_block.filepath, library=script_block.library)
    if script_block.is_in_memory or script_block.is_dirty or script_block.is_modified or not os.path.exists(osl_path):
        source_code = script_block.as_string()
    else:
        code = open(osl_path, 'r')
        source_code = code.read()
        code.close()

    return compiler.compile_buffer(source_code)
