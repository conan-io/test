from conan_tests.test_regression.utils.base_exe import BaseExeTest, run, conan_create_command


class LibPNGTest(BaseExeTest):

    libref = "libpng/1.6.34@bincrafters/stable"
    librepo = "https://github.com/bincrafters/conan-libpng.git"
    branch = "stable/1.6.34"

    def setUp(self):
        super(LibPNGTest, self).setUp()
        run("conan remove %s -f" % self.libref, ignore_error=True)

    def test_repo(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run(conan_create_command("conan/testing"))

    def test_install_remote(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan test test_package %s" % self.libref)
