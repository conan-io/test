import os

from threading import Thread
from conan_tests.test_regression.utils.base_exe import BaseExeTest, run, save
from conans.model.version import Version
from conans.server.rest.bottle_plugins.version_checker import VersionCheckerPlugin
from conans.test.server.utils.server_launcher import TestServerLauncher

count = 10  # Number of parallel processes


class ConcurrencyTest(BaseExeTest):

    def export_test(self):
        conanfile = """from conans import ConanFile
class ConanMeanLib(ConanFile):
    exports = "*.txt"
    """

        save("conanfile.py", conanfile)
        save("file.txt", "whatever")

        total_output = []

        def export():
            out = run("conan export . Pkg/0.1@user/testing", capture=True)
            total_output.append(out)
        ps = []
        for _ in range(count):
            thread = Thread(target=export)
            ps.append(thread)

        for p in ps:
            p.start()
        for p in ps:
            p.join()
        final_output = "\n".join(total_output)
        self.assertEqual(count - 1, final_output.count("Pkg/0.1@user/testing: The stored package has not changed"))
        self.assertEqual(1, final_output.count("Pkg/0.1@user/testing: A new conanfile.py version was exported"))

    def create_test(self):
        conanfile = """from conans import ConanFile
from conans.tools import save
class ConanMeanLib(ConanFile):
    settings = "os"
    exports = "*.txt"
    def source(self):
        save("header.h", "my_header %s" % self.settings.os)
    def build(self):
        save("source.cpp", "my_source %s" % self.settings.os)
    def package(self):
        self.copy("*")
    """

        save("conanfile.py", conanfile)
        save("file.txt", "whatever")

        total_output = []

        def create():
            out = run("conan create . Pkg/0.1@user/testing", capture=True)
            total_output.append(out)
        ps = []
        for _ in range(count):
            thread = Thread(target=create)
            ps.append(thread)

        for p in ps:
            p.start()
        for p in ps:
            p.join()
        final_output = "\n".join(total_output)
        self.assertEqual(1, final_output.count("Pkg/0.1@user/testing: A new conanfile.py version was exported"))
        self.assertEqual(count, final_output.count("Pkg/0.1@user/testing: Calling build()"))
        self.assertEqual(count, final_output.count("Pkg/0.1@user/testing: Calling package()"))


class ConcurrencyDownloadTest(BaseExeTest):
    server = None

    @classmethod
    def setUpClass(cls):
        if not cls.server:
            plugin = VersionCheckerPlugin(Version("0.16.0"), Version("0.16.0"), ["ImCool"])
            cls.server = TestServerLauncher(server_version=Version("0.16.0"),
                                            min_client_compatible_version=Version("0.16.0"),
                                            plugins=[plugin], users = {"user": "user"})
            cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def install_one_test(self):
        conanfile = """from conans import ConanFile
import time
class ConanMeanLib(ConanFile):
    settings = "os"
    exports = "*.txt"
    def package(self):
        self.copy("*")
    # To force some concurrency
    def system_requirements(self):
        time.sleep(0.3)
    """

        save("conanfile.py", conanfile)
        save("file.txt", "whatever")

        run("conan create . Pkg/0.1@user/testing -s os=Windows")
        run("conan remote add local http://localhost:9300 --insert")
        run("conan user user -p user --remote=local")
        run("conan upload Pkg/0.1@user/testing --all -r=local")
        run('conan remove "*" -f')

        os.remove("conanfile.py")
        save("conanfile.txt", "[requires]\nPkg/0.1@user/testing")

        total_output = []
        def install():
            out = run("conan install . -s os=Windows", capture=True)
            total_output.append(out)
        ps = []
        for i in range(count):
            thread = Thread(target=install)
            ps.append(thread)

        for p in ps:
            p.start()
        for p in ps:
            p.join()
        final_output = "\n".join(total_output)
        self.assertEqual(1, final_output.count("Downloading conan_export.tgz"))
        self.assertEqual(1, final_output.count("Downloading conan_package.tgz"))
        skipped_downloads = final_output.count("Pkg/0.1@user/testing: Download skipped. "
                                               "Probable concurrent download")
        cached_installs = final_output.count("Pkg/0.1@user/testing: Already installed!")
        self.assertEqual(count - 1, skipped_downloads + cached_installs)
