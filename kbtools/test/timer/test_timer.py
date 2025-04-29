"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\LPF_butter.py
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
    u           = np.array([  0,  0,  1,  1,  1,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0])
    y1_expected = np.array([  0,  0,  1,  1,  1,  1,  1,  1,  1,  1,  0,  1,  1,  1,  1,  1,  1,  0,  0,  0,  0])   # retrigger=True
    y2_expected = np.array([  0,  0,  1,  1,  1,  1,  1,  1,  0,  0,  0,  1,  1,  1,  1,  1,  1,  0,  0,  0,  0])   # retrigger=False
    
    T = 0.6
    
    y1 = kbtools.monostable_multivibrator(t,u,T)
    y2 = kbtools.monostable_multivibrator(t,u,T,retrigger=False)
    
    
    print "y1         ",y1
    print "y1_expected",y1_expected
    print "y2         ",y2
    print "y2_expected",y2_expected
    
    # report results
    #self.assertItemsEqual(y1,y1_expected,msg="retrigger=True")
    #self.assertItemsEqual(y2,y2_expected,msg="retrigger=False")
    
    self.assertEqual(y1.tolist(), y1_expected.tolist(),msg="retrigger=True")
    self.assertEqual(y2.tolist(), y2_expected.tolist(),msg="retrigger=False")
    
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for timer'
  unittest.main()
  



  
