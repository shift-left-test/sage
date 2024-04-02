#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
Copyright (c) 2020 LG Electronics Inc.
SPDX-License-Identifier: MIT
"""

import argparse
import copy
import logging
import os
import sys
import textwrap

from .tool_wrapper import get_tool_list, get_tool_wrapper, load_tools
from .context import WrapperContext
from .report import Report
from texttable import Texttable


LOGGER = logging.getLogger('SAGE')


def run_tools(ctx):
    for toolname in get_tool_list():
        option = ctx.get_tool(toolname)
        if option is not None:
            wrapper = get_tool_wrapper(toolname)(toolname, option)
            if wrapper.get_tool_path(ctx) is None:
                LOGGER.warning("* %s is not installed!!!", toolname)
                continue
            LOGGER.info("* %s is running...", toolname)
            wrapper.run(ctx)


run_tools.__annotations__ = {'ctx': WrapperContext}


def generate_report(ctx, args_dict):
    report = Report(ctx, args_dict)

    table = Texttable(max_width=0)
    table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
    table.add_rows(report.get_summary_table())

    print(table.draw())

    if ctx.output_path:
        report.write_to_file(ctx.output_path)


generate_report.__annotations__ = {'ctx': WrapperContext, 'args_dict': dict}


def main():
    parser = argparse.ArgumentParser(
        description="Static Analysis Group Execution",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--source-path", help="source path")
    parser.add_argument("--build-path", help="build path")
    parser.add_argument(
        "--tool-path", help="If this option is specified, only tools in this path is executed")
    parser.add_argument("--output-path", help="output path")
    parser.add_argument("--exclude-path", help="exclude path")
    parser.add_argument("--target-triple", help="compile target triple")
    parser.add_argument("--max-files-duplo", help=textwrap.dedent("""\
        If the number of target source files is more than max-files-duplo, duplo does not work.
        If 0 or less, there is no limit. (Default: 10000)"""),
        type=int, default=10000)
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument(
        "tools", nargs="*", help=textwrap.dedent("""\
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
    LOGGER.info("load wrapper")
    load_tools()

    # make WrapperContext
    ctx = WrapperContext(
        args.tools, args.source_path, args.build_path, args.tool_path,
        args.output_path, args.target_triple, args.exclude_path, args.max_files_duplo)

    if not ctx.proj_file_exists():
        LOGGER.error("There is no 'compile_commands.json'")

    LOGGER.info("run tools")
    run_tools(ctx)

    # generate report
    LOGGER.info("reporting")
    generate_report(ctx, args_dict)


if __name__ == "__main__":
    main()
