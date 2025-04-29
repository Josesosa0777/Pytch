import os
import ctypes

def symlink(target, link):
  """
  Create symbolic link
  
  On Windows, the following right is needed: "Create symbolic links".
  
  Source: http://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
  """
  if hasattr(os, "symlink"):
    os.symlink(target, link)
  else:
    csl = ctypes.windll.kernel32.CreateSymbolicLinkW
    csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
    csl.restype = ctypes.c_ubyte
    flags = 1 if os.path.isdir(target) else 0
    if csl(link, target, flags) == 0:
        raise ctypes.WinError()
  return
