"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' class for processing test results'''
''' 
    step1:  Results -> ResultsConsolidated
    step2:  ResultsConsolidated -> ExcelTable
'''

import os
from xlwt import *

# from win32com.client import Dispatch  

class cProcTestResults():
  def __init__(self,FileNameResults,FileNameResultsConsolidated,FileNameExcelTable):
    self.FileNameResults             = FileNameResults
    self.FileNameResultsConsolidated = FileNameResultsConsolidated
    self.FileNameExcelTable          = FileNameExcelTable

    self.run()
    
  def run(self):

    #step1:  Results -> ResultsConsolidated
    self.ExtractResult(self.FileNameResults, self.FileNameResultsConsolidated)
    
    #step2:  ResultsConsolidated -> ExcelTable
    self.CreateExceltable(self.FileNameResultsConsolidated,self.FileNameExcelTable)
    
    
  def ExtractResult(self,FileNameResults, FileNameResultsConsolidated):
    ''' Creating a consolidated results text file. '''
    '''
      input arguments:
         FileNameResults             - file to be read
         FileNameResultsConsolidated - file to be created
    '''
    
    newfile = open(FileNameResultsConsolidated, "w+")
    file    = open(FileNameResults, "r")
    lineno = 0
    start = ["tests", "Ran", "OK", ".F"]
    for line in file:
        lineno = lineno + 1
        line = line.strip()
        if (line.startswith("tests") or line.startswith("Ran") or line.startswith("Test")):
            newfile.write(line)
            newfile.write("\n")
        elif line.startswith("OK"):
            newfile.write(line)
            newfile.write("\n")
            newfile.write("++++++++++++++++++++++++++++")
            newfile.write("\n")
        elif line.startswith("FAILED"):
            newfile.write(line)
            newfile.write("\n")
            newfile.write("++++++++++++++++++++++++++++")
            newfile.write("\n")
            pass
        
    if EOFError:
        newfile.write("\n")
        newfile.write("++++++++++++++++++++++++++++")
        newfile.write("\n")
        newfile.write("Consolidated result entry skimmed from Results.txt")
        newfile.close()
            
            
  def CreateExceltable(self,FileNameResultsConsolidated,FileNameExcelTable):
    ''' Creating an excel table with consolidated results. '''
    ''' input arguments:
          FileNameResultsConsolidated - file to be read
          FileNameExcelTable          - file to be created
    '''
    
    # create a new workbook
    workBookNew = Workbook()
    workSheet1 = workBookNew.add_sheet("Python-Overview")
    workSheet2 = workBookNew.add_sheet("Python-ResultTable")
  
    #write data
    newFont = Font()
    newFont.name = 'BETEX'
    newFont.bold = True
    style = XFStyle()
    style.font =newFont
    workSheet2.write(0,0,'Test Name', style)
    workSheet2.write(0,1,'No.of tests',style)
    workSheet2.write(0,2,'Test Result', style)
    fromfile = open(FileNameResultsConsolidated, "r")
    j = 1
    k = 1
    testFailed = 0
    testPassed = 0
    # Change the width 
    for line in fromfile:
      if (line.startswith("tests")):
        char = line.strip()
        workSheet2.write(j,0,char[10:])
        workSheet2.col(0).width = 5000
      elif(line.startswith("Ran")):
        char = line.strip()
        workSheet2.write(k,1,char[4:6])
        k += 1
      elif(line.startswith("OK") or line.startswith("FAILED")):
        if (line.startswith("OK")):
            workSheet2.write(j,2,"Passed",easyxf('pattern: pattern solid, fore_colour green;'))
            testPassed += 1
        elif(line.startswith("FAILED")):
            workSheet2.write(j,2,"Failed",easyxf('pattern: pattern solid, fore_colour red;'))
            testFailed += 1
        j += 1
    workSheet1.write(0,0,"Number of Tests",style)
    workSheet1.write(0,1,"Passed:",easyxf('pattern: pattern solid, fore_colour green;'))
    workSheet1.write(0,2,testPassed,easyxf('pattern: pattern solid, fore_colour green;')) 
    if testFailed==0:
        pass
    else:
      workSheet1.write(0,3,"Failed:",easyxf('pattern: pattern solid, fore_colour red;'))
      workSheet1.write(0,4,testFailed,easyxf('pattern: pattern solid, fore_colour red;'))
    workSheet1.col(0).width = 5000
    print "Open %s for Intermittent results "%FileNameResultsConsolidated
    print "Open %s for post processing "%FileNameExcelTable
    workBookNew.save(FileNameExcelTable)

#--------------------------------------------------------------------------------------------------------------
# def autofilter():
  # xl = Dispatch("Excel.Application")  
  # xl.Workbooks.Open("C:/util_DAS/python/dataeval/testsuite/kbtools/ResultTable.xls")  
  # xl.ActiveWorkbook.ActiveSheet.Columns(1).AutoFilter(1) 
  # xl.ActiveWorkbook.Close(SaveChanges=1) # 1 is True, 0 is False  
  # xl.Quit()  

# ============================================================================================
if __name__ == "__main__":  

  LocalPath = os.curdir
  
  FileNameResults             = os.path.join(LocalPath,"Results.txt")
  FileNameResultsConsolidated = os.path.join(LocalPath,"Results_Consolidated.txt")
  FileNameExcelTable          = os.path.join(LocalPath,'ResultTable.xls')
    
  myProcTestResults = cProcTestResults(FileNameResults,FileNameResultsConsolidated,FileNameExcelTable)
  
  myProcTestResults.run()
  pass
