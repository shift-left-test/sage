#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
MIT License

Copyright (c) 2020 LG Electronics, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

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
    run.__annotations__ = {'ctx': WrapperContext}
