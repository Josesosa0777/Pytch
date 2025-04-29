"""
This module shall be imported into several modules in order to:
  * avoid pyglet crash if scipy subpackage import was done earlier (#164)
  * avoid WindowsError if user disconnected (#508)
"""

import ctypes
import os
import sys

import pyglet

# pyglet.options shall be set before any pyglet subpackage import
pyglet.options['shadow_window'] = False
if '--nodirectsound' in sys.argv:  # option also in config/Config.py
  # exclude DirectSound to avoid crash if user disconnected (#508)
  pyglet.options['audio'] = ('openal', 'alsa', 'silent')
else:
  pyglet.options['audio'] = ('directsound', 'openal', 'alsa', 'silent')
# avoid later pyglet crash if scipy subpackage import was done earlier (#164)

# No need to put avbin64.dll to c:/windows/system32 if it is already loaded into memory from different location
# https://docs.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order?redirectedfrom=MSDN
avbin_dll = os.path.join(os.path.dirname(__file__), "avbin64.dll")
if os.path.isfile(avbin_dll):
  ctypes.cdll.LoadLibrary(avbin_dll)
else:
  from pyglet.media import avbin

