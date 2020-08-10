import os
import subprocess
from . import register_wrapper, ToolWrapper

class CppCheckWrapper(ToolWrapper):
    def run(self, ctx):
        os.chdir(ctx.work_path)
        args = [self.get_tool_path(ctx), self.get_tool_option(ctx),
        "--project={}".format(ctx.proj_file)]
        subprocess.call(" ".join(args), shell=True)

        # Since'cppcheck' cannot output stderr and file at the same time, it is called again to generate the'report' file.
        if ctx.output_path:
            args += ["--xml",
            "--output-file={}".format(os.path.join(ctx.output_path, "cppcheck_report.xml"))]
            f = open(os.devnull, "w")
            subprocess.call(" ".join(args), shell=True, stdout=f)


register_wrapper("cppcheck", CppCheckWrapper)