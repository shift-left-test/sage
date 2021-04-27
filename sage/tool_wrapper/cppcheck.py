import os
import sys
import json
import xml.etree.ElementTree as ET

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
        args = [
            self.get_tool_path(ctx),
            self.get_tool_option(ctx),
            "--project={}".format(ctx.proj_file),
            "--xml",
            "--enable=all"
        ]

        args += ["-i" + p for p in ctx.exc_path_list]

        proc = Popen(" ".join(args), stdout=DEVNULL, stderr=PIPE, shell=True, cwd=ctx.work_path)
        se = proc.stderr.read()
        if len(se) > 0:
            root = ET.fromstring(se)
            for issue in root.iter('error'):
                for location in issue.iter('location'):
                    filerelpath = os.path.relpath(location.attrib['file'], ctx.src_path)
                    if not str(filerelpath ).startswith("../"):
                        ctx.add_violation_issue(ViolationIssue(
                            "cppcheck",
                            filename=filerelpath,
                            line=int(location.attrib['line']),
                            column=int(location.attrib['column']),
                            id=issue.attrib.get('id', None), 
                            priority=self.severity_map.get(issue.attrib.get('severity', None), Severity.unknown),
                            severity=issue.attrib.get('severity', None),
                            msg=issue.attrib.get('msg', None),
                            verbose=issue.attrib.get('verbose', None),
                            cwe=issue.attrib.get('cwe', None)
                        ))


register_wrapper("cppcheck", CppCheckWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".", sys.argv[2] if len(sys.argv) > 2 else None)
    cppcheck = CppCheckWrapper("cppcheck", None)
    cppcheck.run(ctx)

    print(json.dumps(ctx.file_analysis_map, default=lambda x: x.__dict__, indent=4))
