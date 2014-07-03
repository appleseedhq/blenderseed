
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2013 Franz Beaune, Joel Daniels, Esteban Tovagliari.
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
import os, sys
import multiprocessing
import datetime
from extensions_framework import util as efutil
from shutil import copyfile
from math import tan, atan, degrees
import mathutils
from . import bl_info

#------------------------------------
# Generic utilities and settings.
#------------------------------------
sep = os.sep

thread_count = multiprocessing.cpu_count()

EnableDebug = False

# Addon directory.
for addon_path in bpy.utils.script_paths("addons"):
    if "blenderseed" in os.listdir(addon_path):
        addon_dir = os.path.join(addon_path, "blenderseed")
        
version = str(bl_info['version'][1]) + "." + str(bl_info['version'][2])

def strip_spaces( name):
    return ('_').join( name.split(' '))

def join_names_underscore( name1, name2):
    return ('_').join( (strip_spaces( name1), strip_spaces( name2)))

def join_params( params, directive):
    return ('').join( (('').join( params), directive))

def filter_params( params):
    filter_list = []
    for p in params:
        if p not in filter_list:
            filter_list.append( p)
    return filter_list
        
def get_timestamp():
    now = datetime.datetime.now()
    return "%d-%d-%d %d:%d:%d\n" % (now.month, now.day, now.year, now.hour, now.minute, now.second)
    
def realpath(path):
    return os.path.realpath(efutil.filesystem_path(path))

def inscenelayer(object, scene):
    for i in range(len(object.layers)):
        if object.layers[i] == True and scene.layers[i] == True:
            return True
        else:
            continue
        
def do_export(obj, scene):
    return not obj.hide_render and obj.type in ('MESH', 'SURFACE', 'META', 'TEXT', 'CURVE', 'LAMP') and inscenelayer(obj, scene)

def debug( *args):
    msg = ' '.join(['%s'%a for a in args])
    global EnableDebug
    if EnableDebug:    
        print( "DEBUG:" ,msg)

def asUpdate( *args):
    msg = ' '.join(['%s'%a for a in args])
    print( "appleseed:" ,msg)

def resolution(scene):
    xr = scene.render.resolution_x * scene.render.resolution_percentage / 100.0
    yr = scene.render.resolution_y * scene.render.resolution_percentage / 100.0
    return xr, yr

def get_instance_materials(ob):
    obmats = []
    # Grab materials attached to object instances ...
    if hasattr(ob, 'material_slots'):
        for ms in ob.material_slots:
            obmats.append(ms.material)
    # ... and to the object's mesh data
    if hasattr(ob.data, 'materials'):
        for m in ob.data.materials:
            obmats.append(m)
    return obmats

def is_proxy(ob, scene):
    if ob.type == 'MESH' and ob.appleseed.is_proxy:
        if ob.appleseed.use_external:
            return ob.appleseed.external_instance_mesh != ''
        else:
            return ob.appleseed.instance_mesh is not None and scene.objects[ob.appleseed.instance_mesh].type == 'MESH'

def get_particle_matrix(ob):
    object_matrix = ob.matrix.copy()
    return object_matrix

def get_psys_instances(ob, scene):
    dupli_list = []
    if not hasattr(ob, 'modifiers'):
        return dupli_list
    for modifier in ob.modifiers:
        if modifier.type == 'PARTICLE_SYSTEM':
            psys = modifier.particle_system
            if not psys.settings.render_type in {'OBJECT', 'GROUP'}:
                continue
            ob.dupli_list_create(scene)
            for obj in ob.dupli_list:
                obj_matrix = get_particle_matrix( obj)
                # Append a list containing the matrix, and the object
                dupli_list.append([obj_matrix, obj.object])
            ob.dupli_list_clear()
    return dupli_list

def get_all_psysobs():
    obs = set()
    for settings in bpy.data.particles:
        if settings.render_type == 'OBJECT' and settings.dupli_object is not None:
            obs.add( settings.dupli_object)
        elif settings.render_type == 'GROUP' and settings.dupli_group is not None:
            obs.update( {ob for ob in settings.dupli_group.objects})
    return obs

def get_all_duplis( scene ):
    obs = set()
    for ob in scene.objects:
        if ob.parent and ob.parent.dupli_type in {'FACES', 'VERTS', 'GROUP'}:
            obs.add( ob)
    return obs
            
def get_matrix(obj):
    obj_mat = obj.matrix.copy()
    return obj_mat

def get_instances(obj_parent, scene, mblur = False):
    asr_scn = scene.appleseed
    obj_parent.dupli_list_create(scene)
    dupli_list = []
    if not mblur:
        for obj in obj_parent.dupli_list :
            obj_matrix = get_matrix( obj)
            dupli_list.append( [obj.object, obj_matrix])
    else:
        current_frame = scene.frame_current
        # Set frame for shutter open time
        scene.frame_set( current_frame, subframe = asr_scn.shutter_open)
        for obj in obj_parent.dupli_list:
            obj_matrix = obj.matrix.copy()
            dupli_list.append( [obj.object, obj_matrix])
            # Move to next frame, collect matrices
            scene.frame_set( current_frame, subframe = asr_scn.shutter_close)
            for dupli in dupli_list:
                dupli.append( obj.matrix.copy())
            # Reset to current frame
            scene.frame_set( current_frame)
    obj_parent.dupli_list_clear()
    return dupli_list

