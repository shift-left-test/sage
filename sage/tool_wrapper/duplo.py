import os
import sys
import glob
from subprocess import Popen, PIPE
import json
import xml.etree.ElementTree as ET


if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

from . import register_wrapper, ToolWrapper
from ..context import WrapperContext, CodeBlock

# TODO: use tmp_dir for duplo.xml
class DuploWrapper(ToolWrapper):
    def run(self, ctx):
        result_path = "duplo_out.xml"
        args = [
            "duplo",
            "-xml",
            "-",
            result_path
        ]

        with Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True) as proc:
            cppfiles = \
                glob.glob(os.path.join(ctx.src_path, "**/*.c")) + \
                glob.glob(os.path.join(ctx.src_path, "**/*.cpp"))

            proc.stdin.write("\n".join(cppfiles))
            proc.communicate()

        tree = ET.parse(result_path)
        root = tree.getroot()
        for child in root:
            line_count = int(child.attrib.get("LineCount"))
            blocks = []
            for block in child.findall("block"):
                line_start = int(block.attrib["StartLineNumber"])
                # TODO: duplo's EndLineNumber has bug. so I used line_count
                line_end = line_start + line_count - 1
                blocks.append(CodeBlock(
                    block.attrib["SourceFile"], 
                    line_start, 
                    line_end))
            ctx.add_duplications(line_count, blocks)
       
register_wrapper("duplo", DuploWrapper)

if __name__ == "__main__":
    from ..context import WrapperContext

    ctx = WrapperContext(sys.argv[1] if len(sys.argv) > 1 else ".")
    duplo = DuploWrapper("duplo", None)
    duplo.run(ctx)

    print(json.dumps(ctx.file_analysis_map, default=lambda x: x.__dict__, indent=4))