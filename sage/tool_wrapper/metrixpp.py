import os
import sys
import csv
import json

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

from . import register_wrapper, ToolWrapper
from ..utils import RegionValue

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE, DEVNULL
else:
    from subprocess import Popen, PIPE, DEVNULL

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
            "--std.code.maintindex.simple"
        ]

        for root, dirs, files in os.walk(os.path.abspath(ctx.src_path)):
            for name in dirs:
                p = os.path.join(root, name)
                if os.path.islink(p):
                    args.append('--exclude-files=%s' % os.path.basename(p))

        args.append("--")
        args.append(os.path.abspath(ctx.src_path))

        proc = Popen(args, stdout=DEVNULL, stderr=DEVNULL)
        proc.communicate()

        args = [
            "metrix++",
            "export",
            "--",
            os.path.abspath(ctx.src_path)
        ]

        proc = Popen(args, stdout=PIPE, stderr=DEVNULL, universal_newlines=True)
        results = csv.DictReader(proc.stdout)
        for row in results:
            file_name_ = row["file"]
            rel_file_name_ = os.path.relpath(file_name_, ctx.src_path)
            region_ = row["region"]
            type_ = row["type"]
            start_ = int(row["line start"])
            end_ = int(row["line end"])

            metrics = ctx.get_file_analysis(rel_file_name_)

            for key, value in row.items():
                if len(value) == 0 or key in ["file", "region", "type", "modified", "line start", "line end" ]:
                    continue

                value = int(value)
                if key == "std.code.complexity:cyclomatic":
                    metrics.region_cyclomatic_complexity.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.complexity:maxindent":
                    metrics.region_maxindent_complexity.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.filelines:code":
                    metrics.code_lines = value
                elif key == "std.code.filelines:comments":
                    metrics.comment_lines = value
                elif key == "std.code.filelines:total":
                    metrics.total_lines = value
                elif key == "std.code.lines:code":
                    metrics.region_code_lines.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.magic:numbers":
                    metrics.region_magic_numbers.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:classes":
                    metrics.classes += int(value)
                    metrics.region_classes.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:fields":
                    metrics.region_fields.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:globals":
                    metrics.region_globals.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:interfaces":
                    metrics.region_interfaces.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:methods":
                    metrics.functions += int(value)
                    metrics.region_methods.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:namespaces":
                    metrics.region_namespaces.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:structs":
                    metrics.region_structs.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:types":
                    metrics.region_types.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.mi:simple":
                    metrics.region_maintainability_index.append(RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                else:
                    raise Exception("Unknown metrics key: {}".format(key))

register_wrapper("metrix++", MetrixPPWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".")
    metrixpp = MetrixPPWrapper("metrix++", None)
    metrixpp.run(ctx)

    print(json.dumps(ctx.file_analysis_map, default=lambda x: x.__dict__, indent=4))
