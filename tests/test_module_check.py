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


def test_run_cppcheck_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck"])
    assert len(ctx.file_analysis_map) == 0


def test_run_cpplint_no_issue(basic_build):
    ctx = basic_build.run_tools(["cpplint"])
    assert len(ctx.file_analysis_map) == 0


def test_run_clangtidy_no_issue(basic_build):
    ctx = basic_build.run_tools(["clang-tidy"])
    assert len(ctx.file_analysis_map) == 0


def test_run_cppcheck_no_src(empty_build):
    ctx = empty_build.run_tools(["cppcheck"])
    assert len(ctx.file_analysis_map) == 0


def test_run_cpplint_no_src(empty_build):
    ctx = empty_build.run_tools(["cpplint"])
    assert len(ctx.file_analysis_map) == 0


def test_run_clangtidy_no_src(empty_build):
    ctx = empty_build.run_tools(["clang-tidy"])
    assert len(ctx.file_analysis_map) == 0


def test_run_check_default_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck", "cpplint"])
    assert len(ctx.file_analysis_map) == 0


def test_run_check_all_no_issue(basic_build):
    ctx = basic_build.run_tools(["cppcheck", "cpplint", "clang-tidy"])
    assert len(ctx.file_analysis_map) == 0
