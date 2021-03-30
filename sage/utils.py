from __future__ import division
import os
import subprocess
import hashlib
import logging

logger = logging.getLogger('SAGE')


class RegionValue(object):
    def __init__(self, file_name, region_type, region_name, start, end, value):
        self.file_name = file_name
        self.region_type = region_type
        self.region_name = region_name
        self.start = start
        self.end = end
        self.value = value

    def to_report_data(self):
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


class SecurityFlaw(Issue):
    def __init__(self, toolname, filename, line, column, name, severity, category, warning, suggestion, note, cwes, context, fingerprint):
        super(SecurityFlaw, self).__init__(toolname, filename, line, column, name)

        self.severity = int(severity)
        self.category = category
        self.warning = warning
        self.suggestion = suggestion
        self.note = note
        self.cwes = cwes
        self.context = context
        self.fingerprint = fingerprint


class ViolationIssue(Issue):
    def __init__(self, toolname, filename, line, column, id=None, priority=None, severity=None, msg=None, verbose=None, cwe=None):
        super(ViolationIssue, self).__init__(toolname, filename, line, column, id)

        self.priority = priority
        self.severity = severity
        self.msg = msg
        self.verbose = verbose
        self.cwe = cwe

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
            "cwe": self.cwe,
        }

        return issue


    def append_verbose(self, text):
        if self.verbose == None:
            self.verbose = text
        else:
            self.verbose += text
