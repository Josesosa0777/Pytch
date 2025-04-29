"""
This module overrides Fortran library's Ctrl-C handling
and prevents forrtl: error (200) when aborting application with Ctrl-C
http://stackoverflow.com/a/15472811
"""

import thread
import platform

# Our handler for CTRL_C_EVENT. Other control event
# types will chain to the next handler.
def handler(dwCtrlType, hook_sigint=thread.interrupt_main):
  if dwCtrlType == 0: # CTRL_C_EVENT
      hook_sigint()
      return 1 # don't chain to the next handler
  return 0 # chain to the next handler

if platform.system() == 'Windows':
  # in case of 32-bit conda install this is needed but not for the simple 32-bit version
  try:
    import os
    import imp
    import ctypes
    import win32api

    # Load the DLL manually to ensure its handler gets
    # set before our handler.
    basepath = imp.find_module('numpy')[1]
    ctypes.CDLL(os.path.join(basepath, 'core', 'libmmd.dll'))
    ctypes.CDLL(os.path.join(basepath, 'core', 'libifcoremd.dll'))

    # Now set our handler
    win32api.SetConsoleCtrlHandler(handler, 1)
  except (ImportError, WindowsError):
    pass
