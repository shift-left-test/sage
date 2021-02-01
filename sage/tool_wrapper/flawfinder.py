import os
import sys
import csv
from subprocess import Popen, PIPE
import json

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

from . import register_wrapper, ToolWrapper
from ..context import SecurityFlaw

class FlawFinderWrapper(ToolWrapper):
    def run(self, ctx):
        os.chdir(ctx.src_path)
        args = [
            "flawfinder",
            "--csv",
            ctx.src_path
        ]

        with Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True) as proc:
            results = csv.DictReader(proc.stdout)
            for row in results:
                ctx.add_security_flaw(SecurityFlaw(row))


register_wrapper("flawfinder", FlawFinderWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".")
    flawfinder = FlawFinderWrapper("flawfinder", None)
    flawfinder.run(ctx)

    print(json.dumps(ctx.file_analysis_map, default=lambda x: x.__dict__, indent=4))