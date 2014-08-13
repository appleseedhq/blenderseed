from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import sys

modules = set()

if sys.platform == 'win32':
    mesh_writer = 'mesh_writer'
else:
    mesh_writer = 'mesh_writer_unix'

# Test for selective compiling
args = sys.argv
if 'mesh_writer' in args:
    modules.update( mesh_writer)
    print( "Compiling %s module" % mesh_writer)
    
elif 'project_file_writer' in args:
    modules.update( 'project_file_writer')
    print( "Compiling project_file_writer module")
    
elif 'util' in args:
    modules.update( 'util')    
    print( "Compiling util module")
    
else:
    modules = { mesh_writer, 'project_file_writer', 'util'}
    print( "Compiling all modules")
    
for module in modules:
    ext_module = Extension(
        "%s" % module,
        ["%s.pyx" % module]
    )
        
    setup(
        name = 'Module',
        cmdclass = {'build_ext': build_ext},
        ext_modules = [ext_module]
    )
    
if sys.platform != 'win32':
    import os
    from shutil import copyfile
    files = os.listdir( os.getcwd())
    for i in files:
        if 'cpython-34m.so' in i:
            filename = i.replace( '.cpython-34m', '')
            copyfile( os.path.join( os.getcwd(), i), os.path.join( os.getcwd(), filename))
            os.remove( os.path.join( os.getcwd(), i))
