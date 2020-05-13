import argparse
import os
import subprocess
from .tool_wrapper import *

COMMPILE_COMMAND_FILE = "compile_commands.json"
MAKEFILE = "Makefile"

def main():
    parser = argparse.ArgumentParser(description="Static Analysis Group Execution")
    parser.add_argument("--source", help="source path")
    parser.add_argument("--build", help="build path")
    parser.add_argument("--output-path", help="output path")
    parser.add_argument("tools", nargs="*", help="Static analysis program list",
                        default=["cppcheck", "cpplint", "clang-tidy"])
    args = parser.parse_args()

    TOOL_LIST = args.tools

    ctx = WrapperContext()
    
    if args.source:
        ctx.src_path = os.path.abspath(args.source)

    if args.build:
        ctx.bld_path = os.path.abspath(args.build)

    if args.output_path:
        ctx.output_path = os.path.abspath(args.output_path)

    # move to build directory
    os.chdir(ctx.bld_path)
    # check "compile_commands.json" exist  
    if not os.path.isfile(os.path.join(ctx.bld_path, ctx.proj_file)):
        if not os.path.isfile(os.path.join(ctx.bld_path, MAKEFILE)):
            exit(1)
        # generage CompileCommand
        # compilation db
        subprocess.call(["compiledb", "--command-style", "make"])

    for tool in TOOL_LIST:
        print("* {} is running...".format(tool))
        wrapper = get_tool_wrapper(tool)(ctx)
        wrapper.run()


if __name__ == "__main__":
    main()