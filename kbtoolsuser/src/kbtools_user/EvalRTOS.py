"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: Real Time Operating System (RTOS) evalulation '''

''' to be called by DAS_eval.py '''

import os
import pylab as pl
import numpy as np

# ==============================================================================================
# class storing data of TC Task cycle times evaluation for one sensor (LRR3 or CVR3)
class cEvalTCTask():
  def __init__(self, kb_tex, SensorName):
    # TC Task cycle times (XCP timestamp based)
    
    self.kb_tex = kb_tex
    self.SensorName = SensorName
    
    # ...............................................................
    # determine device from SensorName
    if self.SensorName == 'LRR3':
      self.Device = 'ECU-0-0'
    elif self.SensorName == 'CVR3':
      self.Device = 'MRR1plus-0-0'
    else:
      raise ValueError("%s not known"%self.SensorName)

    
    # ..............................................................
    # global extrem value
    self.global_min_dT = None
    self.global_max_dT = None
    self.global_sum_dT = 0       # used to calculate the global mean value
    self.global_n_dT   = 0       # used to calculate the global mean value
    self.global_mean_dT = None
    
    # histogram parameters
    self.binsIn         = np.arange(0, 0.301, 0.01)         # bin values: 0, 0.01, 0.02, ... 3.0
    self.global_hist_dT = np.zeros(len(self.binsIn)-1)       # hist values (one less than bin values)
    
  
    # headline of the overview table
    self.table_headline = ['Idx','min/max [ms]','mean [ms]','FileName']

    # list
    self.table_array = [self.table_headline]
    self.table_idx   = 0

    # .................................
    # TC_Task_timer
    
    self.TC_Task_timer_Limit = 28e-3
    
    # headline of the overview table
    #   Samples, Waits, WaitsAvg, BelowLimitCool, BelowLimit, Fastest, MdfFile
    self.TC_Task_timer_table_headline = ['Samples',
                                         'Waits/Avg',
                                         '$<$ %3.0f [ms]'%(self.TC_Task_timer_Limit*1000.0),
                                         '$<$ %3.0f [ms]'%(0.9*self.TC_Task_timer_Limit*1000.0),
                                         'Fastest',
                                         'FileName']

    # list
    self.TC_Task_timer_table_array = [self.TC_Task_timer_table_headline]
    self.TC_Task_timer_table_idx   = 0
    
  # -------------------------------------------------------------------------------------
  def eval_TC_Task_XCP_timestamp(self, Source):
    ''' TC Task cycle times (XCP timestamp based) '''
  
    # FileName to specify the origin of the track
    FileName = os.path.basename(Source.FileName)

    self.kb_tex.tex('\n\\paragraph{%s}'%self.SensorName)
  
    try:
      Time   = Source.getSignal(self.Device, 'ohl.ObjData_TC.OhlObj.i0.c.c.Valid_b')[0]
    except:
      Time = []
       
    if len(Time)>10:  
      dT      = np.diff(Time)
      min_dT  = np.min(dT)  
      max_dT  = np.max(dT)  
      mean_dT = np.mean(dT)  

      # calc histogram
      current_hist, bin_edges  = np.histogram(dT, bins=self.binsIn)
      self.global_hist_dT = self.global_hist_dT + current_hist
      
      # calculate global min/max/mean
      if (None==self.global_min_dT)|(min_dT < self.global_min_dT):
        self.global_min_dT = min_dT
      if (None==self.global_max_dT)|(max_dT > self.global_max_dT):
        self.global_max_dT = max_dT
      self.global_sum_dT += np.sum(dT)      # used to calculate the global mean value
      self.global_n_dT   += len(dT)    

      
      # add to table
      self.table_idx += 1
      self.table_array.append(['%d'%self.table_idx,
                               '%3.0f/%3.0f'%(min_dT*1000.0, max_dT*1000.0),
                               '%3.0f'%(mean_dT*1000.0),self.kb_tex.esc_bl(FileName)])
      
       
      #----------------------------------------------------
      # include the plot
      FigNr = 1

      fig=pl.figure(FigNr)
      fig.clear()
      fig.suptitle('File: %s'%FileName)
      sp=fig.add_subplot(111)
      sp.grid()
      width = np.diff(self.binsIn)[0]
      sp.bar(self.binsIn[:-1]*1000.0,current_hist,width*1000.0)
      sp.set_title('TC Task cycle times (XCP timestamps)')
      sp.set_xlim(self.binsIn[0]*1000.0,self.binsIn[-1]*1000.0)
      sp.set_ylabel('counts')
      sp.set_xlabel('TC Task cycle time [ms]')
      #fig.show()
    
      s  =  'Sensor: %s \n\\newline '%self.SensorName
      s +=  'File: %s \n\\newline '%self.kb_tex.esc_bl(FileName)
      s +=  'min/max = %3.0f/%3.0f ms; '%(min_dT*1000.0,max_dT*1000.0)
      s +=  'mean = %3.0f ms' %(mean_dT*1000.0)
      
      label = self.kb_tex.epsfig(fig,s);
    else:
      self.kb_tex.tex('\nsignals not available')   
      
                                             
  # ------------------------------------------------------------------------------------------
  def calc_global_mean_dT(self):
    # calcuate mean value over all measurements
    if self.global_n_dT > 0:
      self.global_mean_dT = self.global_sum_dT/float(self.global_n_dT)
    else:
      self.global_mean_dT = None

  # ------------------------------------------------------------------------------------------
  def createSummaryStatistics(self):
    # create table with summary statistics
    
    # prepare table
    tmp_table_array     = [['cycle time','Value','Unit']]
    if (None==self.global_min_dT) | (None==self.global_max_dT):
      tmp_table_array.append(['min/max', '-/-', 'ms'])
    else:    
      tmp_table_array.append(['min/max', '%3.0f/%3.0f'%(self.global_min_dT*1000.0,self.global_max_dT*1000.0), 'ms'])
      
    if (None==self.global_mean_dT):
      tmp_table_array.append(['mean', '-', 'ms'])
    else:
      tmp_table_array.append(['mean'   , '%3.0f'      %(self.global_mean_dT*1000.0),                          'ms'])
    
    # create table in kb_tex
    label = self.kb_tex.table(tmp_table_array)  
   
  # ------------------------------------------------------------------------------------------
  def createSummaryHistogram(self):
    if self.global_n_dT > 0:
      FigNr = 1
      fig=pl.figure(FigNr)
      fig.clear()
      fig.suptitle('summary of all measurements')
      sp=fig.add_subplot(111)
      sp.grid()
      sp.bar(self.binsIn[:-1]*1000.0,self.global_hist_dT,np.diff(self.binsIn)[0]*1000) # x,y,width
      sp.set_title('TC Task cycle time (XCP timestamp based)')
      sp.set_xlim(self.binsIn[0]*1000.0,self.binsIn[-1]*1000.0)
      sp.set_ylabel('counts')
      sp.set_xlabel('TC Task cycle time [ms]')
      #fig.show()
      s  =  'summary of all measurements: '
      s +=  'min/max = %3.0f/%3.0f ms; '%(self.global_min_dT*1000.0,self.global_max_dT*1000.0)
      s +=  'mean = %3.0f ms' %(self.global_mean_dT*1000.0)
      label = self.kb_tex.epsfig(fig, s);
    else:
      self.kb_tex.tex('\nsignals not available')   


  # ------------------------------------------------------------------------------------------
  def createIndividualStatistics(self):
    label = self.kb_tex.table(self.table_array)

  # ------------------------------------------------------------------------------------------
  def eval_TC_Task_timer(self, Source):
    ''' copied from Gergo's TC_EvalStat_GG.py '''
  
    # FileName to specify the origin of the track
    FileName = os.path.basename(Source.FileName)

    '''
      Source.getSignal('MRR1plus-0-0', 'timer_tc.isRunning_b'),
      Source.getSignal('MRR1plus-0-0', 'timer_tc.tDuration'),
      Source.getSignal('MRR1plus-0-0', 'timer_tc.tStartTime'),
      Source.getSignal('MRR1plus-0-0', 'timer_tc.tWaitTime'),
    '''

    try:
      TC_Time, tWaitTime   = Source.getSignal(self.Device, 'timer_tc.tWaitTime')
    except:
      TC_Time = []
    

    
    if len(TC_Time)>10:
      dTimes    = np.diff(TC_Time)
      waitTimes = np.concatenate([tWaitTime[2:], [0.0]])
      Times     = dTimes + waitTimes
      Mask      = tWaitTime > 0.0
      MaskSum   = Mask.sum()
      WaitAvg   = tWaitTime[Mask].mean() if MaskSum else 0.0
 
 
      Samples         = TC_Time.size
      Waits           = MaskSum
      WaitsAvg        = WaitAvg 
      BelowLimitCool  = (Times < self.TC_Task_timer_Limit).sum()
      BelowLimit      = (Times < self.TC_Task_timer_Limit * 0.9).sum()
      Fastest         = Times.min()

      # add to table
      self.TC_Task_timer_table_idx += 1
      self.TC_Task_timer_table_array.append(['%12d'      %Samples,
                                             '%6d/%3.1f' %(MaskSum, WaitsAvg),
                                             '%16d'      %BelowLimitCool,
                                             '%16d'      %BelowLimit,
                                             '%3.0f ms'  %(Fastest*1000.0),
                                             '%42s'      %self.kb_tex.esc_bl(FileName)])
    else:
      self.kb_tex.tex('\nsignals not available')   


  # ------------------------------------------------------------------------------------------
  def createTC_Task_timer_Statistics(self):
    label = self.kb_tex.table(self.TC_Task_timer_table_array)
    
    
