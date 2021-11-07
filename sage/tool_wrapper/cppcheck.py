#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
MIT License

Copyright (c) 2020 LG Electronics, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import sys
import json
import xml.etree.ElementTree as ET

from . import register_wrapper, ToolWrapper
from ..context import ViolationIssue, Severity
from ..popen_wrapper import check_non_zero_return_code

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE, DEVNULL
else:
    from subprocess import Popen, PIPE, DEVNULL


class CppCheckWrapper(ToolWrapper):
    severity_map = {
        "error": Severity.major,
        "warning": Severity.minor,
        "style": Severity.info,
        "performance": Severity.info,
        "portability": Severity.info,
        "information": Severity.info
    }

    def run(self, ctx):
        if not ctx.proj_file_exists() or len(ctx.get_src_list()) == 0:
            return

        ctx.used_tools[self.executable_name] = self.get_tool_path(ctx)

        args = [ctx.used_tools[self.executable_name]]
        args += self.get_tool_option(ctx)
        args += ["--project={}".format(ctx.proj_file), "--xml", "--enable=all"]
        args += ["-i" + p for p in ctx.exc_path_list]

        proc = Popen(" ".join(args), stdout=PIPE, stderr=PIPE, shell=True, universal_newlines=True, cwd=ctx.work_path)
        out, err = check_non_zero_return_code(proc, args)
        if len(err) > 0:
            root = ET.fromstring(err)
            for issue in root.iter('error'):
                for location in issue.iter('location'):
                    filerelpath = os.path.relpath(location.attrib['file'], ctx.src_path)
                    if not str(filerelpath).startswith("../"):
                        ctx.add_violation_issue(ViolationIssue(
                            "cppcheck",
                            filename=filerelpath,
                            line=int(location.attrib['line']),
                            column=int(location.attrib['column']),
                            iid=issue.attrib.get('id', None),
                            priority=self.severity_map.get(issue.attrib.get('severity', None), Severity.unknown),
                            severity=issue.attrib.get('severity', None),
                            msg=issue.attrib.get('msg', None),
                            verbose=issue.attrib.get('verbose', None)
                        ))


register_wrapper("cppcheck", CppCheckWrapper)
