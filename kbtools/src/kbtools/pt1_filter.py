'''
   
   PT1 Filter
   
   non equidistant sampling
   
   Ulrich Guecker 2011-11-30

'''

'''
  room for improvement
  check if we have equidistance sampling
  np.mean(np.diff(t))
'''

import numpy as np

# ==========================================================
def pt1_filter(t,u,T,u0=None):
  # first order linear filter
  # inputs:
  #   t  - time           numpy array
  #   u  - input signals  numpy array
  #   T  - time constant  numpy array
  #   u0 - intial state   scalar
  # output:
  #   y
  y = np.zeros_like(u)

  # initial state
  if u0:
    y[0] = u0
  else:  
    y[0] = u[0]
    
  for k in xrange(1,u.size):
    y[k] = y[k-1] + (t[k]-t[k-1])/T*(u[k]-y[k-1])  

  return y  
