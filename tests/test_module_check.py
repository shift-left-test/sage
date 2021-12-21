import os
import pytest
import shutil
import subprocess
import sys
from .base_module_check import *

def test_run_check_default(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck", "cpplint"])
    assert len(ctx.file_analysis_map) != 0


    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_check_all(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck", "cpplint", "clang-tidy"])
    assert len(ctx.file_analysis_map) != 0


    for file_name, file_analysis in ctx.file_analysis_map.items():
        num_of_issues = get_num_of_issues(file_analysis)
        assert num_of_issues != 0


def test_run_check_default_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck", "cpplint"])
    assert len(ctx.file_analysis_map) == 0


def test_run_check_all_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck", "cpplint", "clang-tidy"])
    assert len(ctx.file_analysis_map) == 0
