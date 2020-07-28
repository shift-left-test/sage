import os
import json
from distutils.spawn import find_executable

__all__ = ["get_tool_wrapper", "get_tool_executable", "get_tool_list", "WrapperContext", "cppcheck", "cpplint", "clang_tidy"]

WRAPPER_MAP = {}


def get_tool_wrapper(toolname):
    return WRAPPER_MAP[toolname]

def get_tool_executable(toolname):
    return find_executable(toolname)

def register_wrapper(name, clazz):
    global WRAPPER_MAP
    WRAPPER_MAP[name] = clazz

def get_tool_list():
    return WRAPPER_MAP.keys()

class WrapperContext(object):
    src_list = None
    
    def __init__(self, source, build=None, output_path=None, target=None, tool_list=[]):
        self.src_path = os.path.abspath(source) if source else os.getcwd()
        self.bld_path = os.path.abspath(build) if build else None
        self.output_path = os.path.abspath(output_path) if output_path else None
        self.proj_file = "compile_commands.json"
        self.target = target
        self.tool_list = tool_list
        self.work_path = self.bld_path if self.bld_path else self.src_path

    def get_src_list(self):
        if self.src_list:
            return self.src_list

        self.src_list = []
        proj_file_path = os.path.join(self.work_path, self.proj_file)
        if os.path.exists(proj_file_path):
            with open(proj_file_path) as f:
                compile_commands = json.load(f)
                for cmd in compile_commands:
                    src_path = os.path.join(cmd["directory"], cmd["file"])
                    self.src_list.append(src_path)
        else:
            pass

        return self.src_list


class ToolWrapper():
    def __init__(self, ctx):
        self.ctx = ctx

        if self.ctx.output_path and not os.path.exists(self.ctx.output_path):
            os.makedirs(self.ctx.output_path)

    def run(self):
        pass


