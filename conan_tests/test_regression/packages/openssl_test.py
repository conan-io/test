from conan_tests.test_regression.utils.base_exe import BaseExeTest, run, conan_create_command


class OpenSSLTest(BaseExeTest):

    libref = "OpenSSL/1.0.2m@conan/stable"
    librepo = "https://github.com/lasote/conan-openssl.git"
    branch = "release/1.0.2m"

    def setUp(self):
        super(OpenSSLTest, self).setUp()
        run("conan remove %s -f" % self.libref)

    def test_repo(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run(conan_create_command("conan/testing"))

    def test_install_remote(self):
        run("git clone --depth 1 %s -b %s ." % (self.librepo, self.branch))
        run("conan test test_package %s" % self.libref)
