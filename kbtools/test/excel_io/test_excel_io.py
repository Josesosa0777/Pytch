"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''
Unittest for dataeval\lib\kbtools\excel_io.py
'''

import numpy as np
#import matplotlib.pyplot as plt

import unittest
#import os

import kbtools

import xlwt 
import xlrd 

#========================================================================================
class TestSequenceFunctions(unittest.TestCase):
  
    #------------------------------------------------------------------------  
    def test_TC001(self):
        ''' topic: kbtools.cWriteExcel() -> test of method
            expected results:  
        '''
        
        ExcelFilename = 'text_excel.xls'
        SheetName = 'Table1'
    
        # -------------------------------------
        WriteExcel = kbtools.cWriteExcel()
    
        
        ws = WriteExcel.wb.add_sheet(SheetName)
    
        style = xlwt.easyxf('font: name BETEX')
    
        # writing to Excel spreadsheet with method ws_write() in different variations:
        #                  k, ColNr, ColData, expected result
        variation_list = [(0,0,1.5,                                 1.5),           # floating point number
                          (0,1,np.inf,                              "NA"),            # floating point number - inifinity
                          (0,2,np.nan,                              "NA"),            # floating point number - nan
                          (0,3,"Test Test 1,5",                     "Test Test 1,5"), # string
                          (0,4,np.array([np.inf]).astype(np.float64)[0], "NA"),       # floating point number - inifinity
                          (0,5,np.array([np.nan]).astype(np.float64)[0], "NA"),       # floating point number - nan
                          
                          ]
        
        for (k, ColNr, ColData,_) in  variation_list:
            print k, ColNr, ColData
            WriteExcel.ws_write(ws,k,ColNr, ColData, style)

        # -------------------------------------
        # save Excel spreadsheet  
        WriteExcel.save(ExcelFilename)
    
        # -------------------------------------
        # reading and asserting
        rb = xlrd.open_workbook(ExcelFilename)
        
        for (k, ColNr, ColData,expected_result) in  variation_list:
            self.assertEqual(rb.sheet_by_name(SheetName).cell(k,ColNr).value, expected_result, msg="")
            

        
              
    
#============================================================================================
# main
#============================================================================================
#========================================================================================
if __name__ == "__main__":
    print 'unittest for excel_io'
    unittest.main()
  



  
