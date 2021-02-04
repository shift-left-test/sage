import os
import sys
import csv
from subprocess import Popen, PIPE
import json

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

from . import register_wrapper, ToolWrapper

# TODO: use tmp_dir matrixpp.db
class MetrixPPWrapper(ToolWrapper):
    def run(self, ctx):
        args = [
            "metrix++",
            "collect",
            "--std.code.filelines.total",
            "--std.code.filelines.code",
            "--std.code.filelines.comments",
            "--std.code.lines.code",
            "--std.code.member.fields",
            "--std.code.member.globals",
            "--std.code.member.classes",
            "--std.code.member.structs",
            "--std.code.member.interfaces",
            "--std.code.member.types",
            "--std.code.member.methods",
            "--std.code.member.namespaces",
            "--std.code.complexity.cyclomatic",
            "--std.code.complexity.maxindent",
            "--std.code.magic.numbers",
            "--std.code.maintindex.simple",
            "--",
            os.path.abspath(ctx.src_path)
        ]
        proc = Popen(args, stdout=PIPE, stderr=PIPE)
        out, err = proc.communicate()

        args = [
            "metrix++",
            "export",
            "--",
            os.path.abspath(ctx.src_path)
        ]

        proc = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        results = csv.DictReader(proc.stdout)
        for row in results:
            file_name_ = row["file"]
            region_ = row["region"]
            type_ = row["type"]

            metrics = ctx.get_file_analysis(file_name_)

            for key, value in row.items():
                if len(value) == 0 or key in ["file", "region", "type", "modified", "line start", "line end" ]:
                    continue
                elif key == "std.code.complexity:cyclomatic":
                    metrics.region_cyclomatic_complexity.append((type_, region_, value))
                elif key == "std.code.complexity:maxindent":
                    metrics.region_maxindent_complexity.append((type_, region_, value))
                elif key == "std.code.filelines:code":
                    metrics.code_lines = value
                elif key == "std.code.filelines:comments":
                    metrics.comment_lines = value
                elif key == "std.code.filelines:total":
                    metrics.total_lines = value
                elif key == "std.code.lines:code":
                    metrics.region_code_lines.append((type_, region_, value))
                elif key == "std.code.magic:numbers":
                    metrics.region_magic_numbers.append((type_, region_, value))
                elif key == "std.code.member:classes":
                    metrics.region_classes.append((type_, region_, value))
                elif key == "std.code.member:fields":
                    metrics.region_fields.append((type_, region_, value))
                elif key == "std.code.member:globals":
                    metrics.region_globals.append((type_, region_, value))
                elif key == "std.code.member:interfaces":
                    metrics.region_interfaces.append((type_, region_, value))
                elif key == "std.code.member:methods":
                    metrics.region_methods.append((type_, region_, value))
                elif key == "std.code.member:namespaces":
                    metrics.region_namespaces.append((type_, region_, value))
                elif key == "std.code.member:structs":
                    metrics.region_structs.append((type_, region_, value))
                elif key == "std.code.member:types":
                    metrics.region_types.append((type_, region_, value))
                elif key == "std.code.mi:simple":
                    metrics.region_maintainability_index.append((type_, region_, value))
                else:
                    raise Exception("Unknown metrics key: {}".format(key))

register_wrapper("metrix++", MetrixPPWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".")
    metrixpp = MetrixPPWrapper("metrix++", None)
    metrixpp.run(ctx)

    print(json.dumps(ctx.file_analysis_map, default=lambda x: x.__dict__, indent=4))