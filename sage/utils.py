import os
import subprocess
import hashlib
import logging
from texttable import Texttable

from .tool_wrapper import *
from .context import ToolType, WrapperContext

logger = logging.getLogger('SAGE')

def run_tools(ctx, tool_type):
    for tool, option in ctx.get_tools(tool_type):
        wrapper = get_tool_wrapper(tool)(tool, option)
        if wrapper.get_tool_path(ctx) is None:
            logger.warning("* {} is not installed!!!".format(tool))
            continue
        logger.info("* {} is running...".format(tool))
        wrapper.run(ctx)

run_tools.__annotations__ = {'ctx': WrapperContext, 'tool_type': ToolType}

def generate_report(ctx):
    # print metrics
    # print dupilcations
    # print security
    # print violoations
    # File, total(#), loc(#, %), comments(#, %), complexity ?, maintainability index, duplications(#, %), security flaws(#), violations(#)
    table = Texttable(max_width=0)
    table.add_rows([
        ["File", "total", "loc", "comments", "complexity", "maintainability\nindex", "duplications", "security\nflaws", "violations"]
    ])
    for file_name, file_metrics in ctx.metrics.files.items():
        table.add_row([
            os.path.relpath(file_name, ctx.src_path),
            file_metrics.total_lines,
            file_metrics.code_lines,
            file_metrics.comment_lines,
            max(file_metrics.region_cyclomatic_complexity, key=lambda i : i[2])[2] if file_metrics.region_cyclomatic_complexity else '',
            max(file_metrics.region_maxindent_complexity, key=lambda i : i[2])[2] if file_metrics.region_maxindent_complexity else '',
            sum(int(count) for count, blocks in file_metrics.duplications),
            len(file_metrics.security_flaws),
            len(file_metrics.violations)])
    print(table.draw())

generate_report.__annotations__ = {'ctx': WrapperContext}
