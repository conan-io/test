from conan_tests.test_regression.utils.base_exe import BaseExeTest, run, conan_create_command


class OpenSSLTest(BaseExeTest):

    libref = "OpenSSL/1.0.2o@conan/stable"
    librepo = "https://github.com/conan-community/conan-openssl.git"

    def setUp(self):
        super(OpenSSLTest, self).setUp()
        run("conan remove %s -f" % self.libref, ignore_error=True)

    # FIXME: DISABLED UNTIL BINCRAFTERS SOLVE THE OPENSSL REFACTORS
    #def test_repo(self):
    #    run("git clone --depth 1 %s  ." % self.librepo)
    #    run(conan_create_command(self.libref))

    #def test_install_remote(self):
    #    run("git clone --depth 1 %s ." % self.librepo)
    #    run("conan test test_package %s" % self.libref)
