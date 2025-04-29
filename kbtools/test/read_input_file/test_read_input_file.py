"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\read_input_file.py
'''

import unittest
import os

import kbtools



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  #------------------------------------------------------------------------  
  def test_TC001(self):
    ''' topic:            file to read doesn't exist 
        expected results: read_input_file shall return None
    '''
    FileName = 'no_spam.txt'

    # be sure file doesn't exist
    if os.path.exists(FileName): os.remove(FileName)

    # try to read the file
    contents = kbtools.read_input_file('tag_only',FileName)
    
    # check results
    Test_passed = True
    if not (None==contents):
      Test_passed = False
    
    # report results
    self.assertTrue(Test_passed) 

  #------------------------------------------------------------------------  
  def test_TC002(self): 
    ''' topic: check basic functionality
          - comments #, %, ;
          - tokens with only one occurrence
          - tokens with multiple occurrence
        expected results:
          - comments have to be ignored
          - a token with only one occurrence creates an entry in the returned dictionary
          - a token with multiple occurrence creates a list as entry in the returned dictionary 
    '''    
        
    FileName = 'spam.txt'
    
    # clean up before start working
    if os.path.exists(FileName): os.remove(FileName)
    
    # create file to read
    f = open(FileName,'w')
    f.write('# this is a comment \n')
    f.write('% this is a comment \n')
    f.write('; this is a comment \n')
    f.write('spam1 = egg1 \n')            # tokens with only one occurrence
    f.write('spam2 = egg2.1 \n')          # token with multiple occurrence
    f.write('spam2 = egg2.2 \n')
    f.write('spam2 = egg2.3 \n')
    f.write('spam3 = egg3 \n')            # tokens with only one occurrence
    f.write('spam4 = egg4.1 \n')          # token with multiple occurrence
    f.write('spam4 = egg4.2 \n')
    f.write('spam4 = egg4.3 \n')
    f.write('spam5 = egg5 \n')            # tokens with only one occurrence
    f.write('spam6 = egg6=6.1 \n')        # value contain a '=' sign
    f.write('spam7 = egg7=7==7 =\n')      # value contain multiple '=' signs
    f.close()
    
    # read file 
    contents = kbtools.read_input_file('tag_only',FileName)
    
    # check results
    self.assertEqual(contents['spam1'],    'egg1')
    self.assertEqual(contents['spam2'][0], 'egg2.1')
    self.assertEqual(contents['spam2'][1], 'egg2.2')
    self.assertEqual(contents['spam2'][2], 'egg2.3')
    self.assertEqual(contents['spam3'],    'egg3')
    self.assertEqual(contents['spam4'][0], 'egg4.1')
    self.assertEqual(contents['spam4'][1], 'egg4.2')
    self.assertEqual(contents['spam4'][2], 'egg4.3')
    self.assertEqual(contents['spam5'],    'egg5')
    self.assertEqual(contents['spam6'],    'egg6=6.1')
    self.assertEqual(contents['spam7'],    'egg7=7==7 =')
    
    
   
  
  
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for read_input_file'
  unittest.main()
  



  
