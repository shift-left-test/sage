import os
import re
from enum import Enum
import json

from .utils import *

class ToolType(Enum):
    METRICS = 1
    CLONE_DETECTION = 2
    CHECK = 3
    SECURITY = 4


class Severity(Enum):
    major = 0
    minor = 1
    info = 2
    unknown = 3


class FileAnalysis(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.total_lines = 0
        self.code_lines = 0
        self.comment_lines = 0
        self.classes = 0
        self.functions = 0

        # tuple (file name, type, region, start, end, count)
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

        self.violations = {
            Severity.major.name: [],
            Severity.minor.name: [],
            Severity.info.name: [],
            Severity.unknown.name: []
        }

        # 0, 1, 2, 3, 4, 5
        self.security_flaws = [[],[],[],[],[],[]]
        self.duplications = []

        # temporary storage for calculate duplication rate
        self.duplication_ranges = []


    def to_report_data(self):
        data = {}
        data["file"] = self.file_name
        data["total_lines"] = self.total_lines
        data["code_lines"] = self.code_lines
        data["comment_lines"] = self.comment_lines
        data["duplicated_lines"] = self.get_duplications()
        data["classes"] = self.classes
        data["functions"] = self.functions

        return data


    def add_duplications(self, lines, block, blocks):
        self.duplications.append(blocks)

        merged = False
        merged_ranges = []
        last_range = None

        for dup_range in self.duplication_ranges:
            if not merged:
                merged = dup_range.check_merge(block)

            if last_range:
                if not merged and block.start > last_range.end and block.end < dup_range.start:
                    merged = True
                    merged_ranges.append(block)
                if not last_range.check_merge(dup_range):
                    merged_ranges.append(dup_range)
                    last_range = dup_range
            else:
                merged_ranges.append(dup_range)
                last_range = dup_range

        if not merged:
            merged_ranges.append(block)

        self.duplication_ranges = merged_ranges

    
    def get_cyclomatic_complexity(self):
        if self.region_cyclomatic_complexity:
            return int(max(self.region_cyclomatic_complexity, key=lambda i : int(i.value)).value)
        else:
            return 0
    

    def get_maxindent_complexity(self):
        if self.region_maxindent_complexity:
            return int(max(self.region_maxindent_complexity, key=lambda i : int(i.value)).value)
        else:
            return 0

    def get_maintainability_index(self):
        if self.region_maintainability_index:
            return int(max(self.region_maintainability_index, key=lambda i : int(i.value)).value)
        else:
            return 0


    def get_duplications(self):
        result = 0
        for dup_range in self.duplication_ranges:
            assert (dup_range.start <= dup_range.end), "start: {}, end: {}".format(dup_range.start, dup_range.end)
            result += dup_range.end - dup_range.start + 1
        
        return result


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
        self.file_analysis_map = {}


    def get_file_analysis(self, file_name):
        if file_name not in self.file_analysis_map:
            self.file_analysis_map[file_name] = FileAnalysis(file_name)

        return self.file_analysis_map.get(file_name, None)


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
        # Each block is overlapped with each other
        for block in blocks:
            self.get_file_analysis(block.file_name).add_duplications(line_count, block, blocks)


    def add_security_flaw(self, flaw):
        self.get_file_analysis(flaw.file_name).security_flaws[flaw.severity].append(flaw)
    add_security_flaw.__annotations__ = {'flaw': SecurityFlaw}       


    def add_violation_issue(self, issue):
        self.get_file_analysis(issue.file_name).violations[issue.priority.name].append(issue)
    add_violation_issue.__annotations__ = {'issue': ViolationIssue}
