import os
import pytest
import shutil
import subprocess
import sys
from .base_module_check import *


def test_run_clangtidy(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["clang-tidy"])
    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_clangtidy_with_option(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["clang-tidy"])
    assert len(ctx.file_analysis_map) != 0

    num_no_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_no_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(["clang-tidy:-checks=-*,clang-analyzer-*,-clang-analyzer-cplusplus*"])
    assert len(ctx.file_analysis_map) != 0

    num_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_option += get_num_of_issues(file_analysis)

    assert num_option != num_no_option


def test_run_clangtidy_with_options(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(
        ["clang-tidy:-system-headers -checks=clang-analyzer-*,-clang-analyzer-cplusplus*"])
    assert len(ctx.file_analysis_map) != 0

    num_a_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_a_option += get_num_of_issues(file_analysis)

    ctx = basic_build_bad_content.run_tools(
        ["clang-tidy:-system-headers -checks=-*,clang-analyzer-*,-clang-analyzer-cplusplus*"])
    assert len(ctx.file_analysis_map) != 0

    num_b_option = 0
    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_b_option += get_num_of_issues(file_analysis)

    assert num_a_option != num_b_option


def test_run_clangtidy_with_wrong_option(basic_build_bad_content):
    with pytest.raises(SystemExit) as e:
        basic_build_bad_content.run_tools(["clang-tidy:--wrong-option"])

    assert e.type == SystemExit
    assert e.value.code == 1


def test_run_clangtidy_no_issue(basic_build):
    ctx = basic_build.run_tools(["clang-tidy"])
    assert len(ctx.file_analysis_map) == 0


def test_run_clangtidy_no_src(empty_build):
    ctx = empty_build.run_tools(["clang-tidy"])
    assert len(ctx.file_analysis_map) == 0
