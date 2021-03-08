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

class ClangTidyWrapper(ToolWrapper):
    re_log = re.compile(r'^(.*):(\d+):(\d+):\s+(.*):(.*)(\s\[(?P<id>.*)\]|)$')
    severity_map = {
        "ignored" : Severity.Info,
        "note" : Severity.Info,
        "remark" : Severity.Info,
        "warning" : Severity.Minor,
        "error" : Severity.Major,
        "fatal" : Severity.Major
    }

    def run(self, ctx):
        with open(os.path.join(ctx.work_path, "compile_commands.json")) as fcmd:
            compile_commands = json.load(fcmd)

            for compile_command in compile_commands:

                os.chdir(compile_command["directory"])
                src_file = os.path.join(compile_command["directory"], compile_command["file"])
                args = [
                    self.get_tool_path(ctx),
                    self.get_tool_option(ctx),
                    src_file,
                    "--",
                    compile_command["command"]
                ]

                if ctx.target:
                    args.append(" -target {}".format(ctx.target))

                with Popen(" ".join(args), shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True) as proc:
                    issue = None
                    for line in proc.stdout.readlines():
                        m = self.re_log.match(line)
                        if m:
                            issue = ViolationIssue(
                                "clang-tidy",
                                filename=m.group(1),
                                line=m.group(2),
                                column=m.group(3),
                                id=m.group('id'),
                                priority=self.severity_map.get(m.group(4), Severity.Unknown),
                                severity=m.group(4),
                                msg=m.group(5)
                            )
                            ctx.add_violation_issue(issue)
                        else:
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
