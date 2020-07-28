import os
import sys
import subprocess
import json
from . import register_wrapper, ToolWrapper


class ClangTidyWrapper(ToolWrapper):
    def run(self):
        REPORT = None
        if self.ctx.output_path:
            REPORT = open(os.path.join(self.ctx.output_path, "clang-tidy-report.txt"), "w")

        with open(os.path.join(self.ctx.work_path, "compile_commands.json")) as fcmd:
            compile_commands = json.load(fcmd)

            for compile_command in compile_commands:

                os.chdir(compile_command["directory"])
                src_file = os.path.join(compile_command["directory"], compile_command["file"])
                args = ["clang-tidy", src_file, "--", compile_command["command"]]

                if self.ctx.target:
                    args.append(" -target {}".format(self.ctx.target))

                subprocess.call(" ".join(args), shell=True, stdout=REPORT)

        if REPORT:
            REPORT.close()
            with open(os.path.join(self.ctx.output_path, "clang-tidy-report.txt")) as f:
                sys.stdout.write(f.read())


register_wrapper("clang-tidy", ClangTidyWrapper)