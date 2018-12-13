from conan_tests.test_regression.utils.base_exe import BaseExeTest, run, conan_create_command


class LibPNGTest(BaseExeTest):

    libref = "libpng/1.6.34@bincrafters/stable"
    librepo = "https://github.com/lasote/conan-libpng"
    branch = "release/1.6.32"

    def setUp(self):
        super(LibPNGTest, self).setUp()
        run("conan remove %s -f" % self.libref)

    def test_repo(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run(conan_create_command("conan/testing"))

    def test_install_remote(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan test test_package %s" % self.libref)
