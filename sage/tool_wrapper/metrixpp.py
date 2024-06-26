#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
Copyright (c) 2020 LG Electronics Inc.
SPDX-License-Identifier: MIT
"""

import os
import sys
import csv
import json
import re

from . import register_wrapper, ToolWrapper
from ..utils import RegionValue
from ..popen_wrapper import check_non_zero_return_code

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE, DEVNULL
else:
    from subprocess import Popen, PIPE, DEVNULL


# TODO: use tmp_dir matrixpp.db
class MetrixPPWrapper(ToolWrapper):
    def run(self, ctx):

        ctx.used_tools[self.executable_name] = self.get_tool_path(ctx)

        args = [
            ctx.used_tools[self.executable_name],
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

        target_files = []
        for root, dirs, files in os.walk(os.path.abspath(ctx.src_path)):
            for name in dirs:
                p = os.path.join(root, name)
                if os.path.islink(p):
                    args.append('--ed="^%s$"' % os.path.abspath(p))

        for each in ctx.exc_path_list:
            if os.path.isdir(each):
                args.append('--ed="^%s$"' % os.path.abspath(each))
            else:
                args.append('--ef="^%s$"' % os.path.basename(each))

        args.append(r'--if="^.+\.([cC]|[cC][cC]|[cC][pP][pP]|[cC][xX][xX]|[hH]|[hH][hH]|[hH][pP][pP]|[hH][xX][xX])$"')
        args.append("--")
        args.append(ctx.src_path)

        proc = Popen(" ".join(args), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        out, err = check_non_zero_return_code(proc, args)

        if "INFO:\tProcessing:" not in err:
            return

        args = [
            "metrix++",
            "export",
            "--",
            os.path.abspath(ctx.src_path)
        ]

        proc = Popen(" ".join(args), stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        out, err = check_non_zero_return_code(proc, args)
        results = csv.DictReader(out.splitlines())
        for row in results:
            file_name_ = row["file"]
            rel_file_name_ = os.path.relpath(file_name_, ctx.src_path)
            region_ = row["region"]
            type_ = row["type"]
            start_ = int(row["line start"])
            end_ = int(row["line end"])

            metrics = ctx.get_file_analysis(rel_file_name_)

            if type_ == "file":
                metrics.total_lines = end_ - 1

            for key, value in row.items():
                if (len(value) == 0 or
                        key in ["file", "region", "type", "modified", "line start", "line end"]):
                    continue

                value = int(value)
                if key == "std.code.complexity:cyclomatic":
                    metrics.region_cyclomatic_complexity.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.complexity:maxindent":
                    metrics.region_maxindent_complexity.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.filelines:code":
                    metrics.code_lines = value
                elif key == "std.code.filelines:comments":
                    metrics.comment_lines = value
                elif key == "std.code.filelines:total":
                    pass
                elif key == "std.code.lines:code":
                    metrics.region_code_lines.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.magic:numbers":
                    metrics.region_magic_numbers.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:classes":
                    metrics.classes += int(value)
                    metrics.region_classes.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:fields":
                    metrics.region_fields.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:globals":
                    metrics.region_globals.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:interfaces":
                    metrics.region_interfaces.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:methods":
                    metrics.functions += int(value)
                    metrics.region_methods.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:namespaces":
                    metrics.region_namespaces.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:structs":
                    metrics.region_structs.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.member:types":
                    metrics.region_types.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                elif key == "std.code.mi:simple":
                    metrics.region_maintainability_index.append(
                        RegionValue(key, rel_file_name_, type_, region_, start_, end_, value))
                else:
                    raise Exception("Unknown metrics key: {}".format(key))

        if os.path.exists("metrixpp.db"):
            os.remove("metrixpp.db")


register_wrapper("metrix++", MetrixPPWrapper)
