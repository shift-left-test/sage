import os
import pytest
import shutil
import subprocess
import sys
from sage.context import ToolType


def test_run_clone_detection(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(ToolType.CLONE_DETECTION)

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() != 0


def test_run_clone_detection_no_dup(basic_build):
    ctx = basic_build.run_tools(ToolType.CLONE_DETECTION)

    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.get_duplications() == 0
