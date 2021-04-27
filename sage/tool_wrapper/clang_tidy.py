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
        with open(os.path.join(ctx.work_path, "compile_commands.json")) as fcmd:
            compile_commands = json.load(fcmd)

            for compile_command in compile_commands:

                src_file = os.path.realpath(os.path.join(compile_command["directory"], compile_command["file"]))

                if src_file in ctx.exc_path_list:
                    continue

                args = [
                    self.get_tool_path(ctx),
                    self.get_tool_option(ctx),
                    src_file,
                    "--",
                    compile_command["command"]
                ]

                if ctx.target:
                    args.append(" -target {}".format(ctx.target))

                with Popen(" ".join(args), shell=True, stdout=PIPE, stderr=DEVNULL, universal_newlines=True, cwd=compile_command["directory"]) as proc:
                    issue = None
                    for line in proc.stdout.readlines():
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
