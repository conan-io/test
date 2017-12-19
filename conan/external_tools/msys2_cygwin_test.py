import platform

import nose
from nose_parameterized import parameterized

from conan.conf import msys2_in_path
from conan.test_regression.utils.base_exe import BaseExeTest, save_files, run
from conans import tools
from conans.model.ref import ConanFileReference
from conans.model.version import Version
from conans.paths import CONANFILE
from conans.test.utils.cpp_test_files import cpp_hello_conan_files
from conans.test.utils.tools import TestClient
from conans.tools import unix_path
from conans import __version__ as conan_version


class RunInMsys2BashTest(BaseExeTest):

    def run_in_windows_bash_test(self):
        if Version(conan_version) < Version("1.0.0-beta.1") or platform.system() != "Windows":
            raise nose.SkipTest('Only windows test')
        with tools.remove_from_path("bash.exe"):
            with msys2_in_path():
                conanfile = '''
from conans import ConanFile, tools

class ConanBash(ConanFile):
    name = "bash"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"

    def build(self):
        tools.run_in_windows_bash(self, "pwd")

        '''
                client = TestClient()
                client.save({CONANFILE: conanfile})
                client.run("export lasote/stable")
                client.run("install bash/0.1@lasote/stable --build")
                expected_curdir_base = unix_path(
                    client.client_cache.conan(ConanFileReference.loads("bash/0.1@lasote/stable")))
                self.assertIn(expected_curdir_base, client.user_io.out)

    def run_in_windows_bash_relative_path_test(self):
        if Version(conan_version) < Version("1.0.0-beta.1") or platform.system() != "Windows":
            raise nose.SkipTest('Only windows test')
        with tools.remove_from_path("bash.exe"):
            with msys2_in_path():
                conanfile = '''
import os
from conans import ConanFile, tools

class ConanBash(ConanFile):
    name = "bash"
    version = "0.1"

    def build(self):
        tools.mkdir("relative")
        tools.run_in_windows_bash(self, "pwd", "relative")
'''
                client = TestClient()
                client.save({CONANFILE: conanfile})
                client.run("create bash/0.1@lasote/stable")
                self.assertIn("build/5ab84d6acfe1f23c4fae0ab88f26e3a396351ac9/relative", client.user_io.out)

    def run_in_windows_bash_env_var_test(self):
        if Version(conan_version) < Version("1.0.0-beta.1") or platform.system() != "Windows":
            raise nose.SkipTest('Only windows test')
        with tools.remove_from_path("bash.exe"):
            with msys2_in_path():
                conanfile = '''
from conans import ConanFile, tools
import os

class ConanBash(ConanFile):
    name = "THEPACKAGE"
    version = "0.1"

    def package_info(self):
        self.env_info.PATH.append(self.package_folder)
        tools.save(os.path.join(self.package_folder, "myrun.bat"), 'echo "HELLO PARENT!')
'''
                client = TestClient()
                client.save({CONANFILE: conanfile})
                client.run("create lasote/stable")

                conanfile = '''
from conans import ConanFile, tools

class ConanBash(ConanFile):
    name = "bash"
    version = "0.1"
    settings = "os", "compiler", "build_type", "arch"
    requires = "THEPACKAGE/0.1@lasote/stable"

    def build(self):
        with tools.environment_append({"MYVAR": "Hello MYVAR"}):
            tools.run_in_windows_bash(self, "echo $MYVAR")
            tools.run_in_windows_bash(self, 'myrun.bat')
        '''
                client.save({CONANFILE: conanfile}, clean_first=True)
                client.run("export lasote/stable")
                client.run("install bash/0.1@lasote/stable --build")
                self.assertIn("Hello MYVAR", client.user_io.out)
                self.assertIn("HELLO PARENT!", client.user_io.out)


class MSys2CygwinTestBuildRequiresOrderAppliedPath(BaseExeTest):

    @parameterized.expand([("cygwin_installer/2.9.0@bincrafters/stable", ),
                           ("msys2_installer/latest@bincrafters/stable",)])
    def test_base(self, subsystem_require):
        if Version(conan_version) < Version("1.0.0-beta.1") or platform.system() != "Windows":
            raise nose.SkipTest('Only windows test')
        files = cpp_hello_conan_files(name="Hello", version="0.1", deps=None, language=0, static=True,
                                      use_cmake=False)
        files["myprofile"] = """
[build_requires]
mingw_installer/1.0@conan/stable
%s
 
[settings]
build_os=Windows
build_arch=x86_64
os=Windows
arch=x86_64
compiler=gcc
compiler.version=5.4
compiler.libcxx=libstdc++11
compiler.exception=seh
compiler.threads=posix
""" % subsystem_require

        save_files(files)
        run("conan create conan/testing --profile ./myprofile --update")
