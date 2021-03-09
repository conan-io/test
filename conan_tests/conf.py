import os
import platform

import nose

from conans import tools
from contextlib import contextmanager

CONAN_MINGW_PATH = os.getenv("CONAN_MINGW_PATH", "C:/msys64/mingw64/bin")

CONAN_MSYS2_PATH = os.getenv("CONAN_MSYS2_PATH", "C:/msys64/usr/bin")
CONAN_MSYS2_PATH_SPACES = os.getenv("CONAN_MSYS2_PATH_SPACES", "C:/msys64/usr/b in")

CONAN_CYGWIN_PATH = os.getenv("CONAN_CYGWIN_PATH", "C:/cygwin64/bin")
CONAN_CYGWIN_PATH_SPACES = os.getenv("CONAN_CYGWIN_PATH_SPACES", "C:/cygwin64/b in")

CONAN_WSL_PATH = os.getenv("CONAN_WSL_PATH", "c:/windows/sysnative")

CONAN_GIT_BIN_PATH = os.getenv("CONAN_GIT_BIN_PATH", "C:/Tools/Git/bin")
CONAN_GIT_BIN_PATH_SPACES = os.getenv("CONAN_GIT_BIN_PATH_SPACES", "C:/Program Files/Git/bin")

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
    path = os.pathsep.join([path, os.environ["PATH"]])
    with tools.environment_append({"PATH": path}):
        yield


