"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\DAS_eval.py
'''

# python standard imports
import unittest
import shutil
import os
import time
import sys


# home library
import kbtools

  
# ------------------------------------------------------------
# test data 

# measurement file

# path to original location of test data
testdata_dir_src  = r'..\..\..\testdata'

# file with test data (mdf format)
testdata_FileName = r'CVR3_B1_2011-02-10_16-53_020.mdf'



#========================================================================================
# helper functions
def create_local_copy_of_testdata(testdata_dir_dest):
  # create a local copy of the testdata, because we want to keep the testdata dictiornary untouched
  
  if not os.path.isdir(testdata_dir_dest):
    os.makedirs(testdata_dir_dest) 
  shutil.copyfile(os.path.join(testdata_dir_src,testdata_FileName),os.path.join(testdata_dir_dest,testdata_FileName))

def delete_dir(PathName): 
  # delete directory 
  if os.path.isdir(PathName):
    shutil.rmtree(PathName)
  if os.path.isdir(PathName):
    # remove was not successful
    return False
  return True
  
  



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  #------------------------------------------------------------------------  
  def test_TC001(self): 
    ''' call DAS_eval step1 with default configuration file (no file specified) '''

    # path to local copy of test data
    local_testdata_dir = r'testdata01'
    MyNpyHomeDir       = r'MyNpyHomeDir'
    ReportStep1Dir     = r'report_step1'
    EventDir           = r'Event'
    
    print "test_TC001"
    print 
    # --------------------------------------------------------------------------------------
    # step1: prepare test environment
      
    # step 1.1 clean up old stuff -> remove local_testdata_dir
    self.assertTrue(delete_dir(local_testdata_dir))
    self.assertTrue(delete_dir(MyNpyHomeDir))  
    self.assertTrue(delete_dir(ReportStep1Dir))  
    self.assertTrue(delete_dir(EventDir))  
      
    # step 1.2 create a local copy of 
    create_local_copy_of_testdata(local_testdata_dir)

    # --------------------------------------------------------------------------------------
    # step 2: conduct real test case
    try:
      tic = time.clock()

      kbtools.cDAS_eval().step1()

      toc = time.clock()
      print "processing kbtools.cDAS_eval().step1() -> elapsed time: ", toc-tic
      print

      self.assertTrue(True)
 
    except:
      self.assertTrue(False)

  #------------------------------------------------------------------------  
  def test_TC002(self): 
    ''' call DAS_eval step1 with specific configuration file    ''' 
    
    # path to local copy of test data
    local_testdata_dir = r'testdata01'
    MyNpyHomeDir       = r'MyNpyHomeDir'
    ReportStep1Dir     = r'report_step1'
    EventDir           = r'Event'

    print "test_TC002"
    print 
    # --------------------------------------------------------------------------------------
    # step1: prepare test environment
      
    # step 1.1 clean up old stuff -> remove local_testdata_dir
    self.assertTrue(delete_dir(local_testdata_dir))
    self.assertTrue(delete_dir(MyNpyHomeDir))  
    self.assertTrue(delete_dir(ReportStep1Dir))  
    self.assertTrue(delete_dir(EventDir))  
      
      
    # step 1.2 create a local copy of 
    create_local_copy_of_testdata(local_testdata_dir)

    # --------------------------------------------------------------------------------------
    # step 2: conduct real test case
    try:
      FileName = 'specific.txt'
      
      # create a specific file
      shutil.copyfile('conf_DAS_eval_step1.txt',FileName)
      
      tic = time.clock()

      # specific configuration file
      kbtools.cDAS_eval().step1(FileName)
      
      toc = time.clock()
      print "processing kbtools.cDAS_eval().step1() -> elapsed time: ", toc-tic
      print

      self.assertTrue(True)
    except:
      self.assertTrue(False)

  #------------------------------------------------------------------------  
  def test_TC003(self): 
    ''' load configuration file first and deliver it as dictionary to call DAS_eval step1    ''' 
    
    # path to local copy of test data
    local_testdata_dir = r'testdata01'
    MyNpyHomeDir       = r'MyNpyHomeDir'
    ReportStep1Dir     = r'report_step1'
    EventDir           = r'Event'

    
    print "test_TC003"
    print 
    # --------------------------------------------------------------------------------------
    # step1: prepare test environment
      
    # step 1.1 clean up old stuff -> remove local_testdata_dir
    self.assertTrue(delete_dir(local_testdata_dir))
    self.assertTrue(delete_dir(MyNpyHomeDir))  
    self.assertTrue(delete_dir(ReportStep1Dir))  
    self.assertTrue(delete_dir(EventDir))  

    # step 1.2 create a local copy of 
    create_local_copy_of_testdata(local_testdata_dir)

    # --------------------------------------------------------------------------------------
    # step 2: conduct real test case
    try:
      ConfigFileNameStep1 = 'conf_DAS_eval_step1.txt'

      # load contents of configuration file into a dictionary
      cfg_dict = kbtools.read_input_file('tag_only',ConfigFileNameStep1)

      tic = time.clock()

      # deliver dictonary as input for DAS_eval step1
      kbtools.cDAS_eval().step1(cfg_dict)
      
      toc = time.clock()
      print "processing kbtools.cDAS_eval().step1() -> elapsed time: ", toc-tic
      print
      
      
      self.assertTrue(True)
    except:
      self.assertTrue(False)

      
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
  print 'unittest for DAS_eval'
  
  # add local kbtools_user package to start of Python's search path
  sys.path.insert(0, 'kbtools_user')
  
  # run unittest
  unittest.main()
  
  



  
