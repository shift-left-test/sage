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