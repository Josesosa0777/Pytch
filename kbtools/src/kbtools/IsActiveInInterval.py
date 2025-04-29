'''


   Ulrich Guecker 
   
   2014-12-15

'''

import numpy as np
import kbtools

#=================================================================================
class  CIsActiveInInterval(object):

    # ------------------------------------------------------------------------------------------
    def __init__(self, t_start, t_stop,t, sig, t_pre = 0.1, t_post = 0.1, verbose=False):
        '''
         
           t_pre, t_post: tolerance
        
        '''
        self.na_values = 'NA'            # not available value for Excel
        
        self._status  = None
        self._delta_t = None
        self._duration = None
        
        if t is not None:
            self._status  = np.any(sig[np.logical_and(t_start-t_pre<=t,t<t_stop+t_post)])
            
            if self._status:
                if verbose:
                    print "CIsActiveInInterval.init()"
                    print "t_start, t_stop",t_start, t_stop
                idx = np.logical_and(t_start-t_pre<=t,t<t_stop+t_post)
                t_tmp   = t[idx]  
                sig_tmp = sig[idx]
                
                if verbose:
                    print "idx", np.argwhere(idx)
                    print "t_tmp", t_tmp
                    print "sig_tmp", sig_tmp
                
                idx_start   = np.argwhere(sig_tmp>0.5)[0]
                t_sig_start1 = t_tmp[idx_start]
                if verbose:
                    print "idx_start", idx_start
                    print "t_sig_start1",t_sig_start1
        
                t_sig_start2, t_sig_stop2 = kbtools.getIntervalAroundEvent(t,t_sig_start1,sig>0.5,verbose = False,output_mode = 't')
                                
                if verbose:
                    print "t_sig_start2",t_sig_start2
                    print "t_sig_stop2",t_sig_stop2
                
                try:
                    self._delta_t = t_sig_start2 - t_start
                except:
                    pass
                
                try:                
                    self._duration = t_sig_stop2 - t_sig_start2
                except:
                    pass
                
                if verbose:
                    print "_delta_t",self._delta_t
                    print "_duration",self._duration
            
    # ------------------------------------------------------------------------------------------
    def GetStatus(self):
        return self._status
    # ------------------------------------------------------------------------------------------
    def GetStatusStr(self):
        if self._status is None:
            return self.na_values
        else:
            return ("yes" if self._status else "no")

    # ------------------------------------------------------------------------------------------
    def GetDeltaT(self):
        return self._delta_t
    # ------------------------------------------------------------------------------------------
    def GetDeltaTStr(self):
        if self._delta_t is None:
            return self.na_values
        else:
            #print "GetDeltaTStr._delta_t", self._delta_t
            return "%3.3f"%self._delta_t
            
    # ------------------------------------------------------------------------------------------
    def GetDuration(self):
        return self._duration
    # ------------------------------------------------------------------------------------------
    def GetDurationStr(self):
        if self._duration is None:
            return self.na_values
        else:
            return "%3.3f"%self._duration

    # ------------------------------------------------------------------------------------------
    # Properties
    Status    = property(GetStatus)
    StatusStr = property(GetStatusStr)
    
    DeltaT    = property(GetDeltaT)
    DeltaTStr = property(GetDeltaTStr)
    
    Duration    = property(GetDuration)
    DurationStr = property(GetDurationStr)

