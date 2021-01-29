import os
import sys
import subprocess
import shutil

def test_compile_commands_generation(makefile_build):
    from sage.tool_wrapper import load_tools
    from sage.__main__ import run_tools
    from sage.context import WrapperContext, ToolType

    ctx = WrapperContext(makefile_build.src_path, makefile_build.bld_path)

    load_tools()
    run_tools(ctx, ToolType.CLONE_DETECTION)

