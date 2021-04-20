import subprocess

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
