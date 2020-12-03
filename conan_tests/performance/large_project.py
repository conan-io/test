import time
import os
import unittest

from conans.test.assets.cpp_test_files import cpp_hello_conan_files
from conans.test.utils.tools import TestClient


def generate_random_project_graph(depth=15, width=(1, 10), cardinality=(0, 2),
                                  client=None, random_seed=None, **hello_kwargs):
    import random
    random.seed(random_seed)

    user_channel = "jgsogo/stable"
    version = "0.0"
    client = client or TestClient()
    # Generate the graph backwards

    total_libs = 0
    prev_level_libs = []
    current_level_libs = []
    for i_depth in range(depth):
        n_width = random.randint(*width)
        total_libs += n_width
        print("Generate level {} with {} packages".format(i_depth, n_width))

        prev_level_linked = set()
        for i_width in range(n_width):
            min_cardinalinity = min(cardinality[0], len(prev_level_libs))
            max_cardinalinity = min(cardinality[1], len(prev_level_libs))
            reqs = random.sample(prev_level_libs, random.randint(min_cardinalinity, max_cardinalinity))
            prev_level_linked.update(reqs)

            # Add remaining ones to the last one (will broke cardinality, but we do not want an
            # orphan branch in the graph
            if i_width == n_width - 1:
                remaining = set(prev_level_libs).difference(prev_level_linked)
                reqs += remaining

            name = "LibLevel%dWidth%d" % (i_depth, i_width)
            reference = "{}/{}@{}".format(name, version, user_channel)
            files = cpp_hello_conan_files(name, version, reqs, **hello_kwargs)
            client.save(files, clean_first=True)
            client.run("export . {}".format(user_channel))
            current_level_libs.append(reference)

            print(" - {}".format(reference))
            for it in reqs:
                print("   + {}".format(it))

        prev_level_libs = current_level_libs.copy()
        current_level_libs.clear()

    # Create the project one
    print("General PROJECT")
    for it in prev_level_libs:
        print("  + {}".format(it))
    files = cpp_hello_conan_files("project", version, prev_level_libs, **hello_kwargs)
    client.save(files, clean_first=True)

    total_libs += 1
    print("... total libraries in graph: {}".format(total_libs))
    return client


def generate_large_project(num, folder=None, deep=True, client=None):
    # deep = True for N ... -> 3 -> 2 -> 1 -> 0, False for N -> 0, 3-> 0, 2->0, 1->0
    client = client or TestClient()
    if folder:
        client.current_folder = folder
    use_additional_infos = 20

    files = cpp_hello_conan_files("build", "0.1", build=False)
    client.save(files, clean_first=True)
    client.run("create . lasote/stable")
    files = cpp_hello_conan_files("build2", "0.1", build=False)
    client.save(files, clean_first=True)
    client.run("create . lasote/stable")

    for i in range(num):
        if i % 10 == 0:
            print ("Generating ", i)
        if i == 0:
            files = cpp_hello_conan_files("Base", "0.1", build=False)
            client.save(files, clean_first=True)
            client.run("export . lasote/stable")
            files = cpp_hello_conan_files("Base2", "0.1", ["Base/0.1@lasote/stable"], build=False)
            client.save(files, clean_first=True)
            client.run("export . lasote/stable")
            files = cpp_hello_conan_files("Hello0", "0.1", ["Base2/0.1@lasote/stable"], build=False)
        else:
            if not deep:
                files = cpp_hello_conan_files("Hello%d" % i, "0.1",
                                                ["Hello0/0.1@lasote/stable", "Base/0.1@lasote/stable", "Base2/0.1@lasote/stable"], build=False,
                                                use_additional_infos=use_additional_infos)
            else:
                files = cpp_hello_conan_files("Hello%d" % i, "0.1",
                                                ["Hello%s/0.1@lasote/stable" % (i-1)],
                                                build=False,
                                                use_additional_infos=use_additional_infos)
            conanfile = files["conanfile.py"]
            conanfile = conanfile + "    build_requires = 'build/0.1@lasote/stable', 'build2/0.1@lasote/stable'"
            files["conanfile.py"] = conanfile
        client.save(files, clean_first=True)
        client.run("export . lasote/stable")

    # Now lets depend on it
    if deep:
        files = cpp_hello_conan_files("HelloFinal", "0.1",
                                        ["Hello%s/0.1@lasote/stable" % (num - 1)], build=False,
                                        use_additional_infos=use_additional_infos)
    else:
        files = cpp_hello_conan_files("HelloFinal", "0.1",
                                        ["Hello%s/0.1@lasote/stable" % i for i in range(num)],
                                        build=False, use_additional_infos=use_additional_infos)

    client.save(files, clean_first=True)
    return client


class PerformanceTest(unittest.TestCase):
    """ NOT really a test, but a helper to profile performance
    FILE name is not "test" so it will not run under unit testing
    """

    def test_large_project(self):
        client = generate_large_project(num=100, deep=True)
        t1 = time.time()
        client.run("install . --build")
        print("Final time with build %s" % (time.time() - t1))
        t1 = time.time()
        client.run("install .")
        print("Final time %s" % (time.time() - t1))

    def test_graph_project(self):
        client = TestClient()
        client = generate_random_project_graph(depth=15, cardinality=(0, 2), random_seed=23456,
                                               client=client, build=False, use_additional_infos=1)

        graph_html = os.path.abspath(os.path.join(os.getcwd(), "graph.html"))
        client.run("info -g {} .".format(graph_html))
        print("Graph HTML: {}".format(graph_html))

        t1 = time.time()
        client.run("install . --build")
        print("Final time with build %s" % (time.time() - t1))
        t1 = time.time()
        client.run("install .")
        print("Final time %s" % (time.time() - t1))
