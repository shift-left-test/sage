#-*- coding: utf-8 -*-
#!/usr/bin/python3

"""
MIT License

Copyright (c) 2020 LG Electronics, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import sys
import glob
import json
import re
import tempfile
import shutil
import xml.etree.ElementTree as ET

from . import register_wrapper, ToolWrapper
from ..context import CodeBlock
from ..popen_wrapper import check_non_zero_return_code

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE, DEVNULL
else:
    from subprocess import Popen, PIPE, DEVNULL


# TODO: use tmp_dir for duplo.xml
class DuploWrapper(ToolWrapper):
    def run(self, ctx):

        ctx.used_tools[self.executable_name] = self.get_tool_path(ctx)

        tempdir = tempfile.mkdtemp()
        result_path = os.path.join(tempdir, "duplo_out.xml")
        input_path = os.path.join(tempdir, "file_list.txt")

        try:
            args = [ctx.used_tools[self.executable_name]]
            args += self.get_tool_option(ctx)
            args += [
                "-ip",
                "-xml",
                input_path,
                result_path
            ]

            re_ext = re.compile(r'^.+\.(c|cpp|cxx|h|hpp)$')
            all_cppfiles = []
            for root, dirs, files in os.walk(ctx.src_path):
                for filename in files:
                    if re_ext.match(filename.lower()):
                        all_cppfiles.append(os.path.join(root, filename))

            target_cppfiles = []
            for t in all_cppfiles:
                if t not in ctx.exc_path_list:
                    target_cppfiles.append(t)
            with open(input_path, "w") as f:
                f.write("\n".join(target_cppfiles))

            proc = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            check_non_zero_return_code(proc, args)

            tree = ET.parse(result_path)
            root = tree.getroot()
            for child in root:
                line_count = int(child.attrib.get("LineCount"))
                blocks = []
                for block in child.findall("block"):
                    line_start = int(block.attrib["StartLineNumber"])
                    # TODO: duplo's EndLineNumber has bug. so I used line_count
                    line_end = line_start + line_count - 1
                    rel_file_name_ = os.path.relpath(block.attrib["SourceFile"], ctx.src_path)
                    blocks.append(CodeBlock(
                        rel_file_name_,
                        line_start,
                        line_end))
                ctx.add_duplications(blocks)

        finally:
            shutil.rmtree(tempdir, ignore_errors=True)


register_wrapper("duplo", DuploWrapper)
