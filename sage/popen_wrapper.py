import subprocess

PIPE = subprocess.PIPE

class Popen(subprocess.Popen):
  def __enter__(self):
      return self

  def __exit__(self, exc_type, value, traceback):
      if self.stdout:
          self.stdout.close()
      if self.stderr:
          self.stderr.close()
      try:  
          if self.stdin:
              self.stdin.close()
      finally:
          self.wait()
