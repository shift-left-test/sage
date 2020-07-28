import os
import subprocess

from .tool_wrapper import *

MAKEFILE = "Makefile"
COMPILE_DB_MARKER = ".compiledb_mark"

def _create_compile_commands(ctx):
    if not os.path.isfile(os.path.join(ctx.work_path, MAKEFILE)):
        print("WARNING: can't generage compile_commands.json without Makefile")
        return

    os.chdir(ctx.work_path)
    # TODO: rm compile_commands.json and sage_compile_commands.json

    # TODO: generage COMPILE_DB_MARKER as different name
    subprocess.call(["compiledb", "--command-style", "make", "--output", "sage_compile_commands.json"])
    # TODO: append sage_compile_commands.json create data to COMPILE_DB_MARKER and rename compile_commands.json


def generate_compile_commands(ctx):
    # move to work directory

    # check "compile_commands.json" exist  
    if os.path.isfile(os.path.join(ctx.work_path, ctx.proj_file)):
        if not os.path.isfile(os.path.join(ctx.work_path, COMPILE_DB_MARKER)):
            # this compile_commands.json is not generaged by sage. so don't touch
            return
        else:
            # TODO: mark files date with compile_commands.json create date
            pass

    _create_compile_commands(ctx)


def run_check_tools(ctx):
    for tool in ctx.tool_list:
        if get_tool_executable(tool) is None:
            print("* {} is not installed!!!".format(tool))
            continue
        print("* {} is running...".format(tool))
        wrapper = get_tool_wrapper(tool)(ctx)
        wrapper.run()