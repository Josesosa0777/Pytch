'''
   
   resample signals
     
   Ulrich Guecker 
   
   2012-11-30
   
   "zoh_next" correct delay from slow to fast task 
   e.g. Acoopti_SetRequest is calculated in TC and copied to T20, this result in a delay if T20 resampled to TC if ordinary "zoh" used
   
'''

import numpy as np

# ======================================================================================================
def resample(t_old, x_old, t_new, method='zoh', shift=None):
    # resample given signal t_old, x_old for new time axis t_new using a method 
    # method:    'zoh'  zero order hold
    
    #print "t old:", t_old
    #print "x old:", x_old
    #print "t new:", t_new
    
    if t_old is None or x_old is None or t_new is None:
      return None
    
    # resample
    if 'zoh' == method:
      idx = np.searchsorted(t_old,t_new,side='right')-1
      idx = np.maximum(idx,np.zeros_like(idx))  # prevent negavite indices
      x_new = x_old[idx]
    elif 'zoh_next' == method:
      #idx = np.searchsorted(t_old,t_new,side='right')
      idx = np.searchsorted(t_old,t_new,side='left')
      
      idx = np.maximum(idx,np.zeros_like(idx))  # prevent negavite indices
      #print "x_old", x_old
      #print "len(x_old)", len(x_old)
      #print "idx", idx
      #print idx[idx<len(x_old)]
      #idx2 = idx[idx<len(x_old)]
      #print idx2[-1]
      #idx[idx>=len(x_old)] = idx2[-1]
      
      # if idx exceed x_old, continue last value of x_old
      N = len(x_old)
      if (max(idx) >= N):
        idx[idx>=N] = idx[idx<N][-1]
      #print "idx", idx
      #x_new = x_old[idx2]
      x_new = x_old[idx]
    
    #------------------
    if shift is not None:
        if shift > 0:
            x_new[shift:-1] = x_new[:(-1-shift)]
            x_new[:shift] = np.zeros(shift) 
        elif shift < 0:
            x_new[:shift] = x_new[-shift:]
            #print x_new[shift:]
            #print np.zeros(-shift) 
            x_new[shift:] = np.zeros(-shift) 
                    
    
    return x_new
    
