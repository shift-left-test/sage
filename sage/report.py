import os
import json
from .context import Severity


class Report(object):
    def __init__(self, ctx):
        self.data = {}

        files_detail = {}
        project_lines = 0
        project_loc = 0
        project_comments = 0
        project_duplications = 0
        project_violations = {
            Severity.Major.name: 0,
            Severity.Minor.name: 0,
            Severity.Info.name: 0,
            Severity.Unknown.name: 0, # for detecting parsing error
        }

        self.files_summary = {}

        for file_name, file_analysis in ctx.file_analysis_map.items():
            rel_file_name = os.path.relpath(file_name, ctx.src_path)
            files_detail[rel_file_name] = file_analysis

            cyclomatic_complexity = file_analysis.get_cyclomatic_complexity()
            #maxindent_complexity = file_analysis.get_maxindent_complexity()
            #maintainability_index = file_analysis.get_maintainability_index()
            duplications = file_analysis.get_duplications()
            total_lines = float(file_analysis.total_lines)

            self.files_summary[rel_file_name] = [
                file_analysis.total_lines,
                file_analysis.code_lines,
                file_analysis.comment_lines,
                cyclomatic_complexity,
                #maxindent_complexity,
                #maintainability_index,
                duplications / total_lines * 100 if total_lines > 0 else 0,
                "{}/{}/{}".format(
                len(file_analysis.violations[Severity.Major.name]),
                len(file_analysis.violations[Severity.Minor.name]),
                len(file_analysis.violations[Severity.Info.name]))
            ]
        
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
        self.data["files"] = files_detail


    def get_summary_table(self):
        result_table = [[
            "File",
            "total",
            "loc",
            "comments",
            "cyclomatic\ncomplexity",
            #"maxindent\ncomplexity",
            #"maintainability\nindex",
            "duplications",
            "violations\n{}/{}/{}".format(Severity.Major.name, Severity.Minor.name, Severity.Info.name)
        ]]
        for file_name, file_summary in self.files_summary.items():
            result_table.append([file_name] + file_summary)

        result_table.append([
            "Total:",
            self.data["total_lines"],
            self.data["code_lines"],
            self.data["comment_lines"],
            "",
            #"",
            #"",
            self.data["clone_lines"] / self.data["total_lines"] * 100 if self.data["total_lines"] > 0 else 0,
            "{}/{}/{}".format(
                self.data["violations"][Severity.Major.name],
                self.data["violations"][Severity.Minor.name],
                self.data["violations"][Severity.Info.name])
        ])

        return result_table


    def write_to_file(self, filepath):
        def dumper(obj):
            try:
                return obj.to_report_data()
            except:
                return obj.__dict__

        with open(filepath, "w") as f:
            json.dump(self.data, f, default=dumper, indent=4)