import os
import subprocess
from . import register_wrapper, ToolWrapper

class ClangTidyWrapper(ToolWrapper):
    def run(self):
        os.chdir(self.ctx.bld_path)
        args = ["clang-tidy", "-p", self.ctx.bld_path]
        REPORT = None
        if self.ctx.output_path:
            REPORT = open(os.path.join(self.ctx.output_path, "clang-tidy-report.txt"), "w")
        args += self.get_src_list()
        os.chdir(self.ctx.src_path)
        subprocess.call(args, stdout=REPORT)

        if REPORT:
            REPORT.close()


register_wrapper("clang-tidy", ClangTidyWrapper)