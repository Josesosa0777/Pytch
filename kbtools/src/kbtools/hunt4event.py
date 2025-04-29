"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' Class cHunt4Event - clone of hunt4event.m '''

'''
  note:

  works for inpedendent (non consecutive) measurement files

  currently not prepared for proper evaluation of consecutive recording splitted 
  in several measurement files

'''


# python standard imports
import os
import pickle
import numpy as np
import gc

# Utilities_DAS specific imports
# todo import measproc
import kbtools

       
# ============================================================================ 
def check_Time_and_Value_internal(Time,Value):
 
    if (Time is None): 
        return False
    if (Value is None):
        return False
    
    if not isinstance(Time, np.ndarray): 
        return False
    if not isinstance(Value, np.ndarray):
        return False

    if  Time.size <= 2: 
        return False
    if  Value.size <= 2: 
        return False
    
    # len(Time) == len(Value) cause error is Time and Value are ndarray with one element    
    if not (Time.size == Value.size):
        return False
       
    return True

# ============================================================================ 
def check_Time_and_Value(Time,Value,verbose=True):
    '''
      wrapper around check_Time_and_Value_internal
    '''   
    if check_Time_and_Value_internal(Time,Value):
        return True
    else:
        try:
            if verbose:
                print "check_Time_and_Value(): error"
                print "Time",Time, type(Time), Time.size
                print "Value",Value, type(Value), Value.size
        except:
            if verbose:
                print "error"
            pass

        return False

