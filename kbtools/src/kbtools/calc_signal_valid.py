'''
   
   calc_signal_valid
     
   Ulrich Guecker 
   
   2013-06-07  extracted from DataAC100
   
'''

import numpy as np

  
# ======================================================================================================
def calc_signal_valid(t,t1,t_threshold=0.1):
    # t1 is a non continous time axis (e.g. time stamps of received CAN msgs)
    # this method calculate when information can be interpretated as valid
    # for the time axis t taking into account a timeout t_threshold
    # 
    # input:
    #   t : new time axis
    #   t1: existing time axis
    #   t_threshold: time interval during information is regarded as still valid
    # output
    #   valid : bool 

    #print "calc_signal_valid t", t
    if t is None:
        return None
    
    valid = np.ones(t.size)
    x = np.diff(t1)
    x = np.nonzero(x> t_threshold)[0]
    #print x

    # cut away start
    valid[np.nonzero(t<t1[0])] = 0
  
    # cut away end
    valid[np.nonzero(t>t1[-1])] = 0
  
    for idx in x:
      t_start = t1[idx]
      t_stop  = t1[idx+1]
      #print idx,  t_start, t_stop
      valid[np.nonzero((t>=t_start)&(t<=t_stop))] = 0
 
    #print t
    #print valid
    return valid

