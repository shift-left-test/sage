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
import re

from . import register_wrapper, ToolWrapper
from ..context import ViolationIssue, Severity
from ..popen_wrapper import check_non_zero_return_code

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE, DEVNULL
else:
    from subprocess import Popen, PIPE, DEVNULL


class CppLintWrapper(ToolWrapper):
    re_log = re.compile(r'^(.*):(None|\d+):(.*)\[(.*)\]\s+\[(\d+)\]$')
    severity_map = {
        "1": Severity.major,
        "2": Severity.minor,
        "3": Severity.info,
        "4": Severity.info,
        "5": Severity.info
    }

    def run(self, ctx):
        if not ctx.proj_file_exists():
            return

        for filename in ctx.get_src_list():
            if filename in ctx.exc_path_list:
                continue

            ctx.used_tools[self.executable_name] = self.get_tool_path(ctx)

            args = [ctx.used_tools[self.executable_name]]
            args += self.get_tool_option(ctx)
            args += [filename]

            proc = Popen(
                " ".join(args), shell=True, stdout=PIPE, stderr=PIPE,
                universal_newlines=True, cwd=ctx.src_path)
            out, err = check_non_zero_return_code(proc, args, '\nFATAL ERROR: ', False)

            for line in err.splitlines():
                m = self.re_log.match(line)
                if m:
                    filerelpath = os.path.relpath(m.group(1), ctx.src_path)
                    if not str(filerelpath).startswith("../"):
                        ctx.add_violation_issue(ViolationIssue(
                            toolname="cpplint",
                            filename=filerelpath,
                            line=(1 if m.group(2) == 'None' else int(m.group(2))),
                            column=0,
                            iid=m.group(4),
                            priority=self.severity_map.get(m.group(5), Severity.unknown),
                            severity=m.group(5),
                            msg=m.group(3)
                        ))
                else:
                    raise Exception("not match")


register_wrapper("cpplint", CppLintWrapper)
