import os
import platform
import unittest

import nose

from conans import tools
from conans.errors import ConanException
from conans.model.version import Version
from conans import __version__ as client_version
from conans.model import settings
from conans.test.utils.tools import TestClient
from conans.test.assets.visual_project_files import get_vs_project_files


class vswhereTest(unittest.TestCase):

    # Environment supossed:
    #   - BuildTools 14 (2015)
    #   - VS Community 14 (2015)
    #
    #   - BuildTools 15 (2017) OR VS Community 15 (2017)
    modern_products = 1 # 2017 or higher versions without BuildTools -> vswhere()
    all_modern_products = 2 # 2017 or higher versions with BuildTools -> vswhere(products=["*"])
    modern_and_legacy_products = 2 # 2017 and lower versions (without BuildTools) -> vswhere(legacy=True)
    only_legacy_products = 1
    all_products = 3

    def setUp(self):
        if platform.system() != "Windows":
            raise nose.SkipTest("Only Windows test")
        if Version(client_version) < Version("1.1.0-dev"):
            raise nose.SkipTest("Only >= 1.1.0-dev version")

    def vs_comntools_test(self):
        # Fake path
        with tools.environment_append({"VS150COMNTOOLS": "fake/path/here"}):
            path = tools.vs_comntools("15")
            self.assertEqual(path, "fake/path/here")

        # VS 14 path
        path = tools.vs_comntools("14")
        self.assertEqual(path, "C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\Common7\\Tools\\")

        # VS 15 path (shouldn't be found as VS150COMNTOOLS is not set by default)
        path = tools.vs_comntools("15")
        self.assertEqual(path, None)

    def vswhere_test(self):
        # products and legacy not allowed
        self.assertRaises(ConanException, tools.vswhere, products=["*"], legacy=True)

        # Detect only one product (VS Community 15) as vswhere default detection
        nproducts = len(tools.vswhere())
        self.assertEqual(nproducts, self.modern_products)

        # Detect only modern products (VS Community 15 & BuildTools 15)
        products = tools.vswhere(products=["*"])
        nproducts = len(products)
        
        self.assertEqual(nproducts, self.all_modern_products)
        installation_paths = [product["installationPath"] for product in products]
        self.assertTrue(any("Community" in install_path for install_path in installation_paths))
        self.assertTrue(any("BuildTools" in install_path for install_path in installation_paths))

        # Detect also legacy products but no modern BuildTools
        products = tools.vswhere(legacy=True)
        nproducts = len(products)

        self.assertEqual(nproducts, self.modern_and_legacy_products)
        installation_paths = [product["installationPath"] for product in products]
        self.assertTrue(any("Community" in install_path for install_path in installation_paths))
        self.assertTrue(any("Microsoft Visual Studio 14.0" in install_path for install_path in installation_paths))

        # Detect all installed products
        products = tools.vswhere(products=["*"])
        products += tools.vswhere(legacy=["*"])
        seen_products = []
        for product in products:
            if product not in seen_products:
                seen_products.append(product)
        products = seen_products
        nproducts = len(products)

        self.assertEqual(nproducts, self.all_products)
        installation_paths = [product["installationPath"] for product in products]
        self.assertTrue(any("Community" in install_path for install_path in installation_paths))
        self.assertTrue(any("BuildTools" in install_path for install_path in installation_paths))
        self.assertTrue(any("Microsoft Visual Studio 14.0" in install_path for install_path in installation_paths))

    def vs_installation_path_test(self):
        # Default behaviour
        install_path = tools.vs_installation_path("15")
        self.assertIn("Community", install_path)
        install_path = tools.vs_installation_path("14")
        self.assertIn("Microsoft Visual Studio 14.0", install_path)

        # only BuildTools detection
        install_path = tools.vs_installation_path("15", preference=["BuildTools"])
        self.assertIn("BuildTools", install_path)
        install_path = tools.vs_installation_path("14", preference=["BuildTools"])
        self.assertIn("Microsoft Visual Studio 14.0", install_path)

        # Ask for not installed versions
        install_path = tools.vs_installation_path("15", preference=["Enterprise"])
        self.assertIsNone(install_path)
        install_path = tools.vs_installation_path("15", preference=["Professional"])
        self.assertIsNone(install_path)

        # Change preference order
        install_path = tools.vs_installation_path("15", preference=["BuildTools", "Community", "Professional", "Enterprise"])
        self.assertIn("BuildTools", install_path)

        install_path = tools.vs_installation_path("15", preference=["Professional", "Enterprise", "Community"])
        self.assertIn("Community", install_path)

        # Preference order by env var
        with(tools.environment_append({"CONAN_VS_INSTALLATION_PREFERENCE":"BuildTools, Community,Professional, Enterprise"})):
            install_path = tools.vs_installation_path("15")
            self.assertIn("BuildTools", install_path)
        
        with(tools.environment_append({"CONAN_VS_INSTALLATION_PREFERENCE":"Professional, Enterprise,Community"})):
            install_path = tools.vs_installation_path("15")
            self.assertIn("Community", install_path)

    def vvcars_command_test(self):
        fake_settings = settings.Settings({"os":"Windows", "arch": "x86_64"})

        # preference order with VS 15
        with(tools.environment_append({"CONAN_VS_INSTALLATION_PREFERENCE":"BuildTools, Community,Professional, Enterprise"})):
            command = tools.vcvars_command(settings=fake_settings, compiler_version="15")
            self.assertNotIn("Community", command)
            self.assertIn("VC/Auxiliary/Build/vcvarsall.bat", command)
            self.assertIn("Microsoft Visual Studio\\2017\\BuildTools", command)
            self.assertIn("VSCMD_START_DIR", command)

        with(tools.environment_append({"CONAN_VS_INSTALLATION_PREFERENCE":"Professional, Enterprise,Community"})):
            command = tools.vcvars_command(settings=fake_settings, compiler_version="15")
            self.assertNotIn("BuildTools", command)
            self.assertIn("VC/Auxiliary/Build/vcvarsall.bat", command)
            self.assertIn("Microsoft Visual Studio\\2017\\Community", command)
            self.assertIn("VSCMD_START_DIR", command)

        # With VS 14 order of preference does not apply
        command = tools.vcvars_command(settings=fake_settings, compiler_version="14")
        self.assertNotIn("VSCMD_START_DIR", command)
        self.assertIn("VC/vcvarsall.bat", command)
        self.assertIn("Microsoft Visual Studio 14.0\\", command)

    def build_test(self):
        conan_build_vs = """
from conans import ConanFile, MSBuild, tools

class HelloConan(ConanFile):
    name = "Hello"
    version = "1.2.1"
    settings = "os", "build_type", "arch", "compiler"
    export_source = "*"

    def build(self):
        msbuild = MSBuild(self)
        msbuild.build("MyProject.sln", upgrade_project=False)
"""
        client = TestClient()
        files = get_vs_project_files()
        files["conanfile.py"] = conan_build_vs
        client.save(files)

        with(tools.environment_append({"CONAN_PRINT_RUN_COMMANDS": "1"})):
            with(tools.environment_append({"CONAN_VS_INSTALLATION_PREFERENCE": "BuildTools"})):
                client.run("install .")
                client.run("build .")
                self.assertIn("BuildTools", client.out)

            conan_build_vs = conan_build_vs.replace("upgrade_project=False", "upgrade_project=True")
            files["conanfile.py"] = conan_build_vs
            client.save(files)

            with(tools.environment_append({"CONAN_VS_INSTALLATION_PREFERENCE":"BuildTools",
                                           "CONAN_SKIP_VS_PROJECTS_UPGRADE":"True"})):
                client.run("install .")
                client.run("build .")
                self.assertIn("BuildTools", client.out)
