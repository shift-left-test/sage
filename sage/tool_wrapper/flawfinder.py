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

class FlawFinderWrapper(ToolWrapper):
    def run(self, ctx):
        os.chdir("/home/dennis/work/sentinel")
        args = [
            "flawfinder",
            "--csv",
            "/home/dennis/work/sentinel"
        ]

        with Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True) as proc:
            results = csv.DictReader(proc.stdout)
            for row in results:
                ctx.add_security_flaw(row)


register_wrapper("flawfinder", FlawFinderWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".")
    flawfinder = FlawFinderWrapper("flawfinder", None)
    flawfinder.run(ctx)

    print(json.dumps(ctx.securities, default=lambda x: x.__dict__, indent=4))