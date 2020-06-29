import os
import sys
import subprocess
from . import register_wrapper, ToolWrapper

class CppLintWrapper(ToolWrapper):
    def run(self):
        os.chdir(self.ctx.bld_path)
        args = ["cpplint"]
        REPORT = None
        if self.ctx.output_path:
            REPORT = open(os.path.join(self.ctx.output_path, "cpplint_report.txt"), "w")
        args += self.get_src_list()
        os.chdir(self.ctx.src_path)
        subprocess.call(args, stderr=REPORT)

        if REPORT:
            REPORT.close()
            with open(os.path.join(self.ctx.output_path, "cpplint_report.txt")) as f:
                sys.stderr.write(f.read())


register_wrapper("cpplint", CppLintWrapper)