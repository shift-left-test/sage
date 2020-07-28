import os
import subprocess
import shutil

def test_compile_commands_generation(makefile_build):
    from sage.tool_wrapper import WrapperContext
    from sage.utils import generate_compile_commands, run_check_tools

    ctx = WrapperContext(makefile_build.src_path, makefile_build.bld_path)

    generate_compile_commands(ctx)
    assert os.path.exists(os.path.join(makefile_build.bld_path, "compile_commands.json"))

    run_check_tools(ctx)