# ============================================================================ 
class cHunt4Event():

  enable_save_event = False 

  # ------------------------------------------------
  def __init__(self,HuntType,Description,*Par):
    self.HuntType     = HuntType
    # HuntType: 'on_phase'
    
    self.Description  = Description
    # description text used in the report
    
    self.Par          = Par
    # list of additional parameters

    self.EventList = [];
    # List to store
    
    self.EventFolder = 'event'
    # where to store the events in files

    
  # ------------------------------------------------
  def reinit(self):
    # shall be called before each non consecutive part of a measurement 

    # todo: consecutive recording splitted in several measurement files   
    pass


  # ------------------------------------------------
  def process(self,Time, Value,Source, callback_rising_edge = None, err_msg=None, callback_parameters=None):
    # Time:    nparray
    # Value:   nparray
    # Source:  
  
    # -----------------------------------------
    # Name of measurement file
    FileName = Source.FileName
    
    # use orginal measurement name if available
    try:
        FileName = Source.FileName_org
    except:
        pass
   
    # -----------------------------------------
    if 'on_phase' ==  self.HuntType: 
        if check_Time_and_Value(Time,Value):
            
            CheckValue = 0.5
            '''
            #todo Intervals  = measproc.cEventFinder.compare(Time, Value, measproc.relations.greater, CheckValue)
            DistLimitTime = self.Par[0]
            #todo Intervals  = Intervals.merge(DistLimitTime)
            Intervals = None
            if len(Intervals) > 0:
                for Interval in Intervals:
                    # start and stop index
                    start_idx = Interval[0]
                    stop_idx  = Interval[1]
                    stop_idx = stop_idx-1
      
                    # start time, stop time and duration
                    t_start = Time[start_idx]
                    t_stop  = Time[stop_idx]
                    dura = t_stop-t_start

                    # attributes calculated in callback function
                    att = None
                    if callback_rising_edge is not None:
                        if callback_parameters is not None:
                            att = callback_rising_edge(t_start,t_stop,callback_parameters)
                        else:
                            att = callback_rising_edge(t_start,t_stop)
            '''

            iMultitState = kbtools.CMultiState()
            iMultitState.calc(Time,Value>CheckValue,default_value=0)
            
            # merge entries
            DistLimitTime = self.Par[0]
            iMultitState.merge(DistLimitTime)
            
            
            # t_starts, sig_starts, dura
            if len(iMultitState.t_starts) > 0:
                for t_start,sig_start,dura in zip(iMultitState.t_starts,iMultitState.sig_starts,iMultitState.dura):
                          
                    # start time, stop time and duration
                    t_stop  = t_start+dura
                    
          
                    # attributes calculated in callback function
                    att = None
                    if callback_rising_edge is not None:
                        if callback_parameters is not None:
                            att = callback_rising_edge(t_start,t_stop,callback_parameters)
                        else:
                            att = callback_rising_edge(t_start,t_stop)
          
                    # appende event to EventList
                    obj={}
                    obj['FullPath']    = FileName
                    obj['FileName']    = os.path.basename(FileName)
                    obj['DirName']     = os.path.dirname(FileName)
                    obj['description'] = self.Description
                    #obj['interval']    = Interval
                    obj['interval']    = zip(iMultitState.t_starts,iMultitState.sig_starts,iMultitState.dura)
                    obj['switch_on_time'] = None                      # additional
                    obj['t_start']     = t_start
                    try:
                        obj['t_start_abs'] = Source.GetAbsStartTimeOfMeasurement(offset_sec=t_start)
                    except:
                        obj['t_start_abs'] = "error"
                    
                    obj['t_stop']      = t_stop
                    obj['dura']        = dura
                    obj['value']       = None                    # additional
                    obj['att']         = att
                    if err_msg is not None:
                        obj['err_msg'] = err_msg
                    else:
                        obj['err_msg'] = ''
                    self.EventList.append(obj)
        else:
            # appende event to EventList
            obj={}
            obj['FullPath']    = FileName
            obj['FileName']    = os.path.basename(FileName)
            obj['DirName']     = os.path.dirname(FileName)
            obj['description'] = self.Description
            obj['interval']    = None
            obj['switch_on_time'] = None                      # additional
            obj['t_start']     = None
            obj['t_start_abs'] = None
            obj['t_stop']      = None
            obj['dura']        = None
            obj['value']       = None                    # additional
            obj['att']         = None
            if err_msg is not None:
                obj['err_msg'] = err_msg
            else:
                obj['err_msg'] = 'no signal'
            self.EventList.append(obj)
                    
    # -----------------------------------------
    elif 'multi_state' ==  self.HuntType: 
        if check_Time_and_Value(Time,Value):
            default_value = self.Par[0]
            iMultitState = kbtools.CMultiState()
            iMultitState.calc(Time,Value,default_value=default_value)
            # t_starts, sig_starts, dura
            if len(iMultitState.t_starts) > 0:
                for t_start,sig_start,dura in zip(iMultitState.t_starts,iMultitState.sig_starts,iMultitState.dura):
                          
                    # start time, stop time and duration
                    t_stop  = t_start+dura
                    
                    # attributes calculated in callback function
                    att = None
                    if callback_rising_edge is not None:
                        if callback_parameters is not None:
                            att = callback_rising_edge(t_start,t_stop,callback_parameters)
                        else:
                            att = callback_rising_edge(t_start,t_stop)
          
                    # appende event to EventList
                    obj={}
                    obj['FullPath']    = FileName
                    obj['FileName']    = os.path.basename(FileName)
                    obj['DirName']     = os.path.dirname(FileName)
                    obj['description'] = self.Description
                    obj['interval']    = zip(iMultitState.t_starts,iMultitState.sig_starts,iMultitState.dura)
                    obj['switch_on_time'] = None                      # additional
                    obj['t_start']     = t_start
                    try:
                        obj['t_start_abs'] = Source.GetAbsStartTimeOfMeasurement(offset_sec=t_start)
                    except:
                        obj['t_start_abs'] = "error"                  
                    obj['t_stop']      = t_stop
                    obj['dura']        = dura
                    obj['value']       = sig_start                    # additional
                    obj['att']         = att
                    if err_msg is not None:
                        obj['err_msg'] = err_msg
                    else:
                        obj['err_msg'] = ''
                    self.EventList.append(obj)
        else:
            # appende event to EventList
            obj={}
            obj['FullPath']    = FileName
            obj['FileName']    = os.path.basename(FileName)
            obj['DirName']     = os.path.dirname(FileName)
            obj['description'] = self.Description
            obj['interval']    = None
            obj['switch_on_time'] = None                      # additional
            obj['t_start']     = None
            obj['t_start_abs'] = None
            obj['t_stop']      = None
            obj['dura']        = None
            obj['value']       = None                    # additional
            obj['att']         = None
            if err_msg is not None:
                obj['err_msg'] = err_msg
            else:
                obj['err_msg'] = 'no signal'
            self.EventList.append(obj)
    # -----------------------------------------
    elif 'switch_on_time' ==  self.HuntType: 
        if check_Time_and_Value(Time,Value):
            print "switch_on_time"
            
            try:
                dt_vs_Time = np.diff(Time)
                tmp_Values = Value[:-2]       # strip off last sample to have same length as dt_vs_Time
            
                #print "tmp_Values",tmp_Values
            
                CheckValue = 0.5
                idx = np.argwhere(tmp_Values>CheckValue)
                #print idx
                       
                x = tmp_Values[idx]*dt_vs_Time[idx]
            
                #print x
            
                x_cumsum = np.cumsum(x)
                switch_on_time = x_cumsum[-1]
            
            except:
                switch_on_time = 0.0
           
            # start time, stop time and duration
            t_start = Time[0]
            t_stop  = Time[-1]
            dura = t_stop-t_start
          
            # attributes calculated in callback function
            att = None
            if callback_rising_edge is not None:
                if callback_parameters is not None:
                    att = callback_rising_edge(t_start,t_stop,callback_parameters)
                else:
                    att = callback_rising_edge(t_start,t_stop)
          
            # appende event to EventList
            obj={}
            obj['FullPath']    = FileName
            obj['FileName']    = os.path.basename(FileName)
            obj['DirName']     = os.path.dirname(FileName)
            obj['description'] = self.Description
            obj['interval']    = None
            obj['switch_on_time'] = switch_on_time             # additional
            obj['t_start']     = t_start
            try:
                obj['t_start_abs'] = Source.GetAbsStartTimeOfMeasurement(offset_sec=t_start)
            except:
                obj['t_start_abs'] = "error"
            obj['t_stop']      = t_stop
            obj['dura']        = dura
            obj['value']       = None                    # additional
            obj['att']         = att
            if err_msg is not None:
                obj['err_msg'] = err_msg
            else:
                obj['err_msg'] = ''
            self.EventList.append(obj)
        else:
            # appende event to EventList
            obj={}
            obj['FullPath']    = FileName
            obj['FileName']    = os.path.basename(FileName)
            obj['DirName']     = os.path.dirname(FileName)
            obj['description'] = self.Description
            obj['interval']    = None
            obj['switch_on_time'] = None                      # additional
            obj['t_start']     = None
            obj['t_start_abs'] = None
            obj['t_stop']      = None
            obj['dura']        = None
            obj['value']       = None                    # additional
            obj['att']         = None
            if err_msg is not None:
                obj['err_msg'] = err_msg
            else:
                obj['err_msg'] = 'no signal'
            self.EventList.append(obj)
                    
    else:
      pass

  # ------------------------------------------------
  def finish(self):
    # shall be called after all measurement have been processed

    # todo: consecutive recording splitted in several measurement files   
    # tbd.  close all open event (only import consecutive measurement)
    pass      

  # ------------------------------------------------
  def n_entries_EventList(self, extended_b=False):
    n_all = 0
    n_valid = 0
    if 'on_phase' ==  self.HuntType: 
      for Event in self.EventList:
        #out_table_array.append([Event['FileName'],Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'] ])
        n_all=n_all+1
        if Event['t_start'] is not None:
            n_valid = n_valid+1            
    else:
      pass 
    
    if extended_b:
        return  n_valid, n_all
    else:
        return  n_valid

  # ------------------------------------------------
  def table_array(self):
    # create a table to be used by kb_tex.py
    out_table_array = []   

    # --------------------------------------------------------------------------------        
    if 'on_phase' ==  self.HuntType: 
      # headline
      #out_table_array = [['FileName','desc','t_start','dura']]    
      out_table_array = [['Idx','Name','t\_start','dura','FileName']]    

      # body        
      k=0
      for Event in self.EventList:
        #out_table_array.append([Event['FileName'],Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'] ])
        k=k+1
        if Event['t_start'] is not None:
            out_table_array.append(['%d'%k,Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'],kbtools.esc_bl(Event['FileName'])])
        else:
            out_table_array.append(['%d'%k,Event['description'],Event['err_msg'],' ',kbtools.esc_bl(Event['FileName'])])
    # --------------------------------------------------------------------------------        
    elif 'multi_state' ==  self.HuntType: 
      # headline
      #out_table_array = [['FileName','desc','t_start','dura']]    
      out_table_array = [['Idx','Name','t\_start','dura','value','FileName']]    

      # body        
      k=0
      for Event in self.EventList:
        #out_table_array.append([Event['FileName'],Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'] ])
        k=k+1
        if Event['t_start'] is not None:
            out_table_array.append(['%d'%k,Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'],'%d'%Event['value'],kbtools.esc_bl(Event['FileName'])])
        else:
            out_table_array.append(['%d'%k,Event['description'],Event['err_msg'],' ',' ',kbtools.esc_bl(Event['FileName'])])
           
            
    # --------------------------------------------------------------------------------        
    elif 'switch_on_time' ==  self.HuntType: 
      # headline
      #out_table_array = [['FileName','desc','t_start','dura']]    
      out_table_array = [['Idx','Name','switch-on time','file dura','FileName']]    

      # body        
      k=0
      for Event in self.EventList:
        #out_table_array.append([Event['FileName'],Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'] ])
        k=k+1
        if Event['t_start'] is not None:
            out_table_array.append(['%d'%k,Event['description'],'%3.2f (%3.2f \\%%)'%(Event['switch_on_time'],Event['switch_on_time']/Event['dura']*100.0),'%3.2f'%Event['dura'],kbtools.esc_bl(Event['FileName'])])
        else:
            out_table_array.append(['%d'%k,Event['description'],Event['err_msg'],' ',kbtools.esc_bl(Event['FileName'])])
            
        
    else:
      pass 
      
    return  out_table_array
    
  # ------------------------------------------------
  def table_array2(self, AddCols = [], AddColsFormt ={}):
    # create a table to be used by kb_tex.py
    out_table_array = []   
    
    # ------------------------------------------------------------------------------------
    if 'on_phase' ==  self.HuntType: 
      # headline
      #out_table_array = [['FileName','desc','t_start','dura']]    
      
      pre_columns  = ['Idx','Name','t_start','dura','FileName']
      post_columns = ['DirName','t_start_abs']
      
      out_table_array = [pre_columns+AddCols+post_columns]    

      # body        
      k=0
      for Event in self.EventList:
        #out_table_array.append([Event['FileName'],Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'] ])
        k=k+1
        #obj = ['%d'%k,Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'],Event['FileName']]

        if Event['t_start'] is not None:
            # event is available
            
            # 1. pre columns
            obj = [(("ExcelNumFormat", '##0'),k),
                   Event['description'],
                   (("ExcelNumFormat", '##0.00 "s"'),Event['t_start']),
                   (("ExcelNumFormat", '##0.00 "s"'),Event['dura']),
                   Event['FileName']]
        
            # 2. attribute to column
            if 'att' in Event:
                for Col in AddCols:
                    if Col in AddColsFormt:
                        #print "table_array2: AddColsFormt[Col]", AddColsFormt[Col]
                        if isinstance(AddColsFormt[Col], (list, tuple)):
                            obj.append((AddColsFormt[Col], Event['att'][Col]))
                        elif isinstance(AddColsFormt[Col], str):
                            # format string available
                            if Event['att'][Col] is None:
                                obj.append("'None")
                            else:
                                obj.append(AddColsFormt[Col]%Event['att'][Col])
                        else:
                            print "table_array2: error - unknown AddColsFormt[Col] type"
                    else: 
                        obj.append(Event['att'][Col])
            
            # 3. post columns
            obj.append(Event['DirName'])
            obj.append(Event['t_start_abs'])
           
            
        else:
            # event is not available
  
            # 1. pre columns 
            obj = [(("ExcelNumFormat", '##0'),k),
                   Event['description'],
                   Event['err_msg'],
                   ' ',
                   Event['FileName']]

            # 2. attribute to column
            for Col in AddCols:
                obj.append(" ")

            # 3. post columns
            obj.append(Event['DirName'])
            obj.append(Event['t_start_abs'])
            
        # -------------------------
        # obj -> table
        out_table_array.append(obj)
    
    # ------------------------------------------------------------------------------------
    elif 'multi_state' ==  self.HuntType: 
      # headline
      #out_table_array = [['FileName','desc','t_start','dura']]    
      
      pre_columns  = ['Idx','Name','t_start','dura','value','FileName']
      post_columns = ['DirName','t_start_abs']
      
      out_table_array = [pre_columns+AddCols+post_columns]    

      # body        
      k=0
      for Event in self.EventList:
        #out_table_array.append([Event['FileName'],Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'] ])
        k=k+1
        #obj = ['%d'%k,Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'],Event['FileName']]

        if Event['t_start'] is not None:
            # event is available
            
            # 1. pre columns
            obj = [(("ExcelNumFormat", '##0'),k),
                   Event['description'],
                   (("ExcelNumFormat", '##0.00 "s"'),Event['t_start']),
                   (("ExcelNumFormat", '##0.00 "s"'),Event['dura']),
                   float(Event['value']),
                   Event['FileName']]
        
            # 2. attribute to column
            if 'att' in Event:
                for Col in AddCols:
                    if Col in AddColsFormt:
                        #print "table_array2: AddColsFormt[Col]", AddColsFormt[Col]
                        if isinstance(AddColsFormt[Col], (list, tuple)):
                            obj.append((AddColsFormt[Col], Event['att'][Col]))
                        elif isinstance(AddColsFormt[Col], str):
                            # format string available
                            if Event['att'][Col] is None:
                                obj.append("'None")
                            else:
                                obj.append(AddColsFormt[Col]%Event['att'][Col])
                        else:
                            print "table_array2: error - unknown AddColsFormt[Col] type"
                    else: 
                        obj.append(Event['att'][Col])
            
            # 3. post columns
            obj.append(Event['DirName'])
            obj.append(Event['t_start_abs'])
                       
            
        else:
            # event is not available
  
            # 1. pre columns 
            obj = [(("ExcelNumFormat", '##0'),k),    # 'Idx'
                   Event['description'],             # 'Name'
                   Event['err_msg'],                 # 't_start'
                   ' ',                              # 'dura' 
                   ' ',                              # 'value'
                   Event['FileName']]                # 'FileName'

            # 2. attribute to column
            for Col in AddCols:
                obj.append(" ")

            # 3. post columns
            obj.append(Event['DirName'])
            obj.append(Event['t_start_abs'])
            
        # -------------------------
        # obj -> table
        out_table_array.append(obj)
    # ------------------------------------------------------------------------------------
    if 'switch_on_time' ==  self.HuntType: 
      # headline
      #out_table_array = [['FileName','desc','t_start','dura']]    
      
      pre_columns  = ['Idx','Name','switch-on time ratio','switch-on time','dura','FileName']
      post_columns = ['DirName','t_start_abs']
      
      out_table_array = [pre_columns+AddCols+post_columns]    

      # body        
      k=0
      for Event in self.EventList:
        #out_table_array.append([Event['FileName'],Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'] ])
        k=k+1
        #obj = ['%d'%k,Event['description'],'%3.2f'%Event['t_start'],'%3.2f'%Event['dura'],Event['FileName']]

        if Event['t_start'] is not None:
            # event is available
            
            # 1. pre columns
            obj = [(("ExcelNumFormat", '##0'),k),
                   Event['description'],
                   (("ExcelNumFormat", '##0.00 "%"'),Event['switch_on_time']/Event['dura']*100.0),
                   (("ExcelNumFormat", '##0.00 "s"'),Event['switch_on_time']),
                   (("ExcelNumFormat", '##0.00 "s"'),Event['dura']),
                   Event['FileName']]
        
            # 2. attribute to column
            if 'att' in Event:
                for Col in AddCols:
                    if Col in AddColsFormt:
                        #print "table_array2: AddColsFormt[Col]", AddColsFormt[Col]
                        if isinstance(AddColsFormt[Col], (list, tuple)):
                            obj.append((AddColsFormt[Col], Event['att'][Col]))
                        elif isinstance(AddColsFormt[Col], str):
                            # format string available
                            if Event['att'][Col] is None:
                                obj.append("'None")
                            else:
                                obj.append(AddColsFormt[Col]%Event['att'][Col])
                        else:
                            print "table_array2: error - unknown AddColsFormt[Col] type"
                    else: 
                        obj.append(Event['att'][Col])
            
            # 3. post columns
            obj.append(Event['DirName'])
            obj.append(Event['t_start_abs'])
           
            
        else:
            # event is not available
  
            # 1. pre columns 
            obj = [(("ExcelNumFormat", '##0'),k),
                   Event['description'],
                   Event['err_msg'],
                   ' ',
                   Event['FileName']]

            # 2. attribute to column
            for Col in AddCols:
                obj.append(" ")

            # 3. post columns
            obj.append(Event['DirName'])
            obj.append(Event['t_start_abs'])
            
        # -------------------------
        # obj -> table
        out_table_array.append(obj)
        
    else:
      pass 
      
    return  out_table_array
 
  # ------------------------------------------------
  def save_event(self, key):
    
    print "hunt4event::save_event()",key
    
    print "cHunt4Event.enable_save_event", cHunt4Event.enable_save_event
    
    if not cHunt4Event.enable_save_event:
        print "-> no saving at all"
        return
    
    collected = gc.collect()
    print "Garbage collector: collected %d objects." % (collected)
    
    if not os.path.exists(self.EventFolder):
        os.makedirs(self.EventFolder)
       
    # pickle track_list to
    print "len(self.EventList)",len(self.EventList)
    if len(self.EventList) < 1000:
        output = open(os.path.join(self.EventFolder,key+'.pkl'), 'wb')
        pickle.dump(self.EventList, output,-1) # -1: using the highest protocol available
        output.close()
    
    '''
    import cPickle as pickle
    p = pickle.Pickler(open("temp.p","wb")) 
    p.fast = True 
    p.dump(d) # d is your dictionary
    '''
    
  # ------------------------------------------------
  def load_event(self, key):
    
    FileName = os.path.join(self.EventFolder,key+'.pkl')
   
    # load pickl file
    pkl_file = open(FileName, 'rb')
    self.EventList = pickle.load(pkl_file)
    pkl_file.close()

  # ------------------------------------------------
  def return_event(self, key):

    EventList = []
    FileName = os.path.join(self.EventFolder,key+'.pkl')
    if os.path.exists(FileName):
      # get track list from file (pickle)
      pkl_file = open(FileName, 'rb')
      EventList = pickle.load(pkl_file)
      pkl_file.close()
    return EventList
    
  # ------------------------------------------------
  def print_table(self):
    out_list = []   
    if 'on_phase' ==  self.HuntType: 
      print "EventList: "
      for Event in self.EventList:
        print 'FileName    :', Event['FileName'] 
        print 'description :', Event['description'] 
        print 'interval    :', Event['interval'] 
        print 't_start     :', Event['t_start']  
        print 't_stop      :', Event['t_stop']   
        print 'dura        :', Event['dura']     

        
