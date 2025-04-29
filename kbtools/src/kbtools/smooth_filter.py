




import numpy as np
import pylab as pl
import scipy 

import kbtools

import sys, traceback


# ==========================================================
def smooth_filter(t, x, f_g = 2.5, N = 3, filtertype = 'acausal',valid=None):
    '''
       smooth signals like lateral velocity signals using a digital butterworth filter
    '''
    if (t is None) or (x is None):    
        return None
    #if np.isnan(t) or np.isnan(x):
    #    return None
    
    if valid is None:
        valid = np.ones_like(t)
    
    try:
        t_abst = np.mean(np.diff(t))
        f_abst = 1/t_abst
        f_nyq  = f_abst/2.0
    
        # digital butterworth filter coefficients
        [b,a]=scipy.signal.butter(N,f_g/f_nyq)
        
        f_x = np.zeros_like(x)
        
        # ---------------------------------
        # 1. instanciate, inititialize 
        iMultitState = kbtools.CMultiState()

        # 2. calc
        iMultitState.calc(t,valid,default_value=0)
      
        for k,(t_start,dura) in enumerate(zip(iMultitState.t_starts,iMultitState.dura)):
            t_stop = t_start + dura
            idx = np.logical_and(t_start<=t,t<(t_stop))
            #t_tmp = t[idx]
            x_tmp = x[idx]
  
  
            if filtertype == 'causal':
                f_x_tmp=scipy.signal.lfilter(b,a,x_tmp)
            elif filtertype == 'acausal':
                #f_x_tmp=kbtools.filtfilt(b,a,x_tmp)
                padlen = min(30, x_tmp.size-3)
                f_x_tmp=scipy.signal.filtfilt(b,a,x_tmp, padlen=padlen)
                
            
            f_x[idx] = f_x_tmp
            
        return f_x
    except Exception, e:
        print "error - smooth_filter: ",e.message
        traceback.print_exc(file=sys.stdout)
        return None    
