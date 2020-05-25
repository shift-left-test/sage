import argparse
import subprocess
import os

from .tool_wrapper import *
from . import generate_compile_commands, run_check_tools

def main():
    parser = argparse.ArgumentParser(description="Static Analysis Group Execution")
    parser.add_argument("--source", help="source path")
    parser.add_argument("--build", help="build path")
    parser.add_argument("--output-path", help="output path")
    parser.add_argument("tools", nargs="*", help="Static analysis program list",
                        default=["cppcheck", "cpplint", "clang-tidy"])
    args = parser.parse_args()

    ctx = WrapperContext()
    
    if args.source:
        ctx.src_path = os.path.abspath(args.source)

    if args.build:
        ctx.bld_path = os.path.abspath(args.build)

    if args.output_path:
        ctx.output_path = os.path.abspath(args.output_path)

    ctx.tool_list = args.tools

    generate_compile_commands(ctx)

    run_check_tools(ctx)


if __name__ == "__main__":
    main()