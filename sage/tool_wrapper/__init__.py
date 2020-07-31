import os
import json
from distutils.spawn import find_executable

__all__ = ["get_tool_wrapper", "get_tool_list", "WrapperContext", "cppcheck", "cpplint", "clang_tidy"]

WRAPPER_MAP = {}


def get_tool_wrapper(toolname):
    return WRAPPER_MAP[toolname]

def register_wrapper(name, clazz):
    global WRAPPER_MAP
    print("tool {} registered".format(name))
    WRAPPER_MAP[name] = clazz

def get_tool_list():
    return WRAPPER_MAP.keys()

class WrapperContext(object):
    src_list = None
    
    def __init__(self, source_path, build_path=None, tool_path = None, output_path=None, target_triple=None, tool_list=[]):
        self.src_path = os.path.abspath(source_path) if source_path else os.getcwd()
        self.bld_path = os.path.abspath(build_path) if build_path else None
        self.tool_path = os.path.abspath(tool_path) if tool_path else None
        self.output_path = os.path.abspath(output_path) if output_path else None
        self.proj_file = "compile_commands.json"
        self.target = target_triple
        self.tool_list = tool_list
        self.work_path = self.bld_path if self.bld_path else self.src_path
        if self.output_path and not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

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
    def __init__(self, executable_name):
        self.executable_name = executable_name

    def get_tool_path(self, ctx):
        if ctx.tool_path:
            return os.path.join(ctx.tool_path, self.executable_name)
        else:
            return find_executable(self.executable_name)

    def run(self, ctx):
        pass



