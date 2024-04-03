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
    assert len(error) == 0
    assert proc.returncode == 0


def test_empty(empty_build):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        empty_build.src_path,
        "--build-path",
        empty_build.bld_path,
        "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"cpplint is running..." in str(output), str(output)
    assert len(error) == 0
    assert proc.returncode == 0


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


def test_bad_content_with_tool_option_and_report(basic_build_bad_content):
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


def test_bad_content_with_limit_duplo(basic_build_multiple_bad_content):
    proc1 = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build_multiple_bad_content.src_path,
        "--build-path",
        basic_build_multiple_bad_content.bld_path,
        "--verbose",
        "duplo",
        "metrix++"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output1, error1) = proc1.communicate()

    proc2 = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build_multiple_bad_content.src_path,
        "--build-path",
        basic_build_multiple_bad_content.bld_path,
        "--max-files-duplo=2",
        "--verbose",
        "duplo:-ml 10",
        "metrix++"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output2, error2) = proc2.communicate()

    assert u"duplo is skipped!" in str(output2), str(output2)

    assert output1 != output2


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

    for outputfile in ["sage_report.json", "index.html", "style.css"]:
        assert os.path.exists("{}/report/{}".format(basic_build.bld_path, outputfile))


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

    assert u".hidden/visible1.cpp" not in str(output), str(output)
    assert u".hidden/.hidden2.cpp" not in str(output), str(output)
    assert u"visible/.hidden/visible2.cpp" not in str(output), str(output)
    assert u"visible/.hidden/.hidden3.cpp" not in str(output), str(output)
    assert u"visible/visible/.hidden4.cpp" not in str(output), str(output)
    assert u".hidden1.cpp" not in str(output), str(output)
    assert u"main.cpp" in str(output), str(output)


def test_basic_with_exclude_path(basic_build_with_exclude_path):
    proc = subprocess.Popen([
        "sage",
        "--source-path",
        basic_build_with_exclude_path.src_path,
        "--build-path",
        basic_build_with_exclude_path.bld_path,
        "--exclude-path",
        "exclude exclude.cpp",
        "--verbose"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    (output, error) = proc.communicate()

    assert u"exclude.cpp" not in str(output), str(output)
    assert u"exclude1.cpp" not in str(output), str(output)
    assert u"exclude2.cpp" not in str(output), str(output)
    assert u"main.cpp" in str(output), str(output)
