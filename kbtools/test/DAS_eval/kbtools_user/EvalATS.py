"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: ATS evalulation '''

''' to be called by DAS_eval.py '''

# imports
import sys
import os
import numpy as np

# Utilities_DAS specific imports
import kbtools


# ==============================================================================================
class cEvalATS():
    # ------------------------------------------------------------------------------------------
    def __init__(self):       # constructor
      self.myname = 'EvalATS'        # name of this user specific evaluation
      self.H4E = {}                  # H4E hunt4event directory


    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
      pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder):     # general start
       
      t_join = 0 
      
      # LRR3 - ACC Target Selection Objects 0 .. 4
      self.H4E['LRR3_ATS0'] = kbtools.cHunt4Event('on_phase','LRR3 ATS0',t_join)
      self.H4E['LRR3_ATS1'] = kbtools.cHunt4Event('on_phase','LRR3 ATS1',t_join)
      self.H4E['LRR3_ATS2'] = kbtools.cHunt4Event('on_phase','LRR3 ATS2',t_join)
      self.H4E['LRR3_ATS3'] = kbtools.cHunt4Event('on_phase','LRR3 ATS3',t_join)
      self.H4E['LRR3_ATS4'] = kbtools.cHunt4Event('on_phase','LRR3 ATS4',t_join)

      # ATS4 (stationary) object present but no ATS0 object
      self.H4E['LRR3_ATS4_no_ATS0'] = kbtools.cHunt4Event('on_phase','LRR3 ATS4 no ATS0',t_join)

      
      # CVR3 - ACC Target Selection Objects 0 .. 4
      self.H4E['CVR3_ATS0'] = kbtools.cHunt4Event('on_phase','CVR3 ATS0',t_join)
      self.H4E['CVR3_ATS1'] = kbtools.cHunt4Event('on_phase','CVR3 ATS1',t_join)
      self.H4E['CVR3_ATS2'] = kbtools.cHunt4Event('on_phase','CVR3 ATS2',t_join)
      self.H4E['CVR3_ATS3'] = kbtools.cHunt4Event('on_phase','CVR3 ATS3',t_join)
      self.H4E['CVR3_ATS4'] = kbtools.cHunt4Event('on_phase','CVR3 ATS4',t_join)

      # ATS4 (stationary) object present but no ATS0 object
      self.H4E['CVR3_ATS4_no_ATS0'] = kbtools.cHunt4Event('on_phase','CVR3 ATS4 no ATS0',t_join)

    # ------------------------------------------------------------------------------------------
    def reinit(self):          # recording interrupted
      for key in self.H4E.keys():
        self.H4E[key].reinit()

    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file
      
      # ---------------------------------------  
      # LRR3 ATS Object
      device = 'ECU-0-0'

      try:    
    
        # Handle != 0
        Time, Value_ATS0 = Source.getSignal(device, "ats.Po_T20.PO.i0.Handle")
        self.H4E['LRR3_ATS0'].process(Time, (Value_ATS0>0), Source)

        Time, Value_ATS1 = Source.getSignal(device, "ats.Po_T20.PO.i1.Handle")
        self.H4E['LRR3_ATS1'].process(Time, (Value_ATS1>0), Source)

        Time, Value_ATS2 = Source.getSignal(device, "ats.Po_T20.PO.i2.Handle")
        self.H4E['LRR3_ATS2'].process(Time, (Value_ATS2>0), Source)

        Time, Value_ATS3 = Source.getSignal(device, "ats.Po_T20.PO.i3.Handle")
        self.H4E['LRR3_ATS3'].process(Time, (Value_ATS3>0), Source)

        Time, Value_ATS4 = Source.getSignal(device, "ats.Po_T20.PO.i4.Handle")
        self.H4E['LRR3_ATS4'].process(Time, (Value_ATS4>0), Source)
      
        # ATS0 Handle == 0 and ATS4 Handle != 0
        self.H4E['LRR3_ATS4_no_ATS0'].process(Time, np.logical_and (Value_ATS0==0, Value_ATS4>0), Source)
        
      except:
        pass
        
      # ---------------------------------------      
      # CVR3 ATS Object
      device = 'MRR1plus-0-0'

      try:
      
        # Handle != 0
        Time, Value_ATS0 = Source.getSignal(device, "ats.Po_T20.PO.i0.Handle")
        self.H4E['CVR3_ATS0'].process(Time, (Value_ATS0>0), Source)

        Time, Value_ATS1 = Source.getSignal(device, "ats.Po_T20.PO.i1.Handle")
        self.H4E['CVR3_ATS1'].process(Time, (Value_ATS1>0), Source)

        Time, Value_ATS2 = Source.getSignal(device, "ats.Po_T20.PO.i2.Handle")
        self.H4E['CVR3_ATS2'].process(Time, (Value_ATS2>0), Source)

        Time, Value_ATS3 = Source.getSignal(device, "ats.Po_T20.PO.i3.Handle")
        self.H4E['CVR3_ATS3'].process(Time, (Value_ATS3>0), Source)

        Time, Value_ATS4 = Source.getSignal(device, "ats.Po_T20.PO.i4.Handle")
        self.H4E['CVR3_ATS4'].process(Time, (Value_ATS4>0), Source)
      
        # ATS0 Handle == 0 and ATS4 Handle != 0
        self.H4E['CVR3_ATS4_no_ATS0'].process(Time, np.logical_and (Value_ATS0==0, Value_ATS4>0), Source)
      except:
        pass
      
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
      self.kb_tex.workingfile('%s.tex'%self.myname)
      
      # Eval ATS - main section
      self.kb_tex.tex('\n\\newpage\\section{EvalATS}')
      
      # LRR3 ATS
      self.kb_tex.tex('\n\\subsection{LRR3 - ATS}')
 
      self.kb_tex.tex('\n\\subsubsection{ATS0}')
      label = self.kb_tex.table(self.H4E['LRR3_ATS0'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS1}')
      label = self.kb_tex.table(self.H4E['LRR3_ATS1'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS2}')
      label = self.kb_tex.table(self.H4E['LRR3_ATS2'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS3}')
      label = self.kb_tex.table(self.H4E['LRR3_ATS3'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS4}')
      label = self.kb_tex.table(self.H4E['LRR3_ATS4'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS4 no ATS0}')
      label = self.kb_tex.table(self.H4E['LRR3_ATS4_no_ATS0'].table_array())

      
      # CVR3 ATS
      self.kb_tex.tex('\n\\subsection{CVR3 - ATS}')
 
      self.kb_tex.tex('\n\\subsubsection{ATS0}')
      label = self.kb_tex.table(self.H4E['CVR3_ATS0'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS1}')
      label = self.kb_tex.table(self.H4E['CVR3_ATS1'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS2}')
      label = self.kb_tex.table(self.H4E['CVR3_ATS2'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS3}')
      label = self.kb_tex.table(self.H4E['CVR3_ATS3'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS4}')
      label = self.kb_tex.table(self.H4E['CVR3_ATS4'].table_array())

      self.kb_tex.tex('\n\\subsubsection{ATS4 no ATS0}')
      label = self.kb_tex.table(self.H4E['CVR3_ATS4_no_ATS0'].table_array())

      
      self.kb_tex.tex('\nEvalATS-finished')
      

#-------------------------------------------------------------------------      











