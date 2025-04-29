"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: FLR20 CW-Track evalulation '''

''' to be called by DAS_eval.py '''

import numpy as np

import kbtools
import kbtools_user


# ==============================================================================================
class cEvalFLR20CWTrack():
    # ------------------------------------------------------------------------------------------
    def __init__(self):                # constructor
      self.myname = 'EvalFLR20CWTrack' # name of this user specific evaluation
      self.H4E = {}                    # H4E hunt4event directory

    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
      pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
      
      # ----------------------------------------------------------------------
      #  CW-Track 
      t_join = 0
      self.H4E['CWTrack'] = kbtools.cHunt4Event('on_phase','CWTrack',t_join)
      self.H4E['CWTrack_stat'] = kbtools.cHunt4Event('on_phase','CWTrack Stationary',t_join)
      
      
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
    def callback_CWTrack(self,t_start,t_stop):
        print "callback_CWTrack", t_start,t_stop
        FLR20_sig = self.FLR20_sig
     
        # ---------------------------------------------------------------
        # v_ego_at_t_start,v_ego_at_t_stop
        t_v_ego          = FLR20_sig['General']['Time']        
        v_ego            = FLR20_sig['General']['actual_vehicle_speed']*3.6
        v_ego_at_t_start = v_ego[t_v_ego>=t_start][0]
        v_ego_at_t_stop  = v_ego[t_v_ego>=t_stop][0]
       
        # ---------------------------------------------------------------
        # is_video_associated_at_t_start, is_video_associated_at_t_stop, is_video_associated_any, is_video_associated_all
        t_is_video_associated          = FLR20_sig['PosMatrix']['CW']['Time']        
        is_video_associated            = FLR20_sig['PosMatrix']['CW']['is_video_associated']
        is_video_associated_at_t_start = is_video_associated[t_is_video_associated>=t_start][0]
        is_video_associated_at_t_stop  = is_video_associated[t_is_video_associated>=t_stop][0]
        mask = np.logical_and(t_is_video_associated>=t_start, t_is_video_associated<t_stop)
        is_video_associated_any        = any(is_video_associated[mask])
        is_video_associated_all        = all(is_video_associated[mask])
       
        # ---------------------------------------------------------------
        # dx_at_t_start, dx_at_t_stop
        t_dx          = FLR20_sig['PosMatrix']['CW']['Time']        
        dx            = FLR20_sig['PosMatrix']['CW']['dx']
        dx_at_t_start = dx[t_dx>=t_start][0]
        dx_at_t_stop = dx[t_dx>=t_stop][0]
        
        # ---------------------------------------------------------------
        # Was CW valid before?
        # cw_track_starts_before, dx_at_cw_track_start
        
        t_cw_track          = FLR20_sig['PosMatrix']['CW']['Time'] 
        cw_track            = FLR20_sig['PosMatrix']['CW']['Valid']
      
        start_idx, stop_idx = kbtools.getIntervalAroundEvent(t_cw_track,t_start,cw_track>0.5)
        t_start_cw_track    = t_cw_track[start_idx]  
        
        # 1) t_start_cw_track_before_AEBS_warning 
        cw_track_starts_before = t_start - t_start_cw_track
        
        # 2) dx_at_cw_track_start
        t_dx                  = FLR20_sig['PosMatrix']['CW']['Time'] 
        dx                    = FLR20_sig['PosMatrix']['CW']['dx']
        dx_at_cw_track_start  = dx[t_dx>=t_start_cw_track][0]
  
        

        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["v_ego_at_t_start"]                    = v_ego_at_t_start
        att["v_ego_at_t_stop"]                     = v_ego_at_t_stop
        att["dx_at_t_start"]                       = dx_at_t_start
        att["dx_at_t_stop"]                        = dx_at_t_stop
        att["cw_track_starts_before"]              = cw_track_starts_before
        att["dx_at_cw_track_start"]                = dx_at_cw_track_start
        att["is_video_associated_at_t_start"]      = is_video_associated_at_t_start
        att["is_video_associated_at_t_stop"]       = is_video_associated_at_t_stop
        att["is_video_associated_any"]             = is_video_associated_any
        att["is_video_associated_all"]             = is_video_associated_all
                 
        return att

        
    # ------------------------------------------------------------------------------------------
    def callback_CWTrack_stat(self,t_start,t_stop):
        print "callback_CWTrack_stat", t_start,t_stop
        FLR20_sig = self.FLR20_sig
     
        # ---------------------------------------------------------------
        # v_ego_at_t_start,v_ego_at_t_stop
        t_v_ego          = FLR20_sig['General']['Time']        
        v_ego            = FLR20_sig['General']['actual_vehicle_speed']*3.6
        v_ego_at_t_start = v_ego[t_v_ego>=t_start][0]
        v_ego_at_t_stop  = v_ego[t_v_ego>=t_stop][0]
       
        # ---------------------------------------------------------------
        # is_video_associated_at_t_start, is_video_associated_at_t_stop, is_video_associated_any, is_video_associated_all
        t_is_video_associated          = FLR20_sig['PosMatrix']['CW']['Time']        
        is_video_associated            = FLR20_sig['PosMatrix']['CW']['is_video_associated']
        is_video_associated_at_t_start = is_video_associated[t_is_video_associated>=t_start][0]
        is_video_associated_at_t_stop  = is_video_associated[t_is_video_associated>=t_stop][0]
        mask = np.logical_and(t_is_video_associated>=t_start, t_is_video_associated<t_stop)
        is_video_associated_any        = any(is_video_associated[mask])
        is_video_associated_all        = all(is_video_associated[mask])
       
        # ---------------------------------------------------------------
        # dx_at_t_start, dx_at_t_stop
        t_dx          = FLR20_sig['PosMatrix']['CW']['Time']        
        dx            = FLR20_sig['PosMatrix']['CW']['dx']
        dx_at_t_start = dx[t_dx>=t_start][0]
        dx_at_t_stop = dx[t_dx>=t_stop][0]
        
        # ---------------------------------------------------------------
        # Was CW valid before?
        # cw_track_starts_before, dx_at_cw_track_start
        
        t_cw_track          = FLR20_sig['PosMatrix']['CW']['Time'] 
        cw_track            = FLR20_sig['PosMatrix']['CW']['Valid']
      
        start_idx, stop_idx = kbtools.getIntervalAroundEvent(t_cw_track,t_start,cw_track>0.5)
        t_start_cw_track    = t_cw_track[start_idx]  
        
        # 1) t_start_cw_track_before_AEBS_warning 
        cw_track_starts_before = t_start - t_start_cw_track
        
        # 2) dx_at_cw_track_start
        t_dx                  = FLR20_sig['PosMatrix']['CW']['Time'] 
        dx                    = FLR20_sig['PosMatrix']['CW']['dx']
        dx_at_cw_track_start  = dx[t_dx>=t_start_cw_track][0]
  
        

        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["v_ego_at_t_start"]                    = v_ego_at_t_start
        att["v_ego_at_t_stop"]                     = v_ego_at_t_stop
        att["dx_at_t_start"]                       = dx_at_t_start
        att["dx_at_t_stop"]                        = dx_at_t_stop
        att["cw_track_starts_before"]              = cw_track_starts_before
        att["dx_at_cw_track_start"]                = dx_at_cw_track_start
        att["is_video_associated_at_t_start"]      = is_video_associated_at_t_start
        att["is_video_associated_at_t_stop"]       = is_video_associated_at_t_stop
        att["is_video_associated_any"]             = is_video_associated_any
        att["is_video_associated_all"]             = is_video_associated_all
                 
        return att

        
    # ------------------------------------------------------------------------------------------
    def _process_CWTrack(self,Source):
        
        FLR20_sig = self.FLR20_sig
        
        # ---------------------------------------------------------------
        # CW Track on Track[0]
        t_cw_track          = FLR20_sig['Tracks'][0]['Time']
        cw_track            = FLR20_sig['Tracks'][0]['CW_track']
      
        self.H4E['CWTrack'].process(t_cw_track, cw_track, Source, callback_rising_edge=self.callback_CWTrack)
        
        
        # ---------------------------------------------------------------
        # Stationary CW Track
        t_Stationary          = FLR20_sig['PosMatrix']['CW']['Time']        
        Stationary            = FLR20_sig['PosMatrix']['CW']['Stationary']
        
        self.H4E['CWTrack_stat'].process(t_Stationary, Stationary, Source, callback_rising_edge=self.callback_CWTrack_stat)
        

    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file
    
        # --------------------------------------------
        # extract FLR20 signals from measurement (Source -> FLR20_sig)
        FLR20_sig = kbtools_user.cDataAC100.load_AC100_from_Source(Source)
        # store FLR20 signals to be used in callback function "callback_rising_edge"
        self.FLR20_sig = FLR20_sig

        
        try:
            self._process_CWTrack(Source)
            
        except:
            print "EvalFLR20CWTrack::process() error"
        
         

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
        fill_table_array_into_report = False
        
        self.kb_tex.workingfile('%s.tex'%self.myname)
      
        self.kb_tex.tex('\n\\newpage\\section{FLR20EvalCWTrack}')
    
        self.kb_tex.tex('\n\\subsection{CW Track}')
        self.kb_tex.tex('\n %d entries'% self.H4E['CWTrack'].n_entries_EventList())
        if fill_table_array_into_report:
            label = self.kb_tex.table(self.H4E['CWTrack'].table_array())
        
        self.kb_tex.tex('\n\\subsection{CW Track stationary}')
        self.kb_tex.tex('\n %d entries'% self.H4E['CWTrack_stat'].n_entries_EventList())
        if fill_table_array_into_report:
            label = self.kb_tex.table(self.H4E['CWTrack_stat'].table_array())
        
        
        self.kb_tex.tex('\n\n \\medksip \n\n')
        self.kb_tex.tex('\nEvalFLR20CWTrack-finished')
      
      
     
    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        print "excel_export"
        
        
        
        # new format 
        AddColsFormat = {}
        AddColsFormat["v_ego_at_t_start"]                     = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["v_ego_at_t_stop"]                      = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["dx_at_t_start"]                        = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["dx_at_t_stop"]                         = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["cw_track_starts_before"]               = ("ExcelNumFormat", '##0.00 "s"')    # "%4.2f s"
        AddColsFormat["dx_at_cw_track_start"]                 = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["t_offset_AEBS_warning_offline"]        = ("ExcelNumFormat", '##0.000 "s"')   # "%4.3f s"
        
        WriteExcel = kbtools.cWriteExcel()

        # ------------------------------------------------------
        # AEBS_warning, AEBS_partial_brake, AEBS_emergency_brake
        # online
        AddCols_online = ["v_ego_at_t_start","v_ego_at_t_stop", 
                          "dx_at_t_start","dx_at_t_stop",
                          "cw_track_starts_before", "dx_at_cw_track_start",
                          "is_video_associated_at_t_start","is_video_associated_at_t_stop","is_video_associated_any","is_video_associated_any"]
     
        WriteExcel.add_sheet_out_table_array('CWTrack_stat',self.H4E['CWTrack_stat'].table_array2(AddCols_online,AddColsFormat))

        WriteExcel.add_sheet_out_table_array('CWTrack',self.H4E['CWTrack'].table_array2(AddCols_online,AddColsFormat))
        
        # -------------------------------------------------
        # write Excel file
        WriteExcel.save("FLR20EvalCWTrack_results.xls")
        
        print "excel_export() finish"
      
#-------------------------------------------------------------------------      









