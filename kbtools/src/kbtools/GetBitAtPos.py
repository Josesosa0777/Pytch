'''
   
   GetBitAtPos 
   
   Get Bit at a given position
     
   Ulrich Guecker 
   
   2013-06-12
   
   
'''

import numpy as np

# ======================================================================================================
def GetBitAtPos(sig, pos):
    # input:
    #   sig - input signal (integer or float)
    #   pos - bit position (starts with 0)
   
    return (np.bitwise_and(sig.astype(int), 2**pos)>0.5)
    
