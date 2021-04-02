import os
import glob
import sys

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE
else:
    from subprocess import Popen, PIPE

def main():
    
    args = [
        "lizard",
        "-Eduplicate",
        "-o",
        "lizard_out.txt",
        "/home/dennis/work/sentinel"
    ]

    with Popen(args, universal_newlines=True) as proc:
        proc.communicate()

if __name__ == "__main__":
    main()
