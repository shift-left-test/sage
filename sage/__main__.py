import argparse
import logging
import subprocess
import os
import sys

from .tool_wrapper import *
from .utils import generate_compile_commands, run_check_tools

def main():
    parser = argparse.ArgumentParser(description="Static Analysis Group Execution")
    parser.add_argument("--source", help="source path")
    parser.add_argument("--build", help="build path")
    parser.add_argument("--output-path", help="output path")
    parser.add_argument("--tool-list", action='store_true', help="show tool list")
    parser.add_argument("--target", help="compile target triple")
    parser.add_argument("tools", nargs="*", help="Static analysis program list",
                        default=["cppcheck", "cpplint", "clang-tidy"])

    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    if args.tool_list:
        for tool in get_tool_list():
            print("{}: {}".format(tool, get_tool_executable(tool)))
        return

    ctx = WrapperContext(args.source, args.build, args.output_path, args.target, args.tools)
    
    generate_compile_commands(ctx)

    run_check_tools(ctx)


if __name__ == "__main__":
    main()