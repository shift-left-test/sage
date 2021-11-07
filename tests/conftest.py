import pytest
import os
import tempfile
import shutil
from distutils.spawn import find_executable

MAIN_BAD_CPP_CONTENT = """
#include <stdio.h>

namespace test {
  class Test {
    int test(){
      int a[10];
      int b = a[10] / 0;
      char *c;
      *c = 0;
      FILE *f = fopen("good.c", "r");
      return 1; ;
    }

    int test2(){
      test();
      test();
      test();
      test();
      test();
      return test();
    }
  };
  class Test2 {
    int test(){
      return 1; ;
    }

    int test2(){
      test();
      test();
      test();
      test();
      test();
      return test();
    }
  };
}

int main()
{
    return 0;
}
"""

MAIN_GOOD_CPP_CONTENT = """
// Copyright [2021] <Copyright Owner>

int main() {
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

EMPTY_COMPLIE_COMMANDS_CONTENT = """
[
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

    def run_tools(self, target_tools=[], ctx=None):
        from sage.tool_wrapper import load_tools, get_tool_list
        from sage.__main__ import run_tools
        from sage.context import WrapperContext

        if not ctx:
            ctx = WrapperContext(target_tools, self.src_path, self.bld_path)

        for toolname in get_tool_list():
            option = ctx.get_tool(toolname)
            if option and not find_executable(toolname):
                pytest.skip("Fail to find %s" % toolname)

        load_tools()
        run_tools(ctx)

        return ctx

    def destroy(self):
        shutil.rmtree(self.tmp_dir)


@pytest.fixture
def makefile_build(request):
    ctx = TestContext()

    ctx.add_src_file("main.cpp", MAIN_GOOD_CPP_CONTENT)
    ctx.add_build_file("Makefile", MAKEFILE_CONTENT)

    request.addfinalizer(ctx.destroy)
    return ctx


@pytest.fixture
def basic_build(request):
    ctx = TestContext()

    ctx.add_src_file("main.cpp", MAIN_GOOD_CPP_CONTENT)
    ctx.add_build_file("compile_commands.json", COMPLIE_COMMANDS_CONTENT.format(ctx.src_path))

    request.addfinalizer(ctx.destroy)
    return ctx


@pytest.fixture
def empty_build(request):
    ctx = TestContext()

    ctx.add_build_file("compile_commands.json", EMPTY_COMPLIE_COMMANDS_CONTENT.format(ctx.src_path))

    request.addfinalizer(ctx.destroy)
    return ctx


@pytest.fixture
def basic_build_bad_content(request):
    ctx = TestContext()

    ctx.add_src_file("main.cpp", MAIN_BAD_CPP_CONTENT)
    ctx.add_build_file("compile_commands.json", COMPLIE_COMMANDS_CONTENT.format(ctx.src_path))

    request.addfinalizer(ctx.destroy)
    return ctx


@pytest.fixture
def basic_build_hidden_file(request):
    ctx = TestContext()

    ctx.add_src_file("main.cpp", MAIN_GOOD_CPP_CONTENT)
    ctx.add_src_file(".b/a.cpp", MAIN_GOOD_CPP_CONTENT)
    ctx.add_build_file("compile_commands.json", COMPLIE_COMMANDS_CONTENT.format(ctx.src_path))

    request.addfinalizer(ctx.destroy)
    return ctx


@pytest.fixture
def source_only_build(request):
    ctx = TestContext()

    ctx.add_src_file("main.cpp", MAIN_GOOD_CPP_CONTENT)
    ctx.add_src_file("Makefile", MAKEFILE_CONTENT)

    request.addfinalizer(ctx.destroy)
    return ctx
