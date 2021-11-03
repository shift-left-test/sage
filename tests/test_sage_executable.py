import os
import subprocess
import shutil
import pytest
import sys


def test_basic(basic_build):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build.src_path,
        "--build-path",
        basic_build.bld_path,
        "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"cpplint is running..." in str(output), str(output)


def test_bad_content_with_tool_option(basic_build_bad_content):
    proc1 = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build_bad_content.src_path,
        "--build-path",
        basic_build_bad_content.bld_path,
        "--verbose",
        "duplo",
        "metrix++"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output1, error1) = proc1.communicate()

    proc2 = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build_bad_content.src_path,
        "--build-path",
        basic_build_bad_content.bld_path,
        "--verbose",
        "duplo:-ml 10",
        "metrix++"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output2, error2) = proc2.communicate()

    assert output1 != output2


def test_bad_content_with_tool_option(basic_build_bad_content):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build_bad_content.src_path,
        "--build-path",
        basic_build_bad_content.bld_path,
        "--verbose",
        "cpplint:--filter=-runtime/indentation_namespace",
        "cppcheck:--suppress=unusedPrivateFunction -x c++",
        "--output-path",
        "{}/report".format(basic_build_bad_content.bld_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"cpplint is running..." in str(output)

    report_path = "{}/report/sage_report.json".format(basic_build_bad_content.bld_path)
    assert os.path.exists(report_path)

    with open(report_path, "r") as f:
        report = f.readlines()
        assert u"runtime/indentation_namespace" not in report
        assert u"unusedPrivateFunction" not in report


def test_output(basic_build):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build.src_path,
        "--build-path",
        basic_build.bld_path,
        "--output-path",
        "{}/report".format(basic_build.bld_path),
        "--verbose"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert os.path.exists("{}/report/sage_report.json".format(basic_build.bld_path))


def test_invalid_tool_path(basic_build):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build.src_path,
        "--build-path",
        basic_build.bld_path,
        "--tool-path",
        "/bin",
        "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"* cpplint is not installed" in str(output)


def test_invalid_build_path(basic_build):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build.src_path,
        "--build-path",
        os.path.join(basic_build.bld_path, "tmp"),
        "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"There is no 'compile_commands.json'" in str(output)


def test_only_source(source_only_build):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        source_only_build.src_path,
        "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"There is no 'compile_commands.json'" in str(output)


def test_basic_with_hidden_file(basic_build_hidden_file):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build_hidden_file.src_path,
        "--build-path",
        basic_build_hidden_file.bld_path,
        "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u".b/a.cpp" not in str(output), str(output)
