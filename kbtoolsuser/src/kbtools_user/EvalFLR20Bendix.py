"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: FLR20 Bendix evalulation '''

''' to be called by DAS_eval.py '''

import numpy as np

import kbtools
import kbtools_user


# ==============================================================================================
class cEvalFLR20Bendix():
    # ------------------------------------------------------------------------------------------
    def __init__(self):                # constructor
      self.myname = 'EvalFLR20Bendix'    # name of this user specific evaluation
      self.H4E = {}                    # H4E hunt4event directory

    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
      pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
      
           
      # ----------------------------------------------------------------------
      # AEBS outputs
      t_join = 0
      self.H4E['CM_warning']         = kbtools.cHunt4Event('on_phase','CM_warning',t_join)
      self.H4E['CM_braking']         = kbtools.cHunt4Event('on_phase','CM_braking',t_join)
      self.H4E['AudibleFeedback']    = kbtools.cHunt4Event('on_phase','AudibleFeedback',t_join)
      self.H4E['XBRAccDemand']       = kbtools.cHunt4Event('on_phase','XBRAccDemand',t_join)
      
      
            
      
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
    def callback_rising_edge(self,t_start,t_stop):
        print "callback_rising_edge", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
       
        
        # vego
        t_v_ego = FLR20_sig['General']['Time']        
        v_ego_kph = FLR20_sig['General']['actual_vehicle_speed']*3.6
        v_ego_kph_at_t_start  = v_ego_kph[t_v_ego>=t_start][0]
        v_ego_at_t_stop  = v_ego_kph[t_v_ego>=t_stop][0]
        v_ego_reduced = v_ego_kph_at_t_start - v_ego_at_t_stop
       
        # is_video_associated
        t_is_video_associated = FLR20_sig['PosMatrix']['CW']['Time']        
        is_video_associated = FLR20_sig['PosMatrix']['CW']['is_video_associated']
        is_video_associated_at_t_start  = is_video_associated[t_is_video_associated>=t_start][0]
       
        # dx
        t_dx = FLR20_sig['PosMatrix']['CW']['Time']        
        dx =  FLR20_sig['PosMatrix']['CW']['dx']
        dx_at_t_start  = dx[t_dx>=t_start][0]
       
        # ttc
        if v_ego_kph_at_t_start>0:
            ttc_at_t_start = dx_at_t_start/v_ego_kph_at_t_start*3.6
        else:
            ttc_at_t_start = None
        
       
       
        # Stationary
        t_Stationary = FLR20_sig['PosMatrix']['CW']['Time']        
        Stationary =  FLR20_sig['PosMatrix']['CW']['Stationary']
        Stationary_at_t_start  = Stationary[t_Stationary>=t_start][0]
      
        # cm_system_status 4 "WAITING" 3 "BRAKING" 2 "WARNING" 1 "ALLOWED" 0 "NOT_ALLOWED" ;
        CM_status = "NOT_ALLOWED (0)"
        t                    =  FLR20_sig['General']['Time'] 
        AEBS_allowed         =  FLR20_sig['General']["cm_system_status"] == 1
        AEBS_warning         =  FLR20_sig['General']["cm_system_status"] == 2
        AEBS_braking         =  FLR20_sig['General']["cm_system_status"] == 3
        #AEBS_waiting         =  FLR20_sig['General']["cm_system_status"] == 4
 
   
        interval = np.logical_and(t>=t_start,t<=t_stop)
        
        AEBS_allowed_occured = any(AEBS_allowed[interval])
        if AEBS_allowed_occured:
            CM_status = "ALLOWED (1)"
        
        AEBS_warning_occured = any(AEBS_warning[interval])
        if AEBS_warning_occured:
            CM_status = "WARNING (2)"
        
        AEBS_braking_occured = any(AEBS_braking[interval])
        if AEBS_braking_occured:
            CM_status = "BRAKING (3)"
            
        # -----------------------------------------------------        
        # Audible warning occured
        Audible_warning = "No"
        
        t_AudibleFeedback = FLR20_sig['Bendix_CMS']["Time"] 
        AudibleFeedback   = FLR20_sig['Bendix_CMS']["AudibleFeedback"] > 0
        interval = np.logical_and(t_AudibleFeedback>=t_start,t_AudibleFeedback<=t_stop)
       
        Audible_warning_occured = any(AudibleFeedback[interval])
        if Audible_warning_occured:
            Audible_warning = "Yes"
            
        # -----------------------------------------------------        
        # start of CW track  
        t_cw_track           = FLR20_sig['Tracks'][0]['Time']
        cw_track             = FLR20_sig['Tracks'][0]['CW_track']
      
        #print "t_start", t_start
        #print "t_cw_track[0]", t_cw_track[0]
        #print "cw_track[0]", cw_track[0]
        
        start_idx, stop_idx = kbtools.getIntervalAroundEvent(t_cw_track,t_start,cw_track>0.5,verbose = False)
        #print "cw_track>0.5", cw_track>0.5
        #print "start_idx, stop_idx", start_idx, stop_idx
        
        if start_idx is not None:
            t_start_cw_track = t[start_idx]  
            t_start_cw_track_before_AEBS_warning = t_start - t_start_cw_track
        
        
            t_dx = FLR20_sig['Tracks'][0]['Time']
            dx = FLR20_sig['Tracks'][0]['dx']
        
            #print "t_dx", t_dx
            #print "dx", dx
            #print "t_start_cw_track", t_start_cw_track
        
            dx_at_cw_track_start  = dx[t_dx>=t_start_cw_track][0]
        else:
            t_start_cw_track = None
            t_start_cw_track_before_AEBS_warning = None
            dx_at_cw_track_start = None
            
        # -----------------------------------------------------
        print  "t_start", t_start
        print  "t_stop", t_stop
        print  "v_ego_at_t_start", v_ego_kph_at_t_start
        print  "is_video_associated_at_t_start", is_video_associated_at_t_start
        print  "dx_at_t_start",  dx_at_t_start
        print  "ttc_at_t_start",  ttc_at_t_start
        print  "Stationary_at_t_start", Stationary_at_t_start
        print  "CM_status", CM_status
        print  "Audible_warning", Audible_warning
        print  "t_start_cw_track",t_start_cw_track 
        print  "t_start_cw_track_before_AEBS_warning", t_start_cw_track_before_AEBS_warning
        print  "dx_at_cw_track_start", dx_at_cw_track_start
        
        att = {}
        att["v_ego_at_t_start"]= v_ego_kph_at_t_start
        att["v_ego_at_t_stop"]= v_ego_at_t_stop
        att["v_ego_reduced"]= v_ego_reduced       
        att["is_video_associated_at_t_start"]= is_video_associated_at_t_start
        att["dx_at_t_start"]=  dx_at_t_start
        att["ttc_at_t_start"]=  ttc_at_t_start
        att["Stationary_at_t_start"]= Stationary_at_t_start
        att["CM_status"]= CM_status
        att["Audible_warning"]= Audible_warning       
        att["t_start_cw_track_before_AEBS_warning"]= t_start_cw_track_before_AEBS_warning
        att["dx_at_cw_track_start"] = dx_at_cw_track_start
        
        
        
        return att
       
    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file

        FLR20_sig = kbtools_user.cDataAC100.load_AC100_from_Source(Source)
        
        if FLR20_sig['General']['Time'] is None:
           print "%s no signals available"%(FLR20_sig['FileName'],)
           return
           
        # cm_system_status 4 "WAITING" 3 "BRAKING" 2 "WARNING" 1 "ALLOWED" 0 "NOT_ALLOWED" ;
        t_CM_warning = FLR20_sig['General']['Time']
        print "t_CM_warning", t_CM_warning
        CM_warning   = FLR20_sig['General']["cm_system_status"] >= 2

        t_CM_braking = FLR20_sig['General']['Time'] 
        CM_braking   = FLR20_sig['General']["cm_system_status"] == 3
            
        t_AudibleFeedback = FLR20_sig['Bendix_CMS']["Time"] 
        AudibleFeedback   = FLR20_sig['Bendix_CMS']["AudibleFeedback"] > 0
            
        t_XBRAccDemand = FLR20_sig['Bendix_CMS']["Time"] 
        XBRAccDemand   = FLR20_sig['Bendix_CMS']["XBRAccDemand"] < -0.5
                
            
            
        # store FLR20 signals to be used in callback function "callback_rising_edge"
        self.FLR20_sig = FLR20_sig
       
        self.H4E['CM_warning'].process(t_CM_warning, CM_warning, Source,callback_rising_edge=self.callback_rising_edge)
        self.H4E['CM_braking'].process(t_CM_braking, CM_braking, Source)
        self.H4E['AudibleFeedback'].process(t_AudibleFeedback, AudibleFeedback, Source,callback_rising_edge=self.callback_rising_edge)
        self.H4E['XBRAccDemand'].process(t_XBRAccDemand, XBRAccDemand, Source, callback_rising_edge=self.callback_rising_edge)            
        
        #except:
        #    print "error with AEBS software-in-the-loop"   

  
      
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
      
      self.kb_tex.tex('\n\\newpage\\section{FLR20EvalBendix}')
      
      # REactions Patterns REPs of Predictive Safety Systems
      self.kb_tex.tex('\n\\subsection{Bendix CM}')
 
      label = self.kb_tex.table(self.H4E['CM_warning'].table_array())
      label = self.kb_tex.table(self.H4E['CM_braking'].table_array())
      label = self.kb_tex.table(self.H4E['AudibleFeedback'].table_array())
      label = self.kb_tex.table(self.H4E['XBRAccDemand'].table_array())
     
   
      self.kb_tex.tex('\nEvalAEBS-finished')
      
     
    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        print "excel_export"
        
        WriteExcel = kbtools.cWriteExcel()

        # CM_warning, CM_braking
        AddCols = ["ttc_at_t_start","Audible_warning","CM_status","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","t_start_cw_track_before_AEBS_warning","dx_at_cw_track_start"]
        AddColsFormat = {}
        AddColsFormat["v_ego_at_t_start"] = "%3.1f km/h"
        AddColsFormat["dx_at_t_start"] = "%3.1f m"
        AddColsFormat["ttc_at_t_start"] = "%3.1f s"
        AddColsFormat["t_start_cw_track_before_AEBS_warning"] = "%4.2f s"
        AddColsFormat["dx_at_cw_track_start"] = "%3.1f m"
        WriteExcel.add_sheet_out_table_array('CM_warning',self.H4E['CM_warning'].table_array2(AddCols,AddColsFormat))
        WriteExcel.add_sheet_out_table_array('CM_braking',self.H4E['CM_braking'].table_array2())
        
        
        
        # AudibleFeedback
        AddCols = ["ttc_at_t_start","CM_status","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","t_start_cw_track_before_AEBS_warning","dx_at_cw_track_start"]
        AddColsFormat = {}
        AddColsFormat["v_ego_at_t_start"] = "%3.1f km/h"
        AddColsFormat["dx_at_t_start"] = "%3.1f m"
        AddColsFormat["ttc_at_t_start"] = "%3.1f s"
        AddColsFormat["t_start_cw_track_before_AEBS_warning"] = "%4.2f s"
        AddColsFormat["dx_at_cw_track_start"] = "%3.1f m"
        WriteExcel.add_sheet_out_table_array('AudibleFeedback',self.H4E['AudibleFeedback'].table_array2(AddCols,AddColsFormat))
        
        
        # XBRAccDemand
        AddCols = ["v_ego_reduced","ttc_at_t_start","CM_status","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","t_start_cw_track_before_AEBS_warning","dx_at_cw_track_start"]
        AddColsFormat = {}
        AddColsFormat["v_ego_reduced"] = "%6.1f km/h"
        AddColsFormat["v_ego_at_t_start"] = "%6.1f km/h"
        AddColsFormat["dx_at_t_start"] = "%3.1f m"
        AddColsFormat["ttc_at_t_start"] = "%3.1f s"
        AddColsFormat["t_start_cw_track_before_AEBS_warning"] = "%4.2f s"
        AddColsFormat["dx_at_cw_track_start"] = "%3.1f m"
        WriteExcel.add_sheet_out_table_array('XBRAccDemand',self.H4E['XBRAccDemand'].table_array2(AddCols,AddColsFormat))
      
      
        WriteExcel.save("CM_Bendix_output.xls")
        
        print "excel_export finish"
      
#-------------------------------------------------------------------------      









