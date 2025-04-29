'''
   
   excel input output
     
   Ulrich Guecker 
   
   2013-07-31
   2012-11-30
   
'''

import xlwt 
import os
import gc

from datetime import datetime

from xlrd import open_workbook

import numpy as np

#========================================================================================
def ReadExcelWorkbook(FileName, extended_output = False, return_list_of_sheets = False, verbose=False):
    # read Excel Workbook
    # return dict: [sheet][column]
    
    if verbose:
        print "ReadExcelWorkbook"
    
    list_xls = {}
    headings_xls = {}
    
  
    rb = open_workbook(FileName)
    list_of_sheets = rb.sheet_names()

    for sheet in list_of_sheets: 
    
        if verbose:
            print "sheet", sheet
            print "ncols, nrows", rb.sheet_by_name(sheet).ncols, rb.sheet_by_name(sheet).nrows
            
            
            
        list_xls[sheet] = []
        
        # headings_xls
        headings_xls[sheet] = []
        for k_col in xrange(0,rb.sheet_by_name(sheet).ncols):
            headings_xls[sheet].append(rb.sheet_by_name(sheet).cell(0,k_col).value)
            
        # list_xls
        for k_row in xrange(1,rb.sheet_by_name(sheet).nrows):
            tmp_dict = {} 
            for k_col in xrange(0,rb.sheet_by_name(sheet).ncols):
                tmp_dict[rb.sheet_by_name(sheet).cell(0,k_col).value] = rb.sheet_by_name(sheet).cell(k_row,k_col).value
            list_xls[sheet].append(tmp_dict)
    
    if not return_list_of_sheets:
        if extended_output:    
            return list_xls, headings_xls 
        else:
            return list_xls
    else:
        if extended_output:    
            return list_xls, headings_xls, list_of_sheets 
        else:
            return list_xls, list_of_sheets
    
#========================================================================================
def CreateActionListFromExcel(FileName,EnableRowNamesList=["Enable1"], DictOfSheets = False, verbose=False):
    
    if verbose:
        print "CreateActionListFromExcel:", 
        print "FileName",FileName
        print "EnableRowNamesList", EnableRowNamesList
        print "DictOfSheets", DictOfSheets
     
    list_xls, list_of_sheets  = ReadExcelWorkbook(FileName, return_list_of_sheets = True)

   
    if verbose:
        print "list_of_sheets", list_of_sheets
        print "list_xls", list_xls
      
  
    if DictOfSheets:
        out = {}            # return a dictionary of lists - keys of dictionary are the sheets in th Action List
    else:    
        out = []            # return a list 
    
    
    # ---------------------------------------------
    for sheet in list_of_sheets:
        if verbose:
            print "Sheet",sheet, type(sheet)
    
        list_per_sheet = []
        for n_row, row in enumerate(list_xls[sheet]):
            row['***sheet'] = sheet
            if verbose:
                print n_row, row
            if EnableRowNamesList:
                cond = True
                for EnableRowName in EnableRowNamesList:
                    if EnableRowName in row:
                        #print "row[EnableRowName]", row[EnableRowName]
                        if not (cond and ("x" == row[EnableRowName].lower())):
                            cond = False
                            break
                    else:
                        # EnableRowName is not available
                        cond = False
                #print "cond", cond        
                if cond:
                    list_per_sheet.append(row)  
            else:
                # empty list
                list_per_sheet.append(row)    
        # print "list_per_sheet", list_per_sheet
    
        if DictOfSheets:
            out[sheet] = list_per_sheet
        else:
            out += list_per_sheet    
        
    
    # ---------------------------------------------
    if DictOfSheets:
        return  out, list_of_sheets
    else:
        return  out
  
  
#========================================================================================
def show_list_xls(list_xls):

  for sheet in list_xls.keys():
    print "Sheet",sheet
    for n_row, row in enumerate(list_xls[sheet]):
      print n_row
      for col_name in row.keys():
        print "  ",col_name,":",row[col_name]
  
