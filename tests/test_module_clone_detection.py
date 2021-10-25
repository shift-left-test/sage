import os
import pytest
import shutil
import subprocess
import sys


def test_run_clone_detection(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["duplo"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() != 0


def test_run_clone_detection_with_option(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["duplo:-ml 10"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() == 0

    ctx = basic_build_bad_content.run_tools(["duplo:-ml 4"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() != 0


def test_run_clone_detection_with_options(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["duplo:-ml 4 -mc 8"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() == 0


def test_run_clone_detection_no_dup(basic_build):
    ctx = basic_build.run_tools(["duplo"])

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() == 0
