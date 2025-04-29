"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\getIntervalAroundEvent.py
'''

import numpy as np
import matplotlib.pyplot as plt

import unittest
import os

import kbtools



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  
  
    #------------------------------------------------------------------------  
    def abstract_test_case_getIntervalAroundEvent(self,t,u,t_center,t_start_expected,t_stop_expected):
         
        bool_signal = u > 0.5
        t_start, t_stop = kbtools.getIntervalAroundEvent(t,t_center,bool_signal,verbose = True,output_mode = 't')
           
        
        print "t_start,  t_start_expected:",t_start,  t_start_expected
        print "t_stop,  t_stop_expected:",t_stop,  t_stop_expected
    
        self.assertEqual(t_start, t_start_expected, msg="t_start")
        self.assertEqual(t_stop, t_stop_expected, msg="t_stop")

  
    #------------------------------------------------------------------------  
    def test_TC001(self):
        ''' topic: getIntervalAroundEvent
            expected results:  start and stop index of interval detected correctly
        '''
    
        print "test_TC001:"
    
        t           = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0])
        u           = np.array([0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        t_center = 0.5 
        t_start_expected = 0.3
        t_stop_expected = 1.0
        
    
        self.abstract_test_case_getIntervalAroundEvent(t,u,t_center,t_start_expected,t_stop_expected)

    #------------------------------------------------------------------------  
    def test_TC002(self):
        ''' topic: getIntervalAroundEvent
            expected results:  interval is last sampling point
        '''
    
        print "test_TC002:"
    
        t           = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0])
        u           = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
        t_center = 2.0
        t_start_expected = 2.0
        t_stop_expected = 2.0
        
    
        self.abstract_test_case_getIntervalAroundEvent(t,u,t_center,t_start_expected,t_stop_expected)

    #------------------------------------------------------------------------  
    def test_TC003(self):
        ''' topic: getIntervalAroundEvent
            expected results:  start and stop index of interval detected correctly
        '''
    
        print "test_TC003:"
    
        t           = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0])
        u           = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        t_center = 0.5 
        t_start_expected = None
        t_stop_expected = None
        
    
        self.abstract_test_case_getIntervalAroundEvent(t,u,t_center,t_start_expected,t_stop_expected)

    
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for getIntervalAroundEvent.py'
  unittest.main()
  



  
