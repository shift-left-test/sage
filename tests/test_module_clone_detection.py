import os
import pytest
import shutil
import subprocess
import sys


def test_run_clone_detection(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["duplo"])
    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() != 0


def test_run_clone_detection_with_multiple_files(basic_build_multiple_bad_content):
    ctx = basic_build_multiple_bad_content.run_tools(["duplo"])
    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() != 0


def test_run_clone_detection_with_multiple_files_with_limit(basic_build_multiple_bad_content):
    ctx = basic_build_multiple_bad_content.run_tools(["duplo"], 2)
    assert len(ctx.file_analysis_map) == 0


def test_run_clone_detection_with_option(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["duplo:-ml 10"])
    assert len(ctx.file_analysis_map) == 0

    ctx = basic_build_bad_content.run_tools(["duplo:-ml 4"])
    assert len(ctx.file_analysis_map) != 0

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() != 0


def test_run_clone_detection_with_options(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["duplo:-ml 4 -mc 8"])
    assert len(ctx.file_analysis_map) == 0


def test_run_clone_detection_no_dup(basic_build):
    ctx = basic_build.run_tools(["duplo"])
    assert len(ctx.file_analysis_map) == 0


def test_run_clone_detection_no_src(empty_build):
    ctx = empty_build.run_tools(["duplo"])
    assert len(ctx.file_analysis_map) == 0
