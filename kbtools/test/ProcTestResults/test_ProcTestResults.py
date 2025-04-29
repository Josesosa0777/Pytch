"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\ProcTestResults.py
'''

import unittest
import os
import shutil

import kbtools

from xlrd import open_workbook



#========================================================================================
class TestSequenceFunctions(unittest.TestCase):

  def prepare(self):

    # define DebugResultsPath
    self.DebugResultsPath = r'results'

    # remove old generated files
    LocalPath = os.curdir
    self.FileNameResults             = os.path.join(LocalPath,"Results.txt")
    self.FileNameResultsConsolidated = os.path.join(LocalPath,"Results_Consolidated.txt")
    self.FileNameExcelTable          = os.path.join(LocalPath,'ResultTable.xls')
    if os.path.exists(self.FileNameResults):
      os.remove(self.FileNameResults)
    if os.path.exists(self.FileNameResultsConsolidated):
      os.remove(self.FileNameResultsConsolidated)
    if os.path.exists(self.FileNameExcelTable):
      os.remove(self.FileNameExcelTable)

    
    
    # todo: clean DebugResultsPath
    
  #------------------------------------------------------------------------  
  def read_Results_from_ExcelTable(self,FileNameExcelTable):
    ''' read number of passed and failed tests from Excel Table '''
    rb = open_workbook(FileNameExcelTable)
    try: 
      number_passed_tests = rb.sheet_by_name('Python-Overview').cell(0,2).value
    except:
      number_passed_tests = None
    try:  
      number_failed_tests = rb.sheet_by_name('Python-Overview').cell(0,4).value
    except:
      number_failed_tests = None    
    
    #print "pass/fail: ", number_passed_tests,"/",number_failed_tests
    return (number_passed_tests , number_failed_tests)

  #------------------------------------------------------------------------  
  def save_generated_files(self,DestFolder,FileNameList):
    
    if not os.path.exists(DestFolder):
      os.makedirs(DestFolder)
    
    for FileName in FileNameList:
       srcFile = FileName
       dstFile = os.path.join(DestFolder, os.path.basename(FileName))
       shutil.copyfile(srcFile,dstFile)
        

  #------------------------------------------------------------------------  
  def test_TC001(self): 
    ''' testsuites where all testcases will pass '''
  
  
    # --------------------------------------------------------------------------------------
    # start under clean and reproducable conditions
    self.prepare()
       
    
    # --------------------------------------------------------------------------------------
    # do the test: run batch
    os.system('run_test_batch_TC001.bat')
    
    # --------------------------------------------------------------------------------------
    # save generated for debug
    DestFolder = os.path.join(self.DebugResultsPath,'TC001')
    FileNameList = (self.FileNameResults,self.FileNameResultsConsolidated,self.FileNameExcelTable)
    self.save_generated_files(DestFolder,FileNameList)
    
    # --------------------------------------------------------------------------------------
    # check results
    Test_passed = True
    
    # check, that files are created
    if not os.path.exists(self.FileNameResults):             Test_passed = False
    if not os.path.exists(self.FileNameResultsConsolidated): Test_passed = False
    if not os.path.exists(self.FileNameExcelTable):          Test_passed = False

    # check contents of Excel Sheet
    if not self.read_Results_from_ExcelTable(self.FileNameExcelTable) == (2,None): Test_passed = False 
    
       
    # report results
    self.assertTrue(Test_passed) 

  #------------------------------------------------------------------------  
  def test_TC002(self): 
    ''' testsuites where some testcases will fail '''
    
    
    # --------------------------------------------------------------------------------------
    # start under clean and reproducable conditions
    self.prepare()
    
    # --------------------------------------------------------------------------------------
    # do the test: run batch
    ausgabe = os.system('run_test_batch_TC002.bat')
    
    # --------------------------------------------------------------------------------------
    # save generated for debug
    DestFolder = os.path.join(self.DebugResultsPath,'TC002')
    FileNameList = (self.FileNameResults,self.FileNameResultsConsolidated,self.FileNameExcelTable)
    self.save_generated_files(DestFolder,FileNameList)
    
    # --------------------------------------------------------------------------------------
    # check results
    Test_passed = True
    
    if not os.path.exists(self.FileNameResults):             Test_passed = False
    if not os.path.exists(self.FileNameResultsConsolidated): Test_passed = False
    if not os.path.exists(self.FileNameExcelTable):          Test_passed = False

    # check contents of Excel Sheet
    if not self.read_Results_from_ExcelTable(self.FileNameExcelTable) == (2,1): Test_passed = False 

       
    # report results
    self.assertTrue(Test_passed) 

    
    
#========================================================================================
if __name__ == "__main__":
  print 'unittest for ProcTestResults'
  unittest.main()
  

