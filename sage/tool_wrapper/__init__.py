import os
import json
import logging
from distutils.spawn import find_executable
import re

from ..context import WrapperContext

logger = logging.getLogger('SAGE')

WRAPPER_MAP = {}

def load_tools():
    # TODO: load tools from plugin path
    from . import cppcheck
    from . import cpplint
    from . import clang_tidy
    from . import metrixpp
    from . import duplo
    from . import flawfinder

def get_tool_wrapper(toolname):
    return WRAPPER_MAP[toolname]

def register_wrapper(name, clazz):
    global WRAPPER_MAP
    WRAPPER_MAP[name] = clazz

def get_tool_list():
    return WRAPPER_MAP.keys()

class ToolWrapper():
    def __init__(self, executable_name, cmd_line_option):
        self.executable_name = executable_name
        self.cmd_line_option = cmd_line_option

    def get_tool_path(self, ctx):
        if ctx.tool_path:
            return find_executable(self.executable_name, ctx.tool_path)
        else:
            return find_executable(self.executable_name)

    def get_tool_option(self, ctx):
        if self.cmd_line_option:
            return self.cmd_line_option
        else:
            return ""

    def run(self, ctx):
        pass



