import argparse
import logging
import subprocess
import os
import sys

logger = logging.getLogger('SAGE')

from .tool_wrapper import *
from .utils import run_check_tools

def main():
    parser = argparse.ArgumentParser(description="Static Analysis Group Execution")
    parser.add_argument("--source-path", help="source path")
    parser.add_argument("--build-path", help="build path")
    parser.add_argument("--tool-path", help="if this option is specified, only tools in this path is executed")
    parser.add_argument("--output-path", help="output path")
    parser.add_argument("--target-triple", help="compile target triple")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("tools", nargs="*", help="Static analysis program list",
                        default=["cppcheck", "cpplint", "clang-tidy"])

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING

    logging.basicConfig(stream=sys.stdout, level=log_level)

    ctx = WrapperContext(args.source_path, args.build_path, args.tool_path, args.output_path, args.target_triple, args.tools)

    if os.path.exists(os.path.join(ctx.work_path, "compile_commands.json")):
        run_check_tools(ctx)
    else:
        logger.error("There is no 'compile_commands.json'")


if __name__ == "__main__":
    main()