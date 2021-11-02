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

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

from . import register_wrapper, ToolWrapper
from ..context import ViolationIssue, Severity

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE, DEVNULL
else:
    from subprocess import Popen, PIPE, DEVNULL
from ..popen_wrapper import check_non_zero_return_code

class ClangTidyWrapper(ToolWrapper):
    re_log = re.compile(r'^(?P<file>.*):(?P<row>\d+):(?P<col>\d+):\s(?P<lv>.*?):\s(?P<msg>.*?)(\s\[(?P<id>.*)\])?$')
    re_ignored_log = re.compile(r'^(?P<lv>.*?):\s(?P<msg>.*?)(\s\[(?P<id>.*)\])?$')
    severity_map = {
        "ignored" : Severity.info,
        "note" : Severity.info,
        "remark" : Severity.info,
        "warning" : Severity.minor,
        "error" : Severity.major,
        "fatal" : Severity.major
    }

    def run(self, ctx):
        if not ctx.proj_file_exists():
            return

        with open(ctx.proj_file_path) as fcmd:
            compile_commands = json.load(fcmd)

            for compile_command in compile_commands:

                src_file = os.path.realpath(os.path.join(compile_command["directory"], compile_command["file"]))

                if src_file in ctx.exc_path_list:
                    continue

                ctx.used_tools[self.executable_name] = self.get_tool_path(ctx)

                args = [ctx.used_tools[self.executable_name]]
                args += self.get_tool_option(ctx)
                args += [src_file,
                    "--",
                    compile_command["command"]
                ]

                if ctx.target:
                    args.append(" -target {}".format(ctx.target))

                with Popen(" ".join(args), shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True, cwd=compile_command["directory"]) as proc:
                    out, err = check_non_zero_return_code(proc, args, "Found compiler error(s).", True)
                    
                    issue = None
                    for line in out.splitlines():
                        m = self.re_log.match(line)
                        if m:
                            filerelpath = os.path.relpath(m.group('file'), ctx.src_path)
                            issue = ViolationIssue(
                                "clang-tidy",
                                filename=filerelpath,
                                line=int(m.group('row')),
                                column=int(m.group('col')),
                                id=m.group('id'),
                                priority=self.severity_map.get(m.group('lv'), Severity.unknown),
                                severity=m.group('lv'),
                                msg=m.group('msg')
                            )
                            if not str(filerelpath ).startswith("../"):
                                ctx.add_violation_issue(issue)
                        else:
                            m2 = self.re_ignored_log.match(line)
                            if not m2:
                                if issue:
                                    issue.append_verbose(line)
                                else:
                                    raise Exception("parsing error")



register_wrapper("clang-tidy", ClangTidyWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".", sys.argv[2] if len(sys.argv) > 2 else None)
    clangtidy = ClangTidyWrapper("clang-tidy", None)
    clangtidy.run(ctx)

    print(json.dumps(ctx.file_analysis_map, default=lambda x: x.__dict__, indent=4))
