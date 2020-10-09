import os

from conf import winpylocation, linuxpylocation, macpylocation, environment_append, get_environ
import platform

pylocations = {"Windows": winpylocation,
               "Linux": linuxpylocation,
               "Darwin": macpylocation}[platform.system()]


def run_tests(module_path, conan_branch, pyver, tmp_folder, num_cores=3):

    venv_dest = os.path.join(tmp_folder, "venv")
    if not os.path.exists(venv_dest):
        os.makedirs(venv_dest)
    venv_exe = os.path.join(venv_dest,
                            "bin" if platform.system() != "Windows" else "Scripts",
                            "activate")

    pyenv = pylocations[pyver]
    source_cmd = "." if platform.system() != "Windows" else ""
    multiprocess = ""
    if (platform.system() != "Darwin" or pyver == "py27") and num_cores > 1:
        multiprocess = ("--processes=%s --process-timeout=1000 "
                        "--process-restartworker" % num_cores)

    pip_installs = ["pip install -r conan_tests/requirements.txt"]
    if platform.system() == "Windows":
        pip_installs.append("python.exe -m pip install --upgrade pip")
        pip_installs.append("pip install setuptools!=41.5.0") # FIXME: https://github.com/pypa/setuptools/issues/1891
        pip_installs.append('pip install requests["security"]')
        pip_installs.append("pip install scons")

    else:
        pip_installs.append("pip install --upgrade pip")

    change_dir = "/d " if platform.system() == "Windows" else ""
    #  --nocapture
    command = "virtualenv --python \"{pyenv}\" \"{venv_dest}\" && " \
              "{source_cmd} \"{venv_exe}\" && " \
              "{pip_installs} && " \
              "cd {change_dir}{tmp_folder} && git clone --depth 1 " \
              "https://github.com/conan-io/conan.git -b {branch} conan_p && " \
              "cd conan_p && pip install . && cd {change_dir}{cwd} && " \
              "conan --version && conan --help && " \
              "nosetests {module_path} --verbosity=2 " \
              "{multiprocess} ".format(
                                    **{"module_path": module_path,
                                       "pyenv": pyenv,
                                       "branch": conan_branch,
                                       "venv_dest": venv_dest,
                                       "tmp_folder": tmp_folder,
                                       "venv_exe": venv_exe,
                                       "source_cmd": source_cmd,
                                       "multiprocess": multiprocess,
                                       "pip_installs": " && ".join(pip_installs),
                                       "cwd": os.getcwd(),
                                       "change_dir": change_dir})

    env = get_environ(tmp_folder)
    env["CONAN_LOGGING_LEVEL"] = "50" if platform.system() == "Darwin" else "50"
    env['PYTHON_EGG_CACHE'] = os.path.join(tmp_folder, "egg")
    env['PYTHONPATH'] = os.path.join(tmp_folder, "conan_p")
    if pyver.startswith("py2"):
        env["USE_UNSUPPORTED_CONAN_WITH_PYTHON_2"] = "True"

    os.mkdir(env['PYTHON_EGG_CACHE'])
    with environment_append(env):
        print(command)
        run(command)


def run(command):
    print("--CALLING: %s" % command)
    # return os.system(command)
    import subprocess

    # ret = subprocess.call("bash -c '%s'" % command, shell=True)
    shell = '/bin/bash' if platform.system() != "Windows" else None
    ret = subprocess.call(command, shell=True, executable=shell)
    if ret != 0:
        raise Exception("Error running: '%s'" % command)


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser(description='Launch tests in a venv')
    parser.add_argument('module', help='e.j: conans.test')
    parser.add_argument('pyver', help='e.j: py27')
    parser.add_argument('conan_branch', help='Branch to conan to checkout')
    parser.add_argument('tmp_folder', help='Folder to create the venv inside')
    parser.add_argument('--num_cores', type=int, help='Number of cores to use', default=3)

    args = parser.parse_args()
    run_tests(args.module, args.conan_branch, args.pyver, args.tmp_folder, num_cores=args.num_cores)


# python jenkins/runner.py conan.external_tools.conan_package_tools_test py27 develop /tmp/kk --num_cores=1
