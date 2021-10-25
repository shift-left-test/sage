import os
import pytest
import shutil
import subprocess
import sys
from sage.context import Severity


def get_num_of_issues(file_analysis):
    return len(file_analysis.violations[Severity.major.name]) + \
           len(file_analysis.violations[Severity.minor.name]) + \
           len(file_analysis.violations[Severity.info.name])


def test_run_cppcheck(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_cppcheck_with_option(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck"])
    num_no_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_no_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["cppcheck:--suppress=*"])
    num_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_option += get_num_of_issues(file_analysis)

    assert num_option != num_no_option


def test_run_cppcheck_with_options(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck:--suppress=arrayIndexOutOfBounds -x c++"])
    num_a_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_a_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["cppcheck:--suppress=unusedPrivateFunction -x c++"])
    num_b_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_b_option += get_num_of_issues(file_analysis)

    assert num_a_option != num_b_option


def test_run_cpplint(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cpplint"])
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_cpplint_with_option(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cpplint"])
    num_no_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_no_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["cpplint:--filter=-runtime/indentation_namespace"])
    num_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_option += get_num_of_issues(file_analysis)

    assert num_option != num_no_option


def test_run_cpplint_with_options(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cpplint:--extensions=cpp --filter=-runtime/indentation_namespace"])
    num_a_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_a_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["cpplint:--extensions=cpp --filter=-whitespace"])
    num_b_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_b_option += get_num_of_issues(file_analysis)

    assert num_a_option != num_b_option


def test_run_clangtidy(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["clang-tidy"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_clangtidy_with_option(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["clang-tidy"])
    num_no_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_no_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["clang-tidy:-checks=-*,clang-analyzer-*,-clang-analyzer-cplusplus*"])
    num_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_option += get_num_of_issues(file_analysis)

    assert num_option != num_no_option


def test_run_clangtidy_with_options(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["clang-tidy:-system-headers -checks=clang-analyzer-*,-clang-analyzer-cplusplus*"])
    num_a_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_a_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["clang-tidy:-system-headers -checks=-*,clang-analyzer-*,-clang-analyzer-cplusplus*"])
    num_b_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_b_option += get_num_of_issues(file_analysis)

    assert num_a_option != num_b_option


def test_run_check_default(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck", "cpplint"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_check_all(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck", "cpplint", "clang-tidy"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_cppcheck_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0


def test_run_cpplint_no_issue(basic_build):
    ctx = basic_build.run_tools(["cpplint"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0


def test_run_clangtidy_no_issue(basic_build):
    ctx = basic_build.run_tools(["clang-tidy"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0


def test_run_check_default_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck", "cpplint"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0


def test_run_check_all_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck", "cpplint", "clang-tidy"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0
