import os
import subprocess
from . import register_wrapper, ToolWrapper

class CppLintWrapper(ToolWrapper):
    def run(self):
        os.chdir(self.ctx.bld_path)
        args = ["cpplint"]
        REPORT = None
        if self.ctx.output_path:
            args += ["--output=vs7"]
            REPORT = open(os.path.join(self.ctx.output_path, "cpplint_report.txt"), "w")
        args += self.get_src_list()
        os.chdir(self.ctx.src_path)
        subprocess.call(args, stderr=REPORT)

        if REPORT:
            REPORT.close()


register_wrapper("cpplint", CppLintWrapper)