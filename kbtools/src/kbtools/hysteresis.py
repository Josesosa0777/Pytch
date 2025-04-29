'''
    Hysteresis - threshold
    
    calculates threshold with hysteresis for given input signal 

       
'''
import numpy as np

#=================================================================================
def hysteresis_lower_upper_threshold(x, lower_treshold, upper_treshold, y0=False):  
    '''
    Hysteresis with lower and upper threshold 
    
    Calculates the time derivative of a given input signal x and a corresponding time vector t.
      
    inputs: 
        x      input signal 
    parameters:
        lower_treshold      if x is below this threshold output y is set to false
        upper_treshold      if x is above this threshold output y is set to true
    outputs:
        y      hysteresis state    
    '''   
    
        
    if  x is None:
        return None
    
    # outputs
    y = np.zeros_like(x)


    # hysteresis state
    state = y0  
            
     
    for k in xrange(1,x.size):
        if (x[k]>=upper_treshold):
            state = True
        elif (x[k]<=lower_treshold):
            state = False
        y[k]  = state
        
        

    return y    # output
#=================================================================================
