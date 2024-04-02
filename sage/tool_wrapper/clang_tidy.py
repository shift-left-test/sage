#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
Copyright (c) 2020 LG Electronics Inc.
SPDX-License-Identifier: MIT
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


class ClangTidyWrapper(ToolWrapper):
    re_log = re.compile(r'^(?P<file>.*):(?P<row>\d+):(?P<col>\d+):\s(?P<lv>.*?):\s(?P<msg>.*?)(\s\[(?P<id>.*)\])?$')
    re_ignored_log = re.compile(r'^(?P<lv>.*?):\s(?P<msg>.*?)(\s\[(?P<id>.*)\])?$')
    severity_map = {
        "ignored": Severity.info,
        "note": Severity.info,
        "remark": Severity.info,
        "warning": Severity.minor,
        "error": Severity.major,
        "fatal": Severity.major
    }

    def run(self, ctx):
        if not ctx.proj_file_exists():
            return

        with open(ctx.proj_file_path) as fcmd:
            compile_commands = json.load(fcmd)

            for compile_command in compile_commands:

                src_file = os.path.abspath(os.path.join(compile_command["directory"], compile_command["file"]))

                if self._is_file_in_path_list(src_file, ctx.exc_path_list):
                    continue

                ctx.used_tools[self.executable_name] = self.get_tool_path(ctx)

                args = [ctx.used_tools[self.executable_name]]
                args += self.get_tool_option(ctx)
                args += [src_file, "--", compile_command["command"]]

                if ctx.target:
                    args.append(" -target {}".format(ctx.target))

                with Popen(
                        " ".join(args), shell=True, stdout=PIPE, stderr=PIPE,
                        universal_newlines=True, cwd=compile_command["directory"]) as proc:
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
                                iid=m.group('id'),
                                priority=self.severity_map.get(m.group('lv'), Severity.unknown),
                                severity=m.group('lv'),
                                msg=m.group('msg')
                            )
                            if not str(filerelpath).startswith("../"):
                                ctx.add_violation_issue(issue)
                        else:
                            m2 = self.re_ignored_log.match(line)
                            if not m2:
                                if issue:
                                    issue.append_verbose(line)
                                else:
                                    raise Exception("parsing error")


register_wrapper("clang-tidy", ClangTidyWrapper)
