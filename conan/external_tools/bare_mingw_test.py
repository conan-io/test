import os
import unittest

import nose

from conan.conf import mingw_in_path, CONAN_STANDALONE_MAKE_PATH
from conan.test_regression.utils.base_exe import path_dot
from conans import tools
from conans.model.version import Version
from conans.test.utils.cpp_test_files import cpp_hello_conan_files
from conans.test.utils.tools import TestServer, TestClient
from conans import __version__ as client_version


class MinGWDiamondTest(unittest.TestCase):

    def setUp(self):
        test_server = TestServer(
                                 [],  # write permissions
                                 users={"lasote": "mypass"})  # exported users and passwords
        servers = {"default": test_server}
        conan = TestClient(servers=servers, users={"default": [("lasote", "mypass")]})
        if Version(client_version) < Version("0.31"):
            raise nose.SkipTest('Only >= 1.0 version')

        from conans.test.integration.diamond_test import DiamondTester
        self.diamond_tester = DiamondTester(self, conan, servers)
    
    def diamond_mingw_test(self):
        if Version(client_version) < Version("0.31"):
            raise nose.SkipTest('Only >= 1.0 version')
        with tools.remove_from_path("bash.exe"):
            with mingw_in_path():
                not_env = os.system("g++ --version > nul")
                if not_env != 0:
                    raise Exception("This platform does not support G++ command")
                install = "install %s -s compiler=gcc -s compiler.libcxx=libstdc++ " \
                          "-s compiler.version=4.9" % path_dot()
                self.diamond_tester.test(install=install, use_cmake=False)

        
class BuildMingwTest(unittest.TestCase):

    def build_mingw_test(self):
        if Version(client_version) < Version("0.31"):
            raise nose.SkipTest('Only >= 1.0 version')

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


class MinGWUsingCMakeAndMake(unittest.TestCase):

    def build_hello_with_make_test(self):
        if Version(client_version) < Version("1.1.0-dev"):
            raise nose.SkipTest('Only >= 1.1.0-dev')

        client = TestClient()
        files = cpp_hello_conan_files("lib", "1.0")
        client.save(files)
        make_location = "/usr/bin/make" if not tools.os_info.is_windows else CONAN_STANDALONE_MAKE_PATH
        gen = "Unix Makefiles" if not tools.os_info.is_windows else "MinGW Makefiles"
        with tools.environment_append({"CONAN_CMAKE_GENERATOR": gen,
                                       "CONAN_MAKE_PROGRAM": make_location}):
            client.run("create . conan/testing  -s compiler=gcc -s compiler.libcxx=libstdc++ -s compiler.version=4.9")
            self.assertIn('-DCMAKE_MAKE_PROGRAM="%s"' % make_location, client.out)

