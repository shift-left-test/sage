import os
import subprocess
import shutil

def test_basic():
    import sage

    test_proj_root = os.path.dirname(__file__)

    SRC_PATH = os.path.join(test_proj_root, "sample_project")
    BLD_PATH = os.path.join(test_proj_root, "sample_project/build")

    shutil.rmtree(BLD_PATH, ignore_errors=True)
    os.mkdir(BLD_PATH)
    os.chdir(BLD_PATH)
    subprocess.call(["cmake", SRC_PATH])

    ctx = sage.WrapperContext()
    ctx.src_path = SRC_PATH
    ctx.bld_path = BLD_PATH

    sage.generate_compile_commands(ctx)
    assert os.path.exists(os.path.join(BLD_PATH, "compile_commands.json"))

    sage.run_check_tools(ctx)

