import os
import pytest
import shutil
import subprocess
import sys
from sage.context import Severity
from sage.report import Report


def test_report(basic_build_bad_content):
    ctx = basic_build_bad_content.run_tools(["cppcheck", "cpplint", "duplo", "metirx++"])

    report = Report(ctx, {})
    assert len(report.wdata["size"]) != 0
    assert len(report.files_summary) != 0
