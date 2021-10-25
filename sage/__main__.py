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
from .context import WrapperContext
from .report import Report

def run_tools(ctx):
    for toolname in get_tool_list():
        option = ctx.get_tool(toolname)
        if option is not None:
            wrapper = get_tool_wrapper(toolname)(toolname, option)
            if wrapper.get_tool_path(ctx) is None:
                logger.warning("* {} is not installed!!!".format(toolname))
                continue
            logger.info("* {} is running...".format(toolname))
            wrapper.run(ctx)
            

run_tools.__annotations__ = {'ctx': WrapperContext}


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
        List of tools.
        Tool-specific command-line options separated by colons can be added after the tool name.
        ex) 'cppcheck:--library=googletest'"""),
        default=["cppcheck", "cpplint", "duplo", "metrix++"])

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

    if not ctx.proj_file_exists():
        logger.error("There is no 'compile_commands.json'")

    logger.info("run tools")
    run_tools(ctx)

    # generate report
    logger.info("reporting")
    generate_report(ctx, args_dict)


if __name__ == "__main__":
    main()
