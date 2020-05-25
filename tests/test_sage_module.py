import pytest
import os
import subprocess


def test_basic():
    import sage

    test_proj_root = os.path.dirname(__file__)

    SRC_PATH = os.path.join(test_proj_root, "sample_project")
    BLD_PATH = os.path.join(test_proj_root, "sample_project/build")
    COMPILE_COMMANDS_FILE = os.path.join(BLD_PATH, "compile_commands.json")
    if os.path.exists(COMPILE_COMMANDS_FILE):
        os.remove(COMPILE_COMMANDS_FILE)

    ctx = sage.WrapperContext()
    ctx.src_path = SRC_PATH
    ctx.bld_path = BLD_PATH

    sage.generate_compile_commands(ctx)
    assert os.path.exists(COMPILE_COMMANDS_FILE)

    sage.run_check_tools(ctx)

