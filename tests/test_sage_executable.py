import os
import subprocess

def test_basic():
    test_proj_root = os.path.dirname(__file__)

    SRC_PATH = os.path.join(test_proj_root, "sample_project")
    BLD_PATH = os.path.join(test_proj_root, "sample_project/build")
    COMPILE_COMMANDS_FILE = os.path.join(BLD_PATH, "compile_commands.json")
    if os.path.exists(COMPILE_COMMANDS_FILE):
        os.remove(COMPILE_COMMANDS_FILE)

    output = subprocess.check_output(["sage", "--source", SRC_PATH, "--build", BLD_PATH])

    assert os.path.exists(COMPILE_COMMANDS_FILE)

    assert "cpplint is running..." in str(output)