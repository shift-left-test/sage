#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
Copyright (c) 2020 LG Electronics Inc.
SPDX-License-Identifier: MIT
"""

import os
import sys
import json
from defusedxml.ElementTree import fromstring

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
            root = fromstring(err)
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
