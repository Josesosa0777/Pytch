"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for kbtools\extract_values.py
'''

import numpy as np
import matplotlib.pyplot as plt

import unittest
import os

import kbtools



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  
  #------------------------------------------------------------------------  
  def test_TC001(self):
    ''' topic: monostable_multivibrator
        expected results:  both for retriggered and non retriggered mode
    '''
    
    
    t           = np.array([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0])
    x           = np.array([0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0])
    
    # scalar
    print "scalar"
    t_start = 0.25
    x_t_start_expected = 0.2
    x_t_start = kbtools.GetPreviousSample(t, x, t_start, shift=-1)
    print "x_t_start, x_t_start_expected  ",x_t_start,x_t_start_expected
    self.assertEqual(x_t_start, x_t_start_expected, msg="scalar")
    
    # np.array
    print "np.array"
    t_start = np.array([0.25, 0.5])
    x_t_start_expected = np.array([0.2, 0.5])
    x_t_start = kbtools.GetPreviousSample(t, x, t_start, shift=-1)
    print "x_t_start, x_t_start_expected  ",x_t_start,x_t_start_expected
    self.assertEqual(x_t_start.tolist(), x_t_start_expected.tolist(),msg="np.array")
   
    # list
    print "list"
    t_start = [0.25, 0.5]
    x_t_start_expected = [0.2, 0.5]
    x_t_start = kbtools.GetPreviousSample(t, x, t_start, shift=-1)
    print "x_t_start, x_t_start_expected  ",x_t_start,x_t_start_expected
    self.assertEqual(x_t_start, x_t_start_expected,msg="list")
 
     
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for timer'
  unittest.main()
  



  
