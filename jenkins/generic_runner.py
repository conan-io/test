import os
import platform

from runner import pylocations, run


def run_in_venv(command, tmp_folder, pyver=None):

    pyver = pyver or "py36"
    venv_dest = os.path.join(tmp_folder, "venv")
    source_cmd = "." if platform.system() != "Windows" else ""
    if not os.path.exists(venv_dest):
        os.makedirs(venv_dest)
    venv_exe = os.path.join(venv_dest,
                            "bin" if platform.system() != "Windows" else "Scripts",
                            "activate")
    cmd = "virtualenv --python \"{pyenv}\" \"{venv_dest}\" && " \
          "{source_cmd} \"{venv_exe}\" && " \
          "{command}".format(**{"pyenv": pylocations[pyver],
                                "venv_dest": venv_dest,
                                "venv_exe": venv_exe,
                                "source_cmd": source_cmd,
                                "command": command})
    run(cmd)


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='Launch a command in a virtualenv')
    parser.add_argument('command', help='e.j: command to run inside the virtualenv')
    parser.add_argument('tmp_folder', help='Folder to create the venv inside')
    parser.add_argument('--pyver', help='e.j: py27')

    args = parser.parse_args()
    run_in_venv(args.command, args.tmp_folder, args.pyver)

