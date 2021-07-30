import os
import pytest
import shutil
import subprocess
import sys
from sage.context import ToolType

def test_run_metrics(basic_build):
    ctx = basic_build.run_tools(ToolType.METRICS)
    
    for file_name, file_analysis in ctx.file_analysis_map.items():
        assert file_analysis.total_lines != 0
        assert file_analysis.code_lines != 0
        assert file_analysis.comment_lines != 0

