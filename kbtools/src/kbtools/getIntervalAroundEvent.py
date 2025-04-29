'''
   
   getIntervalAroundEvent
     
   Ulrich Guecker 
   
   2012-11-30
   
'''

import numpy as np




#============================================================================================
def getIntervalAroundEvent(t,t_center,bool_signal, verbose = False, output_mode = 'idx'):
    ''''
        determine interval around an event given by time instand t:center
    
        bool_signal =  00000000111111111000000
                                    ^ t_center
                               ^       ^     start_idx and stop_idx
                               ^       ^     t_start and t_stop
    
        output_mode = 'idx' or 't'
    '''
    
    if verbose:
            print "getIntervalAroundEvent()"
    
    if not np.any(bool_signal):
        if verbose:
            print "  -> bool_signal is zero -> quit"
        return None, None    
      
    ##print "bool_signal", bool_signal
    ##m = np.hstack([0,np.logical_and(t <= t_center,bool_signal)])
    ##print m
    
    start_tmp = np.diff(np.hstack([0,np.logical_and(t <= t_center,bool_signal)]))
    if verbose:
      print "  t_center",t_center
      print "  t[0] .. t[-1]:", t[0], t[-1]
      print "  start_tmp: ", start_tmp          
      print "  nonzero(start_tmp):", np.nonzero(start_tmp)
      print "  nonzero(start_tmp)[0]:", np.nonzero(start_tmp)[0]
      
    
    try: 
        start_idx = np.nonzero(start_tmp)[0][-2]
        if verbose:
            print "  start_idx = nonzero(start_tmp)[0][-2]:", start_idx
    except:
        try:
            start_idx = np.nonzero(start_tmp)[0][0]
            if verbose:
                print "  start_idx = nonzero(start_tmp)[0]:", start_idx
        except:
            start_idx = None
        
    stop_tmp = np.diff(np.hstack([np.logical_and(t_center <= t, bool_signal),0]))
    if verbose:
      print "stop_tmp", stop_tmp          
      print "nonzero(stop_tmp)", np.nonzero(stop_tmp)
      print "nonzero(stop_tmp)[0]", np.nonzero(stop_tmp)[0]
      
                
    try:
        stop_idx   = np.nonzero(stop_tmp)[0][1]
        if verbose:
            print "stop_idx = nonzero(stop_tmp)[0][1]", np.nonzero(stop_tmp)[0][1]
    except:
        stop_idx = None
    
    if output_mode == 'idx':
        return start_idx, stop_idx 
    elif output_mode == 't':
        t_start = None
        t_stop = None
        if start_idx is not None:
           t_start = t[start_idx]
        if stop_idx is not None:
           t_stop = t[stop_idx]
        
        return t_start, t_stop
    
    