"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: FLC20 LDWS evalulation '''

''' to be called by DAS_eval.py '''

import os
import numpy as np

import kbtools
import kbtools_user
import sys, traceback



# ==============================================================================================
class cEvalFLC20LDWS():
    # ------------------------------------------------------------------------------------------
    def __init__(self):                # constructor
        self.myname = 'EvalFLC20LDWS'    # name of this user specific evaluation
        self.H4E = {}                    # H4E hunt4event directory

        self.na_values = 'NA'            # not available value for Excel
        
        
    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
        pass
    # ------------------------------------------------------------------------------------------
    def init_Simulation(self,conf_DAS_eval, verbose = True):
              
        if verbose:
            print "EvalFLC20LDWS.init_Simulation() - start" 
        
        # -------------------------------------------------------------
        # initialize re-simulations
        SilLDWS_C_list = []
        for nr in xrange(10):
            if nr == 0:
                nr_str = ''
            else:
                nr_str = "%d"%nr
                
            SilLDWS_C = self._single_init_Simulation(conf_DAS_eval, nr_str = nr_str, verbose = verbose)
            if SilLDWS_C is not None:
                SilLDWS_C_list.append((nr_str, SilLDWS_C))
                
        self.SilLDWS_C_list = SilLDWS_C_list      

        if verbose:
            print "EvalFLC20LDWS.init_Simulation() - end" 
  
    # ------------------------------------------------------------------------------------------
    def _extract_Value_from_conf_DAS_eval(self,Token,conf_DAS_eval):
        '''
           get conf_DAS_eval[Token] but ensure it's a string
        '''
        Value = None
        if Token in conf_DAS_eval:
            if isinstance(conf_DAS_eval[Token],str):
                try: 
                    Value = str(conf_DAS_eval[Token])
                except:
                    Value = None
        return Value
        
    # ------------------------------------------------------------------------------------------
    def _parse_SIM_LDWS_C_ParameterChn(self,SIM_LDWS_C_ParameterChn):
        '''       
          SIM_LDWS_C_ParameterChn -> SIM_LDWS_C_ParameterChnDict
        '''
        SIM_LDWS_C_ParameterChnDict = {}
        if SIM_LDWS_C_ParameterChn is not None:
            ParameterChn_items = SIM_LDWS_C_ParameterChn.split(';')
            for item in ParameterChn_items:
                tmp_list = item.split('=') 
                print tmp_list
                if len(tmp_list) == 2:
                    SIM_LDWS_C_ParameterChnDict[tmp_list[0]] = float(tmp_list[1])
        return SIM_LDWS_C_ParameterChnDict
                    
    # ------------------------------------------------------------------------------------------
    def _single_init_Simulation(self,conf_DAS_eval, nr_str = '', verbose = True):
        '''
        SIM_LDWS_C_ProgName              = r'C:\KBData\tmp\LDWS_C_app\LDWS_CUnit_main2.exe'
        SIM_LDWS_C_InterfaceFileName     = r'C:\KBData\sandboxes\LDWS_eclipse\LDWS_C\test\data\my_packet2\LDWS_sim_interface.py'
        SIM_LDWS_C_SimInterfaceClassName = r'C_sim_interface'
        SIM_LDWS_C_ParameterSet          = r'C:\KBData\DAS_eval\LDWS\LDWS_C\KBDiag_DPV\2014_10_27_NewConfigValues.DPV'
        SIM_LDWS_C_Input_Signal_Modifier = Force_LDW_Enabled;babu
        SIM_LDWS_C_ParameterChn          = LDW_SUPPR_BX_0X80_LNVU_ENABLE=0;babu
        '''
        
        print "nr_str", nr_str
        if nr_str: 
            tag = '_'+ nr_str
        else:
            tag = '' 
       
        
        SIM_LDWS_C_ProgName              = self._extract_Value_from_conf_DAS_eval('SIM_LDWS_C_ProgName'+tag,             conf_DAS_eval)
        SIM_LDWS_C_InterfaceFileName     = self._extract_Value_from_conf_DAS_eval('SIM_LDWS_C_InterfaceFileName'+tag,    conf_DAS_eval)
        SIM_LDWS_C_SimInterfaceClassName = self._extract_Value_from_conf_DAS_eval('SIM_LDWS_C_SimInterfaceClassName'+tag,conf_DAS_eval)
        SIM_LDWS_C_ParameterSet          = self._extract_Value_from_conf_DAS_eval('SIM_LDWS_C_ParameterSet'+tag,         conf_DAS_eval)
        SIM_LDWS_C_Input_Signal_Modifier = self._extract_Value_from_conf_DAS_eval('SIM_LDWS_C_Input_Signal_Modifier'+tag,conf_DAS_eval)
        SIM_LDWS_C_ParameterChn          = self._extract_Value_from_conf_DAS_eval('SIM_LDWS_C_ParameterChn'+tag,         conf_DAS_eval)
                
        
        print "CSimOL_MatlabBinInterface(): nr=%s"%nr_str
        print "  SIM_LDWS_C_ProgName              :", SIM_LDWS_C_ProgName
        print "  SIM_LDWS_C_InterfaceFileName     :", SIM_LDWS_C_InterfaceFileName
        print "  SIM_LDWS_C_SimInterfaceClassName :", SIM_LDWS_C_SimInterfaceClassName
        print "  SIM_LDWS_C_ParameterSet          :", SIM_LDWS_C_ParameterSet
        print "  SIM_LDWS_C_Input_Signal_Modifier :", SIM_LDWS_C_Input_Signal_Modifier
        print "  SIM_LDWS_C_ParameterChn          :", SIM_LDWS_C_ParameterChn
        
        
        # SIM_LDWS_C_ParameterChn -> SIM_LDWS_C_ParameterChnDict
        SIM_LDWS_C_ParameterChnDict =  self._parse_SIM_LDWS_C_ParameterChn(SIM_LDWS_C_ParameterChn)
        print "SIM_LDWS_C_ParameterChnDict", SIM_LDWS_C_ParameterChnDict                        
        
        
        myMetaData = kbtools_user.cMetaDataIO(self.Vehicle,verbose = verbose)
        dbc_list = myMetaData.GetMetaData(category='dbc_list')
        if (SIM_LDWS_C_ProgName is not None) and (SIM_LDWS_C_InterfaceFileName is not None) and (SIM_LDWS_C_SimInterfaceClassName is not None): 
            SilLDWS_C = kbtools.CSimOL_MatlabBinInterface(SIM_LDWS_C_ProgName,SIM_LDWS_C_InterfaceFileName,SimInterfaceClassName=SIM_LDWS_C_SimInterfaceClassName,dbc_list=dbc_list,verbose=verbose)
            # quick and dirty
            SilLDWS_C.SIM_LDWS_C_ParameterSet = SIM_LDWS_C_ParameterSet
            SilLDWS_C.SIM_LDWS_C_Input_Signal_Modifier = SIM_LDWS_C_Input_Signal_Modifier
            SilLDWS_C.SIM_LDWS_C_ParameterChnDict = SIM_LDWS_C_ParameterChnDict
            
        else:
            SilLDWS_C = None
            
        return SilLDWS_C
        
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
      
        print "EvalFLC20LDWS.init() - start"
      
        self.src_dir_meas = conf_DAS_eval['src_dir_meas']
             
                 
        # ----------------------------------------------------------------------
        # switches overwritten by conf_DAS_eval
        self.enable_LDWS_plots = False
        self.enable_LDWS_ME_plots = False
        self.enable_LDWS_LNVU_plots = False
        self.enable_LDWS_High_Lateral_Velocity_plots = False
        
        # switches Excel Spreadsheet generation 
        self.enable_ExcelSheet_ME_LDWS_warning = True
        self.enable_LDWS_ExcelSheet_reduced_mode = False
        
        # other switches
        self.Enable_FLI2_LaneTrackingStatus = False
        self.Enable_FLI2_LineType = False

        

        # ----------------------------------------------------------------------
        # LDWS outputs
        t_join = 0.0

        # on J1939 FLI1
        self.H4E['LDWS_warning_right']         = kbtools.cHunt4Event('on_phase','LDWS warning right',t_join)
        self.H4E['LDWS_warning_left']          = kbtools.cHunt4Event('on_phase','LDWS warning left',t_join)

        # Mobileye generated warnings(before suppressor)
        self.H4E['ME_LDWS_warning_right']      = kbtools.cHunt4Event('on_phase','ME LDWS warning right',t_join)
        self.H4E['ME_LDWS_warning_left']       = kbtools.cHunt4Event('on_phase','ME LDWS warning left',t_join)
        
        # LNVU generated warnings(before suppressor)
        self.H4E['LNVU_LDWS_warning_right']      = kbtools.cHunt4Event('on_phase','LNVU LDWS warning right',t_join)
        self.H4E['LNVU_LDWS_warning_left']       = kbtools.cHunt4Event('on_phase','LNVU LDWS warning left',t_join)
      
        # after suppressor
        self.H4E['LDWS_warning_right_intern']  = kbtools.cHunt4Event('on_phase','LDWS warning right intern',t_join)
        self.H4E['LDWS_warning_left_intern']   = kbtools.cHunt4Event('on_phase','LDWS warning left intern',t_join)
        
        # ----------------------------------------------------------------------
        # FLC20 SensorStatus
        t_join = 0.0
        self.H4E['FLC20_SensorStatus'] = kbtools.cHunt4Event('on_phase','FLC20 SensorStatus',t_join)
        default_value = None
        self.H4E['FLC20_SensorStatus2'] = kbtools.cHunt4Event('multi_state','FLC20 SensorStatus2',default_value)
        default_value = 0 # Fully Operational (0)
        self.H4E['FLC20_SensorStatus3'] = kbtools.cHunt4Event('multi_state','FLC20 SensorStatus3',default_value)
        default_value = [0, 1] # Fully Operational (0); "Warming up / Initializing (1)"
        self.H4E['FLC20_SensorStatus4'] = kbtools.cHunt4Event('multi_state','FLC20 SensorStatus4',default_value)

        # ----------------------------------------------------------------------
        # FLI2_CameraStatus
        default_value = []
        self.H4E['FLI2_CameraStatus'] = kbtools.cHunt4Event('multi_state','FLI2 CameraStatus',default_value)
        
        # ----------------------------------------------------------------------
        # FLI2_StateOfLDWS 
        default_value = []
        self.H4E['FLI2_StateOfLDWS'] = kbtools.cHunt4Event('multi_state','FLI2_StateOfLDWS',default_value)
    
        # ----------------------------------------------------------------------
        # LDWS DM1 
        default_value = 0 # no SPN
        self.H4E['LDWS_DM1'] = kbtools.cHunt4Event('multi_state','LDWS DM1',default_value)

    
        # ----------------------------------------------------------------------
        # FLI2_LaneTrackingStatusRight, FLI2_LaneTrackingStatusLeft
        if self.Enable_FLI2_LaneTrackingStatus:
            default_value = [0]
            self.H4E['FLI2_LaneTrackingStatusLeft']    = kbtools.cHunt4Event('multi_state','FLI2 LaneTrackingStatusLeft',default_value)
            self.H4E['FLI2_LaneTrackingStatusRight']   = kbtools.cHunt4Event('multi_state','FLI2 LaneTrackingStatusRight',default_value)

        # ----------------------------------------------------------------------
        # FLI2_LineTypeRight, FLI2_LineTypeLeft
        if self.Enable_FLI2_LineType:
            default_value = [0]
            self.H4E['FLI2_LineTypeLeft']  = kbtools.cHunt4Event('multi_state','FLI2 LineTypeLeft',default_value)
            self.H4E['FLI2_LineTypeRight'] = kbtools.cHunt4Event('multi_state','FLI2 LineTypeRight',default_value)
        
        # ----------------------------------------------------------------------
        # FLI1_LaneDepartImminentRight FLI1_LaneDepartImminentLeft
        default_value = [0]
        self.H4E['FLI1_LaneDepartImminentLeft']  = kbtools.cHunt4Event('multi_state','FLI1 LaneDepartImminentLeft',default_value)
        self.H4E['FLI1_LaneDepartImminentRight'] = kbtools.cHunt4Event('multi_state','FLI1 LaneDepartImminentRight',default_value)
        
        # ----------------------------------------------------------------------
        # FLI1_OpticalWarningRight FLI1_OpticalWarningLeft
        default_value = [0]
        self.H4E['FLI1_OpticalWarningLeft']  = kbtools.cHunt4Event('multi_state','FLI1 OpticalWarningLeft',default_value)
        self.H4E['FLI1_OpticalWarningRight'] = kbtools.cHunt4Event('multi_state','FLI1 OpticalWarningRight',default_value)

        # ----------------------------------------------------------------------
        # FLI1_AcousticalWarningRight FLI1_AcousticalWarningLeft
        default_value = [0]
        self.H4E['FLI1_AcousticalWarningLeft']  = kbtools.cHunt4Event('multi_state','FLI1 AcousticalWarningLeft',default_value)
        self.H4E['FLI1_AcousticalWarningRight'] = kbtools.cHunt4Event('multi_state','FLI1 AcousticalWarningRight',default_value)
         
        
        # ----------------------------------------------------------------------
        # Turn Signals 
        t_join = 3.0
        self.H4E['DirIndLeft']  = kbtools.cHunt4Event('on_phase','DirIndLeft',t_join)
        self.H4E['DirIndRight'] = kbtools.cHunt4Event('on_phase','DirIndRight',t_join)
           
      
        # ---------------------------------------------------------------
        # enable_LDWS_plots
        if 'enable_LDWS_plots' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['enable_LDWS_plots'],str):
                if conf_DAS_eval['enable_LDWS_plots'].lower() in ["yes","on","1"]:
                    self.enable_LDWS_plots = True    
                else:
                    self.enable_LDWS_plots = False                  

        if 'enable_LDWS_ME_plots' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['enable_LDWS_ME_plots'],str):
                if conf_DAS_eval['enable_LDWS_ME_plots'].lower() in ["yes","on","1"]:
                    self.enable_LDWS_ME_plots = True    
                else:
                    self.enable_LDWS_ME_plots = False                  

        if 'enable_LDWS_LNVU_plots' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['enable_LDWS_LNVU_plots'],str):
                if conf_DAS_eval['enable_LDWS_LNVU_plots'].lower() in ["yes","on","1"]:
                    self.enable_LDWS_LNVU_plots = True    
                else:
                    self.enable_LDWS_LNVU_plots = False                  

        if 'enable_LDWS_High_Lateral_Velocity_plots' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['enable_LDWS_High_Lateral_Velocity_plots'],str):
                if conf_DAS_eval['enable_LDWS_High_Lateral_Velocity_plots'].lower() in ["yes","on","1"]:
                    self.enable_LDWS_High_Lateral_Velocity_plots = True    
                else:
                    self.enable_LDWS_High_Lateral_Velocity_plots = False                  


        # ---------------------------------------------------------------
        # enable_ExcelSheet_ME_LDWS_warning
        if 'enable_ExcelSheet_ME_LDWS_warning' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['enable_ExcelSheet_ME_LDWS_warning'],str):
                if conf_DAS_eval['enable_ExcelSheet_ME_LDWS_warning'].lower() in ["yes","on","1"]:
                    self.enable_ExcelSheet_ME_LDWS_warning = True 
                else:
                    self.enable_ExcelSheet_ME_LDWS_warning = False 

        if 'enable_LDWS_ExcelSheet_reduced_mode' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['enable_LDWS_ExcelSheet_reduced_mode'],str):
                if conf_DAS_eval['enable_LDWS_ExcelSheet_reduced_mode'].lower() in ["yes","on","1"]:
                    self.enable_LDWS_ExcelSheet_reduced_mode = True 
                else:
                    self.enable_LDWS_ExcelSheet_reduced_mode = False 
                                            
        # ---------------------------------------------------------------
        # Vehicle information 
        self.Vehicle = None
        if 'Vehicle' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['Vehicle'],str):
                try: 
                    self.Vehicle = str(conf_DAS_eval['Vehicle'])
                except:
                    pass

        print "after reading from conf_DAS_eval"
        print "enable_LDWS_plots :", self.enable_LDWS_plots  
        print "enable_LDWS_ME_plots :", self.enable_LDWS_ME_plots  
        print "enable_LDWS_LNVU_plots :", self.enable_LDWS_LNVU_plots  
        print "enable_LDWS_High_Lateral_Velocity_plots :", self.enable_LDWS_High_Lateral_Velocity_plots
               
        
        print "enable_ExcelSheet_ME_LDWS_warning :",self.enable_ExcelSheet_ME_LDWS_warning        
        print "Vehicle", self.Vehicle
            
                  
                    
                    
        # ----------------------------------------------------------------------
        # Software-in-the-loop Simulation

        # Init LDWS Simulation
        self.init_Simulation(conf_DAS_eval)
           

 
        # ----------------------------------------------------------------------
        # SIM_WARN_isWarningLeft SIM_WARN_isWarningRight 
        # SIM_KB_LDW_Imminent_State_Left SIM_KB_LDW_Imminent_State_Right 
        # SIM_KB_LDW_Acoustical_State_Left SIM_KB_LDW_Acoustical_State_Right
        t_join = 0.0
        for nr_str, SilLDWS_C in self.SilLDWS_C_list:
            
            self.H4E['SIM_WARN_isWarningLeft'+nr_str]            = kbtools.cHunt4Event('on_phase','SIM WARN isWarningLeft'+nr_str,t_join)
            self.H4E['SIM_WARN_isWarningRight'+nr_str]           = kbtools.cHunt4Event('on_phase','SIM WARN isWarningRight'+nr_str,t_join)
        
            self.H4E['SIM_KB_LDW_Imminent_State_Left'+nr_str]    = kbtools.cHunt4Event('on_phase','SIM KB LDW Imminent State Left'+nr_str,t_join)
            self.H4E['SIM_KB_LDW_Imminent_State_Right'+nr_str]   = kbtools.cHunt4Event('on_phase','SIM KB LDW Imminent State Right'+nr_str,t_join)

            self.H4E['SIM_KB_LDW_Acoustical_State_Left'+nr_str]  = kbtools.cHunt4Event('on_phase','SIM KB LDW Acoustical State Left'+nr_str,t_join)
            self.H4E['SIM_KB_LDW_Acoustical_State_Right'+nr_str] = kbtools.cHunt4Event('on_phase','SIM KB LDW Acoustical State Right'+nr_str,t_join)
        
       
        # ----------------------------------------------------------------------
        # Driving Conditions
        t_join_High_Lateral_Velocity = 1.0

        # High Lateral Velocity 
        self.H4E['High_Lateral_Velocity_right']         = kbtools.cHunt4Event('on_phase','High Lateral Velocity right',t_join_High_Lateral_Velocity)
        self.H4E['High_Lateral_Velocity_left']          = kbtools.cHunt4Event('on_phase','High Lateral Velocity left',t_join_High_Lateral_Velocity)

      
        # ---------------------------------------------------------------
        # FLC20_Image_Delay
        self.H4E['FLC20_Image_Delay']  = kbtools.cHunt4Event('on_phase','FLC20 Image Delay',0.0)

        # ---------------------------------------------------------------
        # FLC20_ME_UpdateInterval
        self.H4E['FLC20_ME_UpdateInterval']  = kbtools.cHunt4Event('on_phase','FLC20 ME UpdateInterval',0.0)

        # ---------------------------------------------------------------
        # FLC20_TxIntervals
        self.H4E['FLC20_TxInterval_FLI1']  = kbtools.cHunt4Event('on_phase','FLC20 Tx FLI1 Intervals',0.0)
        self.H4E['FLC20_TxInterval_FLI2']  = kbtools.cHunt4Event('on_phase','FLC20 Tx FLI2 Intervals',0.0)
        
        
        # ---------------------------------------------------------------
        # load events - required for "Report_Only"
        if load_event:
            for key in self.H4E.keys():
                self.H4E[key].load_event(key)
      
      
        print "EvalFLC20LDWS.Init() - end"
  
    
    # ------------------------------------------------------------------------------------------
    def reinit(self):          # recording interrupted
        for key in self.H4E.keys():
            self.H4E[key].reinit()

    # ------------------------------------------------------------------------------------------
    #def _BX_LDW_Suppr(self, idx):
    def _BX_LDW_Suppr(self, t_start,t_stop):
        ''' 
           Bendix Lane Departure Warning Suppressor 
           
           create string list with active suppressors
        '''
        print "_BX_LDW_Suppr"
        
        F = self.FLR20_sig['FLC20_CAN']

        #if idx>0: 
        #   idx = idx -1

        if F["BX_LDW_Suppr"] is None:
            return "not available"
        
        Time_BX_LDW_Suppr = F["Time_BX_LDW_Suppr"]
        idx = np.argwhere(np.logical_and(t_start<=Time_BX_LDW_Suppr,Time_BX_LDW_Suppr<=t_stop))
               
        print "t_start,t_stop:", t_start,t_stop
        print "idx:", idx.squeeze() 
        print "F['BX_LDW_Suppr'][idx]", F["BX_LDW_Suppr"][idx].squeeze() 
        
        out = []
        if any(F["BX_LDW_Suppr_ALARM_QUIET_TIME"][idx]):
            out.append("ALARM_QUIET_TIME")
            
        if any(F["BX_LDW_Suppr_SYSTEM_DISABLED"][idx]):
            out.append("SYSTEM_DISABLED")

        if any(F["BX_LDW_Suppr_LOW_SPEED"][idx]):
            out.append("LOW_SPEED")

        if any(F["BX_LDW_Suppr_TURN_SIGNAL"][idx]): 
            out.append("TURN_SIGNAL")

        if any(F["BX_LDW_Suppr_HAZARD_LIGHTS"][idx]):  
            out.append("HAZARD_LIGHTS")
            
        if any(F["BX_LDW_Suppr_HIGH_DECEL"][idx]):
            out.append("HIGH_DECEL")

        if any(F["BX_LDW_Suppr_HIGH_LATVEL"][idx]):
            out.append("HIGH_LATVEL")

        if any(F["BX_LDW_Suppr_BRAKE_PRESSED"][idx]):
            out.append("BRAKE_PRESSED")
        
        if any(F["BX_LDW_Suppr_HIGH_CURVATURE"][idx]):
            out.append("HIGH_CURVATURE")

        if any(F["BX_LDW_Suppr_HIGH_STEERING_RATE"][idx]):
            out.append("HIGH_STEERING_RATE")

        if any(F["BX_LDW_Suppr_CONSTRUCTION_ZONE"][idx]):
            out.append("CONSTRUCTION_ZONE")
    
        if any(F["BX_LDW_Suppr_ACC_ALERT_ACTIVE"][idx]):
            out.append("ACC_ALERT_ACTIVE")
    
    
    
        return ",".join(out)    
     

    # ------------------------------------------------------------------------------------------
    def callback_LDWS_DM1(self,t_start,t_stop):
               
        print "callback_LDWS_DM1", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
        try:
            Time_DM1           = FLR20_sig['J1939']["Time_LDWS_DM1"]
            DM1_ActSPN         = FLR20_sig['J1939']["LDWS_DM1_ActSPN"]
            DM1_ActFMI         = FLR20_sig['J1939']["LDWS_DM1_ActFMI"]
            DM1_AmberWarnLStat = FLR20_sig['J1939']["LDWS_DM1_AmberWarnLStat"]
            #  J1939["LDWS_DM1_ActDtcOC"]  
            #  J1939["LDWS_DM1_ActDtcCM"]  
       
            idx = np.argwhere(np.logical_and(t_start<=Time_DM1,Time_DM1<t_stop))
            DM1_ActSPN         = np.unique(DM1_ActSPN[idx])
            DM1_ActFMI         = np.unique(DM1_ActFMI[idx])
            DM1_AmberWarnLStat = np.unique(DM1_AmberWarnLStat[idx])
        
                        
            DM1_ActSPN_str         = ";".join(["%d"%x for x in DM1_ActSPN])  
            DM1_ActFMI_str         = ";".join(["%d"%x for x in DM1_ActFMI])  
            DM1_AmberWarnLStat_str = ";".join(["%d"%x for x in DM1_AmberWarnLStat])  
             
        except Exception, e:
            print "error - callback_LDWS_DM1: ",e.message
            traceback.print_exc(file=sys.stdout)
            DM1_ActSPN_str = "error"
            DM1_ActFMI_str = "error"
            DM1_AmberWarnLStat_str = "error"
            
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["DM1_ActSPN"] = DM1_ActSPN_str  
        att["DM1_ActFMI"] = DM1_ActFMI_str  
        att["DM1_AmberWarnLStat"] = DM1_AmberWarnLStat_str  
        
        return att
             
    # ------------------------------------------------------------------------------------------
    def callback_rising_edge_FLC20_Image_Delay(self,t_start,t_stop):
           
        Attributes = {}
        
        try:
            Time_CAN_Delay = self.FLR20_sig['FLC20_CAN']["Time_CAN_Delay"]
            CAN_Delay      = self.FLR20_sig['FLC20_CAN']["CAN_Delay"]               

            max_CAN_Delay  = np.max(CAN_Delay)
            min_CAN_Delay  = np.min(CAN_Delay)
            mean_CAN_Delay = np.mean(CAN_Delay)
        except:
            max_CAN_Delay  = None
            min_CAN_Delay  = None
            mean_CAN_Delay = None
        
        Attributes['max_CAN_Delay']  = max_CAN_Delay
        Attributes['min_CAN_Delay']  = min_CAN_Delay
        Attributes['mean_CAN_Delay'] = mean_CAN_Delay
          
        return Attributes
        
    # ------------------------------------------------------------------------------------------
    def callback_rising_edge_FLC20_ME_UpdateInterval(self,t_start,t_stop):
    
               
        Attributes = {}
        
        try:
            Time_FLC20_ME_UpdateInterval, FLC20_ME_UpdateInterval = self.videopacket.getSamplingIntervals()         

            max_FLC20_ME_UpdateInterval  = np.max(FLC20_ME_UpdateInterval)
            min_FLC20_ME_UpdateInterval  = np.min(FLC20_ME_UpdateInterval)
            mean_FLC20_ME_UpdateInterval = np.mean(FLC20_ME_UpdateInterval)
        except:
            max_FLC20_ME_UpdateInterval  = None
            min_FLC20_ME_UpdateInterval  = None
            mean_FLC20_ME_UpdateInterval = None
        
        Attributes['max_FLC20_ME_UpdateInterval']  = max_FLC20_ME_UpdateInterval
        Attributes['min_FLC20_ME_UpdateInterval']  = min_FLC20_ME_UpdateInterval
        Attributes['mean_FLC20_ME_UpdateInterval'] = mean_FLC20_ME_UpdateInterval
          
        return Attributes
        
    # ------------------------------------------------------------------------------------------
    def callback_rising_edge_FLC20_TxInterval_FLI1(self,t_start,t_stop):
    
               
        Attributes = {}
        
        try:
            Time_LaneDepartImminentRight = self.FLR20_sig['J1939']["Time_LaneDepartImminentRight"]
            FLC20_FLI1_UpdateInterval = np.diff(Time_LaneDepartImminentRight)
           
            max_FLC20_FLI1_UpdateInterval  = np.max(FLC20_FLI1_UpdateInterval)
            min_FLC20_FLI1_UpdateInterval  = np.min(FLC20_FLI1_UpdateInterval)
            mean_FLC20_FLI1_UpdateInterval = np.mean(FLC20_FLI1_UpdateInterval)
        except:
            max_FLC20_FLI1_UpdateInterval  = None
            min_FLC20_FLI1_UpdateInterval  = None
            mean_FLC20_FLI1_UpdateInterval = None
        
        Attributes['max_FLC20_FLI1_UpdateInterval']  = max_FLC20_FLI1_UpdateInterval
        Attributes['min_FLC20_FLI1_UpdateInterval']  = min_FLC20_FLI1_UpdateInterval
        Attributes['mean_FLC20_FLI1_UpdateInterval'] = mean_FLC20_FLI1_UpdateInterval
          
        return Attributes
        
    # ------------------------------------------------------------------------------------------
    def callback_rising_edge_FLC20_TxInterval_FLI2(self,t_start,t_stop):
    
               
        Attributes = {}
        
        try:
            Time_StateOfLDWS = self.FLR20_sig['J1939']["Time_StateOfLDWS"]
            FLC20_FLI2_UpdateInterval = np.diff(Time_StateOfLDWS)
            
            max_FLC20_FLI2_UpdateInterval  = np.max(FLC20_FLI2_UpdateInterval)
            min_FLC20_FLI2_UpdateInterval  = np.min(FLC20_FLI2_UpdateInterval)
            mean_FLC20_FLI2_UpdateInterval = np.mean(FLC20_FLI2_UpdateInterval)
        except:
            max_FLC20_FLI2_UpdateInterval  = None
            min_FLC20_FLI2_UpdateInterval  = None
            mean_FLC20_FLI2_UpdateInterval = None
        
        Attributes['max_FLC20_FLI2_UpdateInterval']  = max_FLC20_FLI2_UpdateInterval
        Attributes['min_FLC20_FLI2_UpdateInterval']  = min_FLC20_FLI2_UpdateInterval
        Attributes['mean_FLC20_FLI2_UpdateInterval'] = mean_FLC20_FLI2_UpdateInterval
          
        return Attributes
        
    # ------------------------------------------------------------------------------------------
    def callback_DirInd(self,t_start,t_stop):
        
        print "callback_DirInd", t_start,t_stop
        FLR20_sig = self.FLR20_sig
        
        try:
            t_LaneDepartImminentLeft  = FLR20_sig["J1939"]["Time_LaneDepartImminentLeft"]
            LaneDepartImminentLeft    = FLR20_sig["J1939"]["LaneDepartImminentLeft"] 
            LDW_Left  = np.any(LaneDepartImminentLeft[np.logical_and(t_start<=t_LaneDepartImminentLeft,t_LaneDepartImminentLeft<t_stop)])
        except:
            LDW_Left = "error"
         
        try:         
            t_LaneDepartImminentRight = FLR20_sig["J1939"]["Time_LaneDepartImminentRight"]
            LaneDepartImminentRight   = FLR20_sig["J1939"]["LaneDepartImminentRight"]
            LDW_Right  = np.any(LaneDepartImminentRight[np.logical_and(t_start<=t_LaneDepartImminentRight,t_LaneDepartImminentRight<t_stop)])
        except:
            LDW_Right = "error"
    
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["LDW_Left"]             = str(LDW_Left)
        att["LDW_Right"]            = str(LDW_Right)
        
        return att
    # ------------------------------------------------------------------------------------------
  
    # ------------------------------------------------------------------------------------------
    def callback_FLI2_LineType(self,t_start,t_stop):
        
        print "callback_FLI2_LineType", t_start,t_stop
        FLR20_sig = self.FLR20_sig

        att = {}

        
        for side in ['Right', 'Left']:
            try:
                Time_LineType = FLR20_sig['J1939']["Time_LineType%s"%side]
                LineType      = FLR20_sig['J1939']["LineType%s"%side]
    
                idx = np.argwhere(np.logical_and(t_start<=Time_LineType,Time_LineType<t_stop))
                x = LineType[idx]
        
                statii_list = np.unique(x)
                print "   LineType:", statii_list
                statii_list_str =[]
                for status in statii_list:
                    if status == 0:
                        status_str = "No line detected (0)"
                    elif status == 1:
                        status_str = "Solid line detected (1)"
                    elif status == 2: 
                        status_str = "Road edge detected (2)"
                    elif status == 3: 
                        status_str = "Dashed line detected (3)"
                    elif status == 4: 
                        status_str = "Double line detected (4)"
                    elif status == 5: 
                        status_str = "Bott's dots detected (5)"
                    elif status == 6: 
                        status_str = "Error (6)"
                    elif status == 7: 
                        status_str = "Not available / not installed (7)"
                    else:
                        status_str = "Reserved (%d)"%status
                      
                    statii_list_str.append(status_str)
        
                observed_statii = ";".join(statii_list_str)
              
            except:
                observed_statii = "error"
            
            # -----------------------------------------------------
            # return dictionary with attributes
            att["%s"%side]   = observed_statii
        
        return att
           
    # ------------------------------------------------------------------------------------------
    def callback_FLI2_LaneTrackingStatus(self,t_start,t_stop):
        
        print "callback_FLI2_LaneTrackingStatus", t_start,t_stop
        FLR20_sig = self.FLR20_sig

        att = {}

        
        for side in ['Right', 'Left']:
            try:
                Time_LaneTrackingStatus = FLR20_sig['J1939']["Time_LaneTrackingStatus%s"%side]
                LaneTrackingStatus      = FLR20_sig['J1939']["LaneTrackingStatus%s"%side]
    
                idx = np.argwhere(np.logical_and(t_start<=Time_LaneTrackingStatus,Time_LaneTrackingStatus<t_stop))
                x = LaneTrackingStatus[idx]
        
                statii_list = np.unique(x)
                print "   LaneTrackingStatus:", statii_list
                statii_list_str =[]
                for status in statii_list:
                    if status == 0:
                        status_str = "Not tracking side (0)"
                    elif status == 1:
                        status_str = "Tracking side (1)"
                    elif status == 2: 
                        status_str = "Reserved (2)"
                    elif status == 3: 
                        status_str = "Don't care / take no action(3)"
                    else:
                        status_str = "Reserved (%d)"%status
                      
                    statii_list_str.append(status_str)
        
                observed_statii = ";".join(statii_list_str)
              
            except:
                observed_statii = "error"
            
            # -----------------------------------------------------
            # return dictionary with attributes
            att["%s"%side]   = observed_statii
        
        return att
            
    # ------------------------------------------------------------------------------------------
    def callback_FLI2_StateOfLDWS(self,t_start,t_stop):
        
        print "callback_FLI2_StateOfLDWS", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
        try:
            Time_StateOfLDWS = FLR20_sig['J1939']["Time_StateOfLDWS"]
            StateOfLDWS      = FLR20_sig['J1939']["StateOfLDWS"]
    
            idx = np.argwhere(np.logical_and(t_start<=Time_StateOfLDWS,Time_StateOfLDWS<t_stop))
            x = StateOfLDWS[idx]
        
            
        
            statii_list = np.unique(x)
            print "   StateOfLDWS:", statii_list
            statii_list_str =[]
            for status in statii_list:
                if status == 0:
                    status_str = "Not ready (0)"
                elif status == 1:
                    status_str = "Temporarily not available (1)"
                elif status == 2: 
                    status_str = "Deactivated by driver (2)"
                elif status == 3: 
                    status_str = "Ready (3)"
                elif status == 4: 
                    status_str = "Driver override (4)"
                elif status == 5: 
                    status_str = "Warning (5)"
                elif status == 14: 
                    status_str = "Error (14)"
                elif status == 15: 
                    status_str = "NotAvailable (15)"
                else:
                    status_str = "Reserved (%d)"%status
                      
                statii_list_str.append(status_str)
        
            observed_statii = ";".join(statii_list_str)
              
        except:
            observed_statii = "error"
            
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["observed_statii"]                    = observed_statii
        
        return att

    # ------------------------------------------------------------------------------------------
    def callback_FLI2_CameraStatus(self,t_start,t_stop):
        
        print "callback_FLI2_CameraStatus", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
        try:
            Time_SensorStatus = FLR20_sig['J1939']["Time_CameraStatus"]
            SensorStatus      = FLR20_sig['J1939']["CameraStatus"]
    
    
            idx = np.argwhere(np.logical_and(t_start<=Time_SensorStatus,Time_SensorStatus<t_stop))
            x = SensorStatus[idx]
        
            
        
            statii_list = np.unique(x)
            print "   SensorStatus:", statii_list
            statii_list_str =[]
            for status in statii_list:
                if status == 0:
                    status_str = "Fully Operational (0)"
                elif status == 1:
                    status_str = "Warming up / Initializing (1)"
                elif status == 2: 
                    status_str = "Partially Blocked (2)"
                elif status == 3: 
                    status_str = "Blocked (3)"
                elif status == 4: 
                    status_str = "Misaligned (4)"
                elif status == 14: 
                    status_str = "Error (14)"
                elif status == 15: 
                    status_str = "NotAvailable (15)"
                else:
                    status_str = "Reserved (%d)"%status
                      
                statii_list_str.append(status_str)
        
            observed_statii = ";".join(statii_list_str)
              
        except:
            observed_statii = "error"
            
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["observed_statii"]                    = observed_statii
        
        return att

    # ------------------------------------------------------------------------------------------
    def callback_SensorStatus(self,t_start,t_stop):
        
        print "callback_SensorStatus", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
        try:
            Time_SensorStatus = FLR20_sig['FLC20_CAN']["Time_SensorStatus"]
            SensorStatus      = FLR20_sig['FLC20_CAN']["SensorStatus"]
    
            idx = np.argwhere(np.logical_and(t_start<=Time_SensorStatus,Time_SensorStatus<t_stop))
            x = SensorStatus[idx]
        
            
        
            statii_list = np.unique(x)
            print "   SensorStatus:", statii_list
            statii_list_str =[]
            for status in statii_list:
                if status == 0:
                    status_str = "Fully Operational (0)"
                elif status == 1:
                    status_str = "Warming up / Initializing (1)"
                elif status == 2: 
                    status_str = "Partially Blocked (2)"
                elif status == 3: 
                    status_str = "Blocked (3)"
                elif status == 4: 
                    status_str = "Misaligned (4)"
                elif status == 14: 
                    status_str = "Error (14)"
                elif status == 15: 
                    status_str = "NotAvailable (15)"
                else:
                    status_str = "Reserved (%d)"%status
                      
                statii_list_str.append(status_str)
        
            observed_statii = ";".join(statii_list_str)
              
        except:
            observed_statii = "error"
            
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["observed_statii"]                    = observed_statii
        
        return att
                
    # ------------------------------------------------------------------------------------------
    def Is_LDW_suppressed(self, t_start, t_stop, t_LDW_before, LDW_before, t_LDW_after, LDW_after):
        '''
           check if a LDW was suppress, compare input and out of the suppressor
        
           t_LDW_before, LDW_before  : signal before the suppressor
           t_LDW_after, LDW_after    : signal after/behind the suppressor
        
        '''
        
        LDW_suppressed = "unknown"
        LDW_suppressed_reason = "unknown"
    
        if t_LDW_before is not None and t_LDW_after is not None:
            LDW_event_before  = np.any(LDW_before[np.logical_and(t_start<=t_LDW_before,t_LDW_before<t_stop)])
            LDW_event_after   = np.any(LDW_after[np.logical_and(t_start<=t_LDW_after,t_LDW_after<t_stop)])
    
            print "LDW_event_before", LDW_event_before
            print "LDW_event_after", LDW_event_after
        
            if LDW_event_before: 
                if ~LDW_event_after:
                    LDW_suppressed  = "yes"
                    #idx = np.argwhere(t_start<=t_LDW_before)[0]
                    #idx = np.argwhere(np.logical_and(t_start<=t_LDW_before,t_LDW_before<=t_stop))
                    #LDW_suppressed_reason = self._BX_LDW_Suppr(idx)    
                    LDW_suppressed_reason = self._BX_LDW_Suppr(t_start,t_stop)    
                else:
                    LDW_suppressed  = "no"
                    LDW_suppressed_reason = ""
            else:
                LDW_suppressed  = "error"
                LDW_suppressed_reason = ""
                
        print "LDW_suppressed", LDW_suppressed
        print "LDW_suppressed_reason", LDW_suppressed_reason
            

        return LDW_suppressed, LDW_suppressed_reason    
        
    # ------------------------------------------------------------------------------------------
    def CalcLDWS_Att2(self,t_start,t_stop,mode='truck'):

        att ={}   
        
        FLR20_sig = self.FLR20_sig
        
        
        if 'sim_par' in self.FLR20_sig:
            VehicleHalfWidth = (self.FLR20_sig['sim_par']['EOLDistToRtWheel'] + self.FLR20_sig['sim_par']['EOLDistToLtWheel'])/200.0
        else:
            VehicleHalfWidth  = 0.0  
        
       
       
        
               
        # ---------------------------------------------------------------
        # vehicle speed -> v_ego_at_t_start,v_ego_at_t_stop
        try:
            t_v_ego, v_ego = kbtools_user.cDataAC100.get_v_ego(FLR20_sig)
            v_ego_at_t_start, v_ego_at_t_stop = kbtools.GetValuesAtStartAndStop(t_v_ego, v_ego, t_start,t_stop) 
            min_v_ego, max_v_ego = kbtools.GetMinMaxBetweenStartAndStop(t_v_ego, v_ego, t_start,t_stop)            
        except:
            v_ego_at_t_start = self.na_values
            v_ego_at_t_stop = self.na_values
            min_v_ego = self.na_values
            max_v_ego = self.na_values
            
        att["v_ego_at_t_start"]  = v_ego_at_t_start
        att["v_ego_at_t_stop"]   = v_ego_at_t_stop
        att["min_v_ego"]         = min_v_ego
        att["max_v_ego"]         = max_v_ego
       
       
        # ---------------------------------------------------------------
        # road curvature -> road_curvature_at_t_start,road_curvature_at_t_stop
        try:
            t_road_curvature, road_curvature = kbtools_user.cDataAC100.get_road_curvature(FLR20_sig)
            road_curvature_at_t_start, road_curvature_at_t_stop = kbtools.GetValuesAtStartAndStop(t_road_curvature, road_curvature, t_start,t_stop)
        except:
            road_curvature_at_t_start = self.na_values
            road_curvature_at_t_stop = self.na_values
        att["road_curvature_at_t_start"]          = road_curvature_at_t_start
        att["road_curvature_at_t_stop"]           = road_curvature_at_t_stop

        # ---------------------------------------------------------------
        # check if warning was suppressed
       
        # warnings before suppressor
        # a) ME
        t_ME_LDW_LaneDeparture_Left  = FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Left"]
        ME_LDW_LaneDeparture_Left    = FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Left"]
        t_ME_LDW_LaneDeparture_Right = FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Right"]
        ME_LDW_LaneDeparture_Right   = FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Right"]
        # b) LNVU
        t_LNVU_isWarningLeft         = FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningLeft"]
        LNVU_isWarningLeft           = FLR20_sig['FLC20_CAN']["LNVU_isWarningLeft"]
        t_LNVU_isWarningRight        = FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningRight"]
        LNVU_isWarningRight          = FLR20_sig['FLC20_CAN']["LNVU_isWarningRight"]
       
      
        t_LDW_LaneDeparture_Left   = FLR20_sig['FLC20_CAN']["Time_LDW_LaneDeparture_Left"]
        LDW_LaneDeparture_Left     = FLR20_sig['FLC20_CAN']["LDW_LaneDeparture_Left"]
        t_LDW_LaneDeparture_Right  = FLR20_sig['FLC20_CAN']["Time_LDW_LaneDeparture_Right"]
        LDW_LaneDeparture_Right    = FLR20_sig['FLC20_CAN']["LDW_LaneDeparture_Right"]
        
        
        ME_LDW_left_suppressed, ME_LDW_left_suppressed_reason   = self.Is_LDW_suppressed(t_start, t_stop, t_ME_LDW_LaneDeparture_Left, ME_LDW_LaneDeparture_Left,  t_LDW_LaneDeparture_Left,  LDW_LaneDeparture_Left)
        ME_LDW_right_suppressed, ME_LDW_right_suppressed_reason = self.Is_LDW_suppressed(t_start, t_stop, t_ME_LDW_LaneDeparture_Right,ME_LDW_LaneDeparture_Right, t_LDW_LaneDeparture_Right, LDW_LaneDeparture_Right)
        att["ME_LDW_left_suppressed"]                 = ME_LDW_left_suppressed
        att["ME_LDW_right_suppressed"]                = ME_LDW_right_suppressed
        
        att["ME_LDW_left_suppressed_reason"]          = ME_LDW_left_suppressed_reason
        att["ME_LDW_right_suppressed_reason"]         = ME_LDW_right_suppressed_reason

        LNVU_LDW_left_suppressed, LNVU_LDW_left_suppressed_reason   = self.Is_LDW_suppressed(t_start, t_stop, t_LNVU_isWarningLeft, LNVU_isWarningLeft,  t_LDW_LaneDeparture_Left,  LDW_LaneDeparture_Left)
        LNVU_LDW_right_suppressed, LNVU_LDW_right_suppressed_reason = self.Is_LDW_suppressed(t_start, t_stop, t_LNVU_isWarningRight,LNVU_isWarningRight, t_LDW_LaneDeparture_Right, LDW_LaneDeparture_Right)
        att["LNVU_LDW_left_suppressed"]                 = LNVU_LDW_left_suppressed
        att["LNVU_LDW_right_suppressed"]                = LNVU_LDW_right_suppressed
        
        att["LNVU_LDW_left_suppressed_reason"]          = LNVU_LDW_left_suppressed_reason
        att["LNVU_LDW_right_suppressed_reason"]         = LNVU_LDW_right_suppressed_reason

        
        # ---------------------------------------------------------------
        # lane coefficients
        
        '''
        t_Left_C0  = FLR20_sig['FLC20']["Time_org_Video_Lane_Left_C0"]
        Left_C0    = FLR20_sig['FLC20']["org_Video_Lane_Left_C0"]  
        t_Right_C0 = FLR20_sig['FLC20']["Time_org_Video_Lane_Right_C0"]
        Right_C0   = FLR20_sig['FLC20']["org_Video_Lane_Right_C0"] 
        '''
        t_Left_C0  = FLR20_sig['FLC20_CAN']["Time_C0_Left"]
        Left_C0    = FLR20_sig['FLC20_CAN']["C0_Left"]  
        Left_C1    = FLR20_sig['FLC20_CAN']["C1_Left"]  
        Left_C2    = FLR20_sig['FLC20_CAN']["C2_Left"]  
        Left_C3    = FLR20_sig['FLC20_CAN']["C3_Left"]  
        
        t_Right_C0 = FLR20_sig['FLC20_CAN']["Time_C0_Right"]
        Right_C0   = FLR20_sig['FLC20_CAN']["C0_Right"] 
        Right_C1   = FLR20_sig['FLC20_CAN']["C1_Right"] 
        Right_C2   = FLR20_sig['FLC20_CAN']["C2_Right"] 
        Right_C3   = FLR20_sig['FLC20_CAN']["C3_Right"]   
       
       
        t_View_Range_Left  = FLR20_sig["FLC20_CAN"]["Time_View_Range_Left"]
        View_Range_Left    = FLR20_sig["FLC20_CAN"]["View_Range_Left"]
        t_View_Range_Right = FLR20_sig["FLC20_CAN"]["Time_View_Range_Right"]
        View_Range_Right   = FLR20_sig["FLC20_CAN"]["View_Range_Right"]
       
        T = 0.25
        
        # ---------------------------------------------
        # Left_C0_at_t_start
        # Left_C1_at_t_start
        # Left_inv_C2_at_t_start 
        # Left_inv_C3_at_t_start
        # fd_Left_C0_at_t_start

        try:        
            fd_Left_C0, f_Left_C0 = kbtools.svf_1o(t_Left_C0, Left_C0,T)
        
            Left_C0_at_t_start    = kbtools.GetPreviousSample(t_Left_C0,Left_C0,   t_start)
            Left_C0_at_t_start2, Left_C0_at_t_stop = kbtools.GetValuesAtStartAndStop(t_Left_C0, Left_C0, t_start,t_stop)  

            Left_C1_at_t_start    = kbtools.GetPreviousSample(t_Left_C0,Left_C1,   t_start)
            Left_C2_at_t_start    = kbtools.GetPreviousSample(t_Left_C0,Left_C2,   t_start)
            Left_C3_at_t_start    = kbtools.GetPreviousSample(t_Left_C0,Left_C3,   t_start)
            fd_Left_C0_at_t_start = kbtools.GetPreviousSample(t_Left_C0,fd_Left_C0,t_start)
        
            if Left_C1_at_t_start is not None:
                Left_C1_at_t_start     = Left_C1_at_t_start*180.0/np.pi
        
            Left_inv_C2_at_t_start = None
            if Left_C2_at_t_start is not None:
                Left_inv_C2_at_t_start = 1.0/Left_C2_at_t_start
        
            Left_inv_C3_at_t_start = None
            if Left_C3_at_t_start is not None:
                Left_inv_C3_at_t_start = 1.0/Left_C3_at_t_start
                
            View_Range_Left_at_t_start    = kbtools.GetPreviousSample(t_View_Range_Left,View_Range_Left,   t_start)
                 
        except:
            Left_C0_at_t_start     = None
            Left_C0_at_t_stop      = None
            Left_C1_at_t_start     = None
            Left_C2_at_t_start     = None
            Left_C3_at_t_start     = None
            Left_inv_C2_at_t_start = None
            Left_inv_C3_at_t_start = None
            fd_Left_C0_at_t_start  = None
            View_Range_Left_at_t_start = None
        att["Left_C0_at_t_start"]                  = Left_C0_at_t_start
        att["Left_C0_at_t_stop"]                   = Left_C0_at_t_stop
        att["Left_C1_at_t_start"]                  = Left_C1_at_t_start
        att["Left_C2_at_t_start"]                  = Left_C2_at_t_start
        att["Left_C3_at_t_start"]                  = Left_C3_at_t_start
        
        
        att["Left_inv_C2_at_t_start"]              = Left_inv_C2_at_t_start
        att["Left_inv_C3_at_t_start"]              = Left_inv_C3_at_t_start

        att["fd_Left_C0_at_t_start"]               = fd_Left_C0_at_t_start
        
        att["View_Range_Left_at_t_start"]          = View_Range_Left_at_t_start

        
        # ---------------------------------------------
        # Right_C0_at_t_start
        # Right_C1_at_t_start
        # Right_inv_C2_at_t_start
        # Right_inv_C3_at_t_start
        # fd_Right_C0_at_t_start

        try:
            fd_Right_C0, f_Right_C0 = kbtools.svf_1o(t_Right_C0, Right_C0,T)
        
            Right_C0_at_t_start     = kbtools.GetPreviousSample(t_Right_C0,Right_C0,   t_start)
            Right_C0_at_t_start2, Right_C0_at_t_stop = kbtools.GetValuesAtStartAndStop(t_Right_C0, Right_C0, t_start,t_stop)  
            
            Right_C1_at_t_start     = kbtools.GetPreviousSample(t_Right_C0,Right_C1,   t_start)
            Right_C2_at_t_start     = kbtools.GetPreviousSample(t_Right_C0,Right_C2,   t_start)
            Right_C3_at_t_start     = kbtools.GetPreviousSample(t_Right_C0,Right_C3,   t_start)
            fd_Right_C0_at_t_start  = kbtools.GetPreviousSample(t_Right_C0,fd_Right_C0,t_start)
 
            if Right_C1_at_t_start is not None:
                Right_C1_at_t_start     = Right_C1_at_t_start*180.0/np.pi
         
            Right_inv_C2_at_t_start = None
            if Right_C2_at_t_start is not None:
                Right_inv_C2_at_t_start = 1.0/Right_C2_at_t_start
        
            Right_inv_C3_at_t_start = None
            if Right_C3_at_t_start is not None:
                Right_inv_C3_at_t_start = 1.0/Right_C3_at_t_start
                
            View_Range_Right_at_t_start   = kbtools.GetPreviousSample(t_View_Range_Right,View_Range_Right,   t_start)
     
        except:
            Right_C0_at_t_start     = None
            Right_C0_at_t_stop      = None
            Right_C1_at_t_start     = None
            Right_C2_at_t_start     = None
            Right_C3_at_t_start     = None
            Right_inv_C2_at_t_start = None
            Right_inv_C3_at_t_start = None
            fd_Right_C0_at_t_start  = None
            View_Range_Right_at_t_start = None

        att["Right_C0_at_t_start"]                 = Right_C0_at_t_start
        att["Right_C0_at_t_stop"]                  = Right_C0_at_t_stop
        att["Right_C1_at_t_start"]                 = Right_C1_at_t_start
        att["Right_C2_at_t_start"]                 = Right_C2_at_t_start
        att["Right_C3_at_t_start"]                 = Right_C3_at_t_start
       
        att["Right_inv_C2_at_t_start"]             = Right_inv_C2_at_t_start
        att["Right_inv_C3_at_t_start"]             = Right_inv_C3_at_t_start
        
        att["fd_Right_C0_at_t_start"]              = fd_Right_C0_at_t_start
        
        att["View_Range_Right_at_t_start"]         = View_Range_Right_at_t_start

        # ---------------------------------------------
        # LaneWidth_at_t_start
        if Right_C0_at_t_start is not None and Left_C0_at_t_start is not None:
           LaneWidth_at_t_start = Right_C0_at_t_start - Left_C0_at_t_start
        else:
           LaneWidth_at_t_start = self.na_values

        att["LaneWidth_at_t_start"]                = LaneWidth_at_t_start

               
        # ---------------------------------------------
        # TLC from ME
        try:
            t_TLC_Left  = FLR20_sig['FLC20_CAN']["Time_TLC_Left"]
            TLC_Left    = FLR20_sig['FLC20_CAN']["TLC_Left"] 
        
            TLC_Left_at_t_start = kbtools.GetPreviousSample(t_TLC_Left,TLC_Left,   t_start)
        except:  
            TLC_Left_at_t_start = self.na_values
        
        try:
            t_TLC_Right = FLR20_sig['FLC20_CAN']["Time_TLC_Right"]
            TLC_Right   = FLR20_sig['FLC20_CAN']["TLC_Right"] 
            TLC_Right_at_t_start = kbtools.GetPreviousSample(t_TLC_Right,TLC_Right,   t_start)
        except:  
            TLC_Right_at_t_start = self.na_values
        att["TLC_Left_at_t_start"]                 = TLC_Left_at_t_start
        att["TLC_Right_at_t_start"]                = TLC_Right_at_t_start

        # ---------------------------------------------------------------
        # ME warning available 
        t_ME_LDW_LaneDeparture_Left  = FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Left"]
        ME_LDW_LaneDeparture_Left    = FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Left"]
        t_ME_LDW_LaneDeparture_Right = FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Right"]
        ME_LDW_LaneDeparture_Right   = FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Right"]

        t_pre = 1.5 
        t_post = 1.5
        
        iME_LDW_left  = kbtools.CIsActiveInInterval(t_start, t_stop, t_ME_LDW_LaneDeparture_Left,ME_LDW_LaneDeparture_Left,t_pre=t_pre,t_post=t_post)
        iME_LDW_right = kbtools.CIsActiveInInterval(t_start, t_stop, t_ME_LDW_LaneDeparture_Right, ME_LDW_LaneDeparture_Right,t_pre=t_pre,t_post=t_post)
            
        if iME_LDW_left.Status or iME_LDW_right.Status:
            ME_LD_present = 'yes'
        else:
            ME_LD_present = 'no'
        att["ME_LD_present"]                    = ME_LD_present
        att["ME_LD_present_Left_DeltaT"]        = iME_LDW_left.DeltaTStr
        att["ME_LD_present_Right_DeltaT"]       = iME_LDW_right.DeltaTStr
        
        # ---------------------------------------------------------------
        # LNVU warning available 
        t_LNVU_isWarningLeft         = FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningLeft"]
        LNVU_isWarningLeft           = FLR20_sig['FLC20_CAN']["LNVU_isWarningLeft"]
        t_LNVU_isWarningRight        = FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningRight"]
        LNVU_isWarningRight          = FLR20_sig['FLC20_CAN']["LNVU_isWarningRight"]
       
        t_pre = 1.5 
        t_post = 1.5
        
        iLNVU_LDW_left  = kbtools.CIsActiveInInterval(t_start, t_stop, t_LNVU_isWarningLeft,LNVU_isWarningLeft,t_pre=t_pre,t_post=t_post)
        iLNVU_LDW_right = kbtools.CIsActiveInInterval(t_start, t_stop, t_LNVU_isWarningRight, LNVU_isWarningRight,t_pre=t_pre,t_post=t_post)
            
        if iLNVU_LDW_left.Status or iLNVU_LDW_right.Status:
            LNVU_LD_present = 'yes'
        else:
            LNVU_LD_present = 'no'
        att["LNVU_LD_present"]                    = LNVU_LD_present
        att["LNVU_LD_present_Left_DeltaT"]        = iLNVU_LDW_left.DeltaTStr
        att["LNVU_LD_present_Right_DeltaT"]       = iLNVU_LDW_right.DeltaTStr
        
       

        # ---------------------------------------------
        # Lateral_Velocity  
        try:      
            if mode == 'truck':           
                Time_Lateral_Velocity_Right = FLR20_sig['FLC20_CAN']["Time_Lateral_Velocity_Right_B"]
                Lateral_Velocity_Right      = FLR20_sig['FLC20_CAN']["Lateral_Velocity_Right_B"]/100.0   # *(-1)
            elif mode == 'sim':
                Time_Lateral_Velocity_Right =  self.FLR20_sig['sim_out']['t']
                Lateral_Velocity_Right      =  self.FLR20_sig['sim_out']['BX_Lateral_Velocity_Right']               
            Lateral_Velocity_Right_at_t_start, Lateral_Velocity_Right_at_t_stop = kbtools.GetValuesAtStartAndStop(Time_Lateral_Velocity_Right, Lateral_Velocity_Right, t_start,t_stop) 
            min_Lateral_Velocity_Right, max_Lateral_Velocity_Right = kbtools.GetMinMaxBetweenStartAndStop(Time_Lateral_Velocity_Right, Lateral_Velocity_Right, t_start,t_stop) 
              
        except:
            Lateral_Velocity_Right_at_t_start = self.na_values
            Lateral_Velocity_Right_at_t_stop = self.na_values
            min_Lateral_Velocity_Right = self.na_values
            max_Lateral_Velocity_Right = self.na_values
        att["Lateral_Velocity_Right_at_t_start"]  = Lateral_Velocity_Right_at_t_start
        att["Lateral_Velocity_Right_at_t_stop"]   = Lateral_Velocity_Right_at_t_stop
        att["min_Lateral_Velocity_Right"]         = min_Lateral_Velocity_Right
        att["max_Lateral_Velocity_Right"]         = max_Lateral_Velocity_Right
        
            
        try:      
            if mode == 'truck':          
                Time_Lateral_Velocity_Left = FLR20_sig['FLC20_CAN']["Time_Lateral_Velocity_Left_B"]
                Lateral_Velocity_Left      = FLR20_sig['FLC20_CAN']["Lateral_Velocity_Left_B"]/100.0
            elif mode == 'sim':
                Time_Lateral_Velocity_Left =  self.FLR20_sig['sim_out']['t']
                Lateral_Velocity_Left      =  self.FLR20_sig['sim_out']['BX_Lateral_Velocity_Left']               

            Lateral_Velocity_Left_at_t_start, Lateral_Velocity_Left_at_t_stop = kbtools.GetValuesAtStartAndStop(Time_Lateral_Velocity_Left, Lateral_Velocity_Left, t_start,t_stop)  
            min_Lateral_Velocity_Left, max_Lateral_Velocity_Left = kbtools.GetMinMaxBetweenStartAndStop(Time_Lateral_Velocity_Left, Lateral_Velocity_Left, t_start,t_stop) 

        except:
            Lateral_Velocity_Left_at_t_start = self.na_values
            Lateral_Velocity_Left_at_t_stop = self.na_values
            min_Lateral_Velocity_Left = self.na_values
            max_Lateral_Velocity_Left = self.na_values

        att["Lateral_Velocity_Left_at_t_start"]   = Lateral_Velocity_Left_at_t_start
        att["Lateral_Velocity_Left_at_t_stop"]    = Lateral_Velocity_Left_at_t_stop
        att["min_Lateral_Velocity_Left"]         = min_Lateral_Velocity_Left
        att["max_Lateral_Velocity_Left"]         = max_Lateral_Velocity_Left
      
            
        # ---------------------------------------------
        # C0_left_wheel, C0_right_wheel - Bendix Info 1 - direct from Mobileye 
        try:
            if mode == 'truck':        
                Time_C0_left_wheel = FLR20_sig['FLC20_CAN']["Time_C0_left_wheel"]
                C0_left_wheel      = FLR20_sig['FLC20_CAN']["C0_left_wheel"]
            elif mode == 'sim':
                t_Left_C0 = FLR20_sig['FLC20_CAN']["Time_C0_Left"]
                Left_C0   = FLR20_sig['FLC20_CAN']["C0_Left"] 
                Time_C0_left_wheel = t_Left_C0
                C0_left_wheel = Left_C0 + VehicleHalfWidth
                
            C0_left_wheel_at_t_start, C0_left_wheel_at_t_stop = kbtools.GetValuesAtStartAndStop(Time_C0_left_wheel, C0_left_wheel, t_start,t_stop)  
        except:
            C0_left_wheel_at_t_start = self.na_values
            C0_left_wheel_at_t_stop = self.na_values
        att["C0_left_wheel_at_t_start"]           = C0_left_wheel_at_t_start
        att["C0_left_wheel_at_t_stop"]            = C0_left_wheel_at_t_stop
        
        try:      
            if mode == 'truck':           
                Time_C0_right_wheel = FLR20_sig['FLC20_CAN']["Time_C0_right_wheel"]
                C0_right_wheel      = FLR20_sig['FLC20_CAN']["C0_right_wheel"]
            elif mode == 'sim':
                t_Right_C0 = FLR20_sig['FLC20_CAN']["Time_C0_Right"]
                Right_C0   = FLR20_sig['FLC20_CAN']["C0_Right"] 
                Time_C0_right_wheel = t_Right_C0
                C0_right_wheel = Right_C0 - VehicleHalfWidth    
            C0_right_wheel_at_t_start, C0_right_wheel_at_t_stop = kbtools.GetValuesAtStartAndStop(Time_C0_right_wheel, C0_right_wheel, t_start,t_stop)  
        except:
            C0_right_wheel_at_t_start = self.na_values
            C0_right_wheel_at_t_stop = self.na_values
        att["C0_right_wheel_at_t_start"]          = C0_right_wheel_at_t_start
        att["C0_right_wheel_at_t_stop"]           = C0_right_wheel_at_t_stop

        # ---------------------------------------------
        # C0_left_wheel_Left_B, C0_right_wheel_Right_B - # Bendix Info 2 - after filter
        try:        
            Time_C0_left_wheel_Left_B = FLR20_sig['FLC20_CAN']["Time_C0_left_wheel_Left_B"]
            C0_left_wheel_Left_B      = FLR20_sig['FLC20_CAN']["C0_left_wheel_Left_B"]
            C0_left_wheel_at_t_start, C0_left_wheel_at_t_stop = kbtools.GetValuesAtStartAndStop(Time_C0_left_wheel_Left_B, C0_left_wheel_Left_B, t_start,t_stop)  
        except:
            C0_left_wheel_at_t_start = self.na_values
            C0_left_wheel_at_t_stop = self.na_values
        att["C0_left_wheel_filtered_at_t_start"]           = C0_left_wheel_at_t_start
        att["C0_left_wheel_filtered_at_t_stop"]            = C0_left_wheel_at_t_stop
        
        try:        
            Time_C0_right_wheel_Right_B = FLR20_sig['FLC20_CAN']["Time_C0_right_wheel_Right_B"]
            C0_right_wheel_Right_B      = FLR20_sig['FLC20_CAN']["C0_right_wheel_Right_B"]
            C0_right_wheel_at_t_start, C0_right_wheel_at_t_stop = kbtools.GetValuesAtStartAndStop(Time_C0_right_wheel_Right_B, C0_right_wheel_Right_B, t_start,t_stop)  
        except:
            C0_right_wheel_at_t_start = self.na_values
            C0_right_wheel_at_t_stop = self.na_values
        att["C0_right_wheel_filtered_at_t_start"]          = C0_right_wheel_at_t_start
        att["C0_right_wheel_filtered_at_t_stop"]           = C0_right_wheel_at_t_stop
       
       
        # ---------------------------------------------
        # Line_Changed - Mobileye Line Changes
        try: 
            Time_Me_Line_Changed_Left  = FLR20_sig["FLC20_CAN"]["Time_Me_Line_Changed_Left"]
            Me_Line_Changed_Left       = FLR20_sig["FLC20_CAN"]["Me_Line_Changed_Left"]
            iMe_Line_Changed_Left = kbtools.CIsActiveInInterval(t_start, t_stop, Time_Me_Line_Changed_Left,Me_Line_Changed_Left,t_pre = 0.1,t_post = 2.0)
        except:
            iMe_Line_Changed_Left = kbtools.CIsActiveInInterval(t_start, t_stop, None, None)
        att["Me_Line_Changed_Left"]               = iMe_Line_Changed_Left.StatusStr
        att["Me_Line_Changed_Left_DeltaT"]        = iMe_Line_Changed_Left.DeltaTStr
            
        try: 
            Time_Me_Line_Changed_Right  = FLR20_sig["FLC20_CAN"]["Time_Me_Line_Changed_Right"]
            Me_Line_Changed_Right       = FLR20_sig["FLC20_CAN"]["Me_Line_Changed_Right"]
            iMe_Line_Changed_Right = kbtools.CIsActiveInInterval(t_start, t_stop, Time_Me_Line_Changed_Right,Me_Line_Changed_Right,t_pre = 0.1,t_post = 2.0)
        except:
            iMe_Line_Changed_Right = kbtools.CIsActiveInInterval(t_start, t_stop, None, None)
        att["Me_Line_Changed_Right"]              = iMe_Line_Changed_Right.StatusStr
        att["Me_Line_Changed_Right_DeltaT"]       = iMe_Line_Changed_Right.DeltaTStr

    
        # ---------------------------------------------
        # lateral acceleration    
        try:
            t_ay, ay = kbtools_user.cDataAC100.get_ay(FLR20_sig)
            ay_at_t_start, ay_at_t_stop = kbtools.GetValuesAtStartAndStop(t_ay, ay, t_start,t_stop)  
        except:
            ay_at_t_start = self.na_values
            ay_at_t_stop = self.na_values
        att["Ay_at_t_start"]                      = ay_at_t_start 
        att["Ay_at_t_stop"]                       = ay_at_t_stop 
         
        # -----------------------------------         
        # LDW_Tracking

        t_LDW_Left_Tracking   = FLR20_sig["J1939"]["Time_LaneTrackingStatusLeft"]
        LDW_Left_Tracking     = FLR20_sig["J1939"]["LaneTrackingStatusLeft"]
        t_LDW_Right_Tracking  = FLR20_sig["J1939"]["Time_LaneTrackingStatusRight"]
        LDW_Right_Tracking    = FLR20_sig["J1939"]["LaneTrackingStatusRight"]

        t_pre = 1.0
        t_post = 1.5
        
        iLDW_Left_Tracking  = kbtools.CIsActiveInInterval(t_start, t_stop, t_LDW_Left_Tracking, LDW_Left_Tracking,t_pre=t_pre,t_post=t_post)
        iLDW_Right_Tracking = kbtools.CIsActiveInInterval(t_start, t_stop, t_LDW_Right_Tracking, LDW_Right_Tracking,t_pre=t_pre,t_post=t_post)
            
        att["Tracking_present_Left"]               = iLDW_Left_Tracking.Status
        att["Tracking_present_Right"]              = iLDW_Right_Tracking.Status
        att["Tracking_present_Left_DeltaT"]        = iLDW_Left_Tracking.DeltaTStr
        att["Tracking_present_Right_DeltaT"]       = iLDW_Right_Tracking.DeltaTStr

        # ------------------------------------------------------------------
        # OxTS 

        # distance wheel to lane marking        
        Time_LeftLinePosLateral  = FLR20_sig["OxTS"]["Time_LeftFromBPosLateral"]
        LeftLinePosLateral       = FLR20_sig["OxTS"]["LeftFromBPosLateral"] 
        Time_RightLinePosLateral = FLR20_sig["OxTS"]["Time_RightFromCPosLateral"]
        RightLinePosLateral      = FLR20_sig["OxTS"]["RightFromCPosLateral"] 
     
        # lateral velocity
        Time_LeftLineVelLateral  = FLR20_sig["OxTS"]["Time_LeftLineVelLateral"]
        LeftLineVelLateral       = FLR20_sig["OxTS"]["LeftLineVelLateral"] 
        Time_RightLineVelLateral = FLR20_sig["OxTS"]["Time_RightLineVelLateral"]
        RightLineVelLateral      = FLR20_sig["OxTS"]["RightLineVelLateral"] 

        # host vehicle acceleration
        Time_OxTS_host_AccelLateral = FLR20_sig["OxTS"]["Time_AccelLateral"]
        OxTS_host_AccelLateral      = FLR20_sig["OxTS"]["AccelLateral"]

        # filter lateral speed signal
        f_g = 2.5    # Hz
        LeftLineVelLateral_smoothed = None
        RightLineVelLateral_smoothed = None
            
        if Time_LeftLineVelLateral is not None:
            LeftLineVelLateral_smoothed  = kbtools.smooth_filter(Time_LeftLineVelLateral,  LeftLineVelLateral, f_g = f_g,  filtertype = 'acausal', valid = np.fabs(LeftLineVelLateral)< 2.0)
        if Time_RightLineVelLateral is not None:
            RightLineVelLateral_smoothed = kbtools.smooth_filter(Time_RightLineVelLateral, RightLineVelLateral,f_g = f_g,  filtertype = 'acausal', valid = np.fabs(RightLineVelLateral)< 2.0)        


        # filter lateral acceleration signal
        OxTS_host_AccelLateral_smoothed = None
        f_g = 2.5    # Hz
        if Time_OxTS_host_AccelLateral is not None:
           OxTS_host_AccelLateral_smoothed = kbtools.smooth_filter(Time_OxTS_host_AccelLateral, OxTS_host_AccelLateral ,f_g = f_g, filtertype = 'acausal',valid = np.fabs(OxTS_host_AccelLateral)< 10.0)

        LeftLinePosLateral_at_t_start              = kbtools.GetPreviousSample(Time_LeftLinePosLateral, LeftLinePosLateral, t_start)
        RightLinePosLateral_at_t_start             = kbtools.GetPreviousSample(Time_RightLinePosLateral,RightLinePosLateral,t_start)

        OxTS_host_AccelLateral_smoothed_at_t_start = kbtools.GetPreviousSample(Time_OxTS_host_AccelLateral,OxTS_host_AccelLateral_smoothed,t_start)
        LeftLineVelLateral_smoothed_at_t_start     = kbtools.GetPreviousSample(Time_LeftLineVelLateral,LeftLineVelLateral_smoothed,t_start)
        RightLineVelLateral_smoothed_at_t_start    = kbtools.GetPreviousSample(Time_RightLineVelLateral,RightLineVelLateral_smoothed,t_start)

        att["LeftLinePosLateral_at_t_start"]                 = LeftLinePosLateral_at_t_start
        att["RightLinePosLateral_at_t_start"]                = RightLinePosLateral_at_t_start
        att["LeftLineVelLateral_smoothed_at_t_start"]        = LeftLineVelLateral_smoothed_at_t_start
        att["RightLineVelLateral_smoothed_at_t_start"]       = RightLineVelLateral_smoothed_at_t_start
        att["OxTS_host_AccelLateral_smoothed_at_t_start"]    = OxTS_host_AccelLateral_smoothed_at_t_start
               
        
        # -------------------------------------------------------- 
        # steering angle and steering angle rate
        try:
            t_SteerWhlAngle = FLR20_sig["J1939"]["Time_SteerWhlAngle"]
            SteerWhlAngle   = FLR20_sig["J1939"]["SteerWhlAngle"]*180.0/np.pi
            Gradient_SteerWhlAngle = kbtools.ugdiff(t_SteerWhlAngle, SteerWhlAngle, verfahren=1)  # Backwarddifferenz 

            SteerWhlAngle_at_t_LDW_start                   = kbtools.GetPreviousSample(t_SteerWhlAngle,SteerWhlAngle,t_start)
            Gradient_SteerWhlAngle_at_t_LDW_start          = kbtools.GetPreviousSample(t_SteerWhlAngle,Gradient_SteerWhlAngle,t_start)
        except:
            SteerWhlAngle_at_t_LDW_start                   = self.na_values
            Gradient_SteerWhlAngle_at_t_LDW_start          = self.na_values
        
        att["SteerWhlAngle_at_t_LDW_start"]                  = SteerWhlAngle_at_t_LDW_start
        att["Gradient_SteerWhlAngle_at_t_LDW_start"]         = Gradient_SteerWhlAngle_at_t_LDW_start
    
        # -------------------------------------------------------- 
        return att
    # ------------------------------------------------------------------------------------------
    def callback_LDW(self,t_start,t_stop, parameters=None):
        print "callback_LDW", t_start,t_stop
        
        
        FLR20_sig = self.FLR20_sig
     
        #PlotLDWS = kbtools_user.cPlotFLC20LDWS(FLR20_sig,t_start, VehicleName=self.Vehicle)

     
        # ---------------------------------------------------------------
        # check if warning was suppressed
        
        if ('sim_out' in FLR20_sig) and (FLR20_sig['sim_out'] is not None):
            sim_out = FLR20_sig['sim_out']
            iSim_LaneDepartImminentLeft_present  = kbtools.CIsActiveInInterval(t_start, t_stop, sim_out['t'], sim_out['KB_LDW_Imminent_State_Left'] )
            iSim_LaneDepartImminentRight_present = kbtools.CIsActiveInInterval(t_start, t_stop, sim_out['t'], sim_out['KB_LDW_Imminent_State_Right'] )
        else:
            iSim_LaneDepartImminentLeft_present  = kbtools.CIsActiveInInterval(t_start, t_stop, None, None)
            iSim_LaneDepartImminentRight_present = kbtools.CIsActiveInInterval(t_start, t_stop, None, None)
            

            
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
             
        att["SIM_LDImmLeft_present"]              = iSim_LaneDepartImminentLeft_present.StatusStr
        att["SIM_LDImmLeft_present_DeltaT"]       = iSim_LaneDepartImminentLeft_present.DeltaTStr
        att["SIM_LDImmLeft_present_Duration"]     = iSim_LaneDepartImminentLeft_present.DurationStr
        att["SIM_LDImmRight_present"]             = iSim_LaneDepartImminentRight_present.StatusStr
        att["SIM_LDImmRight_present_DeltaT"]      = iSim_LaneDepartImminentRight_present.DeltaTStr
        att["SIM_LDImmRight_present_Duration"]    = iSim_LaneDepartImminentRight_present.DurationStr


        att.update(self.CalcLDWS_Att2(t_start,t_stop))

        #att["Ay_Right_at_t_start"]            = PlotLDWS.right.ay_calc_at_t_LDW  
        #att["Ay_Left_at_t_start"]             = PlotLDWS.left.ay_calc_at_t_LDW 
        
            
          

        
        # ----------------------------------------
        # plotting
        if self.enable_LDWS_plots:
            # default
            enable_LDWS_plot = False
            enable_LDWS_suppressed_plot = False
            enable_ME_LD_present_plot = False
            PngFolderBase = r'.\LDWS_png'
            PlotMode = "standard"
            PlotMode_suppressed_warning = "standard"
           
            enable_png_extract = True     # snapshots from video
            show_figures = False          # open matlablib figures
            warning_is_suppressed = False
            suffix_suppressed_warning = '_suppressed'
            
            # ---------------------------------------------------------------------------
            if (parameters is not None) and ('enable_LDWS_plot' in parameters) and (parameters['enable_LDWS_plot']):
                enable_LDWS_plot = True
                
            if (parameters is not None) and ('enable_LDWS_suppressed_plot' in parameters) and (parameters['enable_LDWS_suppressed_plot']):
                enable_LDWS_suppressed_plot = True
            
            if (parameters is not None) and ('enable_ME_LD_present_plot' in parameters) and (parameters['enable_ME_LD_present_plot']):
                enable_ME_LD_present_plot = True
            
            
            
            if (parameters is not None) and ('PngFolderBase' in parameters) and isinstance(parameters['PngFolderBase'],basestring):
                PngFolderBase = parameters['PngFolderBase'] 
             
            if (parameters is not None) and ('CalledFrom' in parameters) and isinstance(parameters['CalledFrom'],basestring):
                if parameters['CalledFrom']  == 'ME_LD':
                    warning_is_suppressed = (att["ME_LDW_left_suppressed"]  == 'yes') or (att["ME_LDW_right_suppressed"] == 'yes')
                    PlotMode_suppressed_warning = "extended"
            
                elif parameters['CalledFrom']  == 'LNVU_isWarn':
                    warning_is_suppressed = (att["LNVU_LDW_left_suppressed"] == 'yes') or (att["LNVU_LDW_right_suppressed"]  == 'yes')
                    PlotMode_suppressed_warning = "extended"
            
                elif parameters['CalledFrom']  == 'High_Lateral_Velocity':
                    PlotMode = "extended"
                    enable_ME_LD_present_plot = False
                    if att["max_v_ego"] < 55.0:
                        enable_LDWS_plot = False
        
            # ---------------------------------------------------------------------------
            if enable_LDWS_plot:
                if not warning_is_suppressed:
                    PngFolder = PngFolderBase
        
                    PlotLDWS = kbtools_user.cPlotFLC20LDWS(FLR20_sig,t_start, xlim=None, PngFolder = PngFolder, VehicleName=self.Vehicle,show_figures=show_figures,verbose=True)
                    PlotLDWS.PlotAll(enable_png_extract=enable_png_extract,mode=PlotMode)

            # ---------------------------------------------------------------------------
            if enable_LDWS_plot and enable_ME_LD_present_plot:
                # only where ME is not present
                ME_LD_present = att["ME_LD_present"]                       
                if ME_LD_present == 'no':

                    PngFolder = PngFolderBase + '_ME_LD_not_present'
        
                    PlotLDWS = kbtools_user.cPlotFLC20LDWS(FLR20_sig,t_start, xlim=None, PngFolder = PngFolder, VehicleName=self.Vehicle,show_figures=show_figures)
                    PlotLDWS.PlotAll(enable_png_extract=enable_png_extract,mode=PlotMode)
        
            # ---------------------------------------------------------------------------
            if enable_LDWS_plot and enable_LDWS_suppressed_plot:
                # suppressed warnings
                if warning_is_suppressed:

                    PngFolder = PngFolderBase + suffix_suppressed_warning
        
                    PlotLDWS = kbtools_user.cPlotFLC20LDWS(FLR20_sig,t_start, xlim=None, PngFolder = PngFolder, VehicleName=self.Vehicle,show_figures=show_figures)
                    PlotLDWS.PlotAll(enable_png_extract=enable_png_extract,mode=PlotMode_suppressed_warning)
                
                
        
        

        return att

    # ------------------------------------------------------------------------------------------
    def callback_LDW_offline(self,t_start,t_stop, parameters=None):
        print "callback_LDW_offline", t_start,t_stop
        FLR20_sig = self.FLR20_sig
     
        sim_out = FLR20_sig['sim_out']

     
        # ---------------------------------------------------------------
        # vehicle speed -> v_ego_at_t_start,v_ego_at_t_stop
        try:
            t_v_ego, v_ego = kbtools_user.cDataAC100.get_v_ego(FLR20_sig)
            v_ego_at_t_start, v_ego_at_t_stop = kbtools.GetValuesAtStartAndStop(t_v_ego, v_ego, t_start,t_stop)  
        except:
            v_ego_at_t_start = self.na_values
            v_ego_at_t_stop = self.na_values
        
       
        # ---------------------------------------------------------------
        # road curvature -> road_curvature_at_t_start,road_curvature_at_t_stop
        try:
            t_road_curvature, road_curvature = kbtools_user.cDataAC100.get_road_curvature(FLR20_sig)
            road_curvature_at_t_start, road_curvature_at_t_stop = kbtools.GetValuesAtStartAndStop(t_road_curvature, road_curvature, t_start,t_stop)
        except:
            road_curvature_at_t_start = self.na_values
            road_curvature_at_t_stop = self.na_values

        # ---------------------------------------------------------------
        # check if warning was suppressed
        
        iSim_isWarningLeft_present           = kbtools.CIsActiveInInterval(t_start, t_stop, sim_out['t'], sim_out['WARN_isWarningLeft'] )
        iSim_isWarning_presentRight          = kbtools.CIsActiveInInterval(t_start, t_stop, sim_out['t'], sim_out['WARN_isWarningRight'] )

        iSim_LaneDepartImminentLeft_present  = kbtools.CIsActiveInInterval(t_start, t_stop, sim_out['t'], sim_out['KB_LDW_Imminent_State_Left'] )
        iSim_LaneDepartImminentRight_present = kbtools.CIsActiveInInterval(t_start, t_stop, sim_out['t'], sim_out['KB_LDW_Imminent_State_Right'] )
        
        iSim_AcousticalWarningLeft_present   = kbtools.CIsActiveInInterval(t_start, t_stop, sim_out['t'], sim_out['KB_LDW_Acoustical_State_Left'] )
        iSim_AcousticalWarningRight_present  = kbtools.CIsActiveInInterval(t_start, t_stop, sim_out['t'], sim_out['KB_LDW_Acoustical_State_Right'] )

        
        # ---------------------------------------------------------------
        # compare ECU and SIM
        
        
        # --------------------------------------------------    
        # Is ECU_ME_LD present?
        t_ME_LDW_LaneDeparture_Left  = FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Left"]
        ME_LDW_LaneDeparture_Left    = FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Left"]
        t_ME_LDW_LaneDeparture_Right = FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Right"]
        ME_LDW_LaneDeparture_Right   = FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Right"]
        
        iECU_ME_LDLeft_present  = kbtools.CIsActiveInInterval(t_start, t_stop, t_ME_LDW_LaneDeparture_Left,ME_LDW_LaneDeparture_Left)
        iECU_ME_LDRight_present = kbtools.CIsActiveInInterval(t_start, t_stop, t_ME_LDW_LaneDeparture_Right, ME_LDW_LaneDeparture_Right)

        # --------------------------------------------------    
        # Is ECU_LNVU_LD present?
        t_LNVU_isWarningLeft         = FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningLeft"]
        LNVU_isWarningLeft           = FLR20_sig['FLC20_CAN']["LNVU_isWarningLeft"]
        t_LNVU_isWarningRight        = FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningRight"]
        LNVU_isWarningRight          = FLR20_sig['FLC20_CAN']["LNVU_isWarningRight"]
        
        iECU_LNVU_LDLeft_present  = kbtools.CIsActiveInInterval(t_start, t_stop, t_LNVU_isWarningLeft,LNVU_isWarningLeft)
        iECU_LNVU_LDRight_present = kbtools.CIsActiveInInterval(t_start, t_stop, t_LNVU_isWarningRight, LNVU_isWarningRight)

         
        # --------------------------------------------------    
        # Is ECU_LaneDepartImminent present?
        t_ECU_LaneDepartImminentLeft  = FLR20_sig['J1939']["Time_LaneDepartImminentLeft"]
        ECU_LaneDepartImminentLeft    = FLR20_sig['J1939']["LaneDepartImminentLeft"]
        t_ECU_LaneDepartImminentRight = FLR20_sig['J1939']["Time_LaneDepartImminentRight"]
        ECU_LaneDepartImminentRight   = FLR20_sig['J1939']["LaneDepartImminentRight"]
        
        iECU_LDImmLeft_present  = kbtools.CIsActiveInInterval(t_start, t_stop, t_ECU_LaneDepartImminentLeft,ECU_LaneDepartImminentLeft)
        iECU_LDImmRight_present = kbtools.CIsActiveInInterval(t_start, t_stop, t_ECU_LaneDepartImminentRight, ECU_LaneDepartImminentRight)
            
        # --------------------------------------------------    
        # Is ECU_AcousticalWarning present?
        t_ECU_AcousticalWarningLeft  = FLR20_sig['J1939']["Time_AcousticalWarningLeft"]
        ECU_AcousticalWarningLeft    = FLR20_sig['J1939']["AcousticalWarningLeft"]
        t_ECU_AcousticalWarningRight = FLR20_sig['J1939']["Time_AcousticalWarningRight"]
        ECU_AcousticalWarningRight   = FLR20_sig['J1939']["AcousticalWarningRight"]
        
        iECU_AcousWarnLeft_present  = kbtools.CIsActiveInInterval(t_start, t_stop, t_ECU_AcousticalWarningLeft,  ECU_AcousticalWarningLeft)
        iECU_AcousWarnRight_present = kbtools.CIsActiveInInterval(t_start, t_stop, t_ECU_AcousticalWarningRight, ECU_AcousticalWarningRight)
   
        # --------------------------------------------------    
        # Is ECU_OpticalWarning present?
        # FLR20_sig['J1939']["Time_OpticalWarningLeft"], FLR20_sig['J1939']["OpticalWarningLeft"]
        # FLR20_sig['J1939']["Time_OpticalWarningRight"], FLR20_sig['J1939']["OpticalWarningRight"]
         
          
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["v_ego_at_t_start"]                    = v_ego_at_t_start
        att["v_ego_at_t_stop"]                     = v_ego_at_t_stop
        

        '''
        att["Left_C0_at_t_start"]                  = Left_C0_at_t_start
        att["Left_C1_at_t_start"]                  = Left_C1_at_t_start
        att["Left_inv_C2_at_t_start"]              = Left_inv_C2_at_t_start
        att["Left_inv_C3_at_t_start"]              = Left_inv_C3_at_t_start

        att["fd_Left_C0_at_t_start"]               = fd_Left_C0_at_t_start
        
        att["Right_C0_at_t_start"]                 = Right_C0_at_t_start
        att["Right_C1_at_t_start"]                 = Right_C1_at_t_start
        att["Right_inv_C2_at_t_start"]             = Right_inv_C2_at_t_start
        att["Right_inv_C3_at_t_start"]             = Right_inv_C3_at_t_start
        
        att["fd_Right_C0_at_t_start"]              = fd_Right_C0_at_t_start
        att["LaneWidth_at_t_start"]                = LaneWidth_at_t_start
        att["road_curvature_at_t_start"]           = road_curvature_at_t_start
        
        att["LDW_left_suppressed"]                 = LDW_left_suppressed
        att["LDW_right_suppressed"]                = LDW_right_suppressed
        
        att["LDW_left_suppressed_reason"]          = LDW_left_suppressed_reason
        att["LDW_right_suppressed_reason"]         = LDW_right_suppressed_reason

        att["TLC_Left_at_t_start"]                 = TLC_Left_at_t_start
        att["TLC_Right_at_t_start"]                = TLC_Right_at_t_start
        
        att["ME_LD_present"]                       = ME_LD_present
        '''
            

     
        att["SIM_isWarnLeft_present"]             = iSim_isWarningLeft_present.StatusStr
        att["SIM_isWarnLeft_present_DeltaT"]      = iSim_isWarningLeft_present.DeltaTStr
        att["SIM_isWarnLeft_present_Duration"]    = iSim_isWarningLeft_present.DurationStr
        att["SIM_isWarnRight_present"]            = iSim_isWarning_presentRight.StatusStr
        att["SIM_isWarnRight_present_DeltaT"]     = iSim_isWarning_presentRight.DeltaTStr
        att["SIM_isWarnRight_present_Duration"]   = iSim_isWarning_presentRight.DurationStr
        
        att["SIM_LDImmLeft_present"]              = iSim_LaneDepartImminentLeft_present.StatusStr
        att["SIM_LDImmLeft_present_DeltaT"]       = iSim_LaneDepartImminentLeft_present.DeltaTStr
        att["SIM_LDImmLeft_present_Duration"]     = iSim_LaneDepartImminentLeft_present.DurationStr
        att["SIM_LDImmRight_present"]             = iSim_LaneDepartImminentRight_present.StatusStr
        att["SIM_LDImmRight_present_DeltaT"]      = iSim_LaneDepartImminentRight_present.DeltaTStr
        att["SIM_LDImmRight_present_Duration"]    = iSim_LaneDepartImminentRight_present.DurationStr
  
        att["SIM_AcousWarnLeft_present"]           = iSim_AcousticalWarningLeft_present.StatusStr
        att["SIM_AcousWarnLeft_present_DeltaT"]    = iSim_AcousticalWarningLeft_present.DeltaTStr
        att["SIM_AcousWarnLeft_present_Duration"]  = iSim_AcousticalWarningLeft_present.DurationStr
        att["SIM_AcousWarnRight_present"]          = iSim_AcousticalWarningRight_present.StatusStr
        att["SIM_AcousWarnRight_present_DeltaT"]   = iSim_AcousticalWarningRight_present.DeltaTStr
        att["SIM_AcousWarnRight_present_Duration"] = iSim_AcousticalWarningRight_present.DurationStr

        # ECU - Camera
 
        att["ECU_ME_LDLeft_present"]               = iECU_ME_LDLeft_present.StatusStr
        att["ECU_ME_LDLeft_present_DeltaT"]        = iECU_ME_LDLeft_present.DeltaTStr
        att["ECU_ME_LDLeft_present_Duration"]      = iECU_ME_LDLeft_present.DurationStr
        att["ECU_ME_LDRight_present"]              = iECU_ME_LDRight_present.StatusStr
        att["ECU_ME_LDRight_present_DeltaT"]       = iECU_ME_LDRight_present.DeltaTStr
        att["ECU_ME_LDRight_present_Duration"]     = iECU_ME_LDRight_present.DurationStr
        
        att["ECU_LNVU_LDLeft_present"]             = iECU_LNVU_LDLeft_present.StatusStr
        att["ECU_LNVU_LDLeft_present_DeltaT"]      = iECU_LNVU_LDLeft_present.DeltaTStr
        att["ECU_LNVU_LDLeft_present_Duration"]    = iECU_LNVU_LDLeft_present.DurationStr
        att["ECU_LNVU_LDRight_present"]            = iECU_LNVU_LDRight_present.StatusStr
        att["ECU_LNVU_LDRight_present_DeltaT"]     = iECU_LNVU_LDRight_present.DeltaTStr
        att["ECU_LNVU_LDRight_present_Duration"]   = iECU_LNVU_LDRight_present.DurationStr

        att["ECU_LDImmLeft_present"]                = iECU_LDImmLeft_present.StatusStr
        att["ECU_LDImmLeft_present_DeltaT"]         = iECU_LDImmLeft_present.DeltaTStr
        att["ECU_LDImmLeft_present_Duration"]       = iECU_LDImmLeft_present.DurationStr
        att["ECU_LDImmRight_present"]               = iECU_LDImmRight_present.StatusStr
        att["ECU_LDImmRight_present_DeltaT"]        = iECU_LDImmRight_present.DeltaTStr
        att["ECU_LDImmRight_present_Duration"]      = iECU_LDImmRight_present.DurationStr
        
        att["ECU_AcousWarnLeft_present"]            = iECU_AcousWarnLeft_present.StatusStr
        att["ECU_AcousWarnLeft_present_DeltaT"]     = iECU_AcousWarnLeft_present.DeltaTStr
        att["ECU_AcousWarnLeft_present_Duration"]   = iECU_AcousWarnLeft_present.DurationStr
        att["ECU_AcousWarnRight_present"]           = iECU_AcousWarnRight_present.StatusStr
        att["ECU_AcousWarnRight_present_DeltaT"]    = iECU_AcousWarnRight_present.DeltaTStr
        att["ECU_AcousWarnRight_present_Duration"]  = iECU_AcousWarnRight_present.DurationStr
              
        att.update(self.CalcLDWS_Att2(t_start,t_stop,mode='sim'))
      
      
      
        # ----------------------------------------
        # plotting
        if self.enable_LDWS_plots:
            if (parameters is not None) and ('enable_LDWS_plot' in parameters) and (parameters['enable_LDWS_plot']):
                enable_png_extract = True     # snapshots from video
                show_figures = False          # open matlablib figures

                if (parameters is not None) and ('nr_str' in parameters) and (parameters['nr_str']):
                    PngFolder = r'.\LDWS_Sim_png_%s'%parameters['nr_str']
                else:
                    PngFolder = r'.\LDWS_Sim_png'
                #Description = "Automatic Evaluation"
                
                SilLDWS_C = self.tmp_SilLDWS_C
                
                
                #PlotLDWS = kbtools_user.cPlotFLC20LDWS(FLR20_sig,t_start, xlim=None, PngFolder = PngFolder, VehicleName=self.Vehicle,show_figures=show_figures)
                #PlotLDWS.PlotAll(enable_png_extract=enable_png_extract)
                SilLDWS_C.BaseName = self._createVariationName(FLR20_sig['FileName'],t_start)
                SilLDWS_C.xlim = [t_start-10.0,t_stop+10.0]
                PlotLDWS = kbtools_user.cPlotFLC20LDWSSim(SilLDWS_C, PngFolder = PngFolder, t_start=t_start, VehicleName=self.Vehicle, show_figures=show_figures)
                PlotLDWS.PlotAll(enable_png_extract=enable_png_extract)
               
                # only where ME is not present
                if (parameters is not None) and ('enable_LDWS_plot_not_ME_LD_present' in parameters) and (parameters['enable_LDWS_plot_not_ME_LD_present']):
            
                    ME_LD_present = att["ME_LD_present"]                       
                    if ME_LD_present == 'no':

                        if (parameters is not None) and ('nr_str' in parameters) and (parameters['nr_str']):
                            PngFolder = r'.\LDWS_Sim_png_ME_LD_not_present_%s'%parameters['nr_str']
                        else:
                            PngFolder = r'.\LDWS_Sim_png_ME_LD_not_present'
                        #Description = "Automatic Evaluation"
                    
                        #PlotLDWS = kbtools_user.cPlotFLC20LDWS(FLR20_sig,t_start, xlim=None, PngFolder = PngFolder, VehicleName=self.Vehicle,show_figures=show_figures)
                        #PlotLDWS.PlotAll(enable_png_extract=enable_png_extract)
                        PlotLDWS = kbtools_user.cPlotFLC20LDWSSim(SilLDWS_C, PngFolder = PngFolder, t_start=t_start, VehicleName=self.Vehicle, show_figures=show_figures)
                        PlotLDWS.PlotAll(enable_png_extract=enable_png_extract)

   
        return att

    # ------------------------------------------------------------------------------------------
    def _createVariationName(self,FileName,t_start):
        print "_createVariationName() - start"
        print "FileName",FileName
        print "t_start",t_start
        
        BaseName = os.path.basename(FileName)
        BaseName_without_Ext = os.path.splitext(BaseName)[0]
        if t_start is not None:
            # <BaseName_without_Ext>@<t_start>
            t_start_str = "%7.1fs"%t_start
            t_start_str = t_start_str.replace(" ","_")
            VariationName = "%s@%s"%(BaseName_without_Ext,t_start_str)
        else:
            VariationName = BaseName_without_Ext
        print "-> VariationName",VariationName
        print "_createVariationName() - end"
        return VariationName
                
    # ------------------------------------------------------------------------------------------
    def DoSimulation(self, SilLDWS_C):
    
        print "DoSimulation"   
        VariationName = "sim"
        xlim = None
        gate = None
        Description = ""
        create_expected_results = False
        SimOutput_as_ExpectedResult = False
        
        # quick and dirty
        ParameterSet = SilLDWS_C.SIM_LDWS_C_ParameterSet
        ParameterChnDict = SilLDWS_C.SIM_LDWS_C_ParameterChnDict
        
        cfg = dict([('Input_Signal_Modifier',SilLDWS_C.SIM_LDWS_C_Input_Signal_Modifier)])
        FileBaseName_MatlabBin = r'TD_ldws_01'
        SilLDWS_C.Run(self.FLR20_sig, VariationName=VariationName,xlim=xlim,gate=gate,Description=Description,create_expected_results = create_expected_results,SimOutput_as_ExpectedResult=SimOutput_as_ExpectedResult,ParameterSet=ParameterSet,ParameterChnDict=ParameterChnDict,cfg=cfg,FileBaseName_MatlabBin=FileBaseName_MatlabBin)

        '''
        SilLDWS_C.CreateMatlabBin(self.FLR20_sig, VariationName=VariationName,xlim=xlim,gate=gate,Description=Description,create_expected_results = create_expected_results,SimOutput_as_ExpectedResult=SimOutput_as_ExpectedResult,ParameterSet=ParameterSet)
        SilLDWS_C.RunSimulation()
        SilLDWS_C.LoadMatlabBin()
        print "SilLDWS_C.matdata_output", SilLDWS_C.matdata_output
           
        SilLDWS_C.CleanUp()           
            # self.FLR20_sig['sim_out'] = self.SilLDWS_C.matdata_output
        '''
        
        print "DoSimulation - end"   
        
        
        
    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file

        print "============================================"
        print "EvalFLC20LDWS.process()"
        
        # --------------------------------------------
        # extract FLR20 signals from measurement (Source -> FLR20_sig)
        try:
            FLR20_sig = kbtools_user.cDataAC100.load_AC100_from_Source(Source)
            # store FLR20 signals to be used in callback function "callback_rising_edge"
            self.FLR20_sig = FLR20_sig
            
        except:
            print "error with extracting FLR20 signals from measurement"   
            return
 
        print "EvalFLC20LDWS.process(): FileName: ", self.FLR20_sig['FileName']
        
        
        # --------------------------------------------------------------
        try:
            t_head   = self.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Video_Data_General_A"]
            cnt_head = self.FLR20_sig["FLC20_CAN"]["Message_Counter_Video_Data_General_A"]

            t_tail   = self.FLR20_sig["FLC20_CAN"]["Time_Message_Counter_Next_Left_B"]
            cnt_tail = self.FLR20_sig["FLC20_CAN"]["Message_Counter_Next_Left_B"]

            self.videopacket = kbtools_user.CFLC20FusionMsgArray(t_head, cnt_head, t_tail, cnt_tail)
            #t_videopacket = videopacket.t_head
            
            self.videopacket.calc_delay(self.FLR20_sig["FLC20_CAN"]["Time_Frame_ID"],self.FLR20_sig["FLC20_CAN"]["Frame_ID"], self.FLR20_sig["FLC20_CAN"]["Time_LNVU_Frame_Id_LSB"],self.FLR20_sig["FLC20_CAN"]["LNVU_Frame_Id_LSB"]) 
            #t_head_BxInfo =  videopacket.t_head_BxInfo
            
       
        except Exception, e:
            print "error - CFLC20FusionMsgArray: ",e.message
            traceback.print_exc(file=sys.stdout)
            self.videopacket = None
            
        print "self.videopacket", self.videopacket 
        
        # --------------------------------------------------------------
        if 1:
            print "EVALFLC20LDWS: offline - SIM"
            
            #self.DoSimulation()
            
            
            for nr_str, SilLDWS_C in self.SilLDWS_C_list:
                try:
                    self.DoSimulation(SilLDWS_C)
                    self.tmp_SilLDWS_C = SilLDWS_C
                
                    self.FLR20_sig['sim_out'] = SilLDWS_C.matdata_output
                    self.FLR20_sig['sim_par'] = SilLDWS_C.matdata_parameters                  
        
                    sim_out = self.FLR20_sig['sim_out']
                            
                    self.H4E['SIM_WARN_isWarningLeft'+nr_str].process(sim_out['t'], sim_out['WARN_isWarningLeft'] , Source, callback_rising_edge=self.callback_LDW_offline,callback_parameters={'enable_LDWS_plot':False})
                    self.H4E['SIM_WARN_isWarningRight'+nr_str].process(sim_out['t'], sim_out['WARN_isWarningRight'] , Source, callback_rising_edge=self.callback_LDW_offline,callback_parameters={'enable_LDWS_plot':False})

                    self.H4E['SIM_KB_LDW_Imminent_State_Left'+nr_str].process(sim_out['t'], sim_out['KB_LDW_Imminent_State_Left'] , Source, callback_rising_edge=self.callback_LDW_offline, callback_parameters={'enable_LDWS_plot':True,'nr_str':nr_str})
                    self.H4E['SIM_KB_LDW_Imminent_State_Right'+nr_str].process(sim_out['t'], sim_out['KB_LDW_Imminent_State_Right'] , Source, callback_rising_edge=self.callback_LDW_offline, callback_parameters={'enable_LDWS_plot':True,'nr_str':nr_str})
            
                    self.H4E['SIM_KB_LDW_Acoustical_State_Left'+nr_str].process(sim_out['t'], sim_out['KB_LDW_Acoustical_State_Left'] , Source, callback_rising_edge=self.callback_LDW_offline, callback_parameters={'enable_LDWS_plot':False})
                    self.H4E['SIM_KB_LDW_Acoustical_State_Right'+nr_str].process(sim_out['t'], sim_out['KB_LDW_Acoustical_State_Right'] , Source, callback_rising_edge=self.callback_LDW_offline, callback_parameters={'enable_LDWS_plot':False})
                    
                except Exception, e:
                    print "error - simulation: ",e.message
                    traceback.print_exc(file=sys.stdout)
                    print " -> but we go on"
                    self.H4E['SIM_WARN_isWarningLeft'+nr_str].process(None, None , Source,             err_msg='sim error')
                    self.H4E['SIM_WARN_isWarningRight'+nr_str].process(None, None , Source,            err_msg='sim error')

                    self.H4E['SIM_KB_LDW_Imminent_State_Left'+nr_str].process(None, None , Source,     err_msg='sim error')
                    self.H4E['SIM_KB_LDW_Imminent_State_Right'+nr_str].process(None, None , Source,    err_msg='sim error')
            
                    self.H4E['SIM_KB_LDW_Acoustical_State_Left'+nr_str].process(None, None , Source,   err_msg='sim error')
                    self.H4E['SIM_KB_LDW_Acoustical_State_Right'+nr_str].process(None, None , Source,  err_msg='sim error')


        # --------------------------------------------------------------
        # online - ECU
        if 1:
            print "EVALFLC20LDWS: online - ECU"
            
            try:
                nr_str, SilLDWS_C = self.SilLDWS_C_list[0]
                self.FLR20_sig['sim_out'] = SilLDWS_C.matdata_output
            except Exception, e:
                self.FLR20_sig['sim_out'] = None
                print "error - simulation: ",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"
    
            # -------------------------------------------------    
            # Lane Departure Imminent Signal Left/Right on J1939/FLI1
            
            print "Lane Departure Imminent Signal Left/Right on J1939/FLI1"
            
            # left
            t_LaneDepartImminentLeft  = FLR20_sig["J1939"]["Time_LaneDepartImminentLeft"]
            LaneDepartImminentLeft    = FLR20_sig["J1939"]["LaneDepartImminentLeft"] 
            callback_parameters={}
            callback_parameters['enable_LDWS_plot'] = True
            callback_parameters['PngFolderBase'] = r'.\LDWS_FLI1_Imm_Left'
            self.H4E['LDWS_warning_left'].process(t_LaneDepartImminentLeft, LaneDepartImminentLeft, Source, callback_rising_edge=self.callback_LDW, callback_parameters=callback_parameters)
            
            # right
            t_LaneDepartImminentRight = FLR20_sig["J1939"]["Time_LaneDepartImminentRight"]
            LaneDepartImminentRight   = FLR20_sig["J1939"]["LaneDepartImminentRight"]
            callback_parameters={}
            callback_parameters['enable_LDWS_plot'] = True
            callback_parameters['PngFolderBase'] = r'.\LDWS_FLI1_Imm_Right'
            self.H4E['LDWS_warning_right'].process(t_LaneDepartImminentRight, LaneDepartImminentRight, Source, callback_rising_edge=self.callback_LDW, callback_parameters=callback_parameters)

            # -------------------------------------------------  
            # ME LDW - Lane Departure Warnings generated by Mobileye 

            print "ME LDW - Lane Departure Warnings generated by Mobileye"
            
            # left            
            Time_ME_LDW_LaneDeparture_Left  = FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Left"]
            ME_LDW_LaneDeparture_Left       = FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Left"]
            callback_parameters={}
            callback_parameters['enable_LDWS_plot'] = self.enable_LDWS_ME_plots
            callback_parameters['CalledFrom'] = 'ME_LD'
            callback_parameters['enable_LDWS_suppressed_plot'] = True
            callback_parameters['enable_ME_LD_present_plot'] = True
            callback_parameters['PngFolderBase'] = '.\LDWS_ME_Left'
            self.H4E['ME_LDWS_warning_left'].process(Time_ME_LDW_LaneDeparture_Left, ME_LDW_LaneDeparture_Left, Source, callback_rising_edge=self.callback_LDW,callback_parameters=callback_parameters)

            # right 
            Time_ME_LDW_LaneDeparture_Right = FLR20_sig['FLC20_CAN']["Time_ME_LDW_LaneDeparture_Right"]
            ME_LDW_LaneDeparture_Right      = FLR20_sig['FLC20_CAN']["ME_LDW_LaneDeparture_Right"]
            callback_parameters={}
            callback_parameters['enable_LDWS_plot'] = self.enable_LDWS_ME_plots
            callback_parameters['CalledFrom'] = 'ME_LD'
            callback_parameters['enable_LDWS_suppressed_plot'] = True
            callback_parameters['enable_ME_LD_present_plot'] = True
            callback_parameters['PngFolderBase'] =  r'.\LDWS_ME_Right'
            self.H4E['ME_LDWS_warning_right'].process(Time_ME_LDW_LaneDeparture_Right, ME_LDW_LaneDeparture_Right, Source, callback_rising_edge=self.callback_LDW,callback_parameters=callback_parameters)
            
            # -------------------------------------------------  
            # LNVU LDW - Lane Departure Warnings generated by LNVU 

            print "LNVU LDW - Lane Departure Warnings generated by LNVU"
            
            if self.videopacket is not None:
                # left            
                #Time_LNVU_isWarningLeft  = FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningLeft"]
                #LNVU_isWarningLeft       = FLR20_sig['FLC20_CAN']["LNVU_isWarningLeft"]
                Time_LNVU_isWarningLeft = self.videopacket.t_head_BxInfo
                LNVU_isWarningLeft  = self.videopacket.sync(self.FLR20_sig["FLC20_CAN"]["Time_LNVU_isWarningLeft"] ,self.FLR20_sig["FLC20_CAN"]["LNVU_isWarningLeft"])
                callback_parameters={}
                callback_parameters['enable_LDWS_plot'] = self.enable_LDWS_LNVU_plots
                callback_parameters['CalledFrom'] = 'LNVU_isWarn'
                callback_parameters['enable_LDWS_suppressed_plot'] = True
                callback_parameters['enable_ME_LD_present_plot'] = True
                callback_parameters['PngFolderBase'] =  r'.\LDWS_LNVU_isWarn_Left'
                self.H4E['LNVU_LDWS_warning_left'].process(Time_LNVU_isWarningLeft, LNVU_isWarningLeft, Source, callback_rising_edge=self.callback_LDW,callback_parameters=callback_parameters)
            
                # right 
                #Time_LNVU_isWarningRight = FLR20_sig['FLC20_CAN']["Time_LNVU_isWarningRight"]
                #LNVU_isWarningRight      = FLR20_sig['FLC20_CAN']["LNVU_isWarningRight"]
                Time_LNVU_isWarningRight = self.videopacket.t_head_BxInfo
                LNVU_isWarningRight  = self.videopacket.sync(self.FLR20_sig["FLC20_CAN"]["Time_LNVU_isWarningRight"] ,self.FLR20_sig["FLC20_CAN"]["LNVU_isWarningRight"])
                callback_parameters={}
                callback_parameters['enable_LDWS_plot'] = self.enable_LDWS_LNVU_plots
                callback_parameters['CalledFrom'] = 'LNVU_isWarn'
                callback_parameters['enable_LDWS_suppressed_plot'] = True
                callback_parameters['enable_ME_LD_present_plot'] = True
                callback_parameters['PngFolderBase'] =  r'.\LDWS_LNVU_isWarn_Right'

                self.H4E['LNVU_LDWS_warning_right'].process(Time_LNVU_isWarningRight, LNVU_isWarningRight, Source, callback_rising_edge=self.callback_LDW,callback_parameters=callback_parameters)
            else:
                self.H4E['LNVU_LDWS_warning_left'].process(None, None , Source,             err_msg='videopacket error')
                self.H4E['LNVU_LDWS_warning_right'].process(None, None , Source,             err_msg='videopacket error')

                    
            # -------------------------------------------------    
            # Lane Departure internal Signal (after suppressors)

            print "Lane Departure internal Signal (after suppressors)"
            
            # left
            Time_LDW_LaneDeparture_Left  = FLR20_sig['FLC20_CAN']["Time_LDW_LaneDeparture_Left"]
            LDW_LaneDeparture_Left       = FLR20_sig['FLC20_CAN']["LDW_LaneDeparture_Left"]
            self.H4E['LDWS_warning_left_intern'].process(Time_LDW_LaneDeparture_Left, LDW_LaneDeparture_Left, Source, callback_rising_edge=self.callback_LDW)

            # right
            Time_LDW_LaneDeparture_Right = FLR20_sig['FLC20_CAN']["Time_LDW_LaneDeparture_Right"]
            LDW_LaneDeparture_Right      = FLR20_sig['FLC20_CAN']["LDW_LaneDeparture_Right"]
            self.H4E['LDWS_warning_right_intern'].process(Time_LDW_LaneDeparture_Right, LDW_LaneDeparture_Right, Source, callback_rising_edge=self.callback_LDW)
            
            # ----------------------------------------------------------------------
            # FLC20 SensorStatus
 
            print "FLC20 SensorStatus"      
            
            Time_SensorStatus = FLR20_sig['FLC20_CAN']["Time_SensorStatus"]
            SensorStatus      = FLR20_sig['FLC20_CAN']["SensorStatus"]
            self.H4E['FLC20_SensorStatus'].process(Time_SensorStatus, SensorStatus>0.5, Source, callback_rising_edge=self.callback_SensorStatus)
            self.H4E['FLC20_SensorStatus2'].process(Time_SensorStatus, SensorStatus, Source, callback_rising_edge=self.callback_SensorStatus)
            self.H4E['FLC20_SensorStatus3'].process(Time_SensorStatus, SensorStatus, Source, callback_rising_edge=self.callback_SensorStatus)
            self.H4E['FLC20_SensorStatus4'].process(Time_SensorStatus, SensorStatus, Source, callback_rising_edge=self.callback_SensorStatus)
 
            
            
           
            # ----------------------------------------------------------------------
            # FLI2_CameraStatus
            self.H4E['FLI2_CameraStatus'].process(FLR20_sig['J1939']["Time_CameraStatus"], FLR20_sig['J1939']["CameraStatus"], Source, callback_rising_edge=self.callback_FLI2_CameraStatus)
 
            # ----------------------------------------------------------------------
            # FLI2_StateOfLDWS 
            self.H4E['FLI2_StateOfLDWS'].process(FLR20_sig['J1939']["Time_StateOfLDWS"], FLR20_sig['J1939']["StateOfLDWS"], Source, callback_rising_edge=self.callback_FLI2_StateOfLDWS)
  
            # ----------------------------------------------------------------------
            # FLI2_LaneTrackingStatusLeft FLI2_LaneTrackingStatusRight
            if self.Enable_FLI2_LaneTrackingStatus:
                self.H4E['FLI2_LaneTrackingStatusLeft'].process(FLR20_sig['J1939']["Time_LaneTrackingStatusLeft"], FLR20_sig['J1939']["LaneTrackingStatusLeft"], Source, callback_rising_edge=self.callback_FLI2_LaneTrackingStatus)
                self.H4E['FLI2_LaneTrackingStatusRight'].process(FLR20_sig['J1939']["Time_LaneTrackingStatusRight"], FLR20_sig['J1939']["LaneTrackingStatusRight"], Source, callback_rising_edge=self.callback_FLI2_LaneTrackingStatus)
   
            # ----------------------------------------------------------------------
            # FLI2_LineTypeLeft FLI2_LineTypeRight
            if self.Enable_FLI2_LineType:
                self.H4E['FLI2_LineTypeLeft'].process(FLR20_sig['J1939']["Time_LineTypeLeft"], FLR20_sig['J1939']["LineTypeLeft"], Source, callback_rising_edge=self.callback_FLI2_LineType)
                self.H4E['FLI2_LineTypeRight'].process(FLR20_sig['J1939']["Time_LineTypeRight"], FLR20_sig['J1939']["LineTypeRight"], Source, callback_rising_edge=self.callback_FLI2_LineType)
 
       
            # ----------------------------------------------------------------------
            # FLI1_LaneDepartImminentLeft FLI1_LaneDepartImminentRight 
            self.H4E['FLI1_LaneDepartImminentLeft'].process(FLR20_sig['J1939']["Time_LaneDepartImminentLeft"], FLR20_sig['J1939']["LaneDepartImminentLeft"], Source, callback_rising_edge=None)
            self.H4E['FLI1_LaneDepartImminentRight'].process(FLR20_sig['J1939']["Time_LaneDepartImminentRight"], FLR20_sig['J1939']["LaneDepartImminentRight"], Source, callback_rising_edge=None)

            # ----------------------------------------------------------------------
            # FLI1_OpticalWarningLeft FLI1_OpticalWarningRight 
            self.H4E['FLI1_OpticalWarningLeft'].process(FLR20_sig['J1939']["Time_OpticalWarningLeft"], FLR20_sig['J1939']["OpticalWarningLeft"], Source, callback_rising_edge=None)
            self.H4E['FLI1_OpticalWarningRight'].process(FLR20_sig['J1939']["Time_OpticalWarningRight"], FLR20_sig['J1939']["OpticalWarningRight"], Source, callback_rising_edge=None)
    
            # ----------------------------------------------------------------------
            # FLI1_AcousticalWarningLeft FLI1_AcousticalWarningRight 
            self.H4E['FLI1_AcousticalWarningLeft'].process(FLR20_sig['J1939']["Time_AcousticalWarningLeft"], FLR20_sig['J1939']["AcousticalWarningLeft"], Source, callback_rising_edge=None)
            self.H4E['FLI1_AcousticalWarningRight'].process(FLR20_sig['J1939']["Time_AcousticalWarningRight"], FLR20_sig['J1939']["AcousticalWarningRight"], Source, callback_rising_edge=None)
      
            
            
            # ----------------------------------------------------------------------
            # Turn Signal Indicator
            Time_DirIndL_b  = FLR20_sig['J1939']["Time_DirIndL_b"]
            DirIndL_b       = FLR20_sig['J1939']["DirIndL_b"] 
            Time_DirIndR_b  = FLR20_sig['J1939']["Time_DirIndR_b"]
            DirIndR_b       = FLR20_sig['J1939']["DirIndR_b"]
            self.H4E['DirIndLeft'].process(Time_DirIndL_b, DirIndL_b, Source, callback_rising_edge=self.callback_DirInd)
            self.H4E['DirIndRight'].process(Time_DirIndR_b, DirIndR_b, Source, callback_rising_edge=self.callback_DirInd)
        
            # ----------------------------------------------------------------------
            # AEBS DM1_2A 
            self.H4E['LDWS_DM1'].process(FLR20_sig['J1939']["Time_LDWS_DM1"], FLR20_sig['J1939']["LDWS_DM1_ActSPN"], Source, callback_rising_edge=self.callback_LDWS_DM1)
           

            # ----------------------------------------------------------------------
            # High Lateral Velocity 
            print "High Lateral Velocity "
            
            try:        
                Time_Lateral_Velocity_Right = FLR20_sig['FLC20_CAN']["Time_Lateral_Velocity_Right_B"]
                Lateral_Velocity_Right      = FLR20_sig['FLC20_CAN']["Lateral_Velocity_Right_B"]/100.0   # *(-1)
                High_Lateral_Velocity_Right = Lateral_Velocity_Right>0.6
                callback_parameters = {}
                callback_parameters['enable_LDWS_plot'] = self.enable_LDWS_High_Lateral_Velocity_plots
                callback_parameters['CalledFrom'] = 'High_Lateral_Velocity'
                callback_parameters['PngFolderBase'] =  r'.\High_Lateral_Velocity_Right'
                self.H4E['High_Lateral_Velocity_right'].process(Time_Lateral_Velocity_Right,High_Lateral_Velocity_Right , Source, callback_rising_edge=self.callback_LDW, callback_parameters=callback_parameters)
            except Exception, e:
                print "error - High Lateral Velocity Right: ",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"
                self.H4E['High_Lateral_Velocity_right'].process(None, None , Source,             err_msg='sim error')
            
            try:        
                Time_Lateral_Velocity_Left = FLR20_sig['FLC20_CAN']["Time_Lateral_Velocity_Left_B"]
                Lateral_Velocity_Left      = FLR20_sig['FLC20_CAN']["Lateral_Velocity_Left_B"]/100.0
                High_Lateral_Velocity_Left = Lateral_Velocity_Left>0.6
                callback_parameters = {}
                callback_parameters['enable_LDWS_plot'] = self.enable_LDWS_High_Lateral_Velocity_plots
                callback_parameters['CalledFrom'] = 'High_Lateral_Velocity'
                callback_parameters['PngFolderBase'] =  r'.\High_Lateral_Velocity_Left'
                self.H4E['High_Lateral_Velocity_left'].process(Time_Lateral_Velocity_Left, High_Lateral_Velocity_Left, Source, callback_rising_edge=self.callback_LDW, callback_parameters=callback_parameters)
            except Exception, e:
                print "error - High Lateral Velocity Left: ",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"
                self.H4E['High_Lateral_Velocity_left'].process(None, None , Source,             err_msg='sim error')
                
            # ----------------------------------------------------------------------
            # FLC20_Image_Delay 
            print "FLC20_Image_Delay "
            try:
                Time_CAN_Delay = self.FLR20_sig['FLC20_CAN']["Time_CAN_Delay"]
                CAN_Delay      = self.FLR20_sig['FLC20_CAN']["CAN_Delay"]               

                self.H4E['FLC20_Image_Delay'].process(Time_CAN_Delay, np.ones_like(CAN_Delay), Source,callback_rising_edge=self.callback_rising_edge_FLC20_Image_Delay)
            except Exception, e:
                print "error - FLC20_Image_Delay: ",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"
                self.H4E['FLC20_Image_Delay'].process(None, None , Source,             err_msg='sim error')
            
            # ----------------------------------------------------------------------
            # FLC20_ME_UpdateInterval 
            print "FLC20_ME_UpdateInterval "
            try:
                Time_FLC20_ME_UpdateInterval, FLC20_ME_UpdateInterval = self.videopacket.getSamplingIntervals()  
                
                self.H4E['FLC20_ME_UpdateInterval'].process(Time_FLC20_ME_UpdateInterval, np.ones_like(FLC20_ME_UpdateInterval), Source,callback_rising_edge=self.callback_rising_edge_FLC20_ME_UpdateInterval)
            except Exception, e:
                print "error - FLC20_ME_UpdateInterval: ",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"
                self.H4E['FLC20_ME_UpdateInterval'].process(None, None , Source,             err_msg='sim error')
                
            # ----------------------------------------------------------------------
            # FLC20_TxInterval_FLI1 
            print "FLC20_TxInterval_FLI1 "
            try:
                Time_LaneDepartImminentRight = self.FLR20_sig['J1939']["Time_LaneDepartImminentRight"] 
                
                self.H4E['FLC20_TxInterval_FLI1'].process(Time_LaneDepartImminentRight, np.ones_like(Time_LaneDepartImminentRight), Source,callback_rising_edge=self.callback_rising_edge_FLC20_TxInterval_FLI1)
            except Exception, e:
                print "error - FLC20_TxInterval_FLI1: ",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"
                self.H4E['FLC20_TxInterval_FLI1'].process(None, None , Source,             err_msg='sim error')
            
            # ----------------------------------------------------------------------
            # FLC20_TxInterval_FLI2
            print "FLC20_TxInterval_FLI2 "
            try:
                Time_StateOfLDWS = self.FLR20_sig['J1939']["Time_StateOfLDWS"]

                self.H4E['FLC20_TxInterval_FLI2'].process(Time_StateOfLDWS, np.ones_like(Time_StateOfLDWS), Source,callback_rising_edge=self.callback_rising_edge_FLC20_TxInterval_FLI2)
            except Exception, e:
                print "error - FLC20_TxInterval_FLI2: ",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"
                self.H4E['FLC20_TxInterval_FLI2'].process(None, None , Source,             err_msg='sim error')
            
            
        print "end process - EvalFLC20LDWS"
      
      
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
      
        self.kb_tex.tex('\n\\newpage\\section{FLC20EvalLDWS}')
         
        # online ECU   
        self.kb_tex.tex('\n\\subsection{KB LDWS Online ECU}')
        self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['LDWS_warning_left'].n_entries_EventList())
        self.kb_tex.tex('\n \n\\medskip \n')
        self.kb_tex.tex('\nRight: %d entries'% self.H4E['LDWS_warning_right'].n_entries_EventList())
        if fill_table_array_into_report:
            self.kb_tex.table(self.H4E['LDWS_warning_left'].table_array())
            self.kb_tex.table(self.H4E['LDWS_warning_right'].table_array())
   
        self.kb_tex.tex('\n\\subsection{ME LDWS Online ECU}')
        self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['ME_LDWS_warning_left'].n_entries_EventList())
        self.kb_tex.tex('\n \n\\medskip \n')
        self.kb_tex.tex('\nRight: %d entries'% self.H4E['ME_LDWS_warning_right'].n_entries_EventList())
        if fill_table_array_into_report:
            self.kb_tex.table(self.H4E['ME_LDWS_warning_left'].table_array())
            self.kb_tex.table(self.H4E['ME_LDWS_warning_right'].table_array())
            
        self.kb_tex.tex('\n\\subsection{LNVU LDWS Online ECU}')
        self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['LNVU_LDWS_warning_left'].n_entries_EventList())
        self.kb_tex.tex('\n \n\\medskip \n')
        self.kb_tex.tex('\nRight: %d entries'% self.H4E['LNVU_LDWS_warning_right'].n_entries_EventList())
        if fill_table_array_into_report:
            self.kb_tex.table(self.H4E['LNVU_LDWS_warning_left'].table_array())
            self.kb_tex.table(self.H4E['LNVU_LDWS_warning_right'].table_array())

        self.kb_tex.tex('\n\\subsection{LDWS Online ECU intern}')
        self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['LDWS_warning_left_intern'].n_entries_EventList())
        self.kb_tex.tex('\n \n\\medskip \n')
        self.kb_tex.tex('\nRight: %d entries'% self.H4E['LDWS_warning_right_intern'].n_entries_EventList())
        if fill_table_array_into_report:
            self.kb_tex.table(self.H4E['LDWS_warning_left_intern'].table_array())
            self.kb_tex.table(self.H4E['LDWS_warning_right_intern'].table_array())
   
        # FLC20 Sensor Status
        self.kb_tex.tex('\n\\subsection{FLC20 Sensor Status}')
        self.kb_tex.tex('\nVideo\_Data\_General\_B Sensor Status $>$ 0: %d entries; '% self.H4E['FLC20_SensorStatus'].n_entries_EventList())
        self.kb_tex.tex('\nVideo\_Data\_General\_B Sensor Status changes: %d entries; '% self.H4E['FLC20_SensorStatus2'].n_entries_EventList())
        self.kb_tex.tex('\nVideo\_Data\_General\_B Sensor Status changes $>$ 0: %d entries; '% self.H4E['FLC20_SensorStatus3'].n_entries_EventList())
        self.kb_tex.tex('\nVideo\_Data\_General\_B Sensor Status changes $>$ 1: %d entries; '% self.H4E['FLC20_SensorStatus4'].n_entries_EventList())
 
        # ----------------------------------------------------------------------
        # FLI2_CameraStatus
        self.kb_tex.tex('\n\\subsection{FLI2 CameraStatus}')
        self.kb_tex.tex('\nFLI2 CameraStatus: %d entries; '% self.H4E['FLI2_CameraStatus'].n_entries_EventList())
        
        # ----------------------------------------------------------------------
        # FLI2_StateOfLDWS
        self.kb_tex.tex('\n\\subsection{FLI2 StateOfLDWS}')
        self.kb_tex.tex('\nFLI2 StateOfLDWS: %d entries; '% self.H4E['FLI2_StateOfLDWS'].n_entries_EventList())
        
        # ----------------------------------------------------------------------
        # LDWS DM1 
        self.kb_tex.tex('\n\\subsection{AEBS DM1}')
        self.kb_tex.tex('\nAEBS DM1: %d entries; '% self.H4E['LDWS_DM1'].n_entries_EventList())

        
        # ----------------------------------------------------------------------
        # FLI2_LaneTrackingStatusRight, FLI2_LaneTrackingStatusLeft
        if self.Enable_FLI2_LaneTrackingStatus:
            self.kb_tex.tex('\n\\subsection{FLI2 LaneTrackingStatus}')
            self.kb_tex.tex('\nLeft:  %d entries; '% self.H4E['FLI2_LaneTrackingStatusLeft'].n_entries_EventList())
            self.kb_tex.tex('\nRight: %d entries; '% self.H4E['FLI2_LaneTrackingStatusRight'].n_entries_EventList())

        # ----------------------------------------------------------------------
        # FLI2_LineTypeRight, FLI2_LineTypeLeft
        if self.Enable_FLI2_LineType:
            self.kb_tex.tex('\n\\subsection{FLI2 LineType}')
            self.kb_tex.tex('\nLeft:  %d entries; '% self.H4E['FLI2_LineTypeLeft'].n_entries_EventList())
            self.kb_tex.tex('\nRight: %d entries; '% self.H4E['FLI2_LineTypeRight'].n_entries_EventList())
        
        # ----------------------------------------------------------------------
        # FLI1_LaneDepartImminentRight FLI1_LaneDepartImminentLeft
        self.kb_tex.tex('\n\\subsection{FLI1 LaneDepartImminent}')
        self.kb_tex.tex('\nLeft:  %d entries; '% self.H4E['FLI1_LaneDepartImminentLeft'].n_entries_EventList())
        self.kb_tex.tex('\nRight: %d entries; '% self.H4E['FLI1_LaneDepartImminentRight'].n_entries_EventList())
        
        # ----------------------------------------------------------------------
        # FLI1_OpticalWarningRight FLI1_OpticalWarningLeft
        self.kb_tex.tex('\n\\subsection{FLI1 OpticalWarning}')
        self.kb_tex.tex('\nLeft:  %d entries; '% self.H4E['FLI1_OpticalWarningLeft'].n_entries_EventList())
        self.kb_tex.tex('\nRight: %d entries; '% self.H4E['FLI1_OpticalWarningRight'].n_entries_EventList())

        # ----------------------------------------------------------------------
        # FLI1_AcousticalWarningRight FLI1_AcousticalWarningLeft
        self.kb_tex.tex('\n\\subsection{FLI1 AcousticalWarning}')
        self.kb_tex.tex('\nLeft:  %d entries; '% self.H4E['FLI1_AcousticalWarningLeft'].n_entries_EventList())
        self.kb_tex.tex('\nRight: %d entries; '% self.H4E['FLI1_AcousticalWarningRight'].n_entries_EventList())
 
        # ----------------------------------------------------------------------
        # Turn Signal Indicator
        self.kb_tex.tex('\n\\subsection{Turn Signal Indicator}')
        self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['DirIndLeft'].n_entries_EventList())
        self.kb_tex.tex('\nRight: %d entries; '% self.H4E['DirIndRight'].n_entries_EventList())
   
   
        # ----------------------------------------------------------------------
        # LNVU Simulation
        self.kb_tex.tex('\n\\subsection{LNVU Simulation}')
        
        for nr_str, SilLDWS_C in self.SilLDWS_C_list:
            self.kb_tex.tex('\n\\subsubsection{%s}'%nr_str)
        
            self.kb_tex.tex('\n\\paragraph{isWarning}')
            self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['SIM_WARN_isWarningLeft'+nr_str].n_entries_EventList())
            self.kb_tex.tex('\nRight: %d entries; '% self.H4E['SIM_WARN_isWarningRight'+nr_str].n_entries_EventList())
        
            self.kb_tex.tex('\n\\paragraph{KB LDW Imminent State}')
            self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['SIM_KB_LDW_Imminent_State_Left'+nr_str].n_entries_EventList())
            self.kb_tex.tex('\nRight: %d entries; '% self.H4E['SIM_KB_LDW_Imminent_State_Right'+nr_str].n_entries_EventList())
   
            self.kb_tex.tex('\n\\subsubsection{KB LDW Acoustical State}')
            self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['SIM_KB_LDW_Acoustical_State_Left'+nr_str].n_entries_EventList())
            self.kb_tex.tex('\nRight: %d entries; '% self.H4E['SIM_KB_LDW_Acoustical_State_Right'+nr_str].n_entries_EventList())
        
   
        # ----------------------------------------------------------------------
        # High Lateral Velocity 
        self.kb_tex.tex('\n\\subsection{High Lateral Velocity}')
        self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['High_Lateral_Velocity_left'].n_entries_EventList())
        self.kb_tex.tex('\nRight: %d entries; '% self.H4E['High_Lateral_Velocity_right'].n_entries_EventList())

   
   
        self.kb_tex.tex('\n \n\\bigskip \nEvalFLC20LDWS-finished')
      
     
    # ------------------------------------------------------------------------------------------
    def _build_ExcelFilename(self,ExcelBaseFilename):
        if self.src_dir_meas is not None:
            ExcelBaseFilename = "%s_%s"%(ExcelBaseFilename,os.path.basename(self.src_dir_meas))
        ExcelFilename = ExcelBaseFilename+'.xls' 
        return ExcelFilename
        
    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        extended_b = True
    
        if self.enable_LDWS_ExcelSheet_reduced_mode:
            extended_b = False
    
        print "EvalFLC20LDWS.excel_export"
        print "src_dir_meas :",os.path.basename(self.src_dir_meas)
        
        # switches
        # add partial_brake and emergency_brake spreadsheets
        braking_spreadsheets = False

        # new format 
        AddColsFormat = {}
        AddColsFormat["v_ego_at_t_start"]                     = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["Left_C0_at_t_start"]                   = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["fd_Left_C0_at_t_start"]                = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"
        AddColsFormat["Right_C0_at_t_start"]                  = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["fd_Right_C0_at_t_start"]               = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"
        AddColsFormat["LaneWidth_at_t_start"]                 = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["road_curvature_at_t_start"]            = ("ExcelNumFormat", '##0.0 "m"')    # "%3.1f m"

        AddColsFormat["Left_C1_at_t_start"]                   = ("ExcelNumFormat", '##0.00 "degree"')    # "%3.2f m"
        AddColsFormat["Right_C1_at_t_start"]                  = ("ExcelNumFormat", '##0.00 "degree"')    # "%3.2f m"
        
        AddColsFormat["Left_inv_C2_at_t_start"]               = ("ExcelNumFormat", '##0.0 "m"')          # "%3.1f m"
        AddColsFormat["Right_inv_C2_at_t_start"]              = ("ExcelNumFormat", '##0.0 "m"')          # "%3.1f m"
        AddColsFormat["Left_inv_C3_at_t_start"]               = ("ExcelNumFormat", '##0.0 "m*m"')        # "%3.1f m"
        AddColsFormat["Right_inv_C3_at_t_start"]              = ("ExcelNumFormat", '##0.0 "m*m"')        # "%3.1f m"

        AddColsFormat["TLC_Left_at_t_start"]                  = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        AddColsFormat["TLC_Right_at_t_start"]                 = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"

        AddColsFormat["Left_C0_at_t_stop"]                    = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["Right_C0_at_t_stop"]                   = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        
        AddColsFormat["C0_left_wheel_at_t_start"]             = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["C0_left_wheel_at_t_stop"]              = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["C0_right_wheel_at_t_start"]            = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["C0_right_wheel_at_t_stop"]             = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"

        AddColsFormat["C0_left_wheel_filtered_at_t_start"]    = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["C0_left_wheel_filtered_at_t_stop"]     = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["C0_right_wheel_filtered_at_t_start"]   = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["C0_right_wheel_filtered_at_t_stop"]    = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        
        AddColsFormat["Lateral_Velocity_Left_at_t_start"]     = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"
        AddColsFormat["Lateral_Velocity_Left_at_t_stop"]      = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"
        AddColsFormat["Lateral_Velocity_Right_at_t_start"]    = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"
        AddColsFormat["Lateral_Velocity_Right_at_t_stop"]     = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"

        AddColsFormat["min_Lateral_Velocity_Left"]            = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"
        AddColsFormat["max_Lateral_Velocity_Left"]            = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"
        AddColsFormat["min_Lateral_Velocity_Right"]           = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"
        AddColsFormat["max_Lateral_Velocity_Right"]           = ("ExcelNumFormat", '##0.00 "m/s"')  # "%4.2f m/s"

        
        AddColsFormat["Me_Line_Changed_Left_DeltaT"]          = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        AddColsFormat["Me_Line_Changed_Right_DeltaT"]         = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        

        AddColsFormat["Ay_at_t_start"]                        = ("ExcelNumFormat", '##0.00 "m/s^2"')    # "%3.2f s"
        AddColsFormat["Ay_at_t_stop"]                         = ("ExcelNumFormat", '##0.00 "m/s^2"')    # "%3.2f s"

        AddColsFormat["ME_LD_present_Left_DeltaT"]            = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        AddColsFormat["ME_LD_present_Right_DeltaT"]           = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"

        AddColsFormat["Tracking_present_Left_DeltaT"]         = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        AddColsFormat["Tracking_present_Right_DeltaT"]        = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"

        AddColsFormat["View_Range_Left_at_t_start"]           = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
        AddColsFormat["View_Range_Right_at_t_start"]          = ("ExcelNumFormat", '##0.00 "m"')    # "%3.2f m"
      
        # OxTS      
        AddColsFormat["LeftLinePosLateral_at_t_start"]              = ("ExcelNumFormat", '##0.00 "m"')     # "%3.2f m"
        AddColsFormat["RightLinePosLateral_at_t_start"]             = ("ExcelNumFormat", '##0.00 "m"')     # "%3.2f m"
        AddColsFormat["LeftLineVelLateral_smoothed_at_t_start"]     = ("ExcelNumFormat", '##0.00 "m/s"')   # "%4.2f m/s"
        AddColsFormat["RightLineVelLateral_smoothed_at_t_start"]    = ("ExcelNumFormat", '##0.00 "m/s"')   # "%4.2f m/s"
        AddColsFormat["OxTS_host_AccelLateral_smoothed_at_t_start"] = ("ExcelNumFormat", '##0.00 "m/s^2"') # "%3.2f s"
        
        # Steering angle    
        AddColsFormat["SteerWhlAngle_at_t_LDW_start"]               = ("ExcelNumFormat", '##0.00 "degree"')  # "%4.2f m/s"
        AddColsFormat["Gradient_SteerWhlAngle_at_t_LDW_start"]      = ("ExcelNumFormat", '##0.00 "degree/s"')  # "%4.2f m/s"
      
        # FLC20_Image_Delay
        AddColsFormat["max_CAN_Delay"]      = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        AddColsFormat["min_CAN_Delay"]      = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        AddColsFormat["mean_CAN_Delay"]     = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"

        AddColsFormat["max_FLC20_ME_UpdateInterval"]      = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        AddColsFormat["min_FLC20_ME_UpdateInterval"]      = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        AddColsFormat["mean_FLC20_ME_UpdateInterval"]     = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        
        AddColsFormat["max_FLC20_FLI1_UpdateInterval"]      = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        AddColsFormat["min_FLC20_FLI1_UpdateInterval"]      = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        AddColsFormat["mean_FLC20_FLI1_UpdateInterval"]     = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"

        AddColsFormat["max_FLC20_FLI2_UpdateInterval"]      = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        AddColsFormat["min_FLC20_FLI2_UpdateInterval"]      = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
        AddColsFormat["mean_FLC20_FLI2_UpdateInterval"]     = ("ExcelNumFormat", '##0.000 "s"')  # "%4.3f s"
         
          
        # ==================================================================
        # WriteExcel
        ExcelFilename = self._build_ExcelFilename("FLC20EvalLDWS_results")
        print "ExcelFilename: ",ExcelFilename
        WriteExcel = kbtools.cWriteExcel()
        

        # WriteExcel_sim: separate Excel Spreadsheet with all the simulation results        
        ExcelFilename_sim = self._build_ExcelFilename("FLC20EvalLDWS_sim_results")
        print "ExcelFilename_sim: ",ExcelFilename_sim
        WriteExcel_sim = kbtools.cWriteExcel()

        
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # AEBS_warning, AEBS_partial_brake, AEBS_emergency_brake
        
        # ----------------------------------------------------------------------
        # LDWS_DM1
        AddCols_LDWS_DM1 = ["DM1_ActSPN","DM1_ActFMI","DM1_AmberWarnLStat"]
        WriteExcel.add_sheet_out_table_array('LDWS_DM1',self.H4E['LDWS_DM1'].table_array2(AddCols_LDWS_DM1,AddColsFormat))

        
        # ---------------------------------------------------
        # sheet 'LDWS_warning_left' - online - J1939 FLI1 - LaneDepartImminentLeft
        AddCols_online  = ["v_ego_at_t_start"]
        # Does Simulation agree?
        AddCols_online += ["SIM_LDImmLeft_present", "SIM_LDImmLeft_present_DeltaT", "SIM_LDImmLeft_present_Duration"]
        
        # Are ME or LNVU present?
        AddCols_online += ["ME_LD_present","ME_LD_present_Left_DeltaT"]
        AddCols_online += ["LNVU_LD_present","LNVU_LD_present_Left_DeltaT"]
        # Parameter of this LD
        AddCols_online += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
        AddCols_online += ["LaneWidth_at_t_start","road_curvature_at_t_start","Ay_at_t_start"]
        # more details
        AddCols_online += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
        AddCols_online += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
        AddCols_online += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
        AddCols_online += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
        AddCols_online += ["C0_right_wheel_at_t_stop","Lateral_Velocity_Right_at_t_stop"]
        AddCols_online += ["Ay_at_t_stop" ]
        AddCols_online += ["Tracking_present_Left","Tracking_present_Right","Tracking_present_Left_DeltaT","Tracking_present_Right_DeltaT"]
        AddCols_online += ["View_Range_Left_at_t_start", "View_Range_Right_at_t_start" ]
        AddCols_online += ["Left_C0_at_t_start", "Left_C1_at_t_start", "Left_C2_at_t_start", "Left_C3_at_t_start"]
        AddCols_online += ["Right_C0_at_t_start","Right_C1_at_t_start","Right_C2_at_t_start","Right_C3_at_t_start"]
        AddCols_online += ["Left_C0_at_t_stop","Right_C0_at_t_stop"] 
        AddCols_online += ["C0_left_wheel_filtered_at_t_start", "C0_left_wheel_filtered_at_t_stop"] 
        AddCols_online += ["LeftLinePosLateral_at_t_start", "LeftLineVelLateral_smoothed_at_t_start"] 
        # AddCols_online += ["TLC_Left_at_t_start","fd_Left_C0_at_t_start","fd_Right_C0_at_t_start" ]
        WriteExcel.add_sheet_out_table_array('LDWS_warning_left',self.H4E['LDWS_warning_left'].table_array2(AddCols_online,AddColsFormat))
       
   
        # sheet 'LDWS_warning_right' - online - J1939 FLI1 - LaneDepartImminentRight
        AddCols_online  = ["v_ego_at_t_start"]
        # Does Simulation agree?
        AddCols_online += ["SIM_LDImmRight_present","SIM_LDImmRight_present_DeltaT",    "SIM_LDImmRight_present_Duration"]

        # Are ME or LNVU present?
        AddCols_online += ["ME_LD_present","ME_LD_present_Right_DeltaT"]
        AddCols_online += ["LNVU_LD_present","LNVU_LD_present_Right_DeltaT"]
        # Parameter of this LD
        AddCols_online += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
        AddCols_online += ["LaneWidth_at_t_start","road_curvature_at_t_start","Ay_at_t_start"]
        # more details
        AddCols_online += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
        AddCols_online += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
        AddCols_online += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
        AddCols_online += ["C0_right_wheel_at_t_stop", "Lateral_Velocity_Right_at_t_stop"]
        AddCols_online += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
        AddCols_online += ["Ay_at_t_stop" ]
        AddCols_online += ["Tracking_present_Right","Tracking_present_Left","Tracking_present_Right_DeltaT","Tracking_present_Left_DeltaT"]
        AddCols_online += ["View_Range_Right_at_t_start","View_Range_Left_at_t_start"]
        AddCols_online += ["Right_C0_at_t_start","Right_C1_at_t_start","Right_C2_at_t_start","Right_C3_at_t_start"]
        AddCols_online += ["Left_C0_at_t_start", "Left_C1_at_t_start", "Left_C2_at_t_start", "Left_C3_at_t_start"]
        AddCols_online += ["Right_C0_at_t_stop", "Left_C0_at_t_stop"] 
        AddCols_online += ["C0_right_wheel_filtered_at_t_start", "C0_right_wheel_filtered_at_t_stop"] 
        AddCols_online += ["RightLinePosLateral_at_t_start", "RightLineVelLateral_smoothed_at_t_start"] 
        #AddCols_online += ["TLC_Right_at_t_start","fd_Right_C0_at_t_start","fd_Left_C0_at_t_start"]
        WriteExcel.add_sheet_out_table_array('LDWS_warning_right',self.H4E['LDWS_warning_right'].table_array2(AddCols_online,AddColsFormat))

        if self.enable_ExcelSheet_ME_LDWS_warning:
            # ME        
            # sheet 'ME_LDWS_warning_left' - online - Lane Departure Warnings by Mobileye no suppressors
            AddCols_online  = ["v_ego_at_t_start"]
            AddCols_online += ["ME_LDW_left_suppressed","ME_LDW_left_suppressed_reason"]
            AddCols_online += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
            AddCols_online += ["LaneWidth_at_t_start","road_curvature_at_t_start","Ay_at_t_start"]
            # Ford specific
            AddCols_online += ["OxTS_host_AccelLateral_smoothed_at_t_start", "LeftLinePosLateral_at_t_start", "LeftLineVelLateral_smoothed_at_t_start"]
            AddCols_online += ["SteerWhlAngle_at_t_LDW_start", "Gradient_SteerWhlAngle_at_t_LDW_start"]
            # more details
            AddCols_online += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
            AddCols_online += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
            AddCols_online += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
            AddCols_online += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
            AddCols_online += ["C0_right_wheel_at_t_stop","Lateral_Velocity_Right_at_t_stop"]
            AddCols_online += ["Ay_at_t_stop" ]
            AddCols_online += ["Tracking_present_Left","Tracking_present_Right","Tracking_present_Left_DeltaT","Tracking_present_Right_DeltaT"]
            AddCols_online += ["View_Range_Left_at_t_start", "View_Range_Right_at_t_start" ]
            AddCols_online += ["Left_C0_at_t_start", "Left_C1_at_t_start", "Left_C2_at_t_start", "Left_C3_at_t_start"]
            AddCols_online += ["Right_C0_at_t_start","Right_C1_at_t_start","Right_C2_at_t_start","Right_C3_at_t_start"]
            AddCols_online += ["Left_C0_at_t_stop","Right_C0_at_t_stop"] 
            AddCols_online += ["C0_left_wheel_filtered_at_t_start", "C0_left_wheel_filtered_at_t_stop"] 
            if extended_b:
                WriteExcel.add_sheet_out_table_array('ME_LDWS_warning_left',self.H4E['ME_LDWS_warning_left'].table_array2(AddCols_online,AddColsFormat))
        
            # sheet 'ME_LDWS_warning_right' - online - Lane Departure Warnings by Mobileye no suppressors
            AddCols_online  = ["v_ego_at_t_start"]
            AddCols_online += ["ME_LDW_right_suppressed","ME_LDW_right_suppressed_reason"]
            AddCols_online += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
            AddCols_online += ["LaneWidth_at_t_start","road_curvature_at_t_start","Ay_at_t_start"]
            # Ford specific
            AddCols_online += ["OxTS_host_AccelLateral_smoothed_at_t_start", "RightLinePosLateral_at_t_start", "RightLineVelLateral_smoothed_at_t_start"]
            AddCols_online += ["SteerWhlAngle_at_t_LDW_start", "Gradient_SteerWhlAngle_at_t_LDW_start"]
            # more details
            AddCols_online += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
            AddCols_online += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
            AddCols_online += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
            AddCols_online += ["C0_right_wheel_at_t_stop", "Lateral_Velocity_Right_at_t_stop"]
            AddCols_online += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
            AddCols_online += ["Ay_at_t_stop" ]
            AddCols_online += ["Tracking_present_Right","Tracking_present_Left","Tracking_present_Right_DeltaT","Tracking_present_Left_DeltaT"]
            AddCols_online += ["View_Range_Right_at_t_start","View_Range_Left_at_t_start"]
            AddCols_online += ["Right_C0_at_t_start","Right_C1_at_t_start","Right_C2_at_t_start","Right_C3_at_t_start"]
            AddCols_online += ["Left_C0_at_t_start", "Left_C1_at_t_start", "Left_C2_at_t_start", "Left_C3_at_t_start"]
            AddCols_online += ["Right_C0_at_t_stop", "Left_C0_at_t_stop"] 
            AddCols_online += ["C0_right_wheel_filtered_at_t_start", "C0_right_wheel_filtered_at_t_stop"] 
            if extended_b:
                WriteExcel.add_sheet_out_table_array('ME_LDWS_warning_right',self.H4E['ME_LDWS_warning_right'].table_array2(AddCols_online,AddColsFormat))
        
        
        # LNVU
        # sheet 'LNVU_LDWS_warning_left' - online - Lane Departure Warnings by LNVU no suppressors
        AddCols_online  = ["v_ego_at_t_start"]
        AddCols_online += ["LNVU_LDW_left_suppressed","LNVU_LDW_left_suppressed_reason"]
        AddCols_online += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
        AddCols_online += ["LaneWidth_at_t_start","road_curvature_at_t_start","Ay_at_t_start"]
        # Ford specific
        AddCols_online += ["OxTS_host_AccelLateral_smoothed_at_t_start", "LeftLinePosLateral_at_t_start", "LeftLineVelLateral_smoothed_at_t_start"]
        AddCols_online += ["SteerWhlAngle_at_t_LDW_start", "Gradient_SteerWhlAngle_at_t_LDW_start"]
        # more details
        AddCols_online += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
        AddCols_online += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
        AddCols_online += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
        AddCols_online += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
        AddCols_online += ["C0_right_wheel_at_t_stop","Lateral_Velocity_Right_at_t_stop"]
        AddCols_online += ["Ay_at_t_stop" ]
        AddCols_online += ["Tracking_present_Left","Tracking_present_Right","Tracking_present_Left_DeltaT","Tracking_present_Right_DeltaT"]
        AddCols_online += ["View_Range_Left_at_t_start", "View_Range_Right_at_t_start" ]
        AddCols_online += ["Left_C0_at_t_start", "Left_C1_at_t_start", "Left_C2_at_t_start", "Left_C3_at_t_start"]
        AddCols_online += ["Right_C0_at_t_start","Right_C1_at_t_start","Right_C2_at_t_start","Right_C3_at_t_start"]
        AddCols_online += ["Left_C0_at_t_stop","Right_C0_at_t_stop"] 
        AddCols_online += ["C0_left_wheel_filtered_at_t_start", "C0_left_wheel_filtered_at_t_stop"] 
        if extended_b:
            WriteExcel.add_sheet_out_table_array('LNVU_LDWS_warning_left',self.H4E['LNVU_LDWS_warning_left'].table_array2(AddCols_online,AddColsFormat))
        
        # sheet 'LNVU_LDWS_warning_right' - online - Lane Departure Warnings by LNVU no suppressors
        AddCols_online  = ["v_ego_at_t_start"]
        AddCols_online += ["LNVU_LDW_right_suppressed","LNVU_LDW_right_suppressed_reason"]
        AddCols_online += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
        AddCols_online += ["LaneWidth_at_t_start","road_curvature_at_t_start","Ay_at_t_start"]
        # Ford specific
        AddCols_online += ["OxTS_host_AccelLateral_smoothed_at_t_start", "RightLinePosLateral_at_t_start", "RightLineVelLateral_smoothed_at_t_start"]
        AddCols_online += ["SteerWhlAngle_at_t_LDW_start", "Gradient_SteerWhlAngle_at_t_LDW_start"]
        # more details
        AddCols_online += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
        AddCols_online += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
        AddCols_online += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
        AddCols_online += ["C0_right_wheel_at_t_stop", "Lateral_Velocity_Right_at_t_stop"]
        AddCols_online += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
        AddCols_online += ["Ay_at_t_stop" ]
        AddCols_online += ["Tracking_present_Right","Tracking_present_Left","Tracking_present_Right_DeltaT","Tracking_present_Left_DeltaT"]
        AddCols_online += ["View_Range_Right_at_t_start","View_Range_Left_at_t_start"]
        AddCols_online += ["Right_C0_at_t_start","Right_C1_at_t_start","Right_C2_at_t_start","Right_C3_at_t_start"]
        AddCols_online += ["Left_C0_at_t_start", "Left_C1_at_t_start", "Left_C2_at_t_start", "Left_C3_at_t_start"]
        AddCols_online += ["Right_C0_at_t_stop", "Left_C0_at_t_stop"] 
        AddCols_online += ["C0_right_wheel_filtered_at_t_start", "C0_right_wheel_filtered_at_t_stop"] 
        if extended_b:
            WriteExcel.add_sheet_out_table_array('LNVU_LDWS_warning_right',self.H4E['LNVU_LDWS_warning_right'].table_array2(AddCols_online,AddColsFormat))
        
        
        # ---------------------------------------------------
        # LNVU Simulation
        AddCols_offline_0   = ["v_ego_at_t_start"]
        AddCols_offline_1L  = ["ECU_ME_LDLeft_present",      "ECU_ME_LDLeft_present_DeltaT",      "ECU_ME_LDLeft_present_Duration"]
        AddCols_offline_1R  = ["ECU_ME_LDRight_present",     "ECU_ME_LDRight_present_DeltaT",     "ECU_ME_LDRight_present_Duration"]
        AddCols_offline_1bL = ["ECU_LNVU_LDLeft_present",    "ECU_LNVU_LDLeft_present_DeltaT",    "ECU_LNVU_LDLeft_present_Duration"]
        AddCols_offline_1bR = ["ECU_LNVU_LDRight_present",   "ECU_LNVU_LDRight_present_DeltaT",   "ECU_LNVU_LDRight_present_Duration"]
                
        AddCols_offline_2L  = ["ECU_LDImmLeft_present",      "ECU_LDImmLeft_present_DeltaT",      "ECU_LDImmLeft_present_Duration"]
        AddCols_offline_2R  = ["ECU_LDImmRight_present",     "ECU_LDImmRight_present_DeltaT",     "ECU_LDImmRight_present_Duration"]
        
        AddCols_offline_3L  = ["ECU_AcousWarnLeft_present",  "ECU_AcousWarnLeft_present_DeltaT",  "ECU_AcousWarnLeft_present_Duration"]
        AddCols_offline_3R  = ["ECU_AcousWarnRight_present", "ECU_AcousWarnRight_present_DeltaT", "ECU_AcousWarnRight_present_Duration"]
             
        AddCols_offline_4L  = ["SIM_isWarnLeft_present",     "SIM_isWarnLeft_present_DeltaT",     "SIM_isWarnLeft_present_Duration"]
        AddCols_offline_4R  = ["SIM_isWarnRight_present",    "SIM_isWarnRight_present_DeltaT",    "SIM_isWarnRight_present_Duration"]
        AddCols_offline_5L  = ["SIM_LDImmLeft_present",      "SIM_LDImmLeft_present_DeltaT",      "SIM_LDImmLeft_present_Duration"]
        AddCols_offline_5R  = ["SIM_LDImmRight_present",     "SIM_LDImmRight_present_DeltaT",     "SIM_LDImmRight_present_Duration"]
        AddCols_offline_6L  = ["SIM_AcousWarnLeft_present",  "SIM_AcousWarnLeft_present_DeltaT",  "SIM_AcousWarnLeft_present_Duration"]
        AddCols_offline_6R  = ["SIM_AcousWarnRight_present", "SIM_AcousWarnRight_present_DeltaT", "SIM_AcousWarnRight_present_Duration"]

        AddCols_offline_7L  = ["ME_LD_present","ME_LD_present_Left_DeltaT","ME_LD_present_Right_DeltaT"]
        AddCols_offline_7L += ["LNVU_LD_present","LNVU_LD_present_Left_DeltaT","LNVU_LD_present_Right_DeltaT"]
        AddCols_offline_7L += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
        AddCols_offline_7L += ["LaneWidth_at_t_start","road_curvature_at_t_start"]
        AddCols_offline_7L += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
        AddCols_offline_7L += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
        AddCols_offline_7L += ["C0_right_wheel_at_t_stop", "Lateral_Velocity_Right_at_t_stop"]
        AddCols_offline_7L += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
        AddCols_offline_7L += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
        AddCols_offline_7L += ["Ay_at_t_start","Ay_at_t_stop" ]
        AddCols_offline_7L += ["View_Range_Left_at_t_start", "View_Range_Right_at_t_start" ]
        AddCols_offline_7L += ["Left_C0_at_t_start","Right_C0_at_t_start"]
        AddCols_offline_7L += ["Left_C0_at_t_stop","Right_C0_at_t_stop"] 
        

        AddCols_offline_7R  = ["ME_LD_present","ME_LD_present_Right_DeltaT","ME_LD_present_Left_DeltaT"]
        AddCols_offline_7R += ["LNVU_LD_present","LNVU_LD_present_Right_DeltaT","LNVU_LD_present_Left_DeltaT"]
        AddCols_offline_7R += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
        AddCols_offline_7R += ["LaneWidth_at_t_start","road_curvature_at_t_start"]
        AddCols_offline_7R += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
        AddCols_offline_7R += ["C0_right_wheel_at_t_stop", "Lateral_Velocity_Right_at_t_stop"]
        AddCols_offline_7R += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
        AddCols_offline_7R += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
        AddCols_offline_7R += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
        AddCols_offline_7R += ["Ay_at_t_start","Ay_at_t_stop" ]
        AddCols_offline_7R += ["View_Range_Left_at_t_start", "View_Range_Right_at_t_start" ]
        AddCols_offline_7R += ["Right_C0_at_t_start","Left_C0_at_t_start"]
        AddCols_offline_7R += ["Right_C0_at_t_stop", "Left_C0_at_t_stop"] 
        
        nr_str = ''
        # Simulation: Imminent Warning 
        AddCols_offline = AddCols_offline_0+AddCols_offline_2L+AddCols_offline_1L+AddCols_offline_1bL+AddCols_offline_6L+AddCols_offline_4L+AddCols_offline_7L
        if 'SIM_KB_LDW_Imminent_State_Left'+nr_str in self.H4E:
            if extended_b:
                WriteExcel.add_sheet_out_table_array('SIM_LDImmLeft'+nr_str,self.H4E['SIM_KB_LDW_Imminent_State_Left'+nr_str].table_array2(AddCols_offline,AddColsFormat))
        AddCols_offline = AddCols_offline_0+AddCols_offline_2R+AddCols_offline_1R+AddCols_offline_1bR+AddCols_offline_6R+AddCols_offline_4R+AddCols_offline_7R
        if 'SIM_KB_LDW_Imminent_State_Right'+nr_str in self.H4E:
            if extended_b:
                WriteExcel.add_sheet_out_table_array('SIM_LDImmRight'+nr_str,self.H4E['SIM_KB_LDW_Imminent_State_Right'+nr_str].table_array2(AddCols_offline,AddColsFormat))
        
        # Simulation: LNVU Warning 
        AddCols_offline = AddCols_offline_0+AddCols_offline_1L+AddCols_offline_1bL+AddCols_offline_5L+AddCols_offline_6L+AddCols_offline_7L
        if 'SIM_WARN_isWarningLeft'+nr_str in self.H4E:
            if extended_b:
                WriteExcel.add_sheet_out_table_array('SIM_isWarnLeft'+nr_str,self.H4E['SIM_WARN_isWarningLeft'+nr_str].table_array2(AddCols_offline,AddColsFormat))
        AddCols_offline = AddCols_offline_0+AddCols_offline_1R+AddCols_offline_1bR+AddCols_offline_5R+AddCols_offline_6R+AddCols_offline_7R
        if 'SIM_WARN_isWarningRight'+nr_str in self.H4E:
            if extended_b:
               WriteExcel.add_sheet_out_table_array('SIM_isWarnRight'+nr_str,self.H4E['SIM_WARN_isWarningRight'+nr_str].table_array2(AddCols_offline,AddColsFormat))
        
        # Simulation Acoustical Warning
        AddCols_offline = AddCols_offline_0+AddCols_offline_3L+AddCols_offline_4L
        if 'SIM_KB_LDW_Acoustical_State_Left'+nr_str in self.H4E:
            if extended_b:
                WriteExcel.add_sheet_out_table_array('SIM_AcousWarnLeft'+nr_str,self.H4E['SIM_KB_LDW_Acoustical_State_Left'+nr_str].table_array2(AddCols_offline,AddColsFormat))
        AddCols_offline = AddCols_offline_0+AddCols_offline_3R+AddCols_offline_4R
        if 'SIM_KB_LDW_Acoustical_State_Right'+nr_str in self.H4E:
            if extended_b:
                WriteExcel.add_sheet_out_table_array('SIM_AcousWarnRight'+nr_str,self.H4E['SIM_KB_LDW_Acoustical_State_Right'+nr_str].table_array2(AddCols_offline,AddColsFormat))
        

        # ---------------------------------------------------------------------        
        # WriteExcel_sim: separate Excel Spreadsheet with all the simulation results  
        for nr_str, SilLDWS_C in self.SilLDWS_C_list:
            AddCols_offline = AddCols_offline_0+AddCols_offline_2L+AddCols_offline_6L+AddCols_offline_4L+AddCols_offline_7L
            WriteExcel_sim.add_sheet_out_table_array('SIM_LDImmLeft'+nr_str,self.H4E['SIM_KB_LDW_Imminent_State_Left'+nr_str].table_array2(AddCols_offline,AddColsFormat))
            AddCols_offline = AddCols_offline_0+AddCols_offline_2R+AddCols_offline_6R+AddCols_offline_4R+AddCols_offline_7R
            WriteExcel_sim.add_sheet_out_table_array('SIM_LDImmRight'+nr_str,self.H4E['SIM_KB_LDW_Imminent_State_Right'+nr_str].table_array2(AddCols_offline,AddColsFormat))

        for nr_str, SilLDWS_C in self.SilLDWS_C_list:
            AddCols_offline = AddCols_offline_0+AddCols_offline_1L+AddCols_offline_5L+AddCols_offline_6L+AddCols_offline_7L
            WriteExcel_sim.add_sheet_out_table_array('SIM_isWarnLeft'+nr_str,self.H4E['SIM_WARN_isWarningLeft'+nr_str].table_array2(AddCols_offline,AddColsFormat))
            AddCols_offline = AddCols_offline_0+AddCols_offline_1R+AddCols_offline_5R+AddCols_offline_6R+AddCols_offline_7R
            WriteExcel_sim.add_sheet_out_table_array('SIM_isWarnRight'+nr_str,self.H4E['SIM_WARN_isWarningRight'+nr_str].table_array2(AddCols_offline,AddColsFormat))
        
        for nr_str, SilLDWS_C in self.SilLDWS_C_list:
            AddCols_offline = AddCols_offline_0+AddCols_offline_3L+AddCols_offline_4L
            WriteExcel_sim.add_sheet_out_table_array('SIM_AcousWarnLeft'+nr_str,self.H4E['SIM_KB_LDW_Acoustical_State_Left'+nr_str].table_array2(AddCols_offline,AddColsFormat))
            AddCols_offline = AddCols_offline_0+AddCols_offline_3R+AddCols_offline_4R
            WriteExcel_sim.add_sheet_out_table_array('SIM_AcousWarnRight'+nr_str,self.H4E['SIM_KB_LDW_Acoustical_State_Right'+nr_str].table_array2(AddCols_offline,AddColsFormat))
        # ---------------------------------------------------------------------        
           
        # ----------------------------------------------------------------------
        # FLC20_SensorStatus
        AddCols_SensorStatus = ["observed_statii"]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLC20_SensorStatus',self.H4E['FLC20_SensorStatus'].table_array2(AddCols_SensorStatus,AddColsFormat))
            WriteExcel.add_sheet_out_table_array('FLC20_SensorStatus2',self.H4E['FLC20_SensorStatus2'].table_array2(AddCols_SensorStatus,AddColsFormat))
            WriteExcel.add_sheet_out_table_array('FLC20_SensorStatus3',self.H4E['FLC20_SensorStatus3'].table_array2(AddCols_SensorStatus,AddColsFormat))
            WriteExcel.add_sheet_out_table_array('FLC20_SensorStatus4',self.H4E['FLC20_SensorStatus4'].table_array2(AddCols_SensorStatus,AddColsFormat))

        # ----------------------------------------------------------------------
        # FLI2_CameraStatus
        AddCols_SensorStatus = ["observed_statii"]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLI2_CameraStatus',self.H4E['FLI2_CameraStatus'].table_array2(AddCols_SensorStatus,AddColsFormat))
        
        # ----------------------------------------------------------------------
        # FLI2_StateOfLDWS
        AddCols_SensorStatus = ["observed_statii"]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLI2_StateOfLDWS',self.H4E['FLI2_StateOfLDWS'].table_array2(AddCols_SensorStatus,AddColsFormat))
        
        # ----------------------------------------------------------------------
        # FLI2_LaneTrackingStatusLeft, FLI2_LaneTrackingStatusRight
        if self.Enable_FLI2_LaneTrackingStatus:
            AddCols_SensorStatus = ["Left", "Right"]
            if extended_b:
                WriteExcel.add_sheet_out_table_array('FLI2_LaneTrackingStatusLeft',self.H4E['FLI2_LaneTrackingStatusLeft'].table_array2(AddCols_SensorStatus,AddColsFormat))
                WriteExcel.add_sheet_out_table_array('FLI2_LaneTrackingStatusRight',self.H4E['FLI2_LaneTrackingStatusRight'].table_array2(AddCols_SensorStatus,AddColsFormat))
       
        # ----------------------------------------------------------------------
        # FLI2_LineTypeLeft, FLI2_LineTypeRight, 
        if self.Enable_FLI2_LineType:
            AddCols_SensorStatus = ["Left", "Right"]
            if extended_b:
                WriteExcel.add_sheet_out_table_array('FLI2_LineTypeLeft',self.H4E['FLI2_LineTypeLeft'].table_array2(AddCols_SensorStatus,AddColsFormat))
                WriteExcel.add_sheet_out_table_array('FLI2_LineTypeRight',self.H4E['FLI2_LineTypeRight'].table_array2(AddCols_SensorStatus,AddColsFormat))

        # ----------------------------------------------------------------------
        # FLI1_LaneDepartImminentLeft FLI1_LaneDepartImminentRight 
        AddCols_SensorStatus = []
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLI1_LaneDepartImminentLeft',self.H4E['FLI1_LaneDepartImminentLeft'].table_array2(AddCols_SensorStatus,AddColsFormat))
            WriteExcel.add_sheet_out_table_array('FLI1_LaneDepartImminentRight',self.H4E['FLI1_LaneDepartImminentRight'].table_array2(AddCols_SensorStatus,AddColsFormat))
        
        # ----------------------------------------------------------------------
        # FLI1_LaneDepartImminentLeft, FLI1_LaneDepartImminentRight 
        AddCols_SensorStatus = []
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLI1_OpticalWarningLeft',self.H4E['FLI1_OpticalWarningLeft'].table_array2(AddCols_SensorStatus,AddColsFormat))
            WriteExcel.add_sheet_out_table_array('FLI1_OpticalWarningRight',self.H4E['FLI1_OpticalWarningRight'].table_array2(AddCols_SensorStatus,AddColsFormat))
            
        # ----------------------------------------------------------------------
        # FLI1_AcousticalWarningLeft FLI1_AcousticalWarningRight
        AddCols_SensorStatus = []
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLI1_AcousticalWarningLeft',self.H4E['FLI1_AcousticalWarningLeft'].table_array2(AddCols_SensorStatus,AddColsFormat))
            WriteExcel.add_sheet_out_table_array('FLI1_AcousticalWarningRight',self.H4E['FLI1_AcousticalWarningRight'].table_array2(AddCols_SensorStatus,AddColsFormat))

        # ----------------------------------------------------------------------
        # DirIndLeft, DirIndRight
        
        AddCols_DirInd = ["LDW_Left","LDW_Right"]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('DirIndLeft',self.H4E['DirIndLeft'].table_array2(AddCols_DirInd,AddColsFormat))
            WriteExcel.add_sheet_out_table_array('DirIndRight',self.H4E['DirIndRight'].table_array2(AddCols_DirInd,AddColsFormat))
        
        # redundent information -> in future may be dropped 
        
        # sheet 'LDWS_warning_left intern' - online intern after suppressors -> redundent !!!
        AddCols_online = ["v_ego_at_t_start","Left_C0_at_t_start","TLC_Left_at_t_start","fd_Left_C0_at_t_start","Right_C0_at_t_start","fd_Right_C0_at_t_start","LaneWidth_at_t_start","road_curvature_at_t_start"]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('LDWS_warning_left intern',self.H4E['LDWS_warning_left_intern'].table_array2(AddCols_online,AddColsFormat))
        
        # sheet 'LDWS_warning_right intern' - online intern after suppressors -> redundent !!!
        AddCols_online = ["v_ego_at_t_start","Right_C0_at_t_start","TLC_Right_at_t_start","fd_Right_C0_at_t_start","Left_C0_at_t_start","fd_Left_C0_at_t_start","LaneWidth_at_t_start","road_curvature_at_t_start"]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('LDWS_warning_right intern',self.H4E['LDWS_warning_right_intern'].table_array2(AddCols_online,AddColsFormat))
 
        # ----------------------------------------------------------------------
        # High Lateral Velocity 
        
        AddCols_High_Lateral_Velocity_left = ["v_ego_at_t_start"]
        AddCols_High_Lateral_Velocity_left += ["ME_LD_present","ME_LD_present_Left_DeltaT"]
        AddCols_High_Lateral_Velocity_left += ["LNVU_LD_present","LNVU_LD_present_Left_DeltaT"]
        # Parameter of this LD
        AddCols_High_Lateral_Velocity_left += ["C0_left_wheel_at_t_start","max_Lateral_Velocity_Left"]
        AddCols_High_Lateral_Velocity_left += ["LaneWidth_at_t_start","road_curvature_at_t_start","Ay_at_t_start"]
        # more details
        AddCols_High_Lateral_Velocity_left += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
        AddCols_High_Lateral_Velocity_left += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
        AddCols_High_Lateral_Velocity_left += ["C0_right_wheel_at_t_start","Lateral_Velocity_Right_at_t_start"]
        AddCols_High_Lateral_Velocity_left += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
        AddCols_High_Lateral_Velocity_left += ["C0_right_wheel_at_t_stop","Lateral_Velocity_Right_at_t_stop"]
        AddCols_High_Lateral_Velocity_left += ["Ay_at_t_stop" ]
        AddCols_High_Lateral_Velocity_left += ["Tracking_present_Left","Tracking_present_Right","Tracking_present_Left_DeltaT","Tracking_present_Right_DeltaT"]
        AddCols_High_Lateral_Velocity_left += ["View_Range_Left_at_t_start", "View_Range_Right_at_t_start" ]
        AddCols_High_Lateral_Velocity_left += ["Left_C0_at_t_start", "Left_C1_at_t_start", "Left_C2_at_t_start", "Left_C3_at_t_start"]
        AddCols_High_Lateral_Velocity_left += ["Right_C0_at_t_start","Right_C1_at_t_start","Right_C2_at_t_start","Right_C3_at_t_start"]
        AddCols_High_Lateral_Velocity_left += ["Left_C0_at_t_stop","Right_C0_at_t_stop"] 
        AddCols_High_Lateral_Velocity_left += ["C0_left_wheel_filtered_at_t_start", "C0_left_wheel_filtered_at_t_stop"] 
        AddCols_High_Lateral_Velocity_left += ["LeftLinePosLateral_at_t_start", "LeftLineVelLateral_smoothed_at_t_start"] 
        if extended_b:
            WriteExcel.add_sheet_out_table_array('High Lateral Velocity Left',self.H4E['High_Lateral_Velocity_left'].table_array2(AddCols_High_Lateral_Velocity_left,AddColsFormat))
       
        AddCols_High_Lateral_Velocity_right = ["v_ego_at_t_start"]
        # Are ME or LNVU present?
        AddCols_High_Lateral_Velocity_right += ["ME_LD_present","ME_LD_present_Right_DeltaT"]
        AddCols_High_Lateral_Velocity_right += ["LNVU_LD_present","LNVU_LD_present_Right_DeltaT"]
        # Parameter of this LD
        AddCols_High_Lateral_Velocity_right += ["C0_right_wheel_at_t_start","max_Lateral_Velocity_Right"]
        AddCols_High_Lateral_Velocity_right += ["LaneWidth_at_t_start","road_curvature_at_t_start","Ay_at_t_start"]
        # more details
        AddCols_High_Lateral_Velocity_right += ["Me_Line_Changed_Right","Me_Line_Changed_Right_DeltaT"]
        AddCols_High_Lateral_Velocity_right += ["Me_Line_Changed_Left","Me_Line_Changed_Left_DeltaT"]
        AddCols_High_Lateral_Velocity_right += ["C0_left_wheel_at_t_start","Lateral_Velocity_Left_at_t_start"]
        AddCols_High_Lateral_Velocity_right += ["C0_right_wheel_at_t_stop", "Lateral_Velocity_Right_at_t_stop"]
        AddCols_High_Lateral_Velocity_right += ["C0_left_wheel_at_t_stop", "Lateral_Velocity_Left_at_t_stop"]
        AddCols_High_Lateral_Velocity_right += ["Ay_at_t_stop" ]
        AddCols_High_Lateral_Velocity_right += ["Tracking_present_Right","Tracking_present_Left","Tracking_present_Right_DeltaT","Tracking_present_Left_DeltaT"]
        AddCols_High_Lateral_Velocity_right += ["View_Range_Right_at_t_start","View_Range_Left_at_t_start"]
        AddCols_High_Lateral_Velocity_right += ["Right_C0_at_t_start","Right_C1_at_t_start","Right_C2_at_t_start","Right_C3_at_t_start"]
        AddCols_High_Lateral_Velocity_right += ["Left_C0_at_t_start", "Left_C1_at_t_start", "Left_C2_at_t_start", "Left_C3_at_t_start"]
        AddCols_High_Lateral_Velocity_right += ["Right_C0_at_t_stop", "Left_C0_at_t_stop"] 
        AddCols_High_Lateral_Velocity_right += ["C0_right_wheel_filtered_at_t_start", "C0_right_wheel_filtered_at_t_stop"] 
        AddCols_High_Lateral_Velocity_right += ["RightLinePosLateral_at_t_start", "RightLineVelLateral_smoothed_at_t_start"] 
        if extended_b:
            WriteExcel.add_sheet_out_table_array('High Lateral Velocity Right',self.H4E['High_Lateral_Velocity_right'].table_array2(AddCols_High_Lateral_Velocity_right,AddColsFormat))
  
  
        # ----------------------------------------------------------------------
        # FLC20_Image_Delay
        AddCols_FLC20_Image_Delay  = ['mean_CAN_Delay','min_CAN_Delay','max_CAN_Delay' ]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLC20_Image_Delay',self.H4E['FLC20_Image_Delay'].table_array2(AddCols_FLC20_Image_Delay,AddColsFormat))
        
        # ----------------------------------------------------------------------
        # FLC20_ME_UpdateInterval
        AddCols_FLC20_ME_UpdateInterval = ['mean_FLC20_ME_UpdateInterval','min_FLC20_ME_UpdateInterval','max_FLC20_ME_UpdateInterval' ]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLC20_ME_UpdateInterval',self.H4E['FLC20_ME_UpdateInterval'].table_array2(AddCols_FLC20_ME_UpdateInterval,AddColsFormat))
        
        # ----------------------------------------------------------------------
        # FLC20_TxInterval_FLI1
        AddCols_FLC20_ME_UpdateInterval = ['mean_FLC20_FLI1_UpdateInterval','min_FLC20_FLI1_UpdateInterval','max_FLC20_FLI1_UpdateInterval' ]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLC20_TxInterval_FLI1',self.H4E['FLC20_TxInterval_FLI1'].table_array2(AddCols_FLC20_ME_UpdateInterval,AddColsFormat))
        
        # ----------------------------------------------------------------------
        # FLC20_TxInterval_FLI2
        AddCols_FLC20_ME_UpdateInterval = ['mean_FLC20_FLI2_UpdateInterval','min_FLC20_FLI2_UpdateInterval','max_FLC20_FLI2_UpdateInterval' ]
        if extended_b:
            WriteExcel.add_sheet_out_table_array('FLC20_TxInterval_FLI2',self.H4E['FLC20_TxInterval_FLI2'].table_array2(AddCols_FLC20_ME_UpdateInterval,AddColsFormat))
     
  
        # -------------------------------------------------
        # write Excel files
        WriteExcel.save(ExcelFilename)
        print "  -> ",ExcelFilename," written"
        
        if self.SilLDWS_C_list:
            WriteExcel_sim.save(ExcelFilename_sim)
            print "  -> ",ExcelFilename_sim," written"
        else: 
            print "self.SilLDWS_C_list is empty",self.SilLDWS_C_list
            print "  -> ",ExcelFilename_sim," not written"
        
        print "EvalFLC20LDWS.excel_export() finish"
      
#-------------------------------------------------------------------------      









