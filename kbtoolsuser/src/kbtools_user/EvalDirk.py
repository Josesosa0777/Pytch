"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: DIRK evalulation '''

''' to be called by DAS_eval.py '''


'''
Signals:
  "DFM_red_button": ("DIRK", "DFM_red_button"),
  "DFM_green_button": ("DIRK", "DFM_green_button"),
  "DFM_Cnt_red_button": ("DIRK", "DFM_Cnt_red_button"),
  "DFM_Cnt_green_button": ("DIRK", "DFM_Cnt_green_button"),

'''

import os
import numpy as np

import kbtools
import kbtools_user
from scipy.signal import butter

# ==============================================================================================
class cEvalDirk():
    # ------------------------------------------------------------------------------------------
    def __init__(self):                # constructor
      self.myname = 'EvalDirk'         # name of this user specific evaluation
      self.H4E = {}                    # H4E hunt4event directory

    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
      pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
      
      
        self.src_dir_meas = conf_DAS_eval['src_dir_meas']
      
        print "EvalDirk::Init()"
          
        
        
      
        # ----------------------------------------------------------------------
        # LDWS outputs
        t_join = 1.0
        
        self.H4E['DFM_red_button']      = kbtools.cHunt4Event('on_phase','DFM red button',t_join)
        self.H4E['DFM_green_button']       = kbtools.cHunt4Event('on_phase','DFM green button',t_join)
      
      
        # ---------------------------------------------------------------
        # load events - required for "Report_Only"
        if load_event:
            for key in self.H4E.keys():
                self.H4E[key].load_event(key)
      
      
      
    
    # ------------------------------------------------------------------------------------------
    def reinit(self):          # recording interrupted
      for key in self.H4E.keys():
        self.H4E[key].reinit()



    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file

        print "============================================"
        print "EvalDirk::process()"
      
        Time_DFM_red_button,   DFM_red_button   = kbtools.GetSignal(Source, "DIRK", "DFM_red_button")
        Time_DFM_green_button, DFM_green_button = kbtools.GetSignal(Source, "DIRK", "DFM_green_button")

        self.H4E['DFM_red_button'].process(Time_DFM_red_button, DFM_red_button, Source)
        self.H4E['DFM_green_button'].process(Time_DFM_green_button, DFM_green_button, Source)
           
        print "end process - EvalDirk"
      
    # ------------------------------------------------------------------------------------------
    def finish(self):          # end of recording
        for key in self.H4E.keys():
            self.H4E[key].finish()
      
        # save events   
        for key in self.H4E.keys():
            self.H4E[key].save_event(key)
        

    # ------------------------------------------------------------------------------------------
    def report_init(self):     # prepare for report - input tex file to main
        self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
        pass  

    # ------------------------------------------------------------------------------------------
    def report(self):          # report events
        fill_table_array_into_report = True
        
        self.kb_tex.workingfile('%s.tex'%self.myname)
      
        self.kb_tex.tex('\n\\newpage\\section{EvalDirk}')
         
   
        # online ECU   
        self.kb_tex.tex('\n\\subsection{Dirk}')
        self.kb_tex.tex('\nDFM red button: %d entries; '% self.H4E['DFM_red_button'].n_entries_EventList())
        self.kb_tex.tex('\n \n\\medskip \n')
        self.kb_tex.tex('\nDFM green button: %d entries'% self.H4E['DFM_green_button'].n_entries_EventList())
        if fill_table_array_into_report:
            label = self.kb_tex.table(self.H4E['DFM_red_button'].table_array())
            label = self.kb_tex.table(self.H4E['DFM_green_button'].table_array())
      
        self.kb_tex.tex('\n \n\\bigskip \nEvalDirk-finished')
      
     
    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        print "excel_export"
        print "src_dir_meas :",os.path.basename(self.src_dir_meas)
        
        # switches
        # add partial_brake and emergency_brake spreadsheets
        braking_spreadsheets = False

        # new format 
        AddColsFormat = {}
             
        WriteExcel = kbtools.cWriteExcel()

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # AEBS_warning, AEBS_partial_brake, AEBS_emergency_brake
        
        # ---------------------------------------------------
        # online
        AddCols_online = []
        WriteExcel.add_sheet_out_table_array('DFM_red_button',self.H4E['DFM_red_button'].table_array2(AddCols_online,AddColsFormat))
        
        AddCols_online = []
        WriteExcel.add_sheet_out_table_array('DFM_green_button',self.H4E['DFM_green_button'].table_array2(AddCols_online,AddColsFormat))
       
 
        # -------------------------------------------------
        # write Excel file
        ExcelFilename = "EvalDirk_results.xls"
        if self.src_dir_meas is not None:
            ExcelFilename = "EvalDirk_results_%s.xls"%os.path.basename(self.src_dir_meas) 
        WriteExcel.save(ExcelFilename)
       
      
        
        
        print "excel_export() finish"
      
#-------------------------------------------------------------------------      









