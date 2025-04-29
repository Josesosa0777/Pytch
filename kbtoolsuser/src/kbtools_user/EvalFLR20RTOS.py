"""
:Organization: Knorr-Bremse SfN GmbH T/CES3.2 Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: FLR20 - Real Time Operating System (RTOS) evalulation '''

''' to be called by DAS_eval.py '''

import os
import pylab as pl
import numpy as np

import kbtools

# ==============================================================================================
# workaround 
def esc_bl(s):
    # [s] = esc_bl(s)
    # convert understore '_' into  backslash understore '\_'
    # e.g. esc_bl('delta_h') -> 'delta\_h'
    # s_out = strrep(s_in,'_','\_');
    s = s.replace('_','\_')
    return s

# ==============================================================================================
class cSignalStatistics():

  # ------------------------------------------------------------------------------------------
  def __init__(self,SignalName='signal', Unit='',ScalingFactor = 1.0, Format = '%3.0f', hist_start=0.0,hist_stop=1.0,hist_step=0.01):
    
    self.SignalName = SignalName
    self.Unit = Unit
    self.ScalingFactor = ScalingFactor
    self.Format = Format
    
    # --------------------------------------------------------------------------------------
    # a) statistics
    self.global_min  = None
    self.global_max  = None
    self.global_sum  = 0       # used to calculate the global mean value
    self.global_n    = 0       # used to calculate the global mean value
    self.global_mean = None
 
    # --------------------------------------------------------------------------------------
    # b) histogram 
    self.binsIn      = np.arange(hist_start*ScalingFactor, hist_stop*ScalingFactor, hist_step*ScalingFactor) # bin values
    self.global_hist = np.zeros(len(self.binsIn)-1)                # hist values (one less than bin values)
    self.current_hist = None
    
    # --------------------------------------------------------------------------------------
    # c) overview table
    # headline
    self.table_headline = ['Idx','min/max [%s]'%self.Unit,'mean [%s]'%self.Unit,'FileName']
    # list
    self.table_array = [self.table_headline]
    self.table_idx   = 0
    
    self.FileName = None
 
  # ------------------------------------------------------------------------------------------
  def process(self, tmp_input_signal, FileName):
        
    self.FileName = FileName
    input_signal = self.ScalingFactor *tmp_input_signal
    
    # --------------------------------------------------------------------------------------
    # a) statistics
    self.min_input_signal  = np.min(input_signal)  
    self.max_input_signal  = np.max(input_signal)  
    self.mean_input_signal = np.mean(input_signal)  

    # calculate global min/max/mean
    if (None==self.global_min)|(self.min_input_signal < self.global_min):
        self.global_min = self.min_input_signal
    if (None==self.global_max)|(self.max_input_signal > self.global_max):
        self.global_max = self.max_input_signal
    self.global_sum += np.sum(input_signal)      # used to calculate the global mean value
    self.global_n   += len(input_signal)    

    
    # --------------------------------------------------------------------------------------
    # b) statistics
    self.current_hist, bin_edges  = np.histogram(input_signal, bins=self.binsIn)
    self.global_hist = self.global_hist + self.current_hist
         
    
    # --------------------------------------------------------------------------------------
    # c) overview table
    # add to table
    self.table_idx += 1
    Format1 = '%s/%s'%(self.Format, self.Format) 
    self.table_array.append(['%d'%self.table_idx,
                             Format1%(self.min_input_signal, self.max_input_signal),
                             self.Format%(self.mean_input_signal),
                             esc_bl(self.FileName)])
 
 
  # ------------------------------------------------------------------------------------------
  def plot_current_hist(self, title="", xlabel="" ,FigNr = 1):
   
   
    
    fig=pl.figure(FigNr)
    fig.clear()
    if self.FileName is not None:
        fig.suptitle('File: %s'%self.FileName)
    sp=fig.add_subplot(111)
    sp.grid()
    width = np.diff(self.binsIn)[0]
    if self.current_hist is not None:
        sp.bar(self.binsIn[:-1],self.current_hist,width)
    sp.set_title(title)
    sp.set_xlim(self.binsIn[0],self.binsIn[-1])
    sp.set_ylabel('counts')
    sp.set_xlabel(xlabel)
    #fig.show()
    
    Format1 = '%s/%s'%(self.Format,self.Format)
       
    #print "Format1", Format1
    if self.FileName is not None:
       s  =  'File: %s \n\\newline '%esc_bl(self.FileName)
       s +=  'min/max =' + Format1%(self.min_input_signal ,self.max_input_signal ) + " " + self.Unit + "; "
       s +=  'mean = ' + self.Format%(self.mean_input_signal) + " " + self.Unit
    else:
       s = 'File or Signals not available'
    
    return fig,s
    
  # ------------------------------------------------------------------------------------------
  def _calc_global_mean(self):
    # calcuate mean value over all measurements
    if self.global_n > 0:
        self.global_mean = self.global_sum/float(self.global_n)
    else:
        self.global_mean = None
        
  # ------------------------------------------------------------------------------------------
  def create_summary_table(self, headline=None):
  
    self._calc_global_mean()
  
    if headline is None:
        headline=[self.SignalName,'Value','Unit']
  
    Format1 = '%s/%s'%(self.Format,self.Format)
  
    tmp_table_array     = [headline]
    if (None==self.global_min) | (None==self.global_max):
        tmp_table_array.append(['min/max', '-/-', self.Unit])
    else:    
        tmp_table_array.append(['min/max', Format1%(self.global_min,self.global_max), self.Unit])
      
    if (None==self.global_mean):
        tmp_table_array.append(['mean', '-', self.Unit])
    else:
        tmp_table_array.append(['mean'   , self.Format%(self.global_mean),  self.Unit])
 
    return tmp_table_array

  # ------------------------------------------------------------------------------------------
  def plot_summary_hist(self, title="", xlabel="" ,FigNr = 1):
    
    fig = None
    s = ''
    if self.global_n > 0:
        fig=pl.figure(FigNr)
        fig.clear()
        fig.suptitle('summary of all measurements')
        sp=fig.add_subplot(111)
        sp.grid()
        sp.bar(self.binsIn[:-1],self.global_hist,np.diff(self.binsIn)[0]) # x,y,width
        sp.set_title(title)
        sp.set_xlim(self.binsIn[0],self.binsIn[-1])
        sp.set_ylabel('counts')
        sp.set_xlabel(xlabel)
        #fig.show()
        
        Format1 = 'min/max = %s/%s %s; '%(self.Format,self.Format,self.Unit)
        Format2 = 'mean = %s %s'%(self.Format,self.Unit)

        s  =  'summary of all measurements: '
        s +=  Format1%(self.global_min,self.global_max)
        s +=  Format2%(self.global_mean)
     

    return fig,s
 
  
  # ------------------------------------------------------------------------------------------
  def get_overview_table(self):
    return self.table_array  
        
  # ------------------------------------------------------------------------------------------
  def get_total_min(self):
    return self.global_min  
        
  # ------------------------------------------------------------------------------------------
  def get_total_max(self):
    return self.global_max  

  # ------------------------------------------------------------------------------------------
  def get_total_mean(self):
    return self.global_mean

# ==============================================================================================
def plot_time_histories_PTU(Source , FigNr = 1):

    fig = None
    s = ''

    tmp_Time1, tmp_processor_time_used = kbtools.GetSignal(Source,"General_radar_status", "processor_time_used") 
    tmp_Time2, tmp_number_of_targets = kbtools.GetSignal(Source,"General_radar_status", "number_of_targets") 
    tmp_Time3, tmp_number_of_tracks = kbtools.GetSignal(Source,"General_radar_status", "number_of_tracks") 
    
    '''
    print "PTU", len(tmp_Time1), tmp_Time1[0], tmp_Time1[-1]
    print "targets", len(tmp_Time2), tmp_Time2[0], tmp_Time2[-1]
    print "tracks", len(tmp_Time3), tmp_Time3[0], tmp_Time3[-1]
    
    print tmp_Time1[0]-tmp_Time2[0]
    print tmp_Time1[-1]-tmp_Time2[-1]
    t_start = max(tmp_Time1[0],tmp_Time2[0])
    t_stop = min(tmp_Time1[-1],tmp_Time2[-1])
    print "start", t_start
    print "stop", t_stop
    
    if (tmp_Time1[0]-tmp_Time2[0]) > 0.03:
        pass
        
    if (tmp_Time1[-1]-tmp_Time2[-1]) > 0.03:
        t_stop = tmp_Time1[-2]
    '''    
        
 
    dT = np.diff(tmp_Time1)
    t_common = tmp_Time1[1:]
    processor_time_used  = tmp_processor_time_used[1:]
    
    number_of_targets   = kbtools.resample(tmp_Time2,tmp_number_of_targets, t_common,'zoh_next')
    number_of_tracks    = kbtools.resample(tmp_Time3,tmp_number_of_tracks, t_common,'zoh_next')
    
       
    fig=pl.figure(FigNr)
    fig.clear()
    fig.suptitle('time histories of processor time used and radar cycle time')
    
    mode = 3
    
    if mode == 1:
        fig=pl.figure(FigNr)
        fig.clear()
        fig.suptitle('time histories of processor time used and radar cycle time')
        
        # processor time used versus time
        sp=fig.add_subplot(411)
        sp.plot(t_common,processor_time_used,'x')
        sp.grid()
        sp.set_title('processor time used')
        sp.set_ylim(0,120)
        sp.set_ylabel('[%]')
    
        # cycle time versus time
        sp=fig.add_subplot(412)
        sp.plot(t_common,dT*1000,'x')
        sp.grid()
        sp.set_title('cycle time')
        sp.set_ylim(0,60)
        sp.set_ylabel('[ms]')
    
        # number_of_targets versus time
        sp=fig.add_subplot(413)
        sp.plot(t_common,number_of_targets,'xb')
        sp.grid()
        sp.set_title('number_of_targets')
        sp.set_ylim(0,30)
        sp.set_ylabel('no.')

        # number_of_tracks versus time
        sp=fig.add_subplot(414)
        sp.plot(t_common,number_of_tracks,'xb')
        sp.grid()
        sp.set_title('number_of_tracks')
        sp.set_ylim(0,30)
        sp.set_ylabel('no.')
          
        sp.set_xlabel('time [s]')
        
        s  =  'time histories of dT and PTU'
    elif mode == 2:
        fig=pl.figure(FigNr)
        fig.clear()
        fig.suptitle('processor time used vs radar cycle time')
    
    
        sp=fig.add_subplot(111)
        sp.plot(dT*1000,processor_time_used,'xb')
        sp.grid()
        sp.set_title('processor time used vs radar cycle time')
        sp.set_xlim(20,60)
        sp.set_ylim(0,120)
        sp.set_ylabel('processor time [%]')
          
        sp.set_xlabel('radar cycle time [ms]')
    
        s  =  'processor time used vs radar cycle time'

    elif mode == 3:
        fig=pl.figure(FigNr)
        fig.clear()
        fig.suptitle('processor time used vs number of tracks')
    
    
        sp=fig.add_subplot(111)
        sp.plot(number_of_tracks,processor_time_used,'xb')
        sp.grid()
        sp.set_title('processor time used vs number of tracks')
        sp.set_xlim(0,25)
        sp.set_ylim(0,120)
        sp.set_ylabel('processor time [%]')
          
        sp.set_xlabel('number_of_tracks')
    
        s  =  'processor time used vs radar cycle time'

    elif mode == 4:
        fig=pl.figure(FigNr)
        fig.clear()
        fig.suptitle('processor time used vs number of targets')
    
    
        sp=fig.add_subplot(111)
        sp.plot(number_of_targets,processor_time_used,'xb')
        sp.grid()
        sp.set_title('processor time used vs number of targets')
        sp.set_xlim(0,25)
        sp.set_ylim(0,120)
        sp.set_ylabel('processor time [%]')
          
        sp.set_xlabel('number_of_targets')
    
        s  =  'processor time used vs radar cycle time'
    return fig,s 
    
# ==============================================================================================
# ==============================================================================================
class cEvalFLR20CycleTime():
  def __init__(self, kb_tex):
    # FLR20 Processor Time Used : PTU   unit: %
    # signal ("General_radar_status", "processor_time_used")
    
    self.kb_tex = kb_tex
   
    self.SignalStatistics = cSignalStatistics(SignalName='cycle time', 
                                              Unit='ms',
                                              ScalingFactor = 1000.0, 
                                              Format = '%2.0f' ,
                                              hist_start=0.02,hist_stop=0.06,hist_step=0.001) 
    
  # -------------------------------------------------------------------------------------
  def eval_single_measurement(self, Source):
    ''' dT of Radar Cycle Time '''
  
    # FileName to specify the origin of the track
    self.FileName = os.path.basename(Source.FileName)

    # get signal   
    Time, PTU = kbtools.GetSignal(Source,"General_radar_status", "processor_time_used") 
            
    # calc
    if (Time is not None) and (len(Time)>10):  
        dT      = np.diff(Time)
        
        self.SignalStatistics.process(dT,self.FileName)

        fig,s = plot_time_histories_PTU(Source , FigNr = 1)
        label = self.kb_tex.epsfig(fig,s)
        
        # histogramm of current measurement        
        title="Radar Cycle times"    
        xlabel="cycle time"        
        fig,s = self.SignalStatistics.plot_current_hist(title=title, xlabel=xlabel, FigNr = 1)
        label = self.kb_tex.epsfig(fig,s);
        
        
    else:
        self.kb_tex.tex('\nsignals not available')   
      
   # ------------------------------------------------------------------------------------------
  def createSummaryStatistics(self):
       
    # create table
    tmp_table_array = self.SignalStatistics.create_summary_table()

    # insert table in kb_tex
    if tmp_table_array is not None:    
        
        label = self.kb_tex.table(tmp_table_array)  
    else:
        self.kb_tex.tex('\nSummary-Statistics could not be created')  
                                               
   
  # ------------------------------------------------------------------------------------------
  def createSummaryHistogram(self,FigNr = 1):
  
    # create plot
    title="Radar Cycle times"    
    xlabel="cycle time"        
    fig,s = self.SignalStatistics.plot_summary_hist(title=title, xlabel=xlabel, FigNr = 1)
     
    # insert plot in kb_tex     
    if fig is not None:    
        label = self.kb_tex.epsfig(fig,s);
    else:
        self.kb_tex.tex('\nSummary-Histogram could not be created')  
        
  # ------------------------------------------------------------------------------------------
  def createIndividualStatistics(self):
  
    # create table
    tmp_overview_table = self.SignalStatistics.get_overview_table()
    
    # insert table in kb_tex
    if tmp_overview_table is not None:    
        label = self.kb_tex.table(tmp_overview_table) 
    else:
        self.kb_tex.tex('\nIndividual-Statistics could not be created')  


    
# ==============================================================================================
# ==============================================================================================
class cEvalFLR20ProcessorTimeUsed():
  def __init__(self, kb_tex):
    # FLR20 Processor Time Used : PTU   unit: %
    # signal ("General_radar_status", "processor_time_used")
    
    self.kb_tex = kb_tex
   
    self.SignalStatistics = cSignalStatistics(SignalName='processor time used', 
                                              Unit='\%',
                                              ScalingFactor = 1.0, 
                                              Format = '%3.1f' ,
                                              hist_start=0.0,hist_stop=150.0,hist_step=1.0) 
  # -------------------------------------------------------------------------------------
  def eval_single_measurement(self, Source):
    ''' dT of Radar Cycle Time '''
  
    # FileName to specify the origin of the track
    self.FileName = os.path.basename(Source.FileName)

    # get signal   
    Time, PTU = kbtools.GetSignal(Source,"General_radar_status", "processor_time_used") 
       
    # calc
    if (PTU is not None) and (len(PTU)>10):  
   
        self.SignalStatistics.process(PTU,self.FileName)
               
        title="Processor Time Used"    
        xlabel="processor time used"      
        fig,s = self.SignalStatistics.plot_current_hist(title=title, xlabel=xlabel, FigNr = 1)
        
        label = self.kb_tex.epsfig(fig,s);
    else:
        self.kb_tex.tex('\nsignals not available')   
      
  # ------------------------------------------------------------------------------------------
  def createSummaryStatistics(self):
       
    # create table
    tmp_table_array = self.SignalStatistics.create_summary_table()

    # insert table in kb_tex
    if tmp_table_array is not None:    
        
        label = self.kb_tex.table(tmp_table_array)  
    else:
        self.kb_tex.tex('\nSummary-Statistics could not be created')  
                                             
  # ------------------------------------------------------------------------------------------
  def createSummaryHistogram(self,FigNr = 1):
  
    # create plot
    title="Processor Time Used"    
    xlabel="processor time used"        
    fig,s = self.SignalStatistics.plot_current_hist(title=title, xlabel=xlabel, FigNr = 1)
     
    # insert plot in kb_tex     
    if fig is not None:    
        label = self.kb_tex.epsfig(fig,s);
    else:
        self.kb_tex.tex('\nSummary-Histogram could not be created')  
        
  # ------------------------------------------------------------------------------------------
  def createIndividualStatistics(self):
  
    # create table
    tmp_overview_table = self.SignalStatistics.get_overview_table()
    
    # insert table in kb_tex
    if tmp_overview_table is not None:    
        label = self.kb_tex.table(tmp_overview_table) 
    else:
        self.kb_tex.tex('\nIndividual-Statistics could not be created')  


# ==============================================================================================
class cEvalFLR20RTOS():
    def __init__(self):       # constructor
        self.myname = 'EvalFLR20RTOS'
        self.H4E = {}         # H4E = hunt4event instances

    def __del__(self):        # destructor
        pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
   
        self.EvalFLR20CycleTime         = cEvalFLR20CycleTime(self.kb_tex) 
        self.EvalFLR20ProcessorTimeUsed = cEvalFLR20ProcessorTimeUsed(self.kb_tex)
        
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


  
        # TC Task cycle times (XCP timestamp based)
        self.kb_tex.workingfile('%s_details.tex'%self.myname)
        FileName = os.path.basename(Source.FileName)
        self.kb_tex.tex('\n\\subsubsection{%s}'%self.kb_tex.esc_bl(FileName))
       
        self.EvalFLR20CycleTime.eval_single_measurement(Source)
        self.EvalFLR20ProcessorTimeUsed.eval_single_measurement(Source)
        
        

    # ------------------------------------------------------------------------------------------
    def finish(self):          # end of recording
        for key in self.H4E.keys():
           self.H4E[key].finish()
            
    # ------------------------------------------------------------------------------------------
    def report_init(self):     # prepare for report - input tex file to main
  
        # Overview
        self.kb_tex.tex_main('\n\\input{%s.tex}\n'%self.myname)
        self.kb_tex.workingfile('%s.tex'%self.myname)
        self.kb_tex.tex('\n\\newpage\\section{EvalFLR20RTOS}')
        self.kb_tex.tex('\n\\newpage\\subsection{Overview}')

        # Details
        self.kb_tex.tex_main('\n\\input{%s_details.tex}\n'%self.myname)
        self.kb_tex.workingfile('%s_details.tex'%self.myname)
        self.kb_tex.tex('\n\\newpage\\subsection{Details}')
    
    # ------------------------------------------------------------------------------------------
    def report(self):          # report events
      
        self.kb_tex.workingfile('%s.tex'%self.myname)

        #----------------------------------------------------
        # subsection - cycle times
        self.kb_tex.tex('\n\\subsubsection{Cycle Times}')
       
       
        # Summary statistics
        self.kb_tex.tex('\n\\paragraph{Summary statics}')
        self.EvalFLR20CycleTime.createSummaryStatistics()
    
        # histogram
        #self.kb_tex.tex('\n\\paragraph{Histogram}')
        self.EvalFLR20CycleTime.createSummaryHistogram()
   
        # Individual Statistics
        self.kb_tex.tex('\n\\paragraph{Individual statistics}')
        self.EvalFLR20CycleTime.createIndividualStatistics()

        #----------------------------------------------------
        # subsection - pro
        self.kb_tex.tex('\n\\subsubsection{Processor Time Used}')
       
       
        # Summary statistics
        self.kb_tex.tex('\n\\paragraph{Summary statics}')
        self.EvalFLR20ProcessorTimeUsed.createSummaryStatistics()
    
        # histogram
        #self.kb_tex.tex('\n\\paragraph{Histogram}')
        self.EvalFLR20ProcessorTimeUsed.createSummaryHistogram()
   
        # Individual Statistics
        self.kb_tex.tex('\n\\paragraph{Individual statistics}')
        self.EvalFLR20ProcessorTimeUsed.createIndividualStatistics()

    
        
        # --------------------------------------------
        # end    
        self.kb_tex.tex('\nEvalFLR20RTOS-finished')

        # ==========================================================================================
        # private methods
  
    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        print "no excel_export"
        return
                                         
#-------------------------------------------------------------------------      










