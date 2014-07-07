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


def get_all_psysobs():
    '''
    Return a set of all the objects being instanced in particle systems
    '''
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


def get_instances(obj_parent, scene):
    '''
    Get the instanced objects on the parent object (dupli-faces / dupli-verts).
    If motion blur is not enabled, returns list of lists [ [dupli_object.object, dupli matrix]]
    If motion blur is enabled, returns a nested list: [ [dupli_object.object, [dupli matrices]]]
    '''
    dupli_list = []
    if ob_mblur_enabled( obj_parent, scene):
        dupli_list = sample_mblur( obj_parent, scene, dupli = True)
    else:
        obj_parent.dupli_list_create( scene)
        for dupli in obj_parent.dupli_list :
            dupli_matrix = dupli.matrix.copy() 
            dupli_list.append( [ dupli.object, dupli_matrix])
        obj_parent.dupli_list_clear()
    return dupli_list


def sample_mblur( ob, scene, dupli = False):
    '''
    Sample motion blur matrices for the object or duplis.
    Returns a list of matrices, if an object only.
    Returns a nested list of [ [dupli_object.object, [dupli matrix 1, dupli matrix 2]]]
    '''
    matrices = []
    asr_scn = scene.appleseed
    frame_orig = scene.frame_current
    frame_set = scene.frame_set

    # Collect matrices at shutter open.
    frame_set( frame_orig, subframe = asr_scn.shutter_open)
    ob.dupli_list_create( scene)
    for dupli in ob.dupli_list:
        matrices.append( [dupli.object, [dupli.matrix.copy(),]])
    ob.dupli_list_clear()

    # Advance to shutter close, collect matrices.
    frame_set( frame_orig, subframe = asr_scn.shutter_close)
    ob.dupli_list_create( scene)
    for m in range( 0, len(ob.dupli_list)):
        matrices[m][1].append( ob.dupli_list[m].matrix.copy())
    ob.dupli_list_clear()
    
    # Reset timeline and return.
    frame_set( frame_orig)
    return matrices


def get_psys_instances(ob, scene):
    ''' 
    Return a dictionary of 
    particle: [dupli.object, [matrices]] 
    pairs. This function assumes particle systems and 
    face / verts duplication aren't being used on the same object.
    '''
    all_duplis = {}
    current_total = 0
    if not hasattr(ob, 'modifiers'):
        return {}
    if not ob_mblur_enabled( ob, scene):   
        # If no motion blur
        ob.dupli_list_create(scene, settings = 'RENDER')
    for modifier in ob.modifiers:
        if modifier.type == 'PARTICLE_SYSTEM' and modifier.show_render:
            psys = modifier.particle_system
            if not psys.settings.render_type in {'OBJECT', 'GROUP'}:
                continue
            if psys.settings.type == 'EMITTER':
                particles = [p for p in psys.particles if p.alive_state == 'ALIVE']
            else:
                particles = [p for p in psys.particles]
            start = current_total
            current_total += len( particles)
            
            if not ob_mblur_enabled( ob, scene):   
                # No motion blur.
                duplis = []
                for index in range( start, current_total):
                    # Store the dupli.objects for the current particle system only
                    # ob.dupli_list is created in descending order of particle systems
                    # So it should be reliable to match them this way.
                    duplis.append( ob.dupli_list[index].object)
                    
                p_duplis_pairs = list( zip( particles, duplis))     # Match the particles to the duplis
                dupli_dict = {p[0]:[ p[1], []] for p in p_duplis_pairs}  # Create particle:[dupli.object, [matrix]] pairs
                if psys.settings.type == 'EMITTER':
                    for particle in dupli_dict.keys():
                        size = particle.size
                        loc = particle.location
                        scale = dupli_dict[particle][0].scale * size
                        transl = mathutils.Matrix.Translation(( loc))
                        scale = mathutils.Matrix.Scale(scale.x, 4, (1,0,0)) * mathutils.Matrix.Scale(scale.y, 4, (0,1,0)) * mathutils.Matrix.Scale(scale.z, 4, (0,0,1))
                        mat = transl * scale
                        dupli_dict[particle][1].append(mat)
                else:
                    index = 0
                    for particle in dupli_dict.keys():
                        mat = ob.dupli_list[index].matrix.copy()
                        dupli_dict[particle][1].append(mat)
                        index += 1
            else:
                # Using motion blur       
                dupli_dict = sample_psys_mblur( ob, scene, psys)
                     
            # Add current particle system to the collection.
            all_duplis.update( dupli_dict)  
            
    if not ob_mblur_enabled( ob, scene):   
        # If no motion blur
        ob.dupli_list_clear()               
    return all_duplis


def sample_psys_mblur( ob, scene, psys):
    '''
    Return a dictionary of 
    particle: [dupli.object, [matrices]] 
    pairs
    '''
    asr_scn = scene.appleseed
    dupli_dict = {}
    frame_orig = scene.frame_current
    frame_set = scene.frame_set
    
    frame_set( frame_orig, subframe = asr_scn.shutter_open)
    if psys.settings.type == 'EMITTER':
        particles = [p for p in psys.particles if p.alive_state == 'ALIVE']
    else: 
        particles = [p for p in psys.particles]
    if len(particles) == 0:
        return False
    ob.dupli_list_create( scene)
    duplis = [dupli.object for dupli in ob.dupli_list]
    p_duplis_pairs = list( zip( particles, duplis))
    dupli_dict = {p[0]:[ p[1], []] for p in p_duplis_pairs}

    for frame in {asr_scn.shutter_open, asr_scn.shutter_close}:
        frame_set( frame_orig, subframe = frame)
        for particle in dupli_dict.keys():
            size = particle.size 
            transl = particle.location
            scale = dupli_dict[particle][0].scale * size
            transl = mathutils.Matrix.Translation(( transl))
            scale = mathutils.Matrix.Scale(scale.x, 4, (1,0,0)) * mathutils.Matrix.Scale(scale.y, 4, (0,1,0)) * mathutils.Matrix.Scale(scale.z, 4, (0,0,1))
            mat = transl * scale
            if psys.settings.type == 'HAIR':
                mat *= ob.matrix_world.inverted().copy()
            dupli_dict[particle][1].append(mat)

    # Clean up and return
    if psys.settings.type == 'EMITTER':
        del scale, transl, mat
    ob.dupli_list_clear()
    frame_set( frame_orig)
    return dupli_dict

    
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
    
def get_camera_matrix( camera, global_matrix):
    '''
    Get the camera transformation decomposed as origin, forward, up and target.
    '''
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
    Thanks to NOX exporter developers for this solution.
    '''
    camera_angle = degrees(camera_ob.data.angle)
    if width < height:
        length = 18.0/tan(camera_ob.data.angle/2)
        camera_angle = 2*atan(18.0*width/height/length)
        camera_angle = degrees(camera_angle)
    return camera_angle

def calc_decrement( first, last, segments):
    return (( 1 - (last / first)) / segments)
    
def get_hairs( obj, scene, psys, crv_ob, crv_data, mat_name):
    '''
    Get hair curves as mesh objects.
    '''
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

