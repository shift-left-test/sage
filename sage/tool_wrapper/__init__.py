#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
Copyright (c) 2020 LG Electronics Inc.
SPDX-License-Identifier: MIT
"""

import os
import json
import logging
from distutils.spawn import find_executable
import re

from ..context import WrapperContext

LOGGER = logging.getLogger('SAGE')

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

    @staticmethod
    def _is_file_in_path_list(file_path, file_path_list):
        file_path = os.path.abspath(file_path)
        for cur_path in file_path_list:
            cur_path = os.path.abspath(cur_path)
            if os.path.isdir(cur_path):
                if os.path.commonpath([file_path, cur_path]) == cur_path:
                    return True
            elif file_path == cur_path:
                return True
        return False

    def run(self, ctx):
        pass
    run.__annotations__ = {'ctx': WrapperContext}
