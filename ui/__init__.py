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

import bl_ui.properties_data_mesh as properties_data_mesh

from . import camera
from . import lamps
from . import materials
from . import meshes
from . import objects
from . import render
from . import scene
from . import textures
from . import world

# Enable all existing panels for these contexts
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

import bl_ui.properties_physics_common as properties_physics_common

for member in dir(properties_physics_common):
    subclass = getattr(properties_physics_common, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_common

import bl_ui.properties_physics_cloth as properties_physics_cloth

for member in dir(properties_physics_cloth):
    subclass = getattr(properties_physics_cloth, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_cloth

import bl_ui.properties_physics_dynamicpaint as properties_physics_dynamicpaint

for member in dir(properties_physics_dynamicpaint):
    subclass = getattr(properties_physics_dynamicpaint, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_dynamicpaint

import bl_ui.properties_physics_field as properties_physics_field

for member in dir(properties_physics_field):
    subclass = getattr(properties_physics_field, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_field

import bl_ui.properties_physics_fluid as properties_physics_fluid

for member in dir(properties_physics_fluid):
    subclass = getattr(properties_physics_fluid, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_fluid

import bl_ui.properties_physics_rigidbody as properties_physics_rigidbody

for member in dir(properties_physics_rigidbody):
    subclass = getattr(properties_physics_rigidbody, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_rigidbody

import bl_ui.properties_physics_rigidbody_constraint as properties_physics_rigidbody_constraint

for member in dir(properties_physics_rigidbody_constraint):
    subclass = getattr(properties_physics_rigidbody_constraint, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_rigidbody_constraint

import bl_ui.properties_physics_smoke as properties_physics_smoke

for member in dir(properties_physics_smoke):
    subclass = getattr(properties_physics_smoke, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_smoke

import bl_ui.properties_physics_softbody as properties_physics_softbody

for member in dir(properties_physics_softbody):
    subclass = getattr(properties_physics_softbody, member)
    try:
        subclass.COMPAT_ENGINES.add('APPLESEED_RENDER')
    except:
        pass
del properties_physics_softbody


def register():
    render.register()
    scene.register()
    textures.register()
    world.register()
    materials.register()
    meshes.register()
    camera.register()
    objects.register()
    #    particles.register()
    lamps.register()


def unregister():
    lamps.unregister()
    #    particles.unregister()
    objects.unregister()
    camera.unregister()
    meshes.unregister()
    materials.unregister()
    world.unregister()
    textures.unregister()
    scene.unregister()
    render.unregister()
