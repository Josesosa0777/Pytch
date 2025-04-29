"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for kbtools\MultiState.py
'''

import unittest

import kbtools
import numpy as np


#========================================================================================
class TestSequenceFunctions(unittest.TestCase):

    def _abstract_test_case_MultiState(self,TestCaeName,Time,Value,Expected,DistLimitTime,default_value=0):
        '''
            abstract test case for "on_phase" mode of hunt4event
            
            parameters:
                TestCaeName:   Name of this test case
                Time:          ndarray with time 
                Value:         ndarray with value
                Expected:      expected results: list of tupels: (t_start, duration) - t_start and duration are string literals
                DistLimitTime: parameter - merge single events if gap between them is less than DistLimitTime
                default_value: parameter - value that is shall not appear in the evaluation 
        '''
    
        print "-----------------------------"
        print TestCaeName, "- start"
        print "_abstract_test_case_on_phase()"
        print "   DistLimitTime:", DistLimitTime
        print "   default_value:", default_value
        print "   Time:", Time
        print "   Value:", Value
        

        # ---------------------------------
        # 1. instanciate, inititialize 
        iMultitState = kbtools.CMultiState()

        # 2. calc
        iMultitState.calc(Time,Value,default_value=default_value)
      
        # merge entries
        iMultitState.merge(DistLimitTime)
      
       
        # ---------------------------------
        # check results

        # t_starts, sig_starts, dura
        print "   Calculated/Expected:"
        if len(iMultitState.t_starts) > 0:
            for k,(t_start,sig_start,dura) in enumerate(zip(iMultitState.t_starts,iMultitState.sig_starts,iMultitState.dura)):
                t_start_expected = Expected[k][0]
                dura_expected    = Expected[k][1]
                print "      %d. t_start=%f / %f, duration=%f / %f"%(k,t_start,t_start_expected,dura,dura_expected)
        
                self.assertSequenceEqual((t_start,dura),(t_start_expected, dura_expected),msg='%s event: %d'%(TestCaeName,k+1))
            
                          
        print TestCaeName, "- end"
        
        
         
  
        
        
        
    #------------------------------------------------------------------------  
    def test_on_phase_TC001(self, TestCaeName="test_MultiState_TC001"): 
        '''
            basic functionality - no merging (DistLimitTime = 0.0)
        '''
               
        # parameters
        DistLimitTime = 0
        default_value = 0
        
        # input vectors: create time axis and values
        Time  = np.array([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.])
        Value = np.array([0.,1.,0.,1.,0.,1.,0.,0.,0.,0., 0., 1., 1., 0.])
        
        Value = Value.astype(bool)
        
        # expected results: list of tupels: (t_start, duration) - t_start and duration are string literals
        Expected = [(1.0,1.0),(3.0,1.0),(5.0,1.0),(11.0,2.0) ]
      
        self._abstract_test_case_MultiState(TestCaeName,Time,Value,Expected,DistLimitTime,default_value)        

        print "This is test_on_phase_TC001 - end" 
        
        
        
        
    #------------------------------------------------------------------------  
    def test_on_phase_TC002(self, TestCaeName="test_MultiState_TC002"): 
        '''
            test merging capabilities -> DistLimitTime = 2.0
        '''
                
        # parameters
        DistLimitTime = 2.0
        default_value = 0
        
        # input vectors: create time axis and values
        Time  = np.array([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.])
        Value = np.array([0.,1.,0.,1.,0.,1.,0.,0.,0.,0., 0., 1., 1., 0.])
        
        Value = Value.astype(bool)
        
        # list of tupels: (t_start, duration)   - t_start and duration are string literals
        Expected = [(1.0,5.0),(11.0,2.0) ]
      
        self._abstract_test_case_MultiState(TestCaeName,Time,Value,Expected,DistLimitTime,default_value)        
        
    #------------------------------------------------------------------------  
    def test_on_phase_TC003(self, TestCaeName="test_MultiState_TC003"): 
        '''
            active at start and until end - no mergin (DistLimitTime = 0.0)
        '''
              
        # parameters
        DistLimitTime = 0
        default_value = 0
        
        # input vectors: create time axis and values
        Time  = np.array([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.])
        Value = np.array([1.,1.,0.,1.,0.,1.,0.,0.,0.,0., 0., 1., 1., 1.])
        
        Value = Value.astype(bool)
        
        # list of tupels: (t_start, duration)   - t_start and duration are string literals
        Expected = [(0.0,2.0),(3.0,1.0),(5.0,1.0),(11.0,2.0) ]
      
        self._abstract_test_case_MultiState(TestCaeName,Time,Value,Expected,DistLimitTime,default_value)        

       
    #------------------------------------------------------------------------  

    
#========================================================================================
if __name__ == "__main__":
  print 'unittest for hunt4event'
  unittest.main()
  

