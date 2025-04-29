"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""


import os
import kbtools

# ============================================================================================
if __name__ == "__main__":  

  LocalPath = os.curdir
  
  # input file
  FileNameResults             = os.path.join(LocalPath,"Results.txt")
  # generated files
  FileNameResultsConsolidated = os.path.join(LocalPath,"Results_Consolidated.txt")
  FileNameExcelTable          = os.path.join(LocalPath,'ResultTable.xls')
  
  # remove old generated files
  if os.path.exists(FileNameResultsConsolidated):
    os.remove(FileNameResultsConsolidated)
  if os.path.exists(FileNameExcelTable):
    os.remove(FileNameExcelTable)
    
  # generate new files
  kbtools.cProcTestResults(FileNameResults,FileNameResultsConsolidated,FileNameExcelTable)

    
