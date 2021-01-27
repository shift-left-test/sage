import os
import re
from enum import Enum
import json


class ToolType(Enum):
    METRICS = 1
    CLONE_DETECTION = 2
    CHECK = 3
    SECURITY = 4


class FileMetricsDetail(object):
    def __init__(self):
        self.total_lines = 0
        self.code_lines = 0
        self.comment_lines = 0

        # tuple (type, region, count)
        self.region_cyclomatic_complexity = []
        self.region_maxindent_complexity = []
        self.region_code_lines = []
        self.region_magic_numbers = []
        self.region_classes = []
        self.region_fields = []
        self.region_globals = []
        self.region_interfaces = []
        self.region_methods = []
        self.region_methods = []
        self.region_namespaces = []
        self.region_structs = []
        self.region_types = []
        self.region_maintainability_index = []

        self.security_flaws = []
        self.violations = []
        self.duplications = []


class Metrics(object):
    def __init__(self):
        self.files = {}

    def get_file_metrics(self, file_name):
        if file_name not in self.files:
            self.files[file_name] = FileMetricsDetail()

        return self.files.get(file_name, None)


class CodeBlock(object):
    def __init__(self, file_name, start, end):
        self.file_name = file_name
        self.start = start
        self.end = end


class SecurityFlaw(object):
    def __init__(self, data):
        self.file_name = data.get("File")
        self.line = data.get("Line")
        self.column = data.get("Column")
        self.level = data.get("Level")
        self.category = data.get("Category")
        self.name = data.get("Name")
        self.warning = data.get("Warning")
        self.suggestion = data.get("Suggestion")
        self.note = data.get("Note")
        self.cwes = data.get("CWEs")
        self.context = data.get("Context")
        self.fingerprint = data.get("Fingerprint")


class ViolationIssue(object):
    def __init__(self, id, severity, msg, verbose=None, cwe=None, filename=None, line=None, column=None):
        self.id = id
        self.severity = severity
        self.msg = msg
        self.verbose = verbose
        self.cwe = cwe
        self.filename = filename
        self.line = line
        self.column = column

    def append_verbose(self, text):
        if self.verbose == None:
            self.verbose = text
        else:
            self.verbose += text

class WrapperContext(object):
    src_list = None
    re_tool_option = re.compile(r"(.+):(.+)")

    def __init__(self, source_path, build_path=None, tool_path = None, output_path=None, target_triple=None, check_tool_list=[]):
        self.src_path = os.path.abspath(source_path) if source_path else os.getcwd()
        self.bld_path = os.path.abspath(build_path) if build_path else None
        self.tool_path = os.path.abspath(tool_path) if tool_path else None
        self.output_path = os.path.abspath(output_path) if output_path else None
        self.proj_file = "compile_commands.json"
        self.target = target_triple

        self.check_tool_list = [] # tuple (toolname, option)
        for tool_info in check_tool_list:
            m = self.re_tool_option.match(tool_info)
            if m:
                tool_name = m.group(1)
                tool_option = m.group(2)
                self.check_tool_list.append((tool_name, tool_option))
            else:
                self.check_tool_list.append((tool_info, None))
        self.work_path = self.bld_path if self.bld_path else self.src_path
        if self.output_path and not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # data
        self.metrics = Metrics()


    def get_src_list(self):
        if self.src_list:
            return self.src_list

        self.src_list = []
        proj_file_path = os.path.join(self.work_path, self.proj_file)
        if os.path.exists(proj_file_path):
            with open(proj_file_path) as f:
                compile_commands = json.load(f)
                for cmd in compile_commands:
                    src_path = os.path.join(cmd["directory"], cmd["file"])
                    self.src_list.append(src_path)
        else:
            pass

        return self.src_list


    def get_tools(self, tool_type):
        if tool_type == ToolType.METRICS:
            return [('metrix++', None)]
        elif tool_type == ToolType.CLONE_DETECTION:
            return [('duplo', None)]
        elif tool_type == ToolType.SECURITY:
            return [('flawfinder', None)]
        elif tool_type == ToolType.CHECK:
            return self.check_tool_list
        else:
            return None
    get_tools.__annotations__ = { 'tool_type': ToolType }


    def add_duplications(self, line_count, blocks):
        file_names = set()
        for block in blocks:
            if block.file_name not in file_names:
                self.metrics.get_file_metrics(block.file_name).duplications.append((line_count, blocks))
                # TODO: check line overlap with other duplications in same file.
                file_names.add(block.file_name)

    def add_security_flaw(self, data):
        flaw = SecurityFlaw(data)
        self.metrics.get_file_metrics(flaw.file_name).security_flaws.append(flaw)
           

    def add_violation_issue(self, issue):
        self.metrics.get_file_metrics(issue.filename).violations.append(issue)

