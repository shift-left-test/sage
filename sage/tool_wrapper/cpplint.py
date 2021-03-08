import os
import sys
from subprocess import Popen, PIPE
import json
import re

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

from . import register_wrapper, ToolWrapper
from ..context import ViolationIssue, Severity

class CppLintWrapper(ToolWrapper):
    re_log = re.compile(r'^(.*):(\d+):(.*)\[(.*)\]\s+\[(\d+)\]$')
    severity_map = {
        "1" : Severity.Major,
        "2" : Severity.Minor,
        "3" : Severity.Info,
        "4" : Severity.Info,
        "5" : Severity.Info
    }

    def run(self, ctx):
        os.chdir(ctx.src_path)
        for filename in ctx.get_src_list():
            args = [
                self.get_tool_path(ctx),
                self.get_tool_option(ctx),
                filename
            ]

            proc = Popen(" ".join(args), shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            for line in proc.stderr.readlines():
                m = self.re_log.match(line)
                if m:
                    ctx.add_violation_issue(ViolationIssue(
                        toolname="cpplint",
                        filename=m.group(1),
                        line=m.group(2),
                        column=None,
                        id=m.group(4),
                        priority=self.severity_map.get(m.group(5), Severity.Unknown),
                        severity=m.group(5),
                        msg=m.group(3)
                    ))
                else:
                    raise Exception("not match")


register_wrapper("cpplint", CppLintWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".", sys.argv[2] if len(sys.argv) > 2 else None)
    cpplint = CppLintWrapper("cpplint", None)
    cpplint.run(ctx)

    print(json.dumps(ctx.file_analysis_map, default=lambda x: x.__dict__, indent=4))
