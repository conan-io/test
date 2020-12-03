import os
import platform
import textwrap
import unittest

import six
from future.moves import sys

from conan_tests.test_regression.utils.base_exe import path_dot
from conans.paths import CONANFILE
from conans.test.assets.cpp_test_files import cpp_hello_conan_files
from conans.test.utils.tools import TestClient
from conans.util.files import mkdir, load
from nose_parameterized import parameterized


@unittest.skipIf(sys.version_info[0] < 3, "Meson is not available in Python 2")
class PkgConfigGeneratorTest(unittest.TestCase):

    
    @parameterized.expand([(True, ), (False, )])
    def basic_test(self, no_copy_source):
        client = TestClient()
        conanfile = textwrap.dedent("""
            from conans import ConanFile, Meson, load
            import os
            class Conan(ConanFile):
                settings = "os", "compiler", "arch", "build_type"
                exports_sources = "src/*"
                no_copy_source = {}
                def build(self):
                    meson = Meson(self)
                    meson.configure(source_folder="src",
                                    cache_build_folder="build")
                    meson.build()
                def package(self):
                    self.copy("*.h", src="src", dst="include")

                def package_info(self):
                    self.output.info("HEADER %s" % load(os.path.join(self.package_folder, "include/header.h")))
                """).format(no_copy_source)
        meson = textwrap.dedent("""
            project('hello', 'cpp', version : '0.1.0',
		    default_options : ['cpp_std=c++11'])
            """)
        client.save({"conanfile.py": conanfile,
                     "src/meson.build": meson,
                     "src/header.h": "//myheader.h"})
        client.run("create %s Hello/0.1@lasote/channel" % path_dot())
        self.assertIn("Hello/0.1@lasote/channel: HEADER //myheader.h", client.out)
        # Now local flow
        build_folder = os.path.join(client.current_folder, "build")
        mkdir(build_folder)
        client.current_folder = build_folder
        client.run("install ..")
        client.run("build ..")
        client.run("package ..")
        self.assertTrue(os.path.exists(os.path.join(build_folder, "conaninfo.txt")))
        self.assertTrue(os.path.exists(os.path.join(build_folder, "conanbuildinfo.txt")))
        self.assertEqual(load(os.path.join(build_folder, "package/include/header.h")), "//myheader.h")

    def test_base(self):
        client = TestClient(path_with_spaces=False)
        self._export(client, "LIB_C", [])
        self._export(client, "LIB_B", ["LIB_C"])
        self._export(client, "LIB_B2", [])
        self._export(client, "LIB_A", ["LIB_B", "LIB_B2"])

        consumer = textwrap.dedent("""
            from conans import ConanFile, Meson

            class ConanFileToolsTest(ConanFile):
                generators = "pkg_config"
                requires = "LIB_A/0.1@conan/stable"
                settings = "os", "compiler", "build_type"

                def build(self):
                    meson = Meson(self)
                    meson.configure()
                    meson.build()
            """)
        meson_build = textwrap.dedent("""
            project('conan_hello', 'c')
            liba = dependency('LIB_A', version : '>=0')
            executable('demo', 'main.c', dependencies: [liba])
            """)

        main_c = textwrap.dedent("""
            #include "helloLIB_A.h"
            int main(){
            helloLIB_A();
            }
            """)

        client.save({CONANFILE: consumer,
                     "meson.build": meson_build,
                     "main.c": main_c}, clean_first=True)
        mkdir(os.path.join(client.current_folder, "build"))
        client.current_folder = os.path.join(client.current_folder, "build")
        client.run("install .. --build")

        client.run("build .. --source-folder ..")
        command = "demo" if platform.system() == "Windows" else "./demo"
        client.run_command(command)
        self.assertEqual(['Hello LIB_A', 'Hello LIB_B', 'Hello LIB_C', 'Hello LIB_B2'],
                         str(client.out).splitlines()[-4:])

    def _export(self, client, libname, depsname):
        files = cpp_hello_conan_files(libname, "0.1",
                                      ["%s/0.1@conan/stable" % name for name in depsname],
                                      build=six.PY3, pure_c=True)
        client.save(files, clean_first=True)
        files[CONANFILE] = files[CONANFILE].replace('generators = "cmake", "gcc"', "")
        client.run("export %s conan/stable" % path_dot())
