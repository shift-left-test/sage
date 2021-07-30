import os
import pytest
import shutil
import subprocess
import sys
from sage.context import ToolType, Severity


def get_num_of_issues(file_analysis):
    return len(file_analysis.violations[Severity.major.name]) + \
           len(file_analysis.violations[Severity.minor.name]) + \
           len(file_analysis.violations[Severity.info.name])


def test_run_cppcheck(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(ToolType.CHECK, ["cppcheck"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_cpplint(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(ToolType.CHECK, ["cpplint"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_clangtidy(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(ToolType.CHECK, ["clang-tidy"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_check_default(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(ToolType.CHECK, ["cppcheck", "cpplint"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_check_all(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(ToolType.CHECK, ["cppcheck", "cpplint", "clang-tidy"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_cppcheck_no_issue(basic_build):
    ctx = basic_build.run_tools(ToolType.CHECK, ["cppcheck"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0


def test_run_cpplint_no_issue(basic_build):
    ctx = basic_build.run_tools(ToolType.CHECK, ["cpplint"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0


def test_run_clangtidy_no_issue(basic_build):
    ctx = basic_build.run_tools(ToolType.CHECK, ["clang-tidy"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0


def test_run_check_default_no_issue(basic_build):
    ctx = basic_build.run_tools(ToolType.CHECK, ["cppcheck", "cpplint"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0


def test_run_check_all_no_issue(basic_build):
    ctx = basic_build.run_tools(ToolType.CHECK, ["cppcheck", "cpplint", "clang-tidy"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues == 0
