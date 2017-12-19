import os
import unittest

from conan.conf import mingw_in_path
from conans import tools
from conans.test.integration.basic_build_test import build
from conans.test.integration.diamond_test import DiamondTester
from conans.test.utils.tools import TestServer, TestClient


class MinGWDiamondTest(unittest.TestCase):

    def setUp(self):
        test_server = TestServer(
                                 [],  # write permissions
                                 users={"lasote": "mypass"})  # exported users and passwords
        servers = {"default": test_server}
        conan = TestClient(servers=servers, users={"default": [("lasote", "mypass")]})
        self.diamond_tester = DiamondTester(self, conan, servers)
    
    def diamond_mingw_test(self):
        with tools.remove_from_path("bash.exe"):
            with mingw_in_path():
                not_env = os.system("g++ --version > nul")
                if not_env != 0:
                    raise Exception("This platform does not support G++ command")
                install = "install -s compiler=gcc -s compiler.libcxx=libstdc++ -s compiler.version=4.9"
                self.diamond_tester.test(install=install, use_cmake=False)

        
class BuildMingwTest(unittest.TestCase):

    def build_mingw_test(self):
        with tools.remove_from_path("bash.exe"):
            with mingw_in_path():
                not_env = os.system("c++ --version > nul")
                if not_env != 0:
                    raise Exception("This platform does not support G++ command")
                install = "install -s compiler=gcc -s compiler.libcxx=libstdc++ -s compiler.version=4.9"
                for cmd, lang, static, pure_c in [(install, 0, True, True),
                                                  (install + " -o language=1 -o static=False", 1, False, False)]:
                    build(self, cmd, static, pure_c, use_cmake=False, lang=lang)
