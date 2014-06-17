from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import sys

if sys.platform == 'win32':
    modules = [ 'util', 'project_file_writer', 'mesh_writer']
else:
    modules = [ 'util', 'project_file_writer', 'mesh_writer_unix']
 
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
