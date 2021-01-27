import os
import glob
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