import os
import pytest
import shutil
import subprocess
import sys
from sage.context import ToolType, Severity
from sage.report import Report


def test_report(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(ToolType.CHECK, ["cppcheck", "cpplint"])
    ctx = basic_build_bad_content.run_tools(ToolType.CLONE_DETECTION, ctx=ctx)
    ctx = basic_build_bad_content.run_tools(ToolType.METRICS, ctx=ctx)
    
    report = Report(ctx, {})
    assert len(report.wdata["size"]) != 0
    assert len(report.files_summary) != 0


