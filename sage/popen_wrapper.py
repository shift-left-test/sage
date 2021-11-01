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
import subprocess
import select

PIPE = subprocess.PIPE

DEVNULL = open(os.devnull, 'wb')

class Popen(subprocess.Popen):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        if self.stdout and self.stdout != DEVNULL:
            self.stdout.close()
        if self.stderr and self.stderr != DEVNULL:
            self.stderr.close()
        try:  
            if self.stdin:
                self.stdin.close()
        finally:
            self.wait()

# TODO: If Popen(..., stdin = PIPE, ...) or Popen(..., universal_newlines=False,...), then malfunction
def check_non_zero_return_code(proc, args, err_message=None):
    stdout_eof = False
    stderr_eof = False
    stdout_str = ""
    stderr_str = ""
    select_target = []

    if proc.stdout:
        select_target.append(proc.stdout)
    else:
        stdout_eof = True

    if proc.stderr:
        select_target.append(proc.stderr)
    else:
        stderr_eof = True

    while not stdout_eof or not stderr_eof:
        proc.poll()
        ready = select.select(select_target, [], [], 1.0)
        if not stdout_eof:
            if proc.stdout in ready[0]:
                buf = proc.stdout.readline()
                if len(buf) != 0:
                    stdout_str += buf
                else:
                    stdout_eof = True

        if not stderr_eof:
            if proc.stderr in ready[0]:
                buf = proc.stderr.readline()
                if len(buf) != 0:
                    stderr_str += buf
                else:
                    stderr_eof = True
    
    proc.wait()
    if proc.returncode != 0:
        do_exit = True
        if err_message:
            if err_message not in stderr_str:
                do_exit = False
        if do_exit:
            print('''Error occurred when executing %s
    return code:%s
    stdout: %s
    stderr: %s''' % (" ".join(args), proc.returncode, stdout_str, stderr_str))
            exit(1)
    return stdout_str, stderr_str
check_non_zero_return_code.__annotations__ = {'proc': subprocess, 'args': list}
