from conan.test_regression.utils.base_exe import BaseExeTest, run


class ZlibTest(BaseExeTest):

    libref = "zlib/1.2.11@conan/stable"
    librepo = "https://github.com/lasote/conan-zlib.git"
    branch = "release/1.2.11"

    def setUp(self):
        super(ZlibTest, self).setUp()
        run("conan remote add conan-center https://conan.bintray.com --insert 1")
        run("conan remove %s -f" % self.libref)

    def test_repo(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan create . conan/testing")

    def test_install_remote(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan test test_package %s" % self.libref)
