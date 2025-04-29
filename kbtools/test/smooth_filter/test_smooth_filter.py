"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\smooth_filter.py
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
    ''' topic: smoothing filter
        expected results:  time interval for 10%, 50% and 90%
    '''
    
    t_10_expected = 0.055
    t_50_expected = 0.095
    t_90_expected = 0.130

    # t_90_expected = 0.131   checking the testcae

    
    # create signals
    t_end = 10
    dT = 0.01

    # time signal
    t = np.arange(0,t_end,dT)

  
    input_signal = 1.5*np.ones_like(t)
    
     # create sin and cos
    f0=0.5;
    input_signal = 0.5*np.sin(2*np.pi*f0*t) + 1.5
   
    input_signal[np.logical_and(t>2.0, t<4.0)] = 1000.0
 
    valid = input_signal< 1000.0
    #valid = np.ones_like(input_signal)
  
    # filter sinus signal
    output_signal = kbtools.smooth_filter(t, input_signal,valid=valid)

    print "output_signal",output_signal.size

    FigNr = 1

    fig=plt.figure(FigNr)
    fig.suptitle('Matplotlib Example')

    sp=fig.add_subplot(111)
    sp.grid()
    sp.plot(t,input_signal,'rx-',label='input_signal')
    sp.plot(t,output_signal,'bx-',label='output_signal')
    sp.plot(t,valid,label='valid')
    sp.set_title('')
    sp.legend()
    sp.set_ylim(0.0,2.5)

  
    

    #fig.show()
    kbtools.take_a_picture(fig, os.path.join(r'.\PngFolder','Overview'), PlotName='Plot')

    '''
    t_10 = t[output_signal>=0.1][0]-t_start_step
    t_50 = t[output_signal>=0.5][0]-t_start_step
    t_90 = t[output_signal>=0.9][0]-t_start_step

    # report results
    self.assertAlmostEqual(t_10,t_10_expected, places=3) 
    self.assertAlmostEqual(t_50,t_50_expected, places=3) 
    self.assertAlmostEqual(t_90,t_90_expected, places=3) 
    
    '''
  
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for LPF_butter'
  unittest.main()
  



  
