
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

import bpy
import bl_ui
from . import render
from . import scene
from . import world
from . import camera
from . import objects
from . import materials
from . import lamps

import bl_ui.properties_texture as properties_texture
INCLUDE_TEXTURE = ['TEXTURE_MT_specials', 'TEXTURE_PT_context_texture', 'TEXTURE_PT_image', 'TEXTURE_UL_texslots', 'Panel',
                   'Object', 'Material', 'Texture', 'TextureSlotPanel', 'TextureButtonsPanel', 'UIList', 'id_tex_datablock', 'context_tex_datablock']
for member in dir(properties_texture):
    if member in INCLUDE_TEXTURE:
        subclass = getattr(properties_texture, member)
        try:
            subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
        except:
            pass
del properties_texture

# Enable all existing panels for these contexts

import bl_ui.properties_data_mesh as properties_data_mesh
for member in dir(properties_data_mesh):
    subclass = getattr(properties_data_mesh, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_data_mesh

import bl_ui.properties_particle as properties_particle
for member in dir(properties_particle):
    subclass = getattr(properties_particle, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_particle


def register():
    render.register()
    scene.register()
    world.register()
    materials.register()
    camera.register()
    objects.register()
#    particles.register()
    lamps.register()


def unregister():
    render.unregister()
    scene.unregister()
    world.unregister()
    materials.unregister()
    camera.unregister()
    objects.unregister()
#    particles.unregister()
    lamps.unregister()
