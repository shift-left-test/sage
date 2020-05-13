import os
import subprocess
from . import register_wrapper, ToolWrapper

class CppCheckWrapper(ToolWrapper):
    def run(self):
        os.chdir(self.ctx.bld_path)
        args = ["cppcheck", 
        "--project={}".format(self.ctx.proj_file)]
        if self.ctx.output_path:
            args += ["--xml",
            "--output-file={}".format(os.path.join(self.ctx.output_path, "cppcheck_report.xml"))]
 
        subprocess.call(args)


register_wrapper("cppcheck", CppCheckWrapper)