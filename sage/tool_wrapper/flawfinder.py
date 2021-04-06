import os
import sys
import csv
import json

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

from . import register_wrapper, ToolWrapper
from ..context import SecurityFlaw

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE
else:
    from subprocess import Popen, PIPE

class FlawFinderWrapper(ToolWrapper):
    def run(self, ctx):
        args = [
            "flawfinder",
            "--csv",
            ctx.src_path
        ]

        proc = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True, cwd=ctx.src_path)
        results = csv.DictReader(proc.stdout)
        for row in results:
            filerelpath = os.path.relpath(row.get("File"), ctx.src_path)
            if not str(filerelpath ).startswith("../"):
                ctx.add_security_flaw(SecurityFlaw(
                    toolname="flawfinder",
                    filename=filerelpath,
                    line=int(row.get("Line")),
                    column=int(row.get("Column")),
                    name=row.get("Name"),
                    severity=row.get("Level"),
                    category=row.get("Category"),
                    warning=row.get("Warning"),
                    suggestion=row.get("Suggestion"),
                    note=row.get("Note"),
                    cwes=row.get("CWEs"),
                    context=row.get("Context"),
                    fingerprint=row.get("Fingerprint")
                ))


register_wrapper("flawfinder", FlawFinderWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".")
    flawfinder = FlawFinderWrapper("flawfinder", None)
    flawfinder.run(ctx)

    print(json.dumps(ctx.file_analysis_map, default=lambda x: x.__dict__, indent=4))
