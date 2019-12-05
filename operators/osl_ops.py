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


import bpy

import appleseed as asr
from ..properties.nodes import AppleseedOSLScriptNode
from ..utils import path_util, osl_utils, util


class ASMAT_OT_compile_script(bpy.types.Operator):
    bl_idname = "appleseed.compile_osl_script"
    bl_label = "Compile OSL Script Node Parameters"

    def execute(self, context):
        temp_values = dict()
        input_connections = dict()
        output_connections = dict()

        material = context.object.active_material
        node_tree = material.node_tree
        node = node_tree.nodes.active
        location = node.location
        width = node.width
        script = node.script

        if node.script is not None:
            # Save existing connections and parameters
            for key, value in node.items():
                temp_values[key] = value
            for input_iter in node.inputs:
                if input_iter.is_linked:
                    input_connections[input_iter.bl_idname] = input_iter.links[0].from_socket
            for output in node.outputs:
                if output.is_linked:
                    outputs = []
                    for link in output.links:
                        outputs.append(link.to_socket)
                    output_connections[output.bl_idname] = outputs

            stdosl_path = path_util.get_stdosl_paths()
            compiler = asr.ShaderCompiler(stdosl_path)
            osl_bytecode = osl_utils.compile_osl_bytecode(compiler,
                                                          script)

            if osl_bytecode is not None:
                q = asr.ShaderQuery()
                q.open_bytecode(osl_bytecode)

                node_data = osl_utils.parse_shader(q)

                node_name, node_category, node_classes = osl_utils.generate_node(node_data,
                                                                                 AppleseedOSLScriptNode)

                for cls in reversed(node.classes):
                    util.safe_unregister_class(cls)

                for cls in node_classes:
                    util.safe_register_class(cls)

                node_tree.nodes.remove(node)
                new_node = node_tree.nodes.new(node_name)
                new_node.location = location
                new_node.width = width
                new_node.classes.extend(node_classes)
                setattr(new_node, "node_type", "osl_script")

                # Copy variables to new node
                for variable, value in temp_values.items():
                    if variable in dir(new_node):
                        setattr(new_node, variable, value)

                # Recreate node connections
                for connection, sockets in output_connections.items():
                    for output in new_node.outputs:
                        if output.bl_idname == connection:
                            output_socket_class = output
                    if output_socket_class:
                        for output_connection in sockets:
                            node_tree.links.new(output_socket_class,
                                                output_connection)
                for connection, sockets in input_connections.items():
                    for in_socket in new_node.inputs:
                        if in_socket.bl_idname == connection:
                            input_socket_class = in_socket
                    if input_socket_class:
                        for input_connection in sockets:
                            node_tree.links.new(input_socket_class,
                                                input_connection)

            else:
                self.report(
                    {'ERROR'}, "appleseed - OSL script did not compile!")

        else:
            self.report({'ERROR'}, "appleseed - No OSL script selected!")

        return {'FINISHED'}


def register():
    util.safe_register_class(ASMAT_OT_compile_script)


def unregister():
    util.safe_unregister_class(ASMAT_OT_compile_script)
