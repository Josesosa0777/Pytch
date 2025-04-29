"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\hysteresis.py
'''

import numpy as np
#import matplotlib.pyplot as plt

import unittest
#import os

import kbtools



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  
    #------------------------------------------------------------------------  
    def test_TC001(self):
        ''' topic: hysteresis_lower_upper_threshold
            expected results:  
        '''
    
    
        x           = np.array([0.0, 0.1, 0.2, 0.4, 0.5, 0.6, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0])
        y1_expected = np.array([  0,   0,   0,   0,   1,   1,   1,   1,   1,   0,   0,   0,   0,   0])   
    
        y1 = kbtools.hysteresis_lower_upper_threshold(x,lower_treshold=0.4, upper_treshold=0.5)
        
        print "y1         ",y1.astype(int)
        print "y1_expected",y1_expected.astype(int)
    
        self.assertEqual(y1.tolist(), y1_expected.tolist(),msg="")

              
    
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
    print 'unittest for hysteresis'
    unittest.main()
  



  
