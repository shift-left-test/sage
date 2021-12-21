import os
import pytest
import shutil
import subprocess
import sys
from .base_module_check import *


def test_run_cppcheck(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck"])
    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_cppcheck_with_option(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck"])
    assert len(ctx.file_analysis_map) != 0

    num_no_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_no_option += get_num_of_issues(file_analysis)

    assert num_no_option != 0

    ctx = basic_build_bad_content.run_tools(["cppcheck:--suppress=*"])
    assert len(ctx.file_analysis_map) == 0


def test_run_cppcheck_with_options(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck:--suppress=arrayIndexOutOfBounds -x c++"])
    assert len(ctx.file_analysis_map) != 0

    num_a_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_a_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["cppcheck:--suppress=unusedPrivateFunction -x c++"])
    assert len(ctx.file_analysis_map) != 0

    num_b_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_b_option += get_num_of_issues(file_analysis)

    assert num_a_option != num_b_option


def test_run_cppcheck_with_wrong_option(basic_build_bad_content):
    with pytest.raises(SystemExit) as e:
        basic_build_bad_content.run_tools(["cppcheck:--wrong-option"])

    assert e.type == SystemExit
    assert e.value.code == 1


def test_run_cppcheck_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck"])
    assert len(ctx.file_analysis_map) == 0


def test_run_cppcheck_no_src(empty_build):
    ctx = empty_build.run_tools(["cppcheck"])
    assert len(ctx.file_analysis_map) == 0


def test_run_cppcheck_severity_error(basic_build):
    # Division by zero.
    MAIN_CONTENT = """
int main() {
    int a = 1;
    return a / 0;
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cppcheck"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_major_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == 'error'


def test_run_cppcheck_severity_warning(basic_build):
    # Unnecessary comparison of static string
    MAIN_CONTENT = """
int main() {
    return strcmp("a", "a");
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cppcheck"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_minor_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == 'warning'


def test_run_cppcheck_severity_style(basic_build):
    # Variable 'a' is assigned a value that is never used.
    MAIN_CONTENT = """
int main() {
    int a = 1;
    return 0;
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cppcheck"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_info_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == 'style'


def test_run_cppcheck_severity_performance(basic_build):
    # Variable 'a' is assigned a value that is never used.
    MAIN_CONTENT = """
int func(const std::string a) {
    return 0;
}

int main()
{
    func("");
    return 0;
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cppcheck"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_info_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == 'performance'


def test_run_cppcheck_severity_portability(basic_build):
    # Assigning a pointer to an integer is not portable.
    MAIN_CONTENT = """
int foo(int *p) {
    int a = p;
    return a + 4;
}

int main()
{
    int a = 1;
    foo(&a);
    return 0;
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cppcheck"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_info_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == 'portability'


def test_run_cppcheck_severity_information(basic_build):
    # class x y {' is not handled.
    MAIN_CONTENT = """
class x y { };
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cppcheck"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_info_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == 'information'
