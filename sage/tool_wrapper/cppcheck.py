import os
import subprocess
from . import register_wrapper, ToolWrapper, get_tool_executable

class CppCheckWrapper(ToolWrapper):
    def run(self):
        os.chdir(self.ctx.bld_path)
        args = [get_tool_executable("cppcheck"), 
        "--project={}".format(self.ctx.proj_file)]
        if self.ctx.output_path:
            args += ["--xml",
            "--output-file={}".format(os.path.join(self.ctx.output_path, "cppcheck_report.xml"))]
 
        subprocess.call(args)


register_wrapper("cppcheck", CppCheckWrapper)