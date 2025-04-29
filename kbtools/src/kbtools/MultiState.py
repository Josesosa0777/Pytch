'''
   
   Detect changes in a given signal

'''

import numpy as np

# ============================================================================ 
class CMultiState(object):
    '''
    Signals evaluated with this class have different discrete values e.g. 0,1,2,3,..15
    Intervals with constant value can be regarded as segments, as a result signals can be 
    understood as a sequence of segments.
    A segment has a starting point, a duration and a value.
        
    This class determines the segments. 
    
    
    todo: consecutive measurements (currently each measurement file is evaluated independently)
    '''


    def __init__(self, params=None, verbose=False):
        '''
        Constructor
        '''
        
        #  return
        self.t_starts   = None     # list with segment starting points
        self.dura       = None     # list with segment duration
        self.sig_starts = None     # list with segment value

        self.verbose = verbose
        
       
    def calc(self,t,sig,default_value = 0):
        '''
           t             : time    (numpy.array)
           sig           : signal  (numpy.array)
           default_value : exclude this value (scalar or list)
        
        '''
        if self.verbose:
            print "CMultiState::calc()"
        
        t_starts = None
        sig_starts = None
        dura = None

        # signal changes
        #print "type(sig)", type(sig), sig.dtype
        dsig = np.diff(sig.astype(float))
        #print "type(dsig)", type(dsig), dsig.dtype
        dsig = np.insert(dsig,0,1)     # start
        dsig[-1] = 1                   # stop
        
        idx = np.argwhere(abs(dsig)>0)

        tg = np.append(t,t[-1])
        sig = np.append(sig,sig[-1])

        t_starts = t[idx].flatten()
        sig_starts = sig[idx].flatten()

        dura = np.diff(t_starts)
        t_starts = t_starts[:-1]
        sig_starts  = sig_starts[:-1]
        
        if default_value is None:
            default_value = []
        if not isinstance(default_value,list):
            default_value = [default_value]
            
        if self.verbose:
            print "default_value", default_value
            
        for single_default_value in default_value:
            idx2 = sig_starts!=single_default_value
            t_starts = t_starts[idx2]
            sig_starts  = sig_starts[idx2]
            dura = dura[idx2]

        if self.verbose:
            print self.t_starts
        self.t_starts   = t_starts
        self.sig_starts = sig_starts
        self.dura       = dura
        
    def merge(self,DistLimitTime):
        if self.verbose:
            print "CMultiState::merge()",DistLimitTime  
        
        tmp_t_start = None
        tmp_sig_start = None
        tmp_dura = None
        
        new_t_starts = []
        new_sig_starts = []
        new_dura = []
        for t_start,sig_start,dura in zip(self.t_starts,self.sig_starts,self.dura):
            if self.verbose:
                print t_start,sig_start,dura
            if tmp_t_start is None:
                tmp_t_start = t_start
                tmp_sig_start = sig_start
                tmp_dura = dura
            else:
                if ((sig_start==tmp_sig_start) and ((t_start - (tmp_t_start+tmp_dura)) < DistLimitTime)):
                    tmp_dura = (t_start-tmp_t_start) + dura
                else:
                    new_t_starts.append(tmp_t_start)
                    new_sig_starts.append(tmp_sig_start)
                    new_dura.append(tmp_dura)     

                    tmp_t_start = t_start
                    tmp_sig_start = sig_start
                    tmp_dura = dura
        
        # write last pending event        
        if  tmp_t_start is not None:
            new_t_starts.append(tmp_t_start)
            new_sig_starts.append(tmp_sig_start)
            new_dura.append(tmp_dura)     
                    
         
        self.t_starts = new_t_starts
        self.sig_starts = new_sig_starts
        self.dura = new_dura            

        if self.verbose:
            self._print()
        
    def _print(self):
        print "---------------"
        print "t_start,sig_start,dura"
        
        for t_start,sig_start,dura in zip(self.t_starts,self.sig_starts,self.dura):
            print t_start,sig_start,dura
