#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
Copyright (c) 2020 LG Electronics Inc.
SPDX-License-Identifier: MIT
"""

import os
import re
import shlex
from enum import Enum
import json

from .utils import CodeBlock, ViolationIssue
from collections import OrderedDict


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

        # temporary storage for calculate duplication rate
        self.duplication_ranges = []

    def to_report_data(self):
        data = OrderedDict()
        data["file"] = self.file_name
        data["total_lines"] = self.total_lines
        data["code_lines"] = self.code_lines
        data["comment_lines"] = self.comment_lines
        data["duplicated_lines"] = self.get_duplications()
        data["classes"] = self.classes
        data["functions"] = self.functions

        return data

    def add_duplications(self, block):

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
            return int(max(self.region_cyclomatic_complexity, key=lambda i: int(i.value)).value)
        else:
            return 0

    def get_maxindent_complexity(self):
        if self.region_maxindent_complexity:
            return int(max(self.region_maxindent_complexity, key=lambda i: int(i.value)).value)
        else:
            return 0

    def get_maintainability_index(self):
        if self.region_maintainability_index:
            return int(max(self.region_maintainability_index, key=lambda i: int(i.value)).value)
        else:
            return 0

    def get_duplications(self):
        result = 0
        for dup_range in self.duplication_ranges:
            assert (dup_range.start <= dup_range.end), \
                "start: {}, end: {}".format(dup_range.start, dup_range.end)
            result += dup_range.end - dup_range.start + 1

        return result


class WrapperContext(object):
    src_list = None
    re_tool_option = re.compile(r"(.+):(.+)")
    re_ext = re.compile(r'^.+\.(c|cc|cpp|cxx|h|hh|hpp|hxx)$')

    def __init__(
            self, tool_list, source_path, build_path=None, tool_path=None, output_path=None,
            target_triple=None, exclude_path="", max_files_duplo=0):
        def is_hidden(path):
            return path != "." and path != ".." and path.startswith(".")

        self.src_path = os.path.abspath(source_path) if source_path else os.getcwd()
        self.bld_path = os.path.abspath(build_path) if build_path else None
        self.tool_path = os.path.abspath(tool_path) if tool_path else None
        self.output_path = os.path.abspath(output_path) if output_path else None
        self.proj_file = "compile_commands.json"
        self.target = target_triple
        self.max_files_duplo = max_files_duplo

        self.exc_path_list = []

        for exc in shlex.split(exclude_path):
            exc_path = os.path.abspath(os.path.join(self.src_path, exc))
            if not os.path.exists(exc_path):
                continue
            self.exc_path_list.append(exc_path)

        for root, dirs, files in os.walk(self.src_path):
            for dirname in dirs:
                dirpath = os.path.abspath(os.path.join(root, dirname))
                if is_hidden(dirname):
                    self.exc_path_list.append(dirpath)
                    dirs.remove(dirname)

            for filename in files:
                filepath = os.path.abspath(os.path.join(root, filename))
                if is_hidden(filename) and self.re_ext.match(filename.lower()):
                    self.exc_path_list.append(filepath)

        self.tool_dict = {}  # key: tool name, value: option
        for tool_info in tool_list:
            matched = self.re_tool_option.match(tool_info)
            if matched:
                tool_name = matched.group(1)
                tool_option = matched.group(2)

                self.tool_dict[tool_name] = shlex.split(tool_option)
            else:
                self.tool_dict[tool_info] = []
        self.work_path = self.bld_path if self.bld_path else self.src_path
        self.proj_file_path = os.path.join(self.work_path, self.proj_file)

        if self.output_path and not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        # data
        self.file_analysis_map = {}
        self.duplication_blocks = []

        self.used_tools = {}

    def proj_file_exists(self):
        return os.path.exists(self.proj_file_path)

    def get_file_analysis(self, file_name):
        if file_name not in self.file_analysis_map:
            self.file_analysis_map[file_name] = FileAnalysis(file_name)

        return self.file_analysis_map.get(file_name, None)

    def get_src_list(self):
        if self.src_list:
            return self.src_list

        self.src_list = []
        if self.proj_file_exists():
            with open(self.proj_file_path) as proj_f:
                compile_commands = json.load(proj_f)
                for cmd in compile_commands:
                    src_path = os.path.abspath(os.path.join(cmd["directory"], cmd["file"]))
                    self.src_list.append(src_path)
        else:
            pass

        return self.src_list

    def get_tool(self, tool_name):
        if tool_name in self.tool_dict:
            return self.tool_dict[tool_name]
        else:
            return None

    def add_duplications(self, blocks):
        # Each block is overlapped with each other
        self.duplication_blocks.append(blocks)
        for block in blocks:
            tmp_block = CodeBlock(block.file_name, block.start, block.end)
            self.get_file_analysis(block.file_name).add_duplications(tmp_block)

    def add_violation_issue(self, issue):
        self.get_file_analysis(issue.file_name).violations[issue.priority.name].append(issue)
    add_violation_issue.__annotations__ = {'issue': ViolationIssue}
