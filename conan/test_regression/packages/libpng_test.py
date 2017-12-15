from conan.test_regression.utils.base_exe import BaseExeTest, run


class LibPNGTest(BaseExeTest):

    libref = "libpng/1.6.32@conan/stable"
    librepo = "https://github.com/lasote/conan-libpng"
    branch = "release/1.6.32"

    def setUp(self):
        super(LibPNGTest, self).setUp()
        run("conan remote add conan-community https://api.bintray.com/conan/conan-community/conan --insert 1",
            ignore_error=True)
        run("conan remove %s -f" % self.libref)

    def test_repo(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan create conan/testing")

    def test_install_remote(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan test test_package %s" % self.libref)
