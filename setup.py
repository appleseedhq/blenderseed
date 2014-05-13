from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_module = Extension(
    "util",
    ["util.pyx"]
)

setup(
    name = 'Util module',
    cmdclass = {'build_ext': build_ext},
    ext_modules = [ext_module]
)
