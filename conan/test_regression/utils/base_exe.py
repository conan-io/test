import platform
import unittest
import tempfile
import os
import logging
from subprocess import PIPE, Popen
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


logger = logging.getLogger('conan_tests')
logger.setLevel(logging.DEBUG)


def save_files(files_dict):
    for name, content in files_dict.items():
        save(name, content)


def save(filename, content):
    try:
        os.makedirs(os.path.dirname(filename))
    except:
        pass

    with open(filename, "w") as handle:
        handle.write(content)


def load(filename, ):
    with open(filename, "r") as handle:
        return handle.read()


def run(command, ignore_error=False, capture=False):
    if command.startswith("conan") and os.environ.get("CONAN_EXECUTABLE_NAME", None):
        command = os.environ["CONAN_EXECUTABLE_NAME"] + command[5:]

    print("Running: %s" % command)
    if capture:
        stream_output = StringIO()
        try:

            proc = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        except Exception as e:
            raise Exception("Error while executing '%s'\n\t%s" % (command, str(e)))

        def get_stream_lines(the_stream):
            while True:
                line = the_stream.readline()
                if not line:
                    break
                stream_output.write(str(line))

        get_stream_lines(proc.stdout)
        get_stream_lines(proc.stderr)

        proc.communicate()
        ret = proc.returncode
        if ret != 0 and not ignore_error:
            raise Exception("Command failed: %s.\n%s" % (command, stream_output.getvalue()))
        ret = stream_output.getvalue()
        print(ret)
        return ret
    else:
        ret = os.system(command)
        if ret != 0 and not ignore_error:
            raise Exception("Command failed! %s" % command)
        return ret


class BaseExeTest(unittest.TestCase):

    def setUp(self):
        test_folder = os.getenv('CONAN_TEST_FOLDER', "c:/tmp" if platform.system() == "Windows" else "/tmp")
        if not os.path.exists(test_folder):
            os.mkdir(test_folder)
        self.old_folder = os.getcwd()
        folder = tempfile.mkdtemp(suffix='conan', dir=test_folder)
        os.chdir(folder)
        logger.debug("Test code folder %s" % folder)
        user_home = tempfile.mkdtemp(suffix="conan", dir=test_folder)
        # user_home = "c:/tmp/home"  # Cache
        logger.debug("Test user_home folder %s" % user_home)
        self.user_home = user_home
        self.old_env = dict(os.environ)
        os.environ.update({"CONAN_USER_HOME": user_home})
        run("conan remote remove conan-center", ignore_error=True)
        run("conan remote remove conan-transit", ignore_error=True)
        run("conan remote add conan-testuite https://conan.jfrog.io/conan/api/conan/conan-testsuite", ignore_error=True)

    def tearDown(self):
        os.chdir(self.old_folder)
        os.environ.clear()
        os.environ.update(self.old_env)
