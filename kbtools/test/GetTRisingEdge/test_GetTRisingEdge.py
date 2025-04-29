"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\GetTRisingEdge.py
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
    ''' topic: kbtools.GetTRisingEdge
        expected results:  detect first rising edge in a given interval
    '''
    
    
    t = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2 ])
    x = np.array([1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0 ])

    # test case 1
    t_start = 0.1
    t_stop  = 0.7
    TRisingEdge_expected = 0.5
    TRisingEdge = kbtools.GetTRisingEdge(t,x,t_start=t_start,t_stop=t_stop, shift=0)
    print "TRisingEdge", TRisingEdge
    self.assertEqual(TRisingEdge,TRisingEdge_expected) 

    # test case 1
    t_start = 0.8
    t_stop  = 1.2
    TRisingEdge_expected = 0.9
    TRisingEdge = kbtools.GetTRisingEdge(t,x,t_start=t_start,t_stop=t_stop, shift=0)
    print "TRisingEdge", TRisingEdge
    self.assertEqual(TRisingEdge,TRisingEdge_expected) 
    
  
  
  
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for GetTRisingEdge'
  unittest.main()
  



  
