#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
MIT License

Copyright (c) 2020 LG Electronics, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import json
from ._version import __version__
from .context import Severity


class Report(object):
    def __init__(self, ctx, args_dict):
        self.data = {}

        project_lines = 0
        project_loc = 0
        project_comments = 0
        project_duplications = 0
        project_violations = {
            Severity.major.name: 0,
            Severity.minor.name: 0,
            Severity.info.name: 0,
            Severity.unknown.name: 0,  # for detecting parsing error
        }

        self.files_summary = {}

        self.wdata = {}
        self.wdata["properties"] = {}
        self.wdata["properties"]["version"] = __version__
        self.wdata["properties"]["arguments"] = args_dict
        self.wdata["properties"]["tools"] = ctx.used_tools
        self.wdata["complexity"] = list()
        self.wdata["duplications"] = ctx.duplication_blocks
        self.wdata["size"] = list()
        self.wdata["violations"] = list()

        for _, file_analysis in ctx.file_analysis_map.items():
            rel_file_name = file_analysis.file_name
            cyclomatic_complexity = file_analysis.get_cyclomatic_complexity()
            duplications = file_analysis.get_duplications()
            total_lines = float(file_analysis.total_lines)

            self.files_summary[rel_file_name] = [
                file_analysis.total_lines,
                file_analysis.code_lines,
                file_analysis.comment_lines,
                cyclomatic_complexity,
                duplications / total_lines * 100 if total_lines > 0 else 0,
                "{}/{}/{}".format(
                    len(file_analysis.violations[Severity.major.name]),
                    len(file_analysis.violations[Severity.minor.name]),
                    len(file_analysis.violations[Severity.info.name]))
            ]

            self.wdata["complexity"].extend(file_analysis.region_cyclomatic_complexity)
            self.wdata["violations"].extend(file_analysis.violations[Severity.major.name])
            self.wdata["violations"].extend(file_analysis.violations[Severity.minor.name])
            self.wdata["violations"].extend(file_analysis.violations[Severity.info.name])
            self.wdata["violations"].extend(file_analysis.violations[Severity.unknown.name])

            self.wdata["size"].append(file_analysis.to_report_data())

            project_lines += int(file_analysis.total_lines)
            project_loc += int(file_analysis.code_lines)
            project_comments += int(file_analysis.comment_lines)
            project_duplications += duplications

            for severity in project_violations.keys():
                project_violations[severity] += len(file_analysis.violations.get(severity, []))

        self.data["total_lines"] = project_lines
        self.data["code_lines"] = project_loc
        self.data["comment_lines"] = project_comments
        self.data["clone_lines"] = project_duplications
        self.data["violations"] = project_violations

    def get_summary_table(self):
        result_table = [[
            "File",
            "total",
            "loc",
            "comments",
            "cyclomatic\ncomplexity",
            "duplications",
            "violations\n{}/{}/{}".format(
                Severity.major.name, Severity.minor.name, Severity.info.name)
        ]]
        for file_name, file_summary in self.files_summary.items():
            result_table.append([file_name] + file_summary)

        result_table.append([
            "Total:",
            self.data["total_lines"],
            self.data["code_lines"],
            self.data["comment_lines"],
            "",
            (self.data["clone_lines"] / self.data["total_lines"] * 100
             if self.data["total_lines"] > 0 else 0),
            "{}/{}/{}".format(
                self.data["violations"][Severity.major.name],
                self.data["violations"][Severity.minor.name],
                self.data["violations"][Severity.info.name])
        ])

        return result_table

    def write_to_file(self, filepath):
        def dumper(obj):
            return obj.to_report_data()

        with open(filepath, "w") as reportfile:
            json.dump(self.wdata, reportfile, default=dumper, indent=4)
