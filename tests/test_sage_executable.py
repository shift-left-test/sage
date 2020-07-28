import os
import subprocess
import shutil
import pytest

def test_basic(basic_build):
    proc = output = subprocess.Popen([
        "sage",
        "--source",
        basic_build.src_path,
        "--build",
        basic_build.bld_path],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"cpplint is running..." in str(output), str(output)
    assert u"cppcheck is running..." in str(output)


def test_output(basic_build):
    proc = output = subprocess.Popen([
        "sage",
        "--source",
        basic_build.src_path,
        "--build",
        basic_build.bld_path,
        "--output-path",
        "{}/report".format(basic_build.bld_path)
        ],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    
    (output, error) = proc.communicate()
    print(output)
    print(error)
    assert os.path.exists("{}/report/cpplint_report.txt".format(basic_build.bld_path))
    assert os.path.exists("{}/report/cppcheck_report.xml".format(basic_build.bld_path))


def test_only_source(source_only_build):
    proc = output = subprocess.Popen([
        "sage",
        "--source",
        source_only_build.src_path],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"cpplint is running..." in str(output), str(output)
    assert u"cppcheck is running..." in str(output)