"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest test_testsuite3.py
'''

import unittest



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):

  #------------------------------------------------------------------------  
  def test_TC001(self): 
    ''' testcase suppose to pass '''
    self.assertTrue(True)

  def test_TC002(self): 
    ''' testcase suppose to fail '''
    self.assertTrue(False)

  def test_TC003(self): 
    ''' testcase suppose to fail '''
    self.assertTrue(False)

  def test_TC004(self): 
    ''' testcase suppose to pass '''
    self.assertTrue(True)
   
  def test_TC005(self): 
    ''' testcase suppose to pass '''
    self.assertTrue(True)
  #------------------------------------------------------------------------  

    
#========================================================================================
if __name__ == "__main__":
  print 'testsuite1'
  unittest.main()
  

