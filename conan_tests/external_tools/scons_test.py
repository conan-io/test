import platform
import unittest

from conans.test.utils.tools import TestClient
from conans import __version__ as conan_version

import sys
pyver = str("%s.%s" % sys.version_info[0:2])


class SConsTest(unittest.TestCase):

    def test_basic(self):
        if conan_version < "1.3.0": # Avoid 0.30.0
            return
        if platform.system() != "Windows" or pyver < "3.6":
            return
        client = TestClient()
        client.runner("git clone https://github.com/memsharded/conan-scons-template .",
                      cwd=client.current_folder)
        client.run("create . user/testing")
        self.assertIn("Hello World Release!", client.out)
        client.run("create . user/testing -s build_type=Debug")
        self.assertIn("Hello World Debug!", client.out)
