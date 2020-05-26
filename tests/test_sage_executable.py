import os
import subprocess
import shutil

def test_basic():
    test_proj_root = os.path.dirname(__file__)

    SRC_PATH = os.path.join(test_proj_root, "sample_project")
    BLD_PATH = os.path.join(test_proj_root, "sample_project/build")

    shutil.rmtree(BLD_PATH, ignore_errors=True)
    os.mkdir(BLD_PATH)
    os.chdir(BLD_PATH)
    subprocess.call(["cmake", SRC_PATH])

    output = subprocess.check_output(["sage", "--source", SRC_PATH, "--build", BLD_PATH])

    assert os.path.exists(os.path.join(BLD_PATH, "compile_commands.json"))

    assert "cpplint is running..." in str(output)