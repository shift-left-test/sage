import os
import subprocess
import hashlib
import logging

from .tool_wrapper import *

logger = logging.getLogger('SAGE')

def run_check_tools(ctx):
    for tool in ctx.tool_list:
        if get_tool_executable(tool) is None:
            logger.warning("* {} is not installed!!!".format(tool))
            continue
        logger.info("* {} is running...".format(tool))
        wrapper = get_tool_wrapper(tool)(ctx)
        wrapper.run()