'''


   Ulrich Guecker 
   
   2014-07-21

'''

import numpy as np
import sys, traceback


# ------------------------------------------------------------------------------------------
def GetValuesAtStartAndStop(t, x, t_start,t_stop, shift=-1):
    #print "get_start_and_stop"
    #print "t[0], t[-1]", t[0], t[-1]
    
    '''    
    if t_start < t[-1]:
        x_t_start = x[t>=t_start][0]
    else:
        x_t_start = x[-1]
      
    if t_stop < t[-1]:
        x_t_stop  = x[t>=t_stop][0]
    else:
        x_t_stop  = x[-1]
    '''

    x_t_start = GetPreviousSample(t, x, t_start, shift=shift)
    x_t_stop  = GetPreviousSample(t, x, t_stop, shift=shift)

    return x_t_start, x_t_stop
    
#=================================================================================
def GetValueAtCond(signal,cond,shift=-1):
    #Left_C0_at_t_LDW_Left = get_value(Left_C0,t_Left_C0>t_LDW_Left_start,-1)
    #print "Left_C0_at_t_LDW_Left", Left_C0_at_t_LDW_Left

    return signal[np.argwhere(cond)[0]+shift][0]

#=================================================================================
def GetTRisingEdge(t,x,t_start=-np.inf,t_stop=np.inf, shift=0):
    '''
        search in a given interval |t_start, t_stop| for the first rising edge of
        the signal given by its time axis and its values
        
        paramters:
        t - time axis 
        x - signal value
        t_start - start time of interval 
        t_stop  - stop time of interval
        shift   - shift in sampling point
    
    '''
    try:
        
        idx = np.logical_and(t>=t_start,t<=t_stop)
        tmp_t = t[idx]
        tmp_x = x[idx]
        idx_rising_edge = np.argwhere(np.diff(tmp_x)>0.5)[0]
        idx_rising_edge = idx_rising_edge.squeeze()
        idx_rising_edge = idx_rising_edge+1
        t_rising_edge   = tmp_t[idx_rising_edge+shift]
        '''
        # old implementation
        #t_rising_edge = t[np.logical_and(np.logical_and(t>=t_start,t<=t_stop),x>0.5)][0] 
        idx = np.argwhere(np.logical_and(np.logical_and(t>=t_start,t<=t_stop),x>0.5))[0]
        idx = idx.squeeze()
        t_rising_edge = t[idx+shift]
        '''
    #except IndexError:
    except Exception, e:
        print "error - GetTRisingEdge: ",e.message
        traceback.print_exc(file=sys.stdout)
        t_rising_edge = None    # Not available
        
    return t_rising_edge
    
# ------------------------------------------------------------------------------------------
# GetPreviousSample_scalar
def GetPreviousSample_scalar(t, x, t_start, shift=-1):
    try:
        if t_start<t[-1]:
            idx = np.argwhere(t>t_start)[0]
            x_t_start = x[idx+shift][0]
        else:
            x_t_start = x[-1]   
    except:
        x_t_start = None
        
    return x_t_start
# ------------------------------------------------------------------------------------------
def GetPreviousSample(t, x, t_start, shift=-1):
    if isinstance(t_start, (list, tuple, np.ndarray)):
        x_t_start_list = []
        for tmp_t_start in t_start:
            x_t_start_list.append(GetPreviousSample_scalar(t, x, tmp_t_start, shift=shift))
        if isinstance(t_start, np.ndarray):
            return np.array(x_t_start_list)
        else:
            return x_t_start_list
    else:
        # scalar
        return GetPreviousSample_scalar(t, x, t_start, shift=shift)     
        
# ------------------------------------------------------------------------------------------
def GetSampleAround(t, x, t_start, shift=-1):
    try:
        if t_start<t[-1]:
            idx = np.argwhere(t>t_start)[0]
            print "GetSampleAround", idx, idx+1
            x_t_start = [x[idx+shift][0], x[idx+1+shift][0]]
            t_t_start = [t[idx+shift][0], t[idx+1+shift][0]]
        else:
            x_t_start = x[-1]   
            t_t_start = t[-1]
    except:
        x_t_start = None
        t_t_start = None

    return t_t_start, x_t_start

# ------------------------------------------------------------------------------------------
def GetTStop(t, x, t_start):
    
    # stop 
    try:
        t_stop = t[np.logical_and(t>t_start,x<0.5)][0] 
    except IndexError:
        t_stop = t[-2]    # take 2nd last sample
        
    return t_stop
    
# ------------------------------------------------------------------------------------------
def GetMinMaxBetweenStartAndStop(Time, Value, t_start,t_stop):
        
    idx = np.argwhere(np.logical_and(t_start<=Time,Time<t_stop))
    x = Value[idx]
    
    return np.min(x), np.max(x) 