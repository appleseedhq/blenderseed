from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

compile_util = False

if compile_util:
    ext_module = Extension(
        "util",
        ["util.pyx"]
    )
else:
    ext_module = Extension(
    "project_file_writer",
    ["project_file_writer.pyx"]
    )
    
setup(
    name = 'Module',
    cmdclass = {'build_ext': build_ext},
    ext_modules = [ext_module]
)
