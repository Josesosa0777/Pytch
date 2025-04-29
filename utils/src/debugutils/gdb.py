import os
import time
import datetime
import tempfile
import subprocess
from itertools import ifilter

import numpy as np


def debug(gdb_cmd_fpath, pn='python', pid=None, tidy=True, gdb_startup_time=2.):
  """
  Decorator function to get debug variables from simulation. Use it on a
  function that runs the simulation.

  :Parameters:
    gdb_cmd_fpath : str
      Path of command file to be executed at gdb startup. The command file is
      assumed to write into a csv-like log file.
    pn : str, optional
      Process name that gdb attaches to. Default is 'python'
    pid: int, optional
      Process id that gdb attaches to. Default is the pid of this python process
    tidy : bool, optional
      Cleanup after gdb session (remove log file in home dir). Default is True.
    gdb_startup_time : float, optional
      Startup time (in seconds) for gdb to attach to simulation
  :ReturnType: tuple
  :Return: decorated function return value and numpy record array (with fields
  from csv header column names)
  """
  pid = pid or os.getpid()
  def outer(f):
    def inner(*args, **kwargs):
      proc, fpath = start_gdb(pn, pid, gdb_cmd_fpath, gdb_startup_time)
      res = f(*args, **kwargs)
      arr = end_gdb(proc, tidy, fpath)
      return res, arr
    return inner
  return outer

def start_gdb(pn, pid, gdb_cmd_fpath, gdb_startup_time):
  fd, tmp_fpath = tempfile.mkstemp()
  log_fpath = create_gdb_log_fpath(gdb_cmd_fpath)
  os.write(fd, "set logging file %s\n" %log_fpath)
  # -q: start gdb in quiet mode
  # -nx: don't execute init files (avoid interference with e.g. ~/.gdbinit)
  # -ix: execute command file before GDB inferior gets loaded
  # -x: execute command file
  command = "gdb %s %s -q -nx -x %s -x %s" %(pn, pid, tmp_fpath, gdb_cmd_fpath)
  args = command.split(' ')
  try:
    proc = subprocess.Popen(args, stdin=subprocess.PIPE)
  except OSError:
    # tricky to modify an OSError's message, simply raise a runtime error
    raise RuntimeError('The system cannot execute "%s"' %command)
  # gdb stops the process as soon as attached, so we need to send 'continue'
  proc.stdin.write('continue\n')
  proc.stdin.flush()
  # wait for gdb to start, otherwise we can miss simulation (no log file)
  # TODO: synchronize with gdb startup
  time.sleep(gdb_startup_time)
  # close tmp command file
  os.close(fd)
  return proc, log_fpath

def create_gdb_log_fpath(gdb_cmd_fpath):
  """ create a gdb log file path under the user's home dir to avoid permission
  problems if gdb can't create a file in cwd (e.g. C:\Windows\SysWOW64), and
  make it unique with timestamp
  """
  dgb_cmd_fbasename = os.path.basename(gdb_cmd_fpath)
  ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
  fname = "%s_%s.log" %(dgb_cmd_fbasename, ts)
  home = os.path.expanduser('~')
  fpath = os.path.join(home, fname)
  return fpath

def end_gdb(proc, tidy, fpath):
  # gdb no longer needed
  proc.kill()
  # load gdb log (csv) to numpy record array
  invalid_start_chars = '[','('
  assert os.path.exists(fpath), 'GDB log file %s missing' %fpath
  with open(fpath, 'rb') as f:
    # filter invalid lines, so numpy will not complain
    f_filt = ifilter(lambda x: not x.startswith(invalid_start_chars), f)
    arr = np.recfromcsv(f_filt, case_sensitive=True)
  # remove gdb log on request
  if tidy:
    os.remove(fpath)
  return arr
