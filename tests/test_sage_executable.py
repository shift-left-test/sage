import os
import subprocess
import shutil
import pytest

def test_basic(basic_build):
    proc = output = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build.src_path,
        "--build-path",
        basic_build.bld_path,
        "--verbose"],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"cpplint is running..." in str(output)


def test_output(basic_build):
    proc = output = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build.src_path,
        "--build-path",
        basic_build.bld_path,
        "--output-path",
        "{}/report".format(basic_build.bld_path),
        "--verbose"
        ],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    
    (output, error) = proc.communicate()

    assert os.path.exists("{}/report/cpplint_report.txt".format(basic_build.bld_path))


def test_invalid_tool_path(basic_build):
    proc = output = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build.src_path,
        "--build-path",
        basic_build.bld_path,
        "--tool-path",
        "/bin",
        "--verbose"],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"* cpplint is not installed" in str(output)


def test_invalid_build_path(basic_build):
    proc = output = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build.src_path,
        "--build-path",
        os.path.join(basic_build.bld_path, "tmp"),
        "--verbose"],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"There is no 'compile_commands.json'" in str(output)


def test_only_source(source_only_build):
    proc = output = subprocess.Popen([
        "sage",
        "--source-path",
        source_only_build.src_path,
        "--verbose"],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"There is no 'compile_commands.json'" in str(output)
