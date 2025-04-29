import os

def rm(filename, silent=True):
  """
  Remove file.
  """
  if silent:
    if os.path.isfile(filename):  # TODO: apply for link?
      os.remove(filename)
  else:
    os.remove(filename)
  return

def rmdir(dirname, silent=True):
  """
  Remove directory.
  """
  if silent:
    if os.path.isdir(dirname):
      os.rmdir(dirname)
  else:
    os.rmdir(dirname)
  return