#========================================================================================
def create_action_files(list_xls):
  for sheet in list_xls.keys():
    for n_row, row in enumerate(list_xls[sheet]):
      if row.has_key('Enable') and 'x' == row['Enable'].lower():
        out_file = open(row['File']+'.txt',"w")
        out_file.write("par1 = %s\n"%row['Par1'])
        out_file.write("par2 = %s\n"%row['Par2'])
        out_file.close() 
  
  



#-------------------------------------------------  
def createMyExcelFile(Headings, DataList={}, Formats={}, DataLineNumbers=False, FileName=r'MyExcel.xls'):  
  # Excel Sheet  

  # Define styles 
  style_heading = xlwt.easyxf('font: name BETEX, bold on')
  style0 = xlwt.easyxf('font: name BETEX')
  style1 = xlwt.easyxf('font: name BETEX',num_format_str='YYYY-MM-DD HH:MM:SS')
  
  # if requested first column is 'No.'
  if DataLineNumbers:
    Headings.insert(0, 'Number')
  
  # create Excel Workbook
  wb = xlwt.Workbook()
  
  # create sheet in this Excel Workbook
  ws = wb.add_sheet('Test Cases')

  # heading
  for ColNr, ColName in enumerate(Headings):
    ws.write(0, ColNr, ColName, style_heading)
  
  # fill in data  
  for k, Data in enumerate(DataList):
    k +=1   # heading are already in the first row
    for ColNr, ColName in enumerate(Headings):
      if 'Number' == ColName:
        ws.write(k, ColNr, "%3d. "%k, style0)
      else: 
        if Formats.has_key(ColName):      
          ws.write(k, ColNr, Formats[ColName]%Data[ColName], style0)
        else:
          ws.write(k, ColNr, Data[ColName], style0)
         
    
  # create another sheet  
  ws = wb.add_sheet('created by')
  
  ws.write(0, 0, 'created by', style0)
  ws.write(0, 1,  os.path.basename(__file__) , style1)

  ws.write(1, 0, 'created on', style0)
  ws.write(1, 1, datetime.now(), style1)
  
  # save Excel sheet
  wb.save(FileName)
  
