import os
import platform

import nose

from conans import tools
from contextlib import contextmanager

CONAN_MINGW_PATH = os.getenv("CONAN_MINGW_PATH", "C:/Mingw/bin")
CONAN_MSYS2_PATH = os.getenv("CONAN_MSYS2_PATH", "C:/msys64/usr/bin")
CONAN_CYGWIN_PATH = os.getenv("CONAN_CYGWIN_PATH", "C:/cygwin64/bin")


@contextmanager
def mingw_in_path():
    return _in_path_win(CONAN_MINGW_PATH)

@contextmanager
def msys2_in_path():
    return _in_path_win(CONAN_MSYS2_PATH)

@contextmanager
def cygwin_in_path():
    return _in_path_win(CONAN_CYGWIN_PATH)

def _in_path_win(path):
    if platform.system() != "Windows":
        raise nose.SkipTest('Only windows test')

    path = os.pathsep.join([path, os.environ["PATH"]])
    with tools.environment_append({"PATH": path}):
        yield


