#!/usr/bin/python

#
# This source file is part of appleseed.
# Visit https://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2017-2018 Esteban Tovagliari, The appleseedhq Organization
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from __future__ import print_function
from distutils import archive_util, dir_util
from xml.etree.ElementTree import ElementTree
import argparse
import colorama
import datetime
import glob
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import time
import traceback
import urllib


#--------------------------------------------------------------------------------------------------
# Constants.
#--------------------------------------------------------------------------------------------------

VERSION = "1.1.0"
SETTINGS_FILENAME = "blenderseed.package.configuration.xml"


#--------------------------------------------------------------------------------------------------
# Utility functions.
#--------------------------------------------------------------------------------------------------

GREEN_CHECKMARK = u"{0}\u2713{1}".format(colorama.Style.BRIGHT + colorama.Fore.GREEN, colorama.Style.RESET_ALL)
RED_CROSSMARK = u"{0}\u2717{1}".format(colorama.Style.BRIGHT + colorama.Fore.RED, colorama.Style.RESET_ALL)


def trace(message):
    # encode('utf-8') is required to support output redirection to files or pipes.
    print(u"  {0}{1}{2}".format(colorama.Style.DIM + colorama.Fore.WHITE, message, colorama.Style.RESET_ALL).encode('utf-8'))


def info(message):
    print(u"  {0}".format(message).encode('utf-8'))


def progress(message):
    print(u"  {0}...".format(message).encode('utf-8'))


def warning(message):
    print(u"  {0}Warning: {1}.{2}".format(colorama.Style.BRIGHT + colorama.Fore.MAGENTA, message, colorama.Style.RESET_ALL).encode('utf-8'))


def fatal(message):
    print(u"{0}Fatal: {1}. Aborting.{2}".format(colorama.Style.BRIGHT + colorama.Fore.RED, message, colorama.Style.RESET_ALL).encode('utf-8'))
    if sys.exc_info()[0]:
        print(traceback.format_exc())
    sys.exit(1)


def exe(filepath):
    return filepath + ".exe" if os.name == "nt" else filepath


def safe_delete_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        fatal("Failed to delete file '" + path + "'")


def on_rmtree_error(func, path, exc_info):
    # path contains the path of the file that couldn't be removed.
    # Let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def safe_delete_directory(path):
    Attempts = 10
    for attempt in range(Attempts):
        try:
            if os.path.exists(path):
                shutil.rmtree(path, onerror=on_rmtree_error)
            return
        except OSError:
            if attempt < Attempts - 1:
                time.sleep(0.5)
            else:
                fatal("Failed to delete directory '" + path + "'")


def safe_delete_directory_recursively(root_path, directory_name):
    safe_delete_directory(os.path.join(root_path, directory_name))

    for entry in os.listdir(root_path):
        subdirectory = os.path.join(root_path, entry)
        if os.path.isdir(subdirectory):
            safe_delete_directory_recursively(subdirectory, directory_name)


