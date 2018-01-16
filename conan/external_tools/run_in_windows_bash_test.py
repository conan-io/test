import os
import platform
import unittest

import nose

from conan.conf import CONAN_WSL_PATH, CONAN_MSYS2_PATH, CONAN_CYGWIN_PATH, CONAN_GIT_BIN_PATH, CONAN_GIT_BIN_PATH2
from conans import __version__ as conan_version
from conans import tools
from conans.model.version import Version
from conans.test.utils.tools import TestClient


class RunInWindowsBashTest(unittest.TestCase):

    def test_run_bash_in_windows(self):
        if Version(conan_version) < Version("1.0.0-beta.4") or platform.system() != "Windows":
            raise nose.SkipTest('Only windows test')
        conanfile = """
from conans import ConanFile, tools
class LibConan(ConanFile):
    def build(self):
        self.run("echo 'hello Conan!'", win_bash=True)
        self.run("ls", win_bash=True)
"""

        client = TestClient()
        client.save({"conanfile.py": conanfile})
        for bash_path in [CONAN_GIT_BIN_PATH, CONAN_GIT_BIN_PATH2, CONAN_MSYS2_PATH, CONAN_CYGWIN_PATH, CONAN_WSL_PATH]:
            bash_path = os.path.normpath(os.path.join(bash_path, "bash.exe"))
            if not os.path.exists(bash_path):
                raise Exception("Not found tool: %s" % bash_path)

            with tools.environment_append({"CONAN_BASH_PATH": bash_path}):
                client.run("create . lib/1.0@lasote/stable")
                self.assertIn(bash_path, client.out)
                self.assertIn("hello Conan!", client.out)
