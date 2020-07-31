import os
import subprocess
import hashlib
import logging

from .tool_wrapper import *

logger = logging.getLogger('SAGE')

def run_check_tools(ctx):
    for tool in ctx.tool_list:
        wrapper = get_tool_wrapper(tool)(tool)
        if wrapper.get_tool_path(ctx) is None:
            logger.warning("* {} is not installed!!!".format(tool))
            continue
        logger.info("* {} is running...".format(tool))
        wrapper.run(ctx)