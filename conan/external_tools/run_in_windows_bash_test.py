import os
import platform
import unittest

import nose

from conan.conf import CONAN_WSL_PATH, CONAN_MSYS2_PATH, CONAN_CYGWIN_PATH, CONAN_GIT_BIN_PATH, CONAN_GIT_BIN_PATH_SPACES, \
    CONAN_MSYS2_PATH_SPACES, CONAN_CYGWIN_PATH_SPACES
from conans import __version__ as conan_version
from conans import tools
from conans.model.version import Version
from conans.test.utils.tools import TestClient


class RunInWindowsBashTest(unittest.TestCase):

    def test_run_bash_in_windows(self):
        if Version(conan_version) < Version("1.0.3") or platform.system() != "Windows":
            raise nose.SkipTest('Only windows test')
        conanfile = """
import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
class LibConan(ConanFile):
    def build(self):
        self.run("echo 'hello Conan!'", win_bash=True)
        self.run("ls", win_bash=True)
        tools.save("configure", "echo 'configuring...'")
        tools.save("Makefile", "all:\\n\\techo 'makeing...'")
        abe = AutoToolsBuildEnvironment(self, win_bash=True)
        abe.configure(configure_dir=self.build_folder, args=["--enable-silent-rules"])
        abe.make()
"""

        client = TestClient()
        client.save({"conanfile.py": conanfile})
        for bash_path in [CONAN_GIT_BIN_PATH, CONAN_GIT_BIN_PATH_SPACES,
                          CONAN_MSYS2_PATH, CONAN_MSYS2_PATH_SPACES,
                          CONAN_CYGWIN_PATH, CONAN_CYGWIN_PATH_SPACES,
                          CONAN_WSL_PATH]:
            full_path = os.path.normpath(os.path.join(bash_path, "bash.exe"))
            print("Trying %s" % full_path)
            # CI doesn't have WSL (not win10)
            if not os.path.exists(full_path):
                if bash_path != CONAN_WSL_PATH:
                    raise Exception("Not found tool: %s" % full_path)
                else:
                    continue

            with tools.environment_append({"CONAN_BASH_PATH": full_path}):
                client.run("create . lib/1.0@lasote/stable")
                self.assertIn(full_path, client.out)
                print(client.out)
                self.assertIn("hello Conan!", client.out)
                self.assertIn("configuring...", client.out)
                self.assertIn("makeing...", client.out)