#--------------------------------------------------------------------------------------------------
class cWriteExcel():

    def __init__(self):
        
        # create Excel Workbook
        self.wb = xlwt.Workbook()
        
        # DefaultStyleStr
        self.DefaultStyleStr='font: name BETEX'

        # Define styles 
        self.style_heading = xlwt.easyxf('font: name BETEX, bold on')
        self.style0        = xlwt.easyxf('font: name BETEX')
        self.style1        = xlwt.easyxf('font: name BETEX',num_format_str='YYYY-MM-DD HH:MM:SS')
        
        self.style_dic = {}
  
    # ----------------------------------------------
    def add_sheet(self,SheetName,Headings = [], DataList = {}, Formats = {},DataLineNumbers=False):
    
        print "SheetName", SheetName
    
        # create sheet in this Excel Workbook
        ws = self.wb.add_sheet(SheetName)

        # if requested first column is 'No.'
        if DataLineNumbers:
           Headings.insert(0, 'Number')
    
       
    
        # heading
        for ColNr, ColName in enumerate(Headings):
            ws.write(0, ColNr, ColName, self.style_heading)
  
        # fill in data  
        for k, Data in enumerate(DataList):
            k +=1   # heading are already in the first row
            for ColNr, ColName in enumerate(Headings):
              if 'Number' == ColName:
                  ws.write(k, ColNr, "%3d. "%k, self.style0)
              else: 
                if Formats.has_key(ColName):      
                    if isinstance(Formats[ColName], (list, tuple)):
                       if Formats[ColName][0] == "ExcelNumFormat":
                          ws.write(k, ColNr, Data[ColName], xlwt.easyxf(self.DefaultStyleStr,num_format_str=Formats[ColName][1]))
                       else:
                          print "error in  add_sheet()"
                    else:
                        ws.write(k, ColNr, Formats[ColName]%Data[ColName], self.style0)
                    
                else:
                    ws.write(k, ColNr, Data[ColName], self.style0)
    
    # ----------------------------------------------
    def ws_write(self,ws,k,ColNr, ColData, style):
        
        tmp_ColData = ColData
        
        if isinstance(ColData,(float, np.float64,np.float32)):
            if np.isinf(ColData) or np.isnan(ColData):
                ws.write(k, ColNr, "NA", style)
                return
        
        try:
           ws.write(k, ColNr, tmp_ColData, style)
        except:
           ws.write(k, ColNr, tmp_ColData.astype(np.float64), style)
           
    
    # ----------------------------------------------
    def add_sheet_out_table_array(self,SheetName,out_table_array):
        
        Headings = out_table_array[0]
        DataList = out_table_array[1:]   
        
        # create sheet in this Excel Workbook
        ws = self.wb.add_sheet(SheetName)

        # heading
        for ColNr, ColName in enumerate(Headings):
            ws.write(0, ColNr, ColName, self.style_heading)
  
        # fill in data  
        print "add_sheet_out_table_array():"
        print "  SheetName: <%s>"%SheetName
        print "  len(DataList): %d"%len(DataList)
        collected = gc.collect()
        print "Garbage collector: collected %d objects." % (collected)

        
        for k, Data in enumerate(DataList):
            k +=1   # heading are already in the first row
            for ColNr, ColData in enumerate(Data):
                if isinstance(ColData, (list, tuple)):
                    # ColData = (("ExcelNumFormat", '##0.0 "s"'),Event['t_start']),
                    if ColData[0][0] == "ExcelNumFormat":
                        if ColData[0][1] not in self.style_dic:
                            self.style_dic[ColData[0][1]] = xlwt.easyxf(self.DefaultStyleStr,num_format_str=ColData[0][1])
                        #print "k, ColNr, ColData[1]:", k, ColNr, ColData[1],type(ColData[1])
                        
                        #if isinstance(ColData[1],(np.uint8)):
                        #else:
                        '''
                        try:    
                            ws.write(k, ColNr, ColData[1], self.style_dic[ColData[0][1]])
                        except:
                            # ColData[1] is of type np.uint8, np.uint16 etc.
                            ws.write(k, ColNr, ColData[1].astype(np.float64), self.style_dic[ColData[0][1]])
                        '''
                        self.ws_write(ws,k,ColNr, ColData[1], self.style_dic[ColData[0][1]])
                        
                    else:
                        print "error in  add_sheet()"   
                else: 
                    '''                
                    try:    
                       # ColData = Event['description']
                       ws.write(k, ColNr, ColData, self.style0)
                    except: 
                       ws.write(k, ColNr, ColData.astype(np.float64), self.style0)
                    '''
                    self.ws_write(ws,k,ColNr, ColData, self.style0)
   
            if (k%100)==0:
                print "ws.flush_row_data()"
                ws.flush_row_data()
   
        print "ws.flush_row_data()"
        ws.flush_row_data()  
   
   
    # ----------------------------------------------
    def add_sheet_created_by(self):
        # create another sheet  
        ws = self.wb.add_sheet('created by')
  
        ws.write(0, 0, 'created by', self.style0)
        ws.write(0, 1,  os.path.basename(__file__) , self.style1)

        ws.write(1, 0, 'created on', self.style0)
        ws.write(1, 1, datetime.now(), self.style1)

    # ----------------------------------------------
    def save(self,FileName=r'MyExcel.xls'):
        print "save Excel sheet",FileName
        collected = gc.collect()
        print "Garbage collector: collected %d objects." % (collected)
        # save Excel sheet
        self.wb.save(FileName)
         

