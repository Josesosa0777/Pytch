"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: FLR20 Status evalulation '''

''' to be called by DAS_eval.py '''

import os
import numpy as np

import kbtools
import kbtools_user


# ==============================================================================================
class cEvalFLR20Status():
    # ------------------------------------------------------------------------------------------
    def __init__(self):                # constructor
      self.myname = 'EvalFLR20Status'    # name of this user specific evaluation
      self.H4E = {}                    # H4E hunt4event directory

    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
      pass
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
      
      
        self.src_dir_meas = conf_DAS_eval['src_dir_meas']
          
        self.N_AO87_fault = 3
        self.ACC_S02_ActiveFault = 8
        
        # ----------------------------------------------------------------------
        # Faults on AO87
        t_join = 0
        for k in xrange(1,self.N_AO87_fault+1):  
            self.H4E['AO87_fault_%d'%k]                = kbtools.cHunt4Event('on_phase','AO87 fault %d'%k,t_join)
        
        # ----------------------------------------------------------------------
        # SIB1 on AO87
        self.H4E['SIB1_general_status_not_ok']  = kbtools.cHunt4Event('on_phase','SIB1 general status not ok',t_join)
        self.H4E['SIB1_EEPROM_error']           = kbtools.cHunt4Event('on_phase','SIB1 EEPROM error',t_join)
        self.H4E['SIB1_radar_cycle_overrun']    = kbtools.cHunt4Event('on_phase','SIB1 radar cycle overrun',t_join)
        self.H4E['SIB1_misalignment_error']     = kbtools.cHunt4Event('on_phase','SIB1 misalignment error',t_join)
        self.H4E['SIB1_antenna_blocked']        = kbtools.cHunt4Event('on_phase','SIB1 antenna blocked',t_join)
        self.H4E['SIB1_FOV_error']              = kbtools.cHunt4Event('on_phase','SIB1 FOV error',t_join)
        self.H4E['SIB1_ICE_detected']           = kbtools.cHunt4Event('on_phase','SIB1 ICE detected',t_join)

        # ------------------------------------------------------
        # SIB2 on AO87
        self.H4E['SIB2_linearity_error']         = kbtools.cHunt4Event('on_phase','SIB2 linearity error',t_join)
        self.H4E['SIB2_phase_error']             = kbtools.cHunt4Event('on_phase','SIB2 phase error',t_join)
        self.H4E['SIB2_CODI_error']              = kbtools.cHunt4Event('on_phase','SIB2 CODI error',t_join)
        self.H4E['SIB2_MMIC_power_supply_error'] = kbtools.cHunt4Event('on_phase','SIB2 MMIC power supply error',t_join)
        self.H4E['SIB2_COVI_error']              = kbtools.cHunt4Event('on_phase','SIB2 COVI error',t_join)
        self.H4E['SIB2_internal_fault_TRM_off']  = kbtools.cHunt4Event('on_phase','SIB2 internal fault TRM off',t_join)
        self.H4E['SIB2_radar_jamming_detected']  = kbtools.cHunt4Event('on_phase','SIB2 radar jamming detected',t_join)
      

        # ------------------------------------------------------
        # ACC_S02 - ActiveFaults
        for k in xrange(1,self.ACC_S02_ActiveFault+1):  
            self.H4E['ACC_S02_ActiveFault%02d'%k]        = kbtools.cHunt4Event('on_phase','ACC S02 ActiveFault%02d'%k,t_join)
         
        # ------------------------------------------------------
        # FLC20       
        self.H4E['FLC20_SensorStatus']  = kbtools.cHunt4Event('on_phase','FLC20 SensorStatus',t_join)
      
      
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
    def callback_AO87_fault(self,t_start,t_stop):
        FLR20_sig = self.FLR20_sig
        
        nr = self.par_callback_AO87_fault
        print "callback_AO87_fault_%d"%nr, t_start,t_stop
        
        # ---------------------------------------------------------------
        # fault_ID_at_t_start
        t_fault_ID = FLR20_sig['General']['Time']    
        fault_ID   = FLR20_sig['General']["fault_%d_ID"%nr]
        fault_ID_at_t_start = fault_ID[t_fault_ID>=t_start][0]

        # ---------------------------------------------------------------
        # fault_ID_bit8_at_t_start
        t_fault_ID_bit8 = FLR20_sig['General']['Time']    
        fault_ID_bit8   = FLR20_sig['General']["fault_%d_ID_bit8"%nr]
        fault_ID_bit8_at_t_start = fault_ID_bit8[t_fault_ID_bit8>=t_start][0]

        # ---------------------------------------------------------------
        # fault_snapshot_at_t_start
        t_fault_snapshot = FLR20_sig['General']['Time']    
        fault_snapshot   = FLR20_sig['General']["fault_%d_snapshot"%nr]
        fault_snapshot_at_t_start = fault_snapshot[t_fault_snapshot>=t_start][0]
            
            
        # -----------------------------------------------------
        # show for debugging
        print  "  t_start", t_start
        print  "  t_stop", t_stop
        print  "  fault_ID_at_t_start", fault_ID_at_t_start
        print  "  fault_ID_bit8_at_t_start", fault_ID_bit8_at_t_start
        print  "  fault_snapshot_at_t_start", fault_snapshot_at_t_start
        print  "  -fin-"
        
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["fault_ID_at_t_start"]        = fault_ID_at_t_start
        att["fault_ID_bit8_at_t_start"]   = fault_ID_bit8_at_t_start
        att["fault_snapshot_at_t_start"]  = fault_snapshot_at_t_start
                
        return att
    
    # ------------------------------------------------------------------------------------------
    def callback_ACC_S02_ActiveFault(self,t_start,t_stop):
        print "callback_ACC_S02_ActiveFault", t_start,t_stop
        FLR20_sig = self.FLR20_sig
        
        nr = self.par_callback_ACC_S02_ActiveFault
        
        # ---------------------------------------------------------------
        # ActiveFault_at_t_start
        t = FLR20_sig['ACC_Sxy']['Time']    
        ActiveFault  = FLR20_sig['ACC_Sxy']["ActiveFault%02d"%nr]
        ActiveFault_at_t_start = ActiveFault[t>=t_start][0]
       
        # -----------------------------------------------------
        # show for debugging
        print  "  t_start", t_start
        print  "  t_stop", t_stop
        print  "  ActiveFault_at_t_start", ActiveFault_at_t_start
        print  "  -fin-"
        
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["ActiveFault_at_t_start"]                 = ActiveFault_at_t_start
                
        return att

    # ------------------------------------------------------------------------------------------
    def callback_FLC20_SensorStatus(self,t_start,t_stop):
        print "callback_FLC20_SensorStatus", t_start,t_stop
        FLR20_sig = self.FLR20_sig
        
        # ---------------------------------------------------------------
        # ActiveFault_at_t_start
        t = FLR20_sig['FLC20']['Time']    
        SensorStatus  = FLR20_sig['FLC20']["SensorStatus"]
        SensorStatus_at_t_start = SensorStatus[t>=t_start][0]
              
        # -----------------------------------------------------
        # show for debugging
        print  "  t_start", t_start
        print  "  t_stop", t_stop
        print  "  SensorStatus_at_t_start", SensorStatus_at_t_start
        print  "  -fin-"
        
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["SensorStatus_at_t_start"]                 = SensorStatus_at_t_start
                
        return att
    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file

        # --------------------------------------------
        # extract FLR20 signals from measurement (Source -> FLR20_sig)
        FLR20_sig = kbtools_user.cDataAC100.load_AC100_from_Source(Source)
        # store FLR20 signals to be used in callback function "callback_rising_edge"
        self.FLR20_sig = FLR20_sig
        
        print self.FLR20_sig['FileName']
        
        kbtools.tell_BatchServer_WarningMsg('Hi ')
        
        if ('General' in FLR20_sig) and (FLR20_sig['General'] is not None):
            # ---------------------------------------------------------- 
            # Faults on AO87 
            t = FLR20_sig['General']['Time']  
            for k in xrange(1,self.N_AO87_fault+1):        
                self.par_callback_AO87_fault = k
                self.H4E['AO87_fault_%d'%k].process(t, FLR20_sig['General']["fault_%d_ID"%k], Source,callback_rising_edge=self.callback_AO87_fault)
                
            # ----------------------------------------------------------------------
            # SIB1 on AO87
            t = FLR20_sig['General']['Time'] 
            if FLR20_sig['General']["SIB1_general_status_ok"] is not None:
                SIB1_general_status_not_ok = np.logical_not(FLR20_sig['General']["SIB1_general_status_ok"])
            else:
                SIB1_general_status_not_ok = None
            self.H4E['SIB1_general_status_not_ok'].process(t, SIB1_general_status_not_ok, Source)
            self.H4E['SIB1_EEPROM_error'].process(t, FLR20_sig['General']["SIB1_EEPROM_error"], Source)
            self.H4E['SIB1_radar_cycle_overrun'].process(t, FLR20_sig['General']["SIB1_radar_cycle_overrun"], Source)
            self.H4E['SIB1_misalignment_error'].process(t, FLR20_sig['General']["SIB1_misalignment_error"], Source)
            self.H4E['SIB1_antenna_blocked'].process(t, FLR20_sig['General']["SIB1_antenna_blocked"], Source)
            self.H4E['SIB1_FOV_error'].process(t, FLR20_sig['General']["SIB1_FOV_error"], Source)
            self.H4E['SIB1_ICE_detected'].process(t, FLR20_sig['General']["SIB1_ICE_detected"], Source)

            # ------------------------------------------------------
            # SIB2 on AO87
            t = FLR20_sig['General']['Time'] 
            self.H4E['SIB2_linearity_error'].process(t, FLR20_sig['General']["SIB2_linearity_error"], Source)
            self.H4E['SIB2_phase_error'].process(t, FLR20_sig['General']["SIB2_phase_error"], Source)
            self.H4E['SIB2_CODI_error'].process(t, FLR20_sig['General']["SIB2_CODI_error"], Source)
            self.H4E['SIB2_MMIC_power_supply_error'].process(t, FLR20_sig['General']["SIB2_MMIC_power_supply_error"], Source)
            self.H4E['SIB2_COVI_error'].process(t, FLR20_sig['General']["SIB2_COVI_error"], Source)
            self.H4E['SIB2_internal_fault_TRM_off'].process(t, FLR20_sig['General']["SIB2_internal_fault_TRM_off"], Source)
            self.H4E['SIB2_radar_jamming_detected'].process(t, FLR20_sig['General']["SIB2_radar_jamming_detected"], Source)
 
        else:
            kbtools.tell_BatchServer_WarningMsg('EvalFLR20Status: FLC20 A087 General not available')
           
            
        # ------------------------------------------------------
        # ACC_S02 - ActiveFaults
        if ('ACC_Sxy' in FLR20_sig) and (FLR20_sig['ACC_Sxy'] is not None):

            t = FLR20_sig['ACC_Sxy']['Time']
            for k in xrange(1,self.ACC_S02_ActiveFault+1):        
                self.par_callback_ACC_S02_ActiveFault = k
            
                ActiveFault_present = None
                if FLR20_sig['ACC_Sxy']["ActiveFault%02d"%k] is not None:
                    ActiveFault_present = FLR20_sig['ACC_Sxy']["ActiveFault%02d"%k]<255
            
                self.H4E['ACC_S02_ActiveFault%02d'%k].process(t,ActiveFault_present,Source,callback_rising_edge=self.callback_ACC_S02_ActiveFault)
        else:
            kbtools.tell_BatchServer_WarningMsg('EvalFLR20Status: ACC_S02 - ActiveFaults not available')
            
     
        # ------------------------------------------------------
        # FLC20 
        if ('FLC20' in FLR20_sig) and (FLR20_sig['FLC20'] is not None):
            t = FLR20_sig['FLC20']['Time']
            FLC20_SensorStatus_not_okay = None
            if FLR20_sig['FLC20']["SensorStatus"] is not None:
                FLC20_SensorStatus_not_okay = FLR20_sig['FLC20']["SensorStatus"] >  0
        
            self.H4E['FLC20_SensorStatus'].process(t,FLC20_SensorStatus_not_okay, Source,callback_rising_edge=self.callback_FLC20_SensorStatus)        
        else:
            kbtools.tell_BatchServer_WarningMsg('EvalFLR20Status: FLC20 signals not available')

     
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
      
        self.kb_tex.tex('\n\\newpage\\section{FLR20EvalStatus}')
    
        # -----------------------------------------------------
        # Faults on AO87 
        self.kb_tex.tex('\n\\subsection{AO87 faults}')
        for k in xrange(1,self.N_AO87_fault+1):  
            label = self.kb_tex.table(self.H4E['AO87_fault_%d'%k].table_array())

        
        # ----------------------------------------------------------------------
        # SIB1 on AO87
        self.kb_tex.tex('\n\\subsection{SIB1 on AO87}')
        
        self.kb_tex.tex('\n\\subsubsection{general status not ok}')
        label = self.kb_tex.table(self.H4E['SIB1_general_status_not_ok'].table_array())
        
        self.kb_tex.tex('\n\\subsubsection{EEPROM error}')
        label = self.kb_tex.table(self.H4E['SIB1_EEPROM_error'].table_array())
        
        self.kb_tex.tex('\n\\subsubsection{radar cycle overrun}')
        label = self.kb_tex.table(self.H4E['SIB1_radar_cycle_overrun'].table_array())
        
        self.kb_tex.tex('\n\\subsubsection{misalignment error}')
        label = self.kb_tex.table(self.H4E['SIB1_misalignment_error'].table_array())
        
        self.kb_tex.tex('\n\\subsubsection{antenna blocked}')
        label = self.kb_tex.table(self.H4E['SIB1_antenna_blocked'].table_array())
        
        self.kb_tex.tex('\n\\subsubsection{FOV error}')
        label = self.kb_tex.table(self.H4E['SIB1_FOV_error'].table_array())
        
        self.kb_tex.tex('\n\\subsubsection{ICE detected}')
        label = self.kb_tex.table(self.H4E['SIB1_ICE_detected'].table_array())

        # ------------------------------------------------------
        # SIB2 on AO87
        self.kb_tex.tex('\n\\subsection{SIB1 on AO87}')
        self.kb_tex.tex('\n\\subsubsection{linearity error}')
        label = self.kb_tex.table(self.H4E['SIB2_linearity_error'].table_array())

        self.kb_tex.tex('\n\\subsubsection{phase error}')
        label = self.kb_tex.table(self.H4E['SIB2_phase_error'].table_array())

        self.kb_tex.tex('\n\\subsubsection{CODI error}')
        label = self.kb_tex.table(self.H4E['SIB2_CODI_error'].table_array())

        self.kb_tex.tex('\n\\subsubsection{MMIC power supply error}')
        label = self.kb_tex.table(self.H4E['SIB2_MMIC_power_supply_error'].table_array())

        self.kb_tex.tex('\n\\subsubsection{COVI error}')
        label = self.kb_tex.table(self.H4E['SIB2_COVI_error'].table_array())

        self.kb_tex.tex('\n\\subsubsection{internal fault TRM off}')
        label = self.kb_tex.table(self.H4E['SIB2_internal_fault_TRM_off'].table_array())

        self.kb_tex.tex('\n\\subsubsection{radar jamming detected}')
        label = self.kb_tex.table(self.H4E['SIB2_radar_jamming_detected'].table_array())

      
        # ------------------------------------------------------
        # ACC_S02 - ActiveFaults
        self.kb_tex.tex('\n\\subsection{ACC-S02 - ActiveFaults}')
        for k in xrange(1,self.ACC_S02_ActiveFault+1):  
            label = self.kb_tex.table(self.H4E['ACC_S02_ActiveFault%02d'%k].table_array())
        
        # ------------------------------------------------------
        # FLC20 
        self.kb_tex.tex('\n\\subsubsection{FLC20 SensorStatus}')
        label = self.kb_tex.table(self.H4E['FLC20_SensorStatus'].table_array())
      
     
        self.kb_tex.tex('\nEvalFLR20Status-finished')
      
     
    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        print "excel_export"
        print "src_dir_meas :",os.path.basename(self.src_dir_meas)

        # new format 
        AddColsFormat = {}
        AddColsFormat["v_ego_at_t_start"]                     = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["dx_at_t_start"]                        = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["t_start_cw_track_before_AEBS_warning"] = ("ExcelNumFormat", '##0.00 "s"')    # "%4.2f s"
        AddColsFormat["dx_at_cw_track_start"]                 = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["t_offset_AEBS_warning_offline"]        = ("ExcelNumFormat", '##0.000 "s"')   # "%4.3f s"
        
        WriteExcel = kbtools.cWriteExcel()

        # ------------------------------------------------------
        # Faults on AO87 
        AddCols_online = ["fault_ID_at_t_start","fault_ID_bit8_at_t_start","fault_snapshot_at_t_start"] 
        for k in xrange(1,self.N_AO87_fault+1):           
            WriteExcel.add_sheet_out_table_array('AO87 fault %d'%k,self.H4E['AO87_fault_%d'%k].table_array2(AddCols_online,AddColsFormat))
       
        AddCols_online = ["ActiveFault_at_t_start"] 
        for k in xrange(1,self.ACC_S02_ActiveFault+1):           
            WriteExcel.add_sheet_out_table_array('ACC S02 ActiveFault %d'%k,self.H4E['ACC_S02_ActiveFault%02d'%k].table_array2(AddCols_online,AddColsFormat))
        
        # ------------------------------------------------------
        # FLC20 
        AddCols_online = ["SensorStatus_at_t_start"] 
        WriteExcel.add_sheet_out_table_array('FLC20 SensorStatus',self.H4E['FLC20_SensorStatus'].table_array2(AddCols_online,AddColsFormat))
 

   
        
        # -------------------------------------------------
        # write Excel file
        ExcelFilename = "FLR20EvalStatus_results.xls"
        if self.src_dir_meas is not None:
            ExcelFilename = "FLR20EvalStatus_results_%s.xls"%os.path.basename(self.src_dir_meas) 
        WriteExcel.save(ExcelFilename)
               
        
        
        print "excel_export() finish"
      
#-------------------------------------------------------------------------      









