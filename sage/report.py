import os


class Report(object):
    project_lines = 0
    project_loc = 0
    project_comments = 0
    project_cyclomatic_complexity = 0
    project_maxindent_complexity = 0
    project_maintainindex = 0
    project_duplications = 0
    project_security_flaws = [0,0,0,0,0,0]
    project_violations = [0,0,0,0]

    def __init__(self, ctx):
        self.files_detail = {}
        self.files_summary = {}
        for file_name, file_analysis in ctx.file_analysis_map.items():
            rel_file_name = os.path.relpath(file_name, ctx.src_path)
            self.files_detail[rel_file_name] = file_analysis

            cyclomatic_complexity = file_analysis.get_cyclomatic_complexity()
            maxindent_complexity = file_analysis.get_maxindent_complexity()
            maintainability_index = file_analysis.get_maintainability_index()
            duplications = file_analysis.get_duplications()
            total_lines = float(file_analysis.total_lines)

            self.files_summary[rel_file_name] = [
                file_analysis.total_lines,
                file_analysis.code_lines,
                file_analysis.comment_lines,
                cyclomatic_complexity,
                maxindent_complexity,
                maintainability_index,
                duplications / total_lines * 100 if total_lines > 0 else 0,
                "/".join(str(len(x)) for x in file_analysis.security_flaws),
                "/".join(str(len(x)) for x in file_analysis.violations)
            ]
        
            self.project_lines += int(file_analysis.total_lines)
            self.project_loc += int(file_analysis.code_lines)
            self.project_comments += int(file_analysis.comment_lines)
            self.project_cyclomatic_complexity = max([self.project_cyclomatic_complexity, cyclomatic_complexity])
            self.project_maxindent_complexity = max([self.project_maxindent_complexity, maxindent_complexity])
            self.project_maintainindex = max([self.project_maintainindex, maintainability_index])
            self.project_duplications += duplications
            for index in range(len(self.project_security_flaws)):
                self.project_security_flaws[index] += len(file_analysis.security_flaws[index])
            for index in range(len(self.project_violations)):
                self.project_violations[index] += len(file_analysis.violations[index])


    def get_summary_table(self):
        result_table = [[
            "File",
            "total",
            "loc",
            "comments",
            "cyclomatic\ncomplexity",
            "maxindent\ncomplexity",
            "maintainability\nindex",
            "duplications",
            "security\nflaws",
            "violations\nmajor/minor/info"
        ]]
        for file_name, file_summary in self.files_summary.items():
            result_table.append([file_name] + file_summary)

        result_table.append([
            "Total:",
            self.project_lines,
            self.project_loc,
            self.project_comments,
            self.project_cyclomatic_complexity,
            self.project_maxindent_complexity,
            self.project_maintainindex,
            self.project_duplications / self.project_lines * 100 if self.project_lines > 0 else 0,
            "/".join(str(x) for x in self.project_security_flaws),
            "/".join(str(x) for x in self.project_violations)
        ])

        return result_table