"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\dcnvt3.py
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
    ''' topic: ugdiff
        expected results:  constant sampling rate
    '''
    dcnvt3 = kbtools.Cdcnvt3(verbose=True)
   
    
     
    
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for kb_io'
  unittest.main()
  



  
