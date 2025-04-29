import inspect

import numpy

def checkAttributes(obj):
  """ Check if all object member attributes are set
  """
  failedAttribs = []
  members = inspect.getmembers(obj)
  for name, value in members:
    if     not name.startswith('__')\
       and not name.endswith('__')\
       and not callable(value)\
       and not isinstance(value, numpy.ndarray)\
       and not value: # if value can not be evaluated to logical True
        failedAttribs.append((name, value))
  return failedAttribs
