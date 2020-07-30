import os
import subprocess
import shutil

def test_compile_commands_generation(makefile_build):
    from sage.tool_wrapper import WrapperContext
    from sage.utils import run_check_tools

    ctx = WrapperContext(makefile_build.src_path, makefile_build.bld_path)

    run_check_tools(ctx)

