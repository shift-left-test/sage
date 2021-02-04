from __future__ import division
import os
import subprocess
import hashlib
import logging

logger = logging.getLogger('SAGE')


class CodeBlock(object):
    def __init__(self, file_name, start, end):
        self.file_name = file_name
        self.start = int(start)
        self.end = int(end)
        assert (self.start <= self.end), "start: {}, end: {}".format(self.start, self.end)

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
    def __init__(self, toolname, filename, line, column, name, severity):
        self.file_name = filename
        self.tool_name = toolname
        self.line = line
        self.column = column
        self.name = name
        self.severity = severity
    __init__.__annotations__ = {'severity':int}


class SecurityFlaw(Issue):
    def __init__(self, toolname, filename, line, column, name, severity, category, warning, suggestion, note, cwes, context, fingerprint):
        super(SecurityFlaw, self).__init__(toolname, filename, line, column, name, severity)

        self.category = category
        self.warning = warning
        self.suggestion = suggestion
        self.note = note
        self.cwes = cwes
        self.context = context
        self.fingerprint = fingerprint


class ViolationIssue(Issue):
    def __init__(self, toolname, filename, line, column, id=None, severity=None, msg=None, verbose=None, cwe=None):
        super(ViolationIssue, self).__init__(toolname, filename, line, column, id, severity)

        self.msg = msg
        self.verbose = verbose
        self.cwe = cwe


    def append_verbose(self, text):
        if self.verbose == None:
            self.verbose = text
        else:
            self.verbose += text