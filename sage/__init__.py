import os
import subprocess

from .tool_wrapper import *

MAKEFILE = "Makefile"

def generate_compile_commands(ctx):
    # move to build directory
    os.chdir(ctx.bld_path)
    # check "compile_commands.json" exist  
    if not os.path.isfile(os.path.join(ctx.bld_path, ctx.proj_file)):
        if not os.path.isfile(os.path.join(ctx.bld_path, MAKEFILE)):
            exit(1)
        # generage CompileCommand
        # compilation db
        subprocess.call(["compiledb", "--command-style", "make"])


def run_check_tools(ctx):
    for tool in ctx.tool_list:
        if get_tool_executable(tool) is None:
            print("* {} is not installed!!!".format(tool))
            continue
        print("* {} is running...".format(tool))
        wrapper = get_tool_wrapper(tool)(ctx)
        wrapper.run()