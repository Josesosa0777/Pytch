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

    def _abstract_test_case_CIsActiveInInterval(self, t, x, t_start=0.1, t_stop=0.7, t_pre=0.0, t_post=0.0,  Status_expected=True, DeltaT_expected=-0.1, Duration_expected=0.2):
        print "---------------------------"
        print "_abstract_test_case_CIsActiveInInterval():"
        print "  parameters:"
        print "    t_start", t_start
        print "    t_stop", t_stop
        print "    t_pre", t_pre
        print "    t_post", t_post
               
        iIsActiveInInterval  = kbtools.CIsActiveInInterval(t_start, t_stop, t,x,t_pre=t_pre,t_post=t_post,verbose=True)
    
        print "  outputs:"
        print "    Status real/expected:", iIsActiveInInterval.Status,Status_expected
        print "    StatusStr: <%s>"%iIsActiveInInterval.StatusStr
    
        print "    DeltaT real/expected", iIsActiveInInterval.DeltaT,DeltaT_expected
        print "    DeltaTStr: <%s>"%iIsActiveInInterval.DeltaTStr
    
        print "    Duration real/expected", iIsActiveInInterval.Duration,Duration_expected
        print "    DurationStr <%s>"%iIsActiveInInterval.DurationStr
    
        self.assertEqual(iIsActiveInInterval.Status,Status_expected) 
        if iIsActiveInInterval.DeltaT is not None:
            self.assertAlmostEqual(iIsActiveInInterval.DeltaT,DeltaT_expected,places=3) 
           
        if iIsActiveInInterval.Duration is not None:
            self.assertAlmostEqual(iIsActiveInInterval.Duration,Duration_expected,places=3) 


    #------------------------------------------------------------------------  
    def test_TC001(self):
        ''' topic: kbtools.CIsActiveInInterval
            expected results:  detect first rising edge in a given interval
        '''
    
        print "==========================================================="
        print "test_TC001"

        t = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2 ])
        x = np.array([1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0 ])

    
        #self._helper_CIsActiveInInterval(t_start=0.1, t_stop=0.7, t_pre=0.0, t_post=0.0,  Status_expected=True, DeltaT_expected=-0.1, Duration_expected=0.2)
        self._abstract_test_case_CIsActiveInInterval(t,x, 0.1, 0.7, 0.0, 0.0,  True, -0.1, 0.2)
        self._abstract_test_case_CIsActiveInInterval(t,x, 0.4, 0.7, 0.0, 0.0,  True,  0.1, 0.1)
        self._abstract_test_case_CIsActiveInInterval(t,x, 0.3, 0.4, 0.0, 0.0,  False,  None, None)
           
    #------------------------------------------------------------------------  
    def test_TC002(self):
        ''' topic: kbtools.CIsActiveInInterval
            expected results:  only last sample is active
        '''
    
        print "==========================================================="
        print "test_TC002"
    
        t = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2 ])
        x = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0 ])

    
        #self._helper_CIsActiveInInterval(t_start=0.1, t_stop=0.7, t_pre=0.0, t_post=0.0,  Status_expected=True, DeltaT_expected=-0.1, Duration_expected=0.2)
        
        self._abstract_test_case_CIsActiveInInterval(t,x, 0.8, 0.9, 0.1, 0.1, False, None, None)
        self._abstract_test_case_CIsActiveInInterval(t,x, 0.8, 1.1, 0.1, 0.1,  True, 0.4, 0.0)
        self._abstract_test_case_CIsActiveInInterval(t,x, 1.2, 1.3, 0.1, 0.1,  True, 0.0, 0.0)
          
  
  
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
    print 'unittest for test_IsActiveInInterval.py'
    unittest.main()
  



  
