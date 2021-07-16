# -*- coding: utf-8 -*-

import argparse
import copy
import logging
import subprocess
import os
import sys
import textwrap
from texttable import Texttable

logger = logging.getLogger('SAGE')

from .tool_wrapper import *
from .context import WrapperContext, ToolType
from .report import Report

def run_tools(ctx, tool_type):
    for tool, option in ctx.get_tools(tool_type):
        wrapper = get_tool_wrapper(tool)(tool, option)
        if wrapper.get_tool_path(ctx) is None:
            logger.warning("* {} is not installed!!!".format(tool))
            continue
        logger.info("* {} is running...".format(tool))
        wrapper.run(ctx)
            

run_tools.__annotations__ = {'ctx': WrapperContext, 'tool_type': ToolType}


def generate_report(ctx, args_dict):
    report = Report(ctx, args_dict)

    table = Texttable(max_width=0)
    table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
    table.add_rows(report.get_summary_table())

    print(table.draw())

    if ctx.output_path:
        report.write_to_file(os.path.join(ctx.output_path, "sage_report.json"))


generate_report.__annotations__ = {'ctx': WrapperContext, 'args_dict': dict}


def main():
    parser = argparse.ArgumentParser(description="Static Analysis Group Execution", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--source-path", help="source path")
    parser.add_argument("--build-path", help="build path")
    parser.add_argument("--tool-path", help="if this option is specified, only tools in this path is executed")
    parser.add_argument("--output-path", help="output path")
    parser.add_argument("--exclude-path", help="exclude path")
    parser.add_argument("--target-triple", help="compile target triple")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("tools", nargs="*", help=textwrap.dedent("""\
        Static analysis program list.
        Tool-specific command-line options separated by colons can be added after the tool name.
        ex) 'cppcheck:--library=googletest'"""),
        default=["cppcheck", "cpplint"])

    args = parser.parse_args()
    args_dict = copy.deepcopy(vars(args))

    default_exclude_path = " .git"
    if args.exclude_path:
        args.exclude_path += default_exclude_path
    else:
        args.exclude_path = default_exclude_path

    log_level = logging.DEBUG if args.verbose else logging.WARNING

    logging.basicConfig(stream=sys.stdout, level=log_level)

    # load wrapper
    logger.info("load wrapper")
    load_tools()

    # make WrapperContext
    ctx = WrapperContext(args.source_path, args.build_path, args.tool_path, args.output_path, args.target_triple, args.exclude_path, args.tools)

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
    generate_report(ctx, args_dict)


if __name__ == "__main__":
    main()
