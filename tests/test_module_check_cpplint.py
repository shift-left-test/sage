import os
import pytest
import shutil
import subprocess
import sys
from .base_module_check import *


def test_run_cpplint(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cpplint"])
    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_cpplint_with_option(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cpplint"])
    assert len(ctx.file_analysis_map) != 0

    num_no_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_no_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["cpplint:--filter=-runtime/indentation_namespace"])
    assert len(ctx.file_analysis_map) != 0

    num_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_option += get_num_of_issues(file_analysis)

    assert num_option != num_no_option


def test_run_cpplint_with_options(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cpplint:--extensions=cpp --filter=-runtime/indentation_namespace"])
    assert len(ctx.file_analysis_map) != 0

    num_a_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_a_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["cpplint:--extensions=cpp --filter=-whitespace"])
    assert len(ctx.file_analysis_map) != 0

    num_b_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_b_option += get_num_of_issues(file_analysis)

    assert num_a_option != num_b_option


def test_run_cpplint_with_wrong_option(basic_build_bad_content):
    with pytest.raises(SystemExit) as e:
        basic_build_bad_content.run_tools(["cpplint:--wrong-option"])

    assert e.type == SystemExit
    assert e.value.code == 1


def test_run_cpplint_no_issue(basic_build):
    ctx = basic_build.run_tools(["cpplint"])
    assert len(ctx.file_analysis_map) == 0


def test_run_cpplint_no_src(empty_build):
    ctx = empty_build.run_tools(["cpplint"])
    assert len(ctx.file_analysis_map) == 0


def test_run_cpplint_severity_5(basic_build):
    # No copyright message found.
    MAIN_CONTENT = """
int main() {
    return 0;
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cpplint"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_major_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == '5'


def test_run_cpplint_severity_4(basic_build):
    # Extra space before ( in function call
    MAIN_CONTENT = """
// Copyright [2021] <Copyright Owner>

int main () {
    return 0;
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cpplint"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_minor_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == '4'


def test_run_cpplint_severity_3(basic_build):
    # Closing brace should be aligned with beginning of function main
    MAIN_CONTENT = """
// Copyright [2021] <Copyright Owner>

int main() {
    return 0;
 }
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cpplint"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_info_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == '3'


def test_run_cpplint_severity_2(basic_build):
    # const string& members are dangerous.
    MAIN_CONTENT = """
// Copyright [2021] <Copyright Owner>
struct tmp{
    const string& a;
};

int main() {
    return 0;
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cpplint"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_info_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == '2'


def test_run_cpplint_severity_1(basic_build):
    # Tab found
    MAIN_CONTENT = """
// Copyright [2021] <Copyright Owner>

int main() {
	return 0;
}
"""
    basic_build.add_src_file("main.cpp", MAIN_CONTENT)
    ctx = basic_build.run_tools(["cpplint"])

    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert get_num_of_issues(file_analysis) == 1
        issues = get_info_issues(file_analysis)
        assert len(issues) == 1
        assert issues[0].severity == '1'
