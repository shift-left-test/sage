import pytest
import os
import subprocess
"""
    - sh -c "rm -rf {envdir}/report"
    - sh -c "cd sample_project;rm -rf build;mkdir -p build;cd build;cmake .."
    python -m sage --source {toxinidir}/sample_project \
        --build {toxinidir}/sample_project/build \
        --output-path {envdir}/report/sample

    - sh -c "cd other_project;rm -rf build;mkdir -p build;cd build;cmake .."
    python -m sage --source {toxinidir}/other_project \
        --build {toxinidir}/other_project/build \
        --output-path {envdir}/report/other
"""

def test_basic():
    import sage

    test_proj_root = os.path.dirname(__file__)

    ctx = sage.WrapperContext()
    ctx.src_path = os.path.join(test_proj_root, "sample_project")
    ctx.bld_path = os.path.join(test_proj_root, "sample_project/build")
    
    sage.generate_compile_commands(ctx)
    sage.run_check_tools(ctx)

