"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\hunt4event.py
'''

import unittest

import kbtools
import numpy as np

class Source_Stub():
  def __init__(self, FileName):
    self.FileName = FileName

#========================================================================================
class TestSequenceFunctions(unittest.TestCase):

    def _abstract_test_case_on_phase(self,TestCaeName,Time,Value,Expected,t_join):
        '''
            abstract test case for "on_phase" mode of hunt4event
            
            parameters:
                TestCaeName:   Name of this test case
                Time:          ndarray with time 
                Value:         ndarray with value
                Expected:      expected results: list of tupels: (t_start, duration) - t_start and duration are string literals
                t_join:        hunt4event parameter - merge single events if gap between them is less than t_join
        
        '''
    
        print "-----------------------------"
        print TestCaeName, "- start"
        print "_abstract_test_case_on_phase()"
        print "   t_join:", t_join
        print "   Time:", Time
        print "   Value:", Value
        print "   Expected:"
        for k,(t_start,dura) in enumerate(Expected):
           print "      %d. t_start=%s, duration=%s"%(k,t_start,dura)
        

        # ---------------------------------
        # 1. instanciate, inititialize 
        H4E = kbtools.cHunt4Event('on_phase','my_H4E',t_join)

        # 2. re-inittialize
        H4E.reinit()
      
        # 3. process
        Source = Source_Stub('File1')
        H4E.process(Time, Value, Source)
      
        # 4. finish
        H4E.finish()
      
        # 5. read results -> table_array
        table_array = H4E.table_array()
        print "  -> calculated results: table_array:"
        for line in table_array:
            print "     ",line
              
        # ---------------------------------
        # check results
        for k,(t_start,dura) in enumerate(Expected):
            self.assertSequenceEqual((t_start,dura),(table_array[k+1][2],table_array[k+1][3] ),msg='%s event: %d'%(TestCaeName,k+1))
            
        print TestCaeName, "- end"
        
    #------------------------------------------------------------------------  
    def test_on_phase_TC001(self, TestCaeName="test_on_phase_TC001"): 
        '''
            basic functionality - no merging (t_join = 0.0)
        '''
               
        # parameters
        t_join  = 0
        
        # input vectors: create time axis and values
        Time  = np.array([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.])
        Value = np.array([0.,1.,0.,1.,0.,1.,0.,0.,0.,0., 0., 1., 1., 0.])
        
        # expected results: list of tupels: (t_start, duration) - t_start and duration are string literals
        Expected = [('1.00','1.00'),('3.00','1.00'),('5.00','1.00'),('11.00','2.00') ]
      
        self._abstract_test_case_on_phase(TestCaeName,Time,Value,Expected,t_join)        

        print "This is test_on_phase_TC001 - end" 
        
    #------------------------------------------------------------------------  
    def test_on_phase_TC002(self, TestCaeName="test_on_phase_TC002"): 
        '''
            test merging capabilities -> t_join = 2.0
        '''
                
        # parameters
        t_join  = 2.0
        
        # input vectors: create time axis and values
        Time  = np.array([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.])
        Value = np.array([0.,1.,0.,1.,0.,1.,0.,0.,0.,0., 0., 1., 1., 0.])
        
        # list of tupels: (t_start, duration)   - t_start and duration are string literals
        Expected = [('1.00','5.00'),('11.00','2.00') ]
      
        self._abstract_test_case_on_phase(TestCaeName,Time,Value,Expected,t_join)        
        
    #------------------------------------------------------------------------  
    def test_on_phase_TC003(self, TestCaeName="test_on_phase_TC003"): 
        '''
            active at start and until end - no mergin (t_join = 0.0)
        '''
              
        # parameters
        t_join  = 0
        
        # input vectors: create time axis and values
        Time  = np.array([0.,1.,2.,3.,4.,5.,6.,7.,8.,9.,10.,11.,12.,13.])
        Value = np.array([1.,1.,0.,1.,0.,1.,0.,0.,0.,0., 0., 1., 1., 1.])
        
        # list of tupels: (t_start, duration)   - t_start and duration are string literals
        Expected = [('0.00','2.00'),('3.00','1.00'),('5.00','1.00'),('11.00','2.00') ]
      
        self._abstract_test_case_on_phase(TestCaeName,Time,Value,Expected,t_join)        

       
    #------------------------------------------------------------------------  

    
#========================================================================================
if __name__ == "__main__":
  print 'unittest for hunt4event'
  unittest.main()
  