def safe_make_directory(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def pushd(path):
    old_path = os.getcwd()
    os.chdir(path)
    return old_path


def copy_glob(input_pattern, output_path):
    for input_file in glob.glob(input_pattern):
        shutil.copy(input_file, output_path)


#--------------------------------------------------------------------------------------------------
# Settings.
#--------------------------------------------------------------------------------------------------

class Settings:

    def load(self):
        self.this_dir = os.path.dirname(os.path.realpath(__file__))
        self.root_dir = os.path.join(self.this_dir, "..")

        print("Loading settings from " + SETTINGS_FILENAME + "...")
        tree = ElementTree()
        try:
            tree.parse(SETTINGS_FILENAME)
        except IOError:
            fatal("Failed to load configuration file '" + SETTINGS_FILENAME + "'")
        self.__load_values(tree)

    def print_summary(self):
        print("")
        print("  Platform:                        " + self.platform)
        print("  Path to appleseed release:       " + self.appleseed_release_path)
        print("  Path to appleseed binaries:      " + self.appleseed_bin_path)
        print("  Path to appleseed libraries:     " + self.appleseed_lib_path)
        print("  Path to appleseed shaders:       " + self.appleseed_shaders_path)
        print("  Path to appleseed schemas:       " + self.appleseed_schemas_path)
        print("  Path to appleseed settings:      " + self.appleseed_settings_path)
        print("  Path to appleseed.python:        " + self.appleseed_python_path)
        print("  Path to maketx:                  " + self.maketx_path)
        print("  Output directory:                " + self.output_dir)
        print("")

    def __load_values(self, tree):
        self.platform = self.__get_required(tree, "platform")

        self.appleseed_release_path = self.__get_required(tree, "appleseed_release_path")
        os.environ['APPLESEED'] = self.appleseed_release_path

        self.appleseed_bin_path = os.path.expandvars(self.__get_required(tree, "appleseed_bin_path"))
        self.appleseed_lib_path = os.path.expandvars(self.__get_required(tree, "appleseed_lib_path"))
        self.appleseed_shaders_path = os.path.expandvars(self.__get_required(tree, "appleseed_shaders_path"))
        self.appleseed_schemas_path = os.path.expandvars(self.__get_required(tree, "appleseed_schemas_path"))
        self.appleseed_settings_path = os.path.expandvars(self.__get_required(tree, "appleseed_settings_path"))
        self.appleseed_python_path = os.path.expandvars(self.__get_required(tree, "appleseed_python_path"))
        self.maketx_path = os.path.expandvars(self.__get_required(tree, "maketx_path"))
        self.output_dir = os.path.expandvars(self.__get_required(tree, "output_dir"))

    def __get_required(self, tree, key):
        value = tree.findtext(key)
        if value is None:
            fatal("Missing value \"{0}\" in configuration file".format(key))
        return value


#--------------------------------------------------------------------------------------------------
# Base package builder.
#--------------------------------------------------------------------------------------------------

class PackageBuilder(object):

    def __init__(self, settings, package_version, build_date, no_release=False):
        self.settings = settings
        self.package_version = package_version
        self.build_date = build_date
        self.no_release = no_release

    def build_package(self):
        print("Building package:")
        print("")
        self.orchestrate()
        print("")
        print("The package was successfully built.")

    def orchestrate(self):
        self.remove_leftovers()
        self.copy_appleseed_python()
        self.copy_binaries()
        self.copy_dependencies()
        self.copy_schemas()
        self.copy_shaders()
        self.download_settings_files()
        self.remove_pyc_files()
        self.post_process_package()

        if not self.no_release:
            self.deploy_blenderseed_to_stage()
            self.clean_stage()
            self.build_final_zip_file()
            self.remove_stage()

    def remove_leftovers(self):
        progress("Removing leftovers from previous invocations")
        safe_delete_directory(os.path.join(self.settings.root_dir, "appleseed"))
        safe_delete_directory("blenderseed")

    def copy_appleseed_python(self):
        progress("Copying appleseed.python to root directory")

        # Create destination directory.
        lib_dir = os.path.join(self.settings.root_dir, "appleseed", "lib")
        safe_make_directory(lib_dir)

        # Copy appleseed.python.
        dir_util.copy_tree(self.settings.appleseed_python_path, lib_dir)

        # Remove _appleseedpython.so (Python 2) since blenderseed only needs _appleseedpython3.so (Python 3).
        # TODO: implement properly.
        safe_delete_file(os.path.join(lib_dir, "appleseed", "_appleseedpython.so"))
        safe_delete_file(os.path.join(lib_dir, "appleseed", "_appleseedpython.pyd"))

    def copy_binaries(self):
        progress("Copying binaries to root directory")

        # Create destination directory.
        bin_dir = os.path.join(self.settings.root_dir, "appleseed", "bin")
        safe_make_directory(bin_dir)

        # Copy appleseed binaries.
        for bin in [exe("appleseed.cli")]:
            shutil.copy(os.path.join(self.settings.appleseed_bin_path, bin), bin_dir)

        # Copy maketx.
        shutil.copy(exe(self.settings.maketx_path), bin_dir)

    def copy_schemas(self):
        progress("Copying schemas to root directory")

        dir_util.copy_tree(self.settings.appleseed_schemas_path, os.path.join(self.settings.root_dir, "appleseed", "schemas"))
        safe_delete_file(os.path.join(self.settings.root_dir, "appleseed", "schemas", ".gitignore"))

    def copy_shaders(self):
        progress("Copying shaders to root directory")

        # Create destination directory.
        shaders_dir = os.path.join(self.settings.root_dir, "appleseed", "shaders")
        safe_make_directory(shaders_dir)

        self.__do_copy_shaders(os.path.join(self.settings.appleseed_shaders_path, "appleseed"), shaders_dir)
        self.__do_copy_shaders(os.path.join(self.settings.appleseed_shaders_path, "blenderseed"), shaders_dir)

    def __do_copy_shaders(self, source_dir, target_dir):
        for root, dirs, files in os.walk(source_dir):
            for f in files:
                if f.endswith(".oso"):
                    shutil.copy(os.path.join(root, f), target_dir)

    def download_settings_files(self):
        progress("Downloading settings files to root directory")

        # Create destination directory.
        settings_dir = os.path.join(self.settings.root_dir, "appleseed", "settings")
        safe_make_directory(settings_dir)

        for file in ["appleseed.cli.xml"]:
            urllib.urlretrieve(
                "https://raw.githubusercontent.com/appleseedhq/appleseed/master/sandbox/settings/{0}".format(file),
                os.path.join(settings_dir, file))

    def remove_pyc_files(self):
        progress("Removing pyc files from root directory")
        for root, dirs, files in os.walk(os.path.join(self.settings.root_dir, "appleseed", "lib")):
            for f in files:
                if f.endswith(".pyc"):
                    safe_delete_file(os.path.join(root, f))

    def deploy_blenderseed_to_stage(self):
        progress("Deploying blenderseed to staging directory")
        shutil.copytree(self.settings.root_dir, "blenderseed", ignore=shutil.ignore_patterns("scripts"))

    def clean_stage(self):
        progress("Cleaning staging directory")

        safe_delete_directory_recursively("blenderseed", "__pycache__")

        for subdirectory in [".git", ".idea", "archives", "docs", "scripts", "tests"]:
            safe_delete_directory(os.path.join("blenderseed", subdirectory))

        for file in [".gitignore", "README.md"]:
            safe_delete_file(os.path.join("blenderseed", file))

    def build_final_zip_file(self):
        progress("Building final zip file from staging directory")
        package_name = "blenderseed-{0}-{1}-{2}".format(self.package_version, self.settings.platform, self.build_date)
        package_path = os.path.join(self.settings.output_dir, package_name)
        archive_util.make_zipfile(package_path, "blenderseed")
        info("Package path: {0}".format(package_path + ".zip"))

    def remove_stage(self):
        progress("Deleting staging directory")
        safe_delete_directory("blenderseed")

    def run(self, cmdline):
        trace("Running command line: {0}".format(cmdline))
        os.system(cmdline)

    def run_subprocess(self, cmdline):
        p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        return p.returncode, out, err


#--------------------------------------------------------------------------------------------------
# Windows package builder.
#--------------------------------------------------------------------------------------------------

class WindowsPackageBuilder(PackageBuilder):

    def copy_dependencies(self):
        progress("Windows-specific: Copying dependencies")
        bin_dir = self.settings.appleseed_bin_path

        for dll in ["appleseed.dll", "appleseed.shared.dll"]:
            shutil.copy(os.path.join(bin_dir, dll), os.path.join(self.settings.root_dir, "appleseed", "bin"))

    def post_process_package(self):
        pass


#--------------------------------------------------------------------------------------------------
# Mac package builder.
#--------------------------------------------------------------------------------------------------

class MacPackageBuilder(PackageBuilder):

    SYSTEM_LIBS_PREFIXES = [
        "/System/Library/",
        "/usr/lib/libcurl",
        "/usr/lib/libc++",
        "/usr/lib/libbz2",
        "/usr/lib/libSystem",
        #"/usr/lib/libz",
        "/usr/lib/libncurses",
        "/usr/lib/libobjc.A.dylib"
    ]

    def copy_dependencies(self):
        progress("Mac-specific: Copying dependencies")

        # Create destination directory.
        lib_dir = os.path.join(self.settings.root_dir, "appleseed", "lib")
        safe_make_directory(lib_dir)

        # Copy appleseed libraries.
        for lib in ["libappleseed.dylib", "libappleseed.shared.dylib"]:
            shutil.copy(os.path.join(self.settings.appleseed_lib_path, lib), lib_dir)

        # Get shared libs needed by binaries.
        all_libs = set()
        for bin in glob.glob(os.path.join(self.settings.root_dir, "appleseed", "bin", "*")):
            libs = self.__get_dependencies_for_file(bin)
            all_libs = all_libs.union(libs)

        # Get shared libs needed by appleseed.python.
        appleseedpython_libs = self.__get_dependencies_for_file(
            os.path.join(self.settings.root_dir, "appleseed", "lib", "appleseed", "_appleseedpython3.so"))
        all_libs = all_libs.union(appleseedpython_libs)

        # Get shared libs needed by libraries.
        # TODO: we're not computing the full transitive closure here!
        lib_libs = set()
        for lib in all_libs:
            libs = self.__get_dependencies_for_file(lib)
            lib_libs = lib_libs.union(libs)
        all_libs = all_libs.union(lib_libs)

        if True:
            # Print dependencies.
            trace("    Dependencies:")
            for lib in all_libs:
                trace("      {0}".format(lib))

        # Copy needed libs to lib directory.
        for lib in all_libs:
            if True:
                trace("  Copying {0} to {1}...".format(lib, lib_dir))
            shutil.copy(lib, lib_dir)

    def post_process_package(self):
        progress("Mac-specific: Post-processing package")
        self.__fixup_binaries()

    def __fixup_binaries(self):
        progress("Mac-specific: Fixing up binaries")
        self.set_libraries_ids()
        self.__change_library_paths_in_libraries()
        self.__change_library_paths_in_executables()

    def set_libraries_ids(self):
        lib_dir = os.path.join(self.settings.root_dir, "appleseed", "lib")
        for dirpath, dirnames, filenames in os.walk(lib_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1]
                if ext == ".dylib" or ext == ".so":
                    lib_path = os.path.join(dirpath, filename)
                    self.__set_library_id(lib_path, filename)

    def __change_library_paths_in_libraries(self):
        lib_dir = os.path.join(self.settings.root_dir, "appleseed", "lib")
        for dirpath, dirnames, filenames in os.walk(lib_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1]
                if ext == ".dylib" or ext == ".so":
                    lib_path = os.path.join(dirpath, filename)
                    self.__change_library_paths_in_binary(lib_path)

    def __change_library_paths_in_executables(self):
        bin_dir = os.path.join(self.settings.root_dir, "appleseed", "bin")
        for dirpath, dirnames, filenames in os.walk(bin_dir):
            for filename in filenames:
                ext = os.path.splitext(filename)[1]
                if ext != ".py" and ext != ".conf":
                    exe_path = os.path.join(dirpath, filename)
                    self.__change_library_paths_in_binary(exe_path)

    # Can be used on executables and dynamic libraries.
    def __change_library_paths_in_binary(self, bin_path):
        progress("Patching {0}".format(bin_path))
        bin_dir = os.path.dirname(bin_path)
        lib_dir = os.path.join(self.settings.root_dir, "appleseed", "lib")
        path_to_appleseed_lib = os.path.relpath(lib_dir, bin_dir)
        # fix_paths set to False because we must retrieve the unmodified dependency in order to replace it by the correct one.
        for lib_path in self.__get_dependencies_for_file(bin_path, fix_paths=False):
            lib_name = os.path.basename(lib_path)
            if path_to_appleseed_lib == ".":
                self.__change_library_path(bin_path, lib_path, "@loader_path/{0}".format(lib_name))
            else:
                self.__change_library_path(bin_path, lib_path, "@loader_path/{0}/{1}".format(path_to_appleseed_lib, lib_name))

    def __set_library_id(self, target, name):
        self.run('install_name_tool -id "{0}" {1}'.format(name, target))

    def __change_library_path(self, target, old, new):
        self.run('install_name_tool -change "{0}" "{1}" {2}'.format(old, new, target))

    def __get_dependencies_for_file(self, filepath, fix_paths=True):
        filename = os.path.basename(filepath)

        loader_path = os.path.dirname(filepath)
        rpath = "/usr/local/lib/"  # TODO: a great simplification

        if True:
            trace("Gathering dependencies for file")
            trace("    {0}".format(filepath))
            trace("with @loader_path set to")
            trace("    {0}".format(loader_path))
            trace("and @rpath hardcoded to")
            trace("    {0}".format(rpath))

        returncode, out, err = self.run_subprocess(["otool", "-L", filepath])
        if returncode != 0:
            fatal("Failed to invoke otool(1) to get dependencies for {0}: {1}".format(filepath, err))

        libs = set()

        for line in out.split("\n")[1:]:    # skip the first line
            line = line.strip()

            # Ignore empty lines.
            if len(line) == 0:
                continue

            # Parse the line.
            m = re.match(r"(.*) \(compatibility version .*, current version .*\)", line)
            if not m:
                fatal("Failed to parse line from otool(1) output: " + line)
            lib = m.group(1)

            # Ignore self-references (why do these happen?).
            if lib == filename:
                continue

            # Ignore system libs.
            if self.__is_system_lib(lib):
                continue

            # Ignore Qt frameworks.
            if re.search(r"Qt.*\.framework", lib):
                continue

            if fix_paths:
                # Handle libs relative to @loader_path.
                lib = lib.replace("@loader_path", loader_path)

                # Handle libs relative to @rpath.
                lib = lib.replace("@rpath", rpath)

                # Try to handle other relative libs.
                if not os.path.isabs(lib):
                    # TODO: generalize to a collection of user-specified search paths.
                    candidate = os.path.join(loader_path, lib)
                    if not os.path.exists(candidate):
                        candidate = os.path.join("/usr/local/lib/", lib)
                    if os.path.exists(candidate):
                        info("Resolved relative dependency {0} as {1}".format(lib, candidate))
                        lib = candidate

            libs.add(lib)

        if True:
            trace("Dependencies for file {0}:".format(filepath))
            for lib in libs:
                if os.path.isfile(lib):
                    trace(u"    {0} {1}".format(GREEN_CHECKMARK, lib))
                else:
                    trace(u"    {0} {1}".format(RED_CROSSMARK, lib))

        # Don't check for missing dependencies if we didn't attempt to fix them.
        if fix_paths:
            for lib in libs:
                if not os.path.isfile(lib):
                    fatal("Dependency {0} could not be found on disk".format(lib))

        return libs

    def __is_system_lib(self, lib):
        for prefix in self.SYSTEM_LIBS_PREFIXES:
            if lib.startswith(prefix):
                return True
        return False


#--------------------------------------------------------------------------------------------------
# Linux package builder.
#--------------------------------------------------------------------------------------------------

class LinuxPackageBuilder(PackageBuilder):

    SYSTEM_LIBS_PREFIXES = [
        "linux",
        "librt",
        "libpthread",
        "libGL",
        "libX",
        "libselinux",
        "libICE",
        "libSM",
        "libdl",
        "libm.so",
        "libgcc",
        "libc.so",
        "/lib64/ld-linux-",
        "libstdc++",
        "libxcb",
        "libdrm",
        "libnsl",
        "libuuid",
        "libgthread",
        "libglib",
        "libgobject",
        "libglapi",
        "libffi",
        "libfontconfig",
        "libutil",
        "libpython",
        "libxshmfence.so"
    ]

    def plugin_extension(self):
        return ".so"

    def copy_dependencies(self):
        progress("Linux-specific: Copying dependencies")

        # Create destination directory.
        lib_dir = os.path.join(self.settings.root_dir, "appleseed", "lib")
        safe_make_directory(lib_dir)

        # Copy appleseed libraries.
        for lib in ["libappleseed.so", "libappleseed.shared.so"]:
            shutil.copy(os.path.join(self.settings.appleseed_lib_path, lib), lib_dir)

        # Get shared libs needed by binaries.
        all_libs = set()
        for bin in glob.glob(os.path.join(self.settings.root_dir, "appleseed", "bin", "*")):
            libs = self.__get_dependencies_for_file(bin)
            all_libs = all_libs.union(libs)

        # Get shared libs needed by appleseed.python.
        appleseedpython_libs = self.__get_dependencies_for_file(
            os.path.join(self.settings.root_dir, "appleseed", "lib", "appleseed", "_appleseedpython3.so"))
        all_libs = all_libs.union(appleseedpython_libs)

        # Get shared libs needed by libraries.
        lib_libs = set()
        for lib in all_libs:
            libs = self.__get_dependencies_for_file(lib)
            lib_libs = lib_libs.union(libs)
        all_libs = all_libs.union(lib_libs)

        # Copy all shared libraries.
        for lib in all_libs:
            shutil.copy(lib, lib_dir)

    def post_process_package(self):
        progress("Linux-specific: Post-processing package")

        for bin in glob.glob(os.path.join(self.settings.root_dir, "appleseed", "bin", "*")):
            self.run("chrpath -r \$ORIGIN/../lib " + bin)

        for lib in glob.glob(os.path.join(self.settings.root_dir, "appleseed", "lib", "*.so")):
             self.run("chrpath -d " + lib)

        appleseed_python_dir = os.path.join(self.settings.root_dir, "appleseed", "lib", "appleseed")
        for py_cpp_module in glob.glob(os.path.join(appleseed_python_dir, "*.so")):
            self.run("chrpath -r \$ORIGIN/../ " + py_cpp_module)

    def __is_system_lib(self, lib):
        for prefix in self.SYSTEM_LIBS_PREFIXES:
            if lib.startswith(prefix):
                return True
        return False

    def __get_dependencies_for_file(self, filepath):
        returncode, out, err = self.run_subprocess(["ldd", filepath])
        if returncode != 0:
            fatal("Failed to invoke ldd(1) to get dependencies for {0}: {1}".format(filepath, err))

        libs = set()

        for line in out.split("\n"):
            line = line.strip()

            # Ignore empty lines.
            if len(line) == 0:
                continue

            # Ignore system libs.
            if self.__is_system_lib(line):
                continue

            # Ignore appleseed libs.
            if "libappleseed" in line:
                continue

            libs.add(line.split()[2])

        return libs


#--------------------------------------------------------------------------------------------------
# Entry point.
#--------------------------------------------------------------------------------------------------

def main():
    colorama.init()

    parser = argparse.ArgumentParser(description="build a blenderseed package from sources")

    parser.add_argument("--nozip", action="store_true", help="copies appleseed binaries to blenderseed folder but does not build a release package")

    args = parser.parse_args()

    no_release = args.nozip
    package_version = subprocess.Popen("git describe --long", stdout=subprocess.PIPE, shell=True).stdout.read().strip()

    build_date = datetime.date.today().isoformat()

    print("blenderseed.package version " + VERSION)
    print("")

    settings = Settings()
    settings.load()
    settings.print_summary()

    if os.name == "nt":
        package_builder = WindowsPackageBuilder(settings, package_version, build_date, no_release)
    elif os.name == "posix" and platform.mac_ver()[0] != "":
        package_builder = MacPackageBuilder(settings, package_version, build_date, no_release)
    elif os.name == "posix" and platform.mac_ver()[0] == "":
        package_builder = LinuxPackageBuilder(settings, package_version, build_date, no_release)
    else:
        fatal("Unsupported platform: " + os.name)

    package_builder.build_package()

if __name__ == "__main__":
    main()
