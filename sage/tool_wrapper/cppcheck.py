import os
import sys
from subprocess import Popen, PIPE
import json
import xml.etree.ElementTree as ET

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

from . import register_wrapper, ToolWrapper
from ..context import ViolationIssue

class CppCheckWrapper(ToolWrapper):
    def run(self, ctx):
        os.chdir(ctx.work_path)
        args = [
            self.get_tool_path(ctx),
            self.get_tool_option(ctx),
            "--project={}".format(ctx.proj_file),
            "--xml",
            "--enable=all"
        ]

        proc = Popen(" ".join(args), stdout=PIPE, stderr=PIPE, shell=True)
        root = ET.fromstring(proc.stderr.read())
        for issue in root.iter('error'):
            for location in issue.iter('location'):
                ctx.add_violation_issue(ViolationIssue(
                    "cppcheck",
                    filename=location.attrib['file'],
                    line=location.attrib['line'],
                    column=location.attrib['column'],
                    id=issue.attrib.get('id', None), 
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
