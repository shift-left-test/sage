import os
import json
from distutils.spawn import find_executable

__all__ = ["get_tool_wrapper", "get_tool_executable", "WrapperContext", "cppcheck", "cpplint", "clang_tidy"]

WRAPPER_MAP = {}


def get_tool_wrapper(toolname):
    return WRAPPER_MAP[toolname]

def get_tool_executable(toolname):
    return find_executable(toolname)

def register_wrapper(name, clazz):
    global WRAPPER_MAP
    WRAPPER_MAP[name] = clazz


class WrapperContext(object):
    src_path = os.getcwd()
    bld_path = os.getcwd()
    proj_file = "compile_commands.json"
    output_path = None
    tool_list = []


class ToolWrapper():
    def __init__(self, ctx):
        self.ctx = ctx

        if self.ctx.output_path and not os.path.exists(self.ctx.output_path):
            os.makedirs(self.ctx.output_path)


    def run(self):
        pass

    def get_src_list(self):
        src_list = []
        with open(self.ctx.proj_file) as f:
            os.chdir(self.ctx.bld_path)
            compile_commands = json.load(f)
            for cmd in compile_commands:
                src_path = os.path.join(cmd["directory"], cmd["file"])
                src_list.append(src_path)
        
        return src_list
