import os
import glob
from subprocess import Popen, PIPE

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