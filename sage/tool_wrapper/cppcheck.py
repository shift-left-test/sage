import os
import subprocess
from . import register_wrapper, ToolWrapper

class CppCheckWrapper(ToolWrapper):
    def run(self):
        os.chdir(self.ctx.src_path)
        args = ["cppcheck", 
        "--project={}".format(os.path.join(self.ctx.bld_path, self.ctx.proj_file))]
        if self.ctx.output_path:
            args += ["--xml",
            "--output-file={}".format(os.path.join(self.ctx.output_path, "cppcheck_report.xml"))]

        os.chdir(self.ctx.src_path)    
        subprocess.call(args)


register_wrapper("cppcheck", CppCheckWrapper)