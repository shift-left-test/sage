import pytest
import os
import tempfile
import shutil

MAIN_CPP_CONTENT = """
#include <stdio.h>

int main()
{
    return 0;
}
"""

MAKEFILE_CONTENT = """
cc = gcc

main: main.o
\tgcc -o main main.o

main.o: main.cpp
\tgcc -c -o main.o main.cpp
"""

COMPLIE_COMMANDS_CONTENT = """
[
 {{
  "directory": "{}",
  "command": "/usr/bin/cc -o main.cpp.o -c main.cpp",
  "file": "main.cpp"
 }}
]
"""


class TestContext():
    def __init__(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.src_path = os.path.join(self.tmp_dir, 'source')
        self.bld_path = os.path.join(self.tmp_dir, 'build')
        os.makedirs(self.src_path)
        os.makedirs(self.bld_path)


    def _add_file(self, basepath, filepath, content):
        fullfilepath = os.path.join(basepath, filepath)
        if not os.path.exists(os.path.dirname(fullfilepath)):
            os.makedirs(os.path.dirname(fullfilepath))

        with open(fullfilepath, "w") as f:
            f.write(content)
                    

    def add_src_file(self, filepath, content):
        self._add_file(self.src_path, filepath, content)


    def add_build_file(self, filepath, content):
        self._add_file(self.bld_path, filepath, content)


    def destroy(self):
        shutil.rmtree(self.tmp_dir)


@pytest.fixture
def makefile_build(request):
    ctx = TestContext()

    ctx.add_src_file("main.cpp", MAIN_CPP_CONTENT)
    ctx.add_build_file("Makefile", MAKEFILE_CONTENT)

    request.addfinalizer(ctx.destroy)
    return ctx


@pytest.fixture
def basic_build(request):
    ctx = TestContext()

    ctx.add_src_file("main.cpp", MAIN_CPP_CONTENT)
    ctx.add_build_file("compile_commands.json", COMPLIE_COMMANDS_CONTENT.format(ctx.src_path))

    request.addfinalizer(ctx.destroy)
    return ctx


@pytest.fixture
def source_only_build(request):
    ctx = TestContext()

    ctx.add_src_file("main.cpp", MAIN_CPP_CONTENT)
    ctx.add_src_file("Makefile", MAKEFILE_CONTENT)

    #request.addfinalizer(ctx.destroy)
    return ctx