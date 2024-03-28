#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
Copyright (c) 2020 LG Electronics Inc.
SPDX-License-Identifier: MIT
"""

import os
import json
import shutil
import sys
from ._version import __version__
from .context import Severity
from collections import OrderedDict

if sys.version_info[:2] < (3, 0):
    from cgi import escape as html_escape
else:
    from html import escape as html_escape


class Report(object):
    def __init__(self, ctx, args_dict):
        self.data = OrderedDict()

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

        self.files_summary = OrderedDict()

        self.wdata = OrderedDict()
        self.wdata["properties"] = OrderedDict()
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

    def get_summary_table_json_style(self):
        result_table = []
        violations_names = "violations {}/{}/{}".format(Severity.major.name,
            Severity.minor.name, Severity.info.name)

        for file_name, file_summary in self.files_summary.items():
            tmp_dict = OrderedDict()
            tmp_dict["File"] = file_name
            tmp_dict["total"] = file_summary[0]
            tmp_dict["loc"] = file_summary[1]
            tmp_dict["comments"] = file_summary[2]
            tmp_dict["cyclomatic complexity"] = file_summary[3]
            tmp_dict["duplications"] = "{:.2f}%".format(file_summary[4])
            tmp_dict[violations_names] = file_summary[5]

            result_table.append(tmp_dict)

        total_dict = OrderedDict()
        total_dict["File"] = "Total:"
        total_dict["total"] = self.data["total_lines"]
        total_dict["loc"] = self.data["code_lines"]
        total_dict["comments"] = self.data["comment_lines"]
        total_dict["cyclomatic complexity"] = ""
        total_dict["duplications"] = "{:.2f}%".format((self.data["clone_lines"] /
            self.data["total_lines"] * 100 if self.data["total_lines"] > 0 else 0))
        total_dict[violations_names] = "{}/{}/{}".format(
            self.data["violations"][Severity.major.name],
            self.data["violations"][Severity.minor.name],
            self.data["violations"][Severity.info.name])

        result_table.append(total_dict)

        return result_table

    def write_to_file(self, dirpath):
        def dumper(obj):
            return obj.to_report_data()

        def json_style_to_html_table(source):
            # source = [{"c1":"t1","c2":"t2"}, {"c1":"t3","c2":"t4"}, ...]
            ret = ""
            rows = []
            head = []
            for s in source:
                try:
                    d = s.to_report_data()
                except:
                    d = s
                for k in d.keys():
                    if k not in head:
                        head.append(k)
                rows.append(d)

            if rows:
                ret += '<table border="1">'
                ret += '<thead><tr>'
                for h in head:
                    ret += '<th>'
                    ret += h
                    ret += '</th>'
                ret += '</tr></thead>'

                ret += '<tbody>'
                for r in rows:
                    ret += '<tr>'
                    for h in head:
                        ret += '<td>'
                        if h in r and r[h] is not None:
                            ret += html_escape(str(r[h]))
                        ret += '</td>'
                    ret += '</tr>'
                ret += '</tbody>'
                ret += '</table>'

            return ret

        def duplications_to_json_style(duplications):
            dup_no = 0
            ret = []
            for duplication in duplications:
                dup_no += 1
                for block in duplication:
                    new_dict = OrderedDict([("block no", dup_no)])
                    new_dict.update(block.to_report_data())
                    ret.append(new_dict)
            return ret

        # Write json file
        with open(os.path.join(dirpath, "sage_report.json"), "w") as reportfile:
            json.dump(self.wdata, reportfile, default=dumper, indent=4)

        # Copy css file
        css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "style.css")
        shutil.copy(css_path, os.path.join(dirpath, "style.css"))

        # Write html file
        head = '<html><head><title>Sage Report</title><link rel="stylesheet" href="./style.css"></head>'
        body = '<body><a name="top"></a><h1>Sage Report</h1>'
        sub_title = '<br><h2>{0}</h2>'
        nav_tag_b = '<nav class="sticky"><ul>'
        nav_tag_e = '</ul></nav>'
        go_to_anchor = '<li><a href="#{0}">{0}</a></li>'
        anchor_tag = '<a name="{0}"></a>'
        tail = '</body></html>'
        br = '<br>'
        message_duplications = '<h5>Code blocks with the same "block no" are duplicated code.</h5>'
        keys = ["summary", "complexity", "duplications", "size", "violations"]

        with open(os.path.join(dirpath, "index.html"), "w") as htmlfile:
            htmlfile.write(head)
            htmlfile.write(body)
            htmlfile.write(br)
            htmlfile.write(nav_tag_b)
            for k in keys:
                htmlfile.write(go_to_anchor.format(k))
            htmlfile.write(nav_tag_e)
            htmlfile.write(br)

            for k in keys:
                htmlfile.write(anchor_tag.format(k))
                htmlfile.write(sub_title.format(k))
                if k == "summary":
                    target = self.get_summary_table_json_style()
                elif k == "duplications":
                    htmlfile.write(message_duplications)
                    target = duplications_to_json_style(self.wdata[k])
                else:
                    target = self.wdata[k]
                html_contents = json_style_to_html_table(target)
                htmlfile.write(html_contents)

            htmlfile.write(tail)

