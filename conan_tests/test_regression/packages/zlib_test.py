from conan_tests.test_regression.utils.base_exe import BaseExeTest, run, conan_create_command


class ZlibTest(BaseExeTest):

    libref = "zlib/1.2.11@conan/stable"
    librepo = "https://github.com/conan-community/conan-zlib.git"
    branch = "release/1.2.11"

    def setUp(self):
        super(ZlibTest, self).setUp()
        run("conan remove %s -f" % self.libref)

    def test_repo(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run(conan_create_command("conan/testing"))

    def test_install_remote(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan test test_package %s" % self.libref)
