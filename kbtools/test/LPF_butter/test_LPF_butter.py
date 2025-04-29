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
    ''' topic: Butterworth Low Pass Filter (4th order)
               corner frequency: 5Hz
               acceleration filtering for AEBS tests
               Step response 
        expected results:  time interval for 10%, 50% and 90%
    '''
    
    t_10_expected = 0.055
    t_50_expected = 0.095
    t_90_expected = 0.130

    # t_90_expected = 0.131   checking the testcae

    
    # create signals
    N = 200
    dT = 0.005

    # time signal
    t = np.arange(0,N*dT,dT)

    # 5 Hz sinus signal  (corner frequency; filter shall attentuate signal by 3dB = 0.707)
    t_start_step = 0.1
  
    input_signal = np.zeros_like(t)
    input_signal[t>0.1] = 1.0
  
    # filter sinus signal
    output_signal = kbtools.LPF_butter(t, input_signal)

    t_10 = t[output_signal>=0.1][0]-t_start_step
    t_50 = t[output_signal>=0.5][0]-t_start_step
    t_90 = t[output_signal>=0.9][0]-t_start_step

    # report results
    self.assertAlmostEqual(t_10,t_10_expected, places=3) 
    self.assertAlmostEqual(t_50,t_50_expected, places=3) 
    self.assertAlmostEqual(t_90,t_90_expected, places=3) 
    
  
  
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for LPF_butter'
  unittest.main()
  



  
