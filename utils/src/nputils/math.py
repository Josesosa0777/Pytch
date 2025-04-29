import numpy as np

def hyst(x, th_lo, th_hi, initial=False):
  """
  Hysteresis functionality that returns a bool array with True where the values
  in 'x' are "high" and False where they are "low", in terms of the two 
  threshold parameters.
  
  Source:
  http://stackoverflow.com/questions/23289976/how-to-find-zero-crossings-with-hysteresis
  """
  hi = x >= th_hi
  lo_or_hi = (x <= th_lo) | hi
  ind = np.nonzero(lo_or_hi)[0]
  if not ind.size: # prevent index error if ind is empty
      return np.zeros_like(x, dtype=bool) | initial
  cnt = np.cumsum(lo_or_hi) # from 0 to len(x)
  return np.where(cnt, hi[ind[cnt-1]], initial)
