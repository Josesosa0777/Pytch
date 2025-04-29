"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\scan4handles.py
'''

import unittest

import kbtools
import numpy as np


#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  def logical_test1(self,Handle,expected_results):
    real_results = kbtools.scan4handles(Handle)
    
    #self.print_results(Handle,real_results)
      
    return np.allclose(expected_results,real_results)

  def print_results(self,Handle,handle_list):
    print Handle
    print handle_list
    for idx_start, idx_stop in handle_list:
      print idx_start, idx_stop

  #------------------------------------------------------------------------  
  def test_TC001(self): 
    ''' good situation; zero at beginning and at end '''
    Handle = np.array([0,0,3,3,0,0,0,4,4,4,4,0])
    expected_results = np.array([[2, 3], [7, 10]])
    self.assertTrue(self.logical_test1(Handle,expected_results))

  def test_TC002(self): 
    ''' no zero at the end '''
    Handle = np.array([0,0,3,3,0,0,0,4,4,4,4])
    expected_results = np.array([[2, 3], [7, 10]])
    self.assertTrue(self.logical_test1(Handle,expected_results))

  def test_TC003(self): 
    ''' no zero at the start and the end '''
    Handle = np.array([3,3,0,0,0,4,4,4,4])
    expected_results = np.array([[0, 1], [5, 8]])
    self.assertTrue(self.logical_test1(Handle,expected_results))

  def test_TC004(self): 
    ''' no zero at all '''
    Handle = np.array([3,3,4,4,4,4])
    expected_results = np.array([[0, 1], [2, 5]])
    self.assertTrue(self.logical_test1(Handle,expected_results))

  def test_TC005(self): 
    ''' only one type of Handle '''
    Handle = np.array([4,4,4,4])
    expected_results = np.array([[0, 3]])
    self.assertTrue(self.logical_test1(Handle,expected_results))
  #------------------------------------------------------------------------  

    
#========================================================================================
if __name__ == "__main__":
  print 'unittest for scan4handles'
  unittest.main()
  

