import os
import unittest

from conan_tests.conf import mingw_in_path
from conan_tests.test_regression.utils.base_exe import path_dot
from conans import tools
from conans.model.version import Version
from conans.test.utils.tools import TestClient, TestServer
from conans.test.assets.cpp_test_files import cpp_hello_conan_files
from conans import __version__ as client_version


@unittest.skipIf(Version(client_version) < Version("0.31"), 'Only >= 1.0 version')
class MinGWDiamondTest(unittest.TestCase):

    def setUp(self):
        test_server = TestServer([],  # write permissions
                                 users={"lasote": "mypass"})  # exported users and passwords
        self.servers = {"default": test_server}
        self.client = TestClient(servers=self.servers, users={"default": [("lasote", "mypass")]})

    def _export(self, name, version=None, deps=None, use_cmake=True, cmake_targets=False):
        files = cpp_hello_conan_files(name, version, deps, need_patch=True, use_cmake=use_cmake,
                                        cmake_targets=cmake_targets, with_exe=False)
        self.client.save(files, clean_first=True)
        self.client.run("export . lasote/stable")

    def diamond_mingw_test(self):
        use_cmake = cmake_targets = False
        self._export("Hello0", "0.1", use_cmake=use_cmake, cmake_targets=cmake_targets)
        self._export("Hello1", "0.1", ["Hello0/0.1@lasote/stable"], use_cmake=use_cmake,
                     cmake_targets=cmake_targets)
        self._export("Hello2", "0.1", ["Hello0/0.1@lasote/stable"], use_cmake=use_cmake,
                     cmake_targets=cmake_targets)
        self._export("Hello3", "0.1", ["Hello1/0.1@lasote/stable", "Hello2/0.1@lasote/stable"],
                     use_cmake=use_cmake, cmake_targets=cmake_targets)

        files3 = cpp_hello_conan_files("Hello4", "0.1", ["Hello3/0.1@lasote/stable"],
                                       language=1, use_cmake=use_cmake,
                                       cmake_targets=cmake_targets)

        self.client.save(files3)

        with tools.remove_from_path("bash.exe"):
            with mingw_in_path():
                not_env = os.system("g++ --version > nul")
                if not_env != 0:
                    raise Exception("This platform does not support G++ command")
                install = "install %s -s compiler=gcc -s compiler.libcxx=libstdc++ " \
                          "-s compiler.version=4.9" % path_dot()

                self.client.run("install %s -s compiler=gcc -s compiler.libcxx=libstdc++ " 
                                "-s compiler.version=4.9 --build=missing" % path_dot())
                self.client.run("build .")
                
                command = os.sep.join([".", "bin", "say_hello"])
                self.client.run_command(command)
                self.assertEqual(['Hola Hello4', 'Hola Hello3', 'Hola Hello1', 'Hola Hello0',
                                'Hola Hello2', 'Hola Hello0'],
                                str(self.client.out).splitlines()[-6:])


@unittest.skipIf(Version(client_version) < Version("0.31"), 'Only >= 1.0 version')        
class BuildMingwTest(unittest.TestCase):

    def build_mingw_test(self):
        with tools.remove_from_path("bash.exe"):
            with mingw_in_path():
                not_env = os.system("c++ --version > nul")
                if not_env != 0:
                    raise Exception("This platform does not support G++ command")
                install = "install %s -s compiler=gcc -s compiler.libcxx=libstdc++ " \
                          "-s compiler.version=4.9" % path_dot()
                for cmd, lang, static, pure_c in [(install, 0, True, True),
                                                  (install + " -o language=1 -o static=False", 1, False, False)]:
                    from conans.test.integration.basic_build_test import build
                    build(self, cmd, static, pure_c, use_cmake=False, lang=lang)
