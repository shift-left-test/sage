import os
import glob
import sys

if __name__ == "__main__":
    root_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "../..")
    sys.path.append(root_path)
    __package__ = 'sage.tool_wrapper'

if sys.version_info.major == 2:
    from ..popen_wrapper import Popen, PIPE, DEVNULL
else:
    from subprocess import Popen, PIPE, DEVNULL

def main():
    
    args = [
        "sim_c++",
        "-i",
        "-d",
        "-a",
        "-osim_out.txt"
    ]
    with Popen(args, stdin=PIPE, universal_newlines=True) as proc:
        cppfiles = \
            glob.glob("/home/dennis/work/sentinel/**/*.c") + \
            glob.glob("/home/dennis/work/sentinel/**/*.cpp")

        proc.stdin.write("\n".join(cppfiles))
        proc.stdin.write("\n")
        proc.communicate()

if __name__ == "__main__":
    main()
