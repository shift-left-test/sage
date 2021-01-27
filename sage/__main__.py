# -*- coding: utf-8 -*-

import argparse
import logging
import subprocess
import os
import sys
import textwrap

logger = logging.getLogger('SAGE')

from .tool_wrapper import *
from .utils import run_tools, generate_report
from .context import WrapperContext, ToolType


def main():
    parser = argparse.ArgumentParser(description="Static Analysis Group Execution", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--source-path", help="source path")
    parser.add_argument("--build-path", help="build path")
    parser.add_argument("--tool-path", help="if this option is specified, only tools in this path is executed")
    parser.add_argument("--output-path", help="output path")
    parser.add_argument("--target-triple", help="compile target triple")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("tools", nargs="*", help=textwrap.dedent("""\
        Static analysis program list.
        Tool-specific command-line options separated by colons can be added after the tool name.
        ex) 'cppcheck:--library=googletest'"""),
        default=["cppcheck", "cpplint"])

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.WARNING

    logging.basicConfig(stream=sys.stdout, level=log_level)

    # load wrapper
    logger.info("load wrapper")
    load_tools()

    # context 구성
    ctx = WrapperContext(args.source_path, args.build_path, args.tool_path, args.output_path, args.target_triple, args.tools)

    # metrics
    logger.info("measure source code")
    run_tools(ctx, ToolType.METRICS)

    # clone detection
    logger.info("clone detection")
    run_tools(ctx, ToolType.CLONE_DETECTION)

    # static analysis
    logger.info("check violations")
    if os.path.exists(os.path.join(ctx.work_path, "compile_commands.json")):
        run_tools(ctx, ToolType.CHECK)
    else:
        logger.error("There is no 'compile_commands.json'")

    # security analysis
    logger.info("check security")
    run_tools(ctx, ToolType.SECURITY)

    # generate report
    logger.info("reporting")
    generate_report(ctx)


if __name__ == "__main__":
    main()