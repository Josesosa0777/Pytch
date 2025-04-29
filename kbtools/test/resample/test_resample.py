"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\resample.py
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
    ''' topic: resample - basic
        expected results:  
    '''
    
    
    t1          = np.array([0.0,0.5,1.0,1.5,2.0])
    u1          = np.array([  0,  1,  1,  0,  0])
    
    t2          = np.array([0.0,0.4,0.8,1.2,1.6,2.0,2.4])
    y2_expected = np.array([  0,  0,  1,  1,  0,  0,  0])   
    
       
    y2 = kbtools.resample(t1,u1,t2)
    
    
    
    print y2
    
    # report results
    self.assertEqual(y2.tolist(), y2_expected.tolist(),msg="")
    
    
  #------------------------------------------------------------------------  
  def test_TC002(self):
    ''' topic: resample - shift
        expected results:  
    '''
    
    
    t1          = np.array([0.0,0.5,1.0,1.5,2.0])
    u1          = np.array([  0,  1,  1,  0,  0])
    
    t2          = np.array([0.0,0.4,0.8,1.2,1.6,2.0,2.4])
  

    expected_list = [ ( 0, np.array([  0,  0,  1,  1,  0,  0,  0])), \
                      ( 1, np.array([  0,  0,  0,  1,  1,  0,  0])), \
                      ( 2, np.array([  0,  0,  0,  0,  1,  1,  0])), \
                      (-1, np.array([  0,  1,  1,  0,  0,  0,  0])), \
                      (-2, np.array([  1,  1,  0,  0,  0,  0,  0]))  ] 
    
    print "test_TC002"
    for k, (n, y2_expected) in enumerate(expected_list):
        y2 = kbtools.resample(t1,u1,t2,shift=n)
   
        print k, "n=", n, ":"
        print "   y2          :", y2
        print "   y2_expected :", y2_expected
    
        self.assertEqual(y2.tolist(), y2_expected.tolist(),msg="")    # report results

    
    
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for timer'
  unittest.main()
  



  
