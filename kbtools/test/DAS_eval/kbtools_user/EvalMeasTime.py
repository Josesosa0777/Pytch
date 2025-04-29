"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: Time evalulation '''

''' to be called by DAS_eval.py '''


# imports
import sys
import os

# Utilities_DAS specific imports
import kbtools
import pylab as pl
import numpy as np




# ==============================================================================================
class cEvalMeasTime():
  def __init__(self):       # constructor
    self.myname = 'EvalFUS'
    self.H4E = {}

  def __del__(self):         # destructor
    pass
      
  # ------------------------------------------------------------------------------------------
  def init(self,folder):     # general start
  
    # headline
    self.table_headline = ['Idx','t start','dura','gap','FileName']

    # list
    self.table_array = [self.table_headline]
    self.table_idx   = 0

    self.last_t_stop = None
   
  # ------------------------------------------------------------------------------------------
  def reinit(self):          # recording interrupted
    for key in self.H4E.keys():
      self.H4E[key].reinit()

  # ------------------------------------------------------------------------------------------
  def finish(self):          # end of recording
    for key in self.H4E.keys():
      self.H4E[key].finish()

  # ------------------------------------------------------------------------------------------
  def process(self,Source):  # evaluate recorded file

    # FileName to specify the origin of the track
    FileName = os.path.basename(Source.FileName)

    try:
      SignalGroups = [{"VBOX_Time_Since_Midnight": ("VBOX_1", "Time_Since_Midnight"),
                      },]

      Group = Source.selectSignalGroup(SignalGroups)
     
      Time, Value = Source.getSignalFromSignalGroup(Group, "VBOX_Time_Since_Midnight") 
    
      t_start        = Value[0]
      t_stop         = Value[-1]
      dura           = t_stop - t_start

      if  self.last_t_stop != None:
        t_gap = t_start - self.last_t_stop
      else:
        t_gap = 0
        
      self.last_t_stop = t_stop 
    
        
      # add to table
      self.table_idx += 1
      self.table_array.append(['%d'%self.table_idx,'%3.2f'%t_start,'%3.2f'%dura,'%3.2f'%t_gap,kbtools.esc_bl(FileName)])
    except:
      pass   

  # ------------------------------------------------------------------------------------------
  def report_init(self):     # prepare for report - input tex file to main
    self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\section{EvalTime Overview}')

  # ------------------------------------------------------------------------------------------
  def report(self):          # report events
      
    self.kb_tex.workingfile('%s.tex'%self.myname)

    # experimental
    self.kb_tex.tex('\n\\newpage\\subsection{Start and Stop times}')
        
    label = self.kb_tex.table(self.table_array)


     
    self.kb_tex.tex('\nEvalTime-finished')

      
#-------------------------------------------------------------------------      










