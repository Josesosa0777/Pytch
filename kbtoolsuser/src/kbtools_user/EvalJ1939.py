"""
:Organization: Knorr-Bremse SfN GmbH
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: J1939 evalulation '''

''' to be called by DAS_eval.py '''

import os
import numpy as np

import kbtools
import kbtools_user

# ==============================================================================================
class cEvalJ1939():
    # ------------------------------------------------------------------------------------------
    def __init__(self):       # constructor
        self.myname = 'EvalJ1939'      # name of this user specific evaluation
        self.H4E = {}                  # H4E hunt4event directory

    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
        pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
 
       
        self.src_dir_meas = conf_DAS_eval['src_dir_meas']
      
        print "EvalJ1939::Init()"
 
        #t_join = 0 
        ## ACC1 msg - ACC Distance Alert signal
        #self.H4E['ACCDistanceAlert'] = kbtools.cHunt4Event('on_phase','ACCDistanceAlert',t_join)
        
        
        # ---------------------------------------------------------------
        # Mileage
        t_join = 0
        self.H4E['Mileage_VDHR']  = kbtools.cHunt4Event('on_phase','Mileage VDHR',t_join)
               
        
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
    def _get_v_ego(self):

        # unit: km/h
    
        FLR20_sig = self.FLR20_sig    
        
        t_v_ego = None
        v_ego = None
        
        # take signals from J1939
        if ('J1939' in FLR20_sig) and (FLR20_sig['J1939']) is not None:      
            if ("Time_MeanSpdFA" in FLR20_sig['J1939']) and FLR20_sig['J1939']["Time_MeanSpdFA"] is not None:
                print "EBC2: MeanSpdFA used"
                t_v_ego = FLR20_sig['J1939']["Time_MeanSpdFA"]
                v_ego   = FLR20_sig['J1939']["MeanSpdFA"]
            elif ("Time_WheelbasedVehSpd" in FLR20_sig['J1939']) and FLR20_sig['J1939']["Time_WheelbasedVehSpd"] is not None:
                print "CCVS1: WheelbasedVehSpd used"
                t_v_ego = FLR20_sig['J1939']["Time_WheelbasedVehSpd"]
                v_ego   = FLR20_sig['J1939']["WheelbasedVehSpd"]  
            elif ("Time_VehSpd" in FLR20_sig['J1939']) and FLR20_sig['J1939']["Time_VehSpd"] is not None:
                print "TCO1:  VehSpd used"
                t_v_ego = FLR20_sig['J1939']["Time_VehSpd"]
                v_ego   = FLR20_sig['J1939']["VehSpd"]    

        print "t_v_ego", t_v_ego
        print "v_ego", v_ego
        
        return t_v_ego, v_ego

            
    # ------------------------------------------------------------------------------------------
    def callback_rising_edge_VDHR(self,t_start,t_stop):
    
    
    
        FLR20_sig = self.FLR20_sig
       
        General_Attributes_of_VDHR = {}
    
        # ---------------------------------------------------------------
        # VehDist_start, VehDist_end, DrivenDistance
        VehDist_start     = None
        VehDist_end       = None
        DrivenDistance    = None   
        
        # 1. input signal: HRTotVehDist  (High Resolution Vehicle Distance)
        print "DrivenDistance calculation based on HRTotVehDist"
        try:
            Time_HRTotVehDist = FLR20_sig['J1939']["Time_HRTotVehDist"]
            HRTotVehDist      = FLR20_sig['J1939']["HRTotVehDist"]
            
            VehDist_start     = HRTotVehDist[0]
            VehDist_end       = HRTotVehDist[-1]
            DrivenDistance    = VehDist_end-VehDist_start
            print "HRTotVehDist: DrivenDistance [km]", DrivenDistance
 
        except:
            print "HRTotVehDist: error"
            VehDist_start     = None
            VehDist_end       = None
            DrivenDistance    = None       
    
        # if previous was not successfull try next
        # 2. input signal: TotVehDist 
        if VehDist_start is None:
            print "DrivenDistance calculation based on TotVehDist"
            try:
                Time_TotVehDist = FLR20_sig['J1939']["Time_TotVehDist"]
                TotVehDist      = FLR20_sig['J1939']["TotVehDist"]

                VehDist_start     = TotVehDist[0]
                VehDist_end       = TotVehDist[-1]
                DrivenDistance    = VehDist_end-VehDist_start
                print "TotVehDist: DrivenDistance [km]", DrivenDistance
            except:
                print "TotVehDist: error"
                VehDist_start     = None
                VehDist_end       = None
                DrivenDistance    = None       

    
    
        # ---------------------------------------------------------------
        # DrivenDistance_v_ego
        # input signal: vehicle speed 
        print "DrivenDistance_v_ego calculation based on vehicle speed"
        try:
            t_v_ego, v_ego = self._get_v_ego()   # unit: km/h
 
                
            dt_raw = np.diff(t_v_ego)
            dt = np.mean(dt_raw)
            dt_std = np.std(dt_raw)
            print "dt     [s]:", dt
            print "dt_std [s]:", dt_std
            # todo: additional check that repetition rate is reliabel
            #    e.g.  dt_std has to be less than 10% of sampling rate
            
            v_ego_cumsum = np.cumsum(v_ego)/3.6*dt/1000.0    # unit km
            
            DrivenDistance_v_ego = v_ego_cumsum[-1]
            print "DrivenDistance_v_ego [km]:", DrivenDistance_v_ego
        except:
            DrivenDistance_v_ego = None       
    
    
    
        # -------------------------------------------------------------
        # HRTotVehDist
        General_Attributes_of_VDHR['VehDist_start']   = VehDist_start
        General_Attributes_of_VDHR['VehDist_end']     = VehDist_end
        General_Attributes_of_VDHR['DrivenDistance']  = DrivenDistance
        
        # v_ego
        General_Attributes_of_VDHR['DrivenDistance_v_ego'] = DrivenDistance_v_ego
        
        # ----------------------------------------------------------------------
        # cumsum absolute steering wheel angle steps
        #Time_SteerWhlAngle =  FLR20_sig['J1939']["Time_SteerWhlAngle"]
        try:
            SteerWhlAngle = FLR20_sig['J1939']["SteerWhlAngle"]      # unit: rad
            CumsumAbsDeltaSteerWhlAngle = np.cumsum(np.fabs(np.diff(SteerWhlAngle)))
            General_Attributes_of_VDHR['CumsumAbsDeltaSteerWhlAngle'] = CumsumAbsDeltaSteerWhlAngle[-1]
        except:
            General_Attributes_of_VDHR['CumsumAbsDeltaSteerWhlAngle'] = 'error'
          
        return General_Attributes_of_VDHR
        
        
    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file
      
        print "============================================"
        print "EvalJ1939::process() - start"
        
        # --------------------------------------------
        # extract FLR20 signals from measurement (Source -> FLR20_sig)
        try:
            FLR20_sig = kbtools_user.cDataAC100.load_AC100_from_Source(Source)
            # store FLR20 signals to be used in callback function "callback_rising_edge"
            self.FLR20_sig = FLR20_sig
            
        except:
            print "error with extract FLR20 signals from measurement"   
            return
 
        print "EvalJ1939::process(): FileName: ", self.FLR20_sig['FileName']

        #Time_HRTotVehDist = FLR20_sig['J1939']["Time_HRTotVehDist"]
        #HRTotVehDist      = FLR20_sig['J1939']["HRTotVehDist"]
        #try: 
        #    self.H4E['Mileage_VDHR'].process(Time_HRTotVehDist, np.ones_like(Time_HRTotVehDist), Source,callback_rising_edge=self.callback_rising_edge_VDHR)
        #except:
        #    pass        
      
      
        t_v_ego, v_ego = self._get_v_ego()   # unit: km/h
        self.H4E['Mileage_VDHR'].process(t_v_ego, np.ones_like(v_ego), Source,callback_rising_edge=self.callback_rising_edge_VDHR)
        #try: 
        #    self.H4E['Mileage_VDHR'].process(t_v_ego, np.ones_like(v_ego), Source,callback_rising_edge=self.callback_rising_edge_VDHR)
        #except:
        #    pass        
      
      
        ## ACC1 msg - ACC Distance Alert Signal
        #try:
        #  SignalGroups = [{"ACCDistanceAlertSignal": ("ACC1_27", "ACCDistanceAlertSignal"),},]
        #  Group = Source.selectSignalGroup(SignalGroups)
        #  Time, Value = Source.getSignalFromSignalGroup(Group, "ACCDistanceAlertSignal") 
    
        #  self.H4E['ACCDistanceAlert'].process(Time, (Value>0), Source)
        #except:
        #  pass
        
        print "EvalJ1939::process() - end"
        
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
      
        # J1939 main section
        self.kb_tex.tex('\n\\newpage\\section{EvalJ1939}')
      
        # ACC1 Msg subsection
        self.kb_tex.tex('\n\\subsection{Mileage}')
 
        # ACC Distance Alert signal
        self.kb_tex.tex('\n\\subsubsection{VDHR}')
        label = self.kb_tex.table(self.H4E['Mileage_VDHR'].table_array())

        '''
        # ACC1 Msg subsection
        self.kb_tex.tex('\n\\subsection{ACC1-Msg}')
 
        # ACC Distance Alert signal
        self.kb_tex.tex('\n\\subsubsection{ACCDistanceAlert}')
        label = self.kb_tex.table(self.H4E['ACCDistanceAlert'].table_array())
        '''
        
        self.kb_tex.tex('\nEvalJ1939-finished')

    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        print "excel_export"
        print "src_dir_meas :",os.path.basename(self.src_dir_meas)
        
        # switches
        # add partial_brake and emergency_brake spreadsheets
    
        # new format 
        AddColsFormat = {}
        AddColsFormat["VehDist_start"]                        = ("ExcelNumFormat", '##0.0 "km"')  # "%3.1f km"
        AddColsFormat["VehDist_end"]                          = ("ExcelNumFormat", '##0.0 "km"')  # "%3.1f km"
        AddColsFormat["DrivenDistance"]                       = ("ExcelNumFormat", '##0.0 "km"')  # "%3.1f km"
        AddColsFormat["DrivenDistance_v_ego"]                 = ("ExcelNumFormat", '##0.0 "km"')  # "%3.1f km"
        AddColsFormat["CumsumAbsDeltaSteerWhlAngle"]          = ("ExcelNumFormat", '##0.0 "rad"')  # "%3.1f rad"
        
        
        #AddColsFormat["t_start_cw_track_before_AEBS_warning"] = ("ExcelNumFormat", '##0.00 "s"')    # "%4.2f s"
        #AddColsFormat["dx_at_cw_track_start"]                 = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        #AddColsFormat["t_offset_AEBS_warning_offline"]        = ("ExcelNumFormat", '##0.000 "s"')   # "%4.3f s"
        #AddColsFormat["ttc_at_t_start"]                       = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        #AddColsFormat["dx_at_allow_entry_global_conditions_start"] = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        
      
        WriteExcel = kbtools.cWriteExcel()

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # AEBS_warning, AEBS_partial_brake, AEBS_emergency_brake
        
        # ---------------------------------------------------
        # online
        #AddCols_online = ["t_offset_AEBS_warning_offline","AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","cm_allow_entry_global_conditions_at_t_start","cw_allow_entry_at_t_start","cmb_allow_entry_at_t_start","dx_at_allow_entry_global_conditions_start","t_start_cw_track_before_AEBS_warning"]

        AddCols_online = ['VehDist_start','VehDist_end','DrivenDistance','DrivenDistance_v_ego','CumsumAbsDeltaSteerWhlAngle']
         
                   
        WriteExcel.add_sheet_out_table_array('Mileage_VDHR',self.H4E['Mileage_VDHR'].table_array2(AddCols_online,AddColsFormat))
    
        
        # -------------------------------------------------
        # write Excel file
        ExcelFilename = "EvalJ1939_results.xls"
        if self.src_dir_meas is not None:
            ExcelFilename = "EvalJ1939_results_%s.xls"%os.path.basename(self.src_dir_meas) 
        WriteExcel.save(ExcelFilename)
       
        
      
        
        
        print "excel_export() finish"
   
#-------------------------------------------------------------------------      











