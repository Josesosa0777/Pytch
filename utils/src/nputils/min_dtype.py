"""
Original author: Stefan van der Walt
https://gist.github.com/stefanv/6413742

See discussion on numpy mailing list:
http://www.mail-archive.com/numpy-discussion@scipy.org/msg42540.html
"""

import numpy as np

ints = (np.uint8, np.int8,
        np.uint16,np.int16,
        np.uint32,np.int32,
        np.uint64,np.int64)

dtype_range = [ (np.bool, False, True) ]
for int_type in ints:
  info = np.iinfo(int_type)
  dtype_range.append( (int_type, info.min, info.max) )

def min_typecode(a):
  " Find the minimum type code needed to represent the integers in `a`. "
  a = np.asarray(a)
  if not np.issubdtype(a.dtype, np.integer):
    raise ValueError("Can only handle integer arrays.")
  a_min, a_max = a.min(), a.max()
  for t, t_min, t_max in dtype_range:
    if a_min >= t_min and a_max <= t_max:
      return t
  raise ValueError("Could not find suitable dtype.")
