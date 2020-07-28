import os
import sys
import subprocess
from . import register_wrapper, ToolWrapper

class ClangTidyWrapper(ToolWrapper):
    def run(self):
        args = ["clang-tidy", "-p", self.ctx.bld_path]
        REPORT = None
        if self.ctx.output_path:
            REPORT = open(os.path.join(self.ctx.output_path, "clang-tidy-report.txt"), "w")
        args += self.ctx.get_src_list()
        os.chdir(self.ctx.src_path)
        subprocess.call(args, stdout=REPORT)

        if REPORT:
            REPORT.close()
            with open(os.path.join(self.ctx.output_path, "clang-tidy-report.txt")) as f:
                sys.stdout.write(f.read())


register_wrapper("clang-tidy", ClangTidyWrapper)