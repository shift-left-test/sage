import os
import subprocess
from . import register_wrapper, ToolWrapper, get_tool_executable

class CppCheckWrapper(ToolWrapper):
    def run(self):
        os.chdir(self.ctx.work_path)
        args = [get_tool_executable("cppcheck"), 
        "--project={}".format(self.ctx.proj_file)]
        subprocess.call(args)

        # Since'cppcheck' cannot output stderr and file at the same time, it is called again to generate the'report' file.
        if self.ctx.output_path:
            args += ["--xml",
            "--output-file={}".format(os.path.join(self.ctx.output_path, "cppcheck_report.xml"))]
            f = open(os.devnull, "w")
            subprocess.call(args, stdout=f)


register_wrapper("cppcheck", CppCheckWrapper)