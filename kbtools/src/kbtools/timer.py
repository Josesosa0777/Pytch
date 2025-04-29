'''
   
   monostable multivibrator
   
   non equidistant sampling
   
   Ulrich Guecker 2015-01-14

'''



import numpy as np

# ==========================================================
def monostable_multivibrator(t,u,T,retrigger=True):
    # mono flop 
    # inputs:
    #   t  - time           numpy array
    #   u  - input signals  numpy array
    #   T  - time constant  scalar
    #   retrigger - mode 
    # output:
    #   y
    
    y = np.zeros_like(u)

    
    timer = -1.0   # timer is stopped
    for k in xrange(1,u.size):
        # count down time
        dT = (t[k]-t[k-1])
        timer = (timer - dT)
        if timer < 0.5*dT:
           timer = 0.0
 
        # set timer if condition is fulfilled    
        if retrigger:
            if u[k]>0.5:
                timer = T
        else:
            if (u[k]>0.5) & (u[k-1]<0.5):
                # rising edge
                timer = T
                
        # check if timer active
        if timer > 0:
            y[k] = 1
       
        #print k, t[k], timer       
        

    return y  
