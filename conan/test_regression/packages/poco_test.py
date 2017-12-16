from conan.test_regression.utils.base_exe import BaseExeTest, run


class PocoTest(BaseExeTest):

    libref = "Poco/1.8.0.1@pocoproject/stable"
    librepo = "https://github.com/pocoproject/conan-poco.git"
    branch = "release/1.8.0.1"

    def setUp(self):
        super(PocoTest, self).setUp()
        run("conan remote add conan-center https://conan.bintray.com --insert 1")
        run("conan remove %s -f" % self.libref)

    def test_repo(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan create conan/testing")

    def test_install_remote(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan test test_package %s" % self.libref)
