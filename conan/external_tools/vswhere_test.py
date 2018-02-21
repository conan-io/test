import os
import unittest

import nose

from conans import tools
from conans.errors import ConanException
from conans.model.version import Version
from conans import __version__ as client_version


class vswhereTest(unittest.TestCase):

    # Environment supossed:
    #   - BuildTools 14 (2015)
    #   - VS Community 14 (2015)
    #
    #   - BuildTools 15 (2017) OR VS Community 15 (2017)
    modern_products = 1 # 2017 or higher versions -> vswhere()
    all_modern_products = 2 # 2017 or higher versions -> vswhere(products=["*"])
    modern_and_legacy_products = 2 # 2017 and lower versions -> vswhere(legacy=True)
    only_legacy_products = 1
    all_products = 3

    def setUp(self):
        if Version(client_version) < Version("1.1"):
            raise nose.SkipTest('Only >= 1.1 version')

    def vs_comntools_test(self):
        # Fake path
        print(tools.__file__)
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
        # test there is some output
        output = tools.vswhere()
        self.assertIsNotNone(output)

        # products and legacy not allowed
        self.assertRaises(ConanException, tools.vswhere, products=["*"], legacy=True)

        # Detect only one product (VS Community 15) as vswhere default detection
        nproducts = len(tools.vswhere())
        self.assertEqual(nproducts, self.modern_products)

        # Detect only modern products (VS Community 15 & BuildTools 15)
        products = tools.vswhere(products=["*"])
        nproducts = len(products)
        
        self.assertEqual(nproducts, self.all_modern_products)
        for product in products:
            install_path = product["installationPath"]
            self.assertTrue("Community" in install_path or
                            "BuildTools" in install_path)

        # Detect also legacy products but no modern BuildTools
        products = tools.vswhere(legacy=True)
        nproducts = len(products)

        self.assertEqual(nproducts, self.modern_and_legacy_products)
        for product in products:
            install_path = product["installationPath"]
            self.assertTrue("Community" in install_path or
                            "Microsoft Visual Studio 14.0" in install_path)

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
        for product in products:
            install_path = product["installationPath"]
            self.assertTrue("Community" in install_path or
                            "BuildTools" in install_path or
                            "Microsoft Visual Studio 14.0" in install_path)

    # def vs_installation_path_test(self):
    #     # test installation paths w/o preference parameter and ENV_VAR

    # def vvcars_command_test(self):
    #     # get right paths for installations (similar to vs_where)

    # def build_test(self):
    #     if Version(client_version) < Version("1.1"):
    #         raise nose.SkipTest('Only >= 1.1 version')

    #     with tools.remove_from_path("bash.exe"):
    #         with mingw_in_path():
    #             not_env = os.system("c++ --version > nul")
    #             if not_env != 0:
    #                 raise Exception("This platform does not support G++ command")
    #             install = "install %s -s compiler=gcc -s compiler.libcxx=libstdc++ " \
    #                       "-s compiler.version=4.9" % path_dot()
    #             for cmd, lang, static, pure_c in [(install, 0, True, True),
    #                                               (install + " -o language=1 -o static=False", 1, False, False)]:
    #                 from conans.test.integration.basic_build_test import build
    #                 build(self, cmd, static, pure_c, use_cmake=False, lang=lang)