# ==============================================================================================
class cEvalRTOS():
  def __init__(self):       # constructor
    self.myname = 'EvalRTOS'
    self.H4E = {}               # H4E = hunt4event instances

  def __del__(self):        # destructor
    pass
      
  # ------------------------------------------------------------------------------------------
  def init(self,folder):    # general start
  
    self.LRR3_EvalTCTask = cEvalTCTask(self.kb_tex, 'LRR3') 
    self.CVR3_EvalTCTask = cEvalTCTask(self.kb_tex, 'CVR3') 
     
  # ------------------------------------------------------------------------------------------
  def reinit(self):          # recording interrupted
    for key in self.H4E.keys():
      self.H4E[key].reinit()

  # ------------------------------------------------------------------------------------------
  def process(self,Source):  # evaluate recorded file


  
    # TC Task cycle times (XCP timestamp based)
    self.kb_tex.workingfile('%s_details.tex'%self.myname)
    FileName = os.path.basename(Source.FileName)
    self.kb_tex.tex('\n\\subsubsection{%s}'%self.kb_tex.esc_bl(FileName))
       
    self.LRR3_EvalTCTask.eval_TC_Task_XCP_timestamp(Source)
    self.CVR3_EvalTCTask.eval_TC_Task_XCP_timestamp(Source)
    

    # TC Task timer 
    self.LRR3_EvalTCTask.eval_TC_Task_timer(Source)
    self.CVR3_EvalTCTask.eval_TC_Task_timer(Source)


  # ------------------------------------------------------------------------------------------
  def finish(self):          # end of recording
    for key in self.H4E.keys():
      self.H4E[key].finish()
      
    # calcuate mean value over all measurements
    self.LRR3_EvalTCTask.calc_global_mean_dT()
    self.CVR3_EvalTCTask.calc_global_mean_dT()
      
  # ------------------------------------------------------------------------------------------
  def report_init(self):     # prepare for report - input tex file to main
  
    # Overview
    self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\section{EvalRTOS}')
    self.kb_tex.tex('\n\\newpage\\subsection{Overview}')

    # Details
    self.kb_tex.tex_main('\n\\input{%s_details.tex}\n'%self.myname)
    self.kb_tex.workingfile('%s_details.tex'%self.myname)
    self.kb_tex.tex('\n\\newpage\\subsection{Details}')
    
  # ------------------------------------------------------------------------------------------
  def report(self):          # report events
      
    self.kb_tex.workingfile('%s.tex'%self.myname)

    #----------------------------------------------------
    # subsection - TC Task cycle times
    self.kb_tex.tex('\n\\subsubsection{TC Task cycle times (XCP timestamp based)}')
       
       
    # Summary statistics
    # LRR3
    self.kb_tex.tex('\n\\paragraph{Summary statistics LRR3}')
    self.kb_tex.tex('\nSummary statics about TC Task cycle times (XCP timestamp based):')
    tmp_table_array = self.LRR3_EvalTCTask.createSummaryStatistics()
    # CVR3
    self.kb_tex.tex('\n\\paragraph{Summary statistics CVR3}')
    self.kb_tex.tex('\nSummary statics about TC Task cycle times (XCP timestamp based):')
    tmp_table_array = self.CVR3_EvalTCTask.createSummaryStatistics()
    
    # histogram
    # LRR3
    self.kb_tex.tex('\n\\paragraph{Histogram LRR3}')
    self.LRR3_EvalTCTask.createSummaryHistogram()
    # CVR3
    self.kb_tex.tex('\n\\paragraph{Histogram CVR3}')
    self.CVR3_EvalTCTask.createSummaryHistogram()
    
   
    # Individual Statistics
    # LRR3
    self.kb_tex.tex('\n\\paragraph{Individual statistics LRR3}')
    self.kb_tex.tex('\nIndividual statistics about TC Task cycle times (XCP timestamp based):')
    self.LRR3_EvalTCTask.createIndividualStatistics()

    # CVR3
    self.kb_tex.tex('\n\\paragraph{Individual statistics CVR3}')
    self.kb_tex.tex('\nIndividual statistics about TC Task cycle times (XCP timestamp based):')
    self.CVR3_EvalTCTask.createIndividualStatistics()


    
    #-----------------------------------------------------------------------------------    
    # subsection - TC Task timer
    self.kb_tex.tex('\n\\subsubsection{TC Task timer}')

    # Individual statistics
    # LRR3
    self.kb_tex.tex('\n\\paragraph{Individual statistics LRR3}')
    self.kb_tex.tex('\nIndividual statistics about TC Task timer:')
    self.LRR3_EvalTCTask.createTC_Task_timer_Statistics()
    # CVR3
    self.kb_tex.tex('\n\\paragraph{Individual statistics CVR3}')
    self.kb_tex.tex('\nIndividual statistics about TC Task timer:')
    self.CVR3_EvalTCTask.createTC_Task_timer_Statistics()
    

    # --------------------------------------------
    # end    
    self.kb_tex.tex('\nEvalRTOS-finished')

  # ==========================================================================================
  # private methods
  
                                           
#-------------------------------------------------------------------------      










