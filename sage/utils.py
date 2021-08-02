from __future__ import division
import os
import subprocess
import hashlib
import logging

logger = logging.getLogger('SAGE')


class RegionValue(object):
    def __init__(self, key, file_name, region_type, region_name, start, end, value):
        self.file_name = file_name
        self.region_type = region_type
        self.region_name = region_name
        self.start = start
        self.end = end
        self.value = value
        self.key = key

    def to_report_data(self):
        if self.key == "std.code.complexity:cyclomatic":
            region_value = {
                "file": self.file_name,
                "function": self.region_name,
                "start": self.start,
                "end": self.end,
                "value": self.value
            }
        else:
            region_value = {
                "file": self.file_name,
                "region_type": self.region_type,
                "region_name": self.region_name,
                "start": self.start,
                "end": self.end,
                "value": self.value
            }

        return region_value

        
class CodeBlock(object):
    def __init__(self, file_name, start, end):
        self.file_name = file_name
        self.start = int(start)
        self.end = int(end)
        assert (self.start <= self.end), "start: {}, end: {}".format(self.start, self.end)

    def to_report_data(self):
        block = {
            "file": self.file_name,
            "start": self.start,
            "end": self.end
        }

        return block


    def check_merge(self, block):
        if block.start <= self.start and block.end >= self.start:
            self.start = block.start
            self.end = max([block.end, self.end])
            return True
        elif block.start > self.start and block.start <= self.end:
            self.end = max([block.end, self.end])
            return True
        
        return False


class Issue(object):
    def __init__(self, toolname, filename, line, column, name):
        self.file_name = filename
        self.tool_name = toolname
        self.line = line
        self.column = column
        self.name = name


class ViolationIssue(Issue):
    def __init__(self, toolname, filename, line, column, id=None, priority=None, severity=None, msg=None, verbose=None):
        super(ViolationIssue, self).__init__(toolname, filename, line, column, id)

        self.priority = priority
        self.severity = severity
        self.msg = msg
        self.verbose = verbose

    def to_report_data(self):
        issue = {
            "file": self.file_name,
            "tool": self.tool_name,
            "rule": self.name,
            "level": self.priority.name,
            "severity": self.severity,
            "message": self.msg,
            "description": self.verbose,
            "line": self.line,
            "column": self.column,
        }

        return issue


    def append_verbose(self, text):
        if self.verbose == None:
            self.verbose = text
        else:
            self.verbose += text