def render_emitter(ob):
    render = False
    for psys in ob.particle_systems:
        if psys.settings.use_render_emitter:
            render = True
            break
    return render

def is_psys_emitter( ob):
    emitter = False
    for mod in ob.modifiers:
        if mod.type == 'PARTICLE_SYSTEM' and mod.show_render:
            psys = mod.particle_system
            if psys.settings.render_type == 'OBJECT' and psys.settings.dupli_object is not None:
                emitter = True
                break
            elif psys.settings.render_type == 'GROUP' and psys.settings.dupli_group is not None:
                emitter = True
                break
    return emitter

def has_hairsys( ob):
    has_hair = False
    for mod in ob.modifiers:
        if mod.type == 'PARTICLE_SYSTEM' and mod.show_render:
            psys = mod.particle_system
            if psys.settings.type == 'HAIR' and psys.settings.render_type == 'PATH':
                has_hair = True
                break
    return has_hair

cdef calc_decrement( double first, double last, int segments):
    return (( 1 - (last / first)) / segments)
    
def get_hairs( obj, scene, psys, crv_ob, crv_data, mat_name):
    cdef int p, steps, num_parents, num_children, step
    cdef double p_rad, rad_decrement
    cdef double root_size, tip_size
    root_size = psys.settings.appleseed.root_size
    tip_size = psys.settings.appleseed.tip_size
    # Set the render resolution of the particle system
    psys.set_resolution( scene, obj, 'RENDER')
    steps = 2 ** psys.settings.render_step + 1
    num_parents = len( psys.particles)
    num_children = len( psys.child_particles)
    transform = obj.matrix_world.inverted()      
    crv = bpy.data.curves.new( 'appleseed_hair_curve', 'CURVE') 
    for p in range( 0, num_parents + num_children):   
        crv.splines.new( 'NURBS')
        points = crv.splines[p].points
        crv.splines[p].points.add( steps - 1)
        crv.splines[p].use_endpoint_u = True
        crv.splines[p].order_u = 4
        p_rad = 1.0
        rad_decrement = calc_decrement( root_size, tip_size, steps)
        for step in range(0, steps):
            co = psys.co_hair( obj, p, step)
            points[step].co = mathutils.Vector( ( co.x, co.y, co.z, 1.0)) 
            points[step].radius = p_rad
            p_rad -= rad_decrement
    # Transform the curve.
    crv.transform( transform)
    crv.dimensions = '3D'
    crv.fill_mode = 'FULL'
    if psys.settings.appleseed.shape == 'thick':
        crv.bevel_depth = psys.settings.appleseed.scaling
        crv.bevel_resolution = psys.settings.appleseed.resolution
    else: 
        crv.extrude = psys.settings.appleseed.scaling
    crv.resolution_u = 1   
    # Create an object for the curve, add the material, then convert to mesh
    crv_ob.data = bpy.data.curves[crv.name]
    crv_ob.data.materials.append( bpy.data.materials[mat_name])
    mesh = crv_ob.to_mesh( scene, True, 'RENDER', calc_tessface = True)
    crv_ob.data = crv_data
    # Remove the curve.
    bpy.data.curves.remove( crv)
    psys.set_resolution( scene, obj, 'PREVIEW')
    return mesh
    
def get_camera_matrix( camera, global_matrix):
    camera_mat = global_matrix * camera.matrix_world
    origin = camera_mat.col[3]
    forward = -camera_mat.col[2]
    up = camera_mat.col[1]
    target = origin + forward
    return origin, forward, up, target

def is_uv_img( tex):
    if tex and tex.type == 'IMAGE' and tex.image:
        return True

    return False

def ob_mblur_enabled( object, scene):
    return object.appleseed.mblur_enable and object.appleseed.mblur_type == 'object' and scene.appleseed.mblur_enable and scene.appleseed.ob_mblur

def def_mblur_enabled( object, scene):
    return object.appleseed.mblur_enable and object.appleseed.mblur_type == 'deformation' and scene.appleseed.mblur_enable and scene.appleseed.def_mblur

def calc_fov(camera_ob, width, height):
    ''' 
    Calculate horizontal FOV if rendered height is greater than rendered with
    Thanks to NOX exporter developers for this and the next solution 
    '''
    camera_angle = degrees(camera_ob.data.angle)
    if width < height:
        length = 18.0/tan(camera_ob.data.angle/2)
        camera_angle = 2*atan(18.0*width/height/length)
        camera_angle = degrees(camera_angle)
    return camera_angle
