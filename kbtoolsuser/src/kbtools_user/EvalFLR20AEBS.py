"""
:Organization: Knorr-Bremse SfN GmbH 
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' User module: FLR20 AEBS evalulation '''

''' to be called by DAS_eval.py '''

import os
import numpy as np

import kbtools
import kbtools_user
import sys, traceback


# ==============================================================================================
class cEvalFLR20AEBS():
    # ------------------------------------------------------------------------------------------
    def __init__(self):                # constructor
        self.myname = 'EvalFLR20AEBS'    # name of this user specific evaluation
        self.H4E = {}                    # H4E hunt4event directory
      
        self.enable_AUTOBOX = False
        self.na_values = 'NA'            # not available value for Excel

        self.err_msg_no_signal="no signal"
      
        # switches
        # add partial_brake and emergency_brake spreadsheets
        self.braking_spreadsheets = False
        self.do_AEBS_warnings_Offline_Radar_only = False
        self.do_AEBS_warnings_Offline_Fused = False
        self.do_Sim_AEBS_new_framework = True
     
        self.do_AEBS_DM1_A0 = False

      
    # ------------------------------------------------------------------------------------------
    def __del__(self):         # destructor
        pass
      
    # ------------------------------------------------------------------------------------------
    def init_Simulation(self,conf_DAS_eval, verbose = True):
        SilAEBS_C_list = []
        
        for nr in xrange(10):
            if nr == 0:
                nr_str = ''
            else:
                nr_str = "%d"%nr
                
            SilAEBS_C = self._single_init_Simulation(conf_DAS_eval, nr_str = nr_str, verbose = verbose)
            if SilAEBS_C is not None:
                SilAEBS_C_list.append((nr_str, SilAEBS_C))
                
        self.SilAEBS_C_list = SilAEBS_C_list      
    
    def _single_init_Simulation(self,conf_DAS_eval, nr_str = '', verbose = True):
        SIM_AEBS_C_ProgName = None                # r'C:\KBData\tmp\LDWS_C_app\LDWS_CUnit_main2.exe'
        SIM_AEBS_C_InterfaceFileName = None       # r'C:\KBData\sandboxes\LDWS_eclipse\LDWS_C\test\data\my_packet2\LDWS_sim_interface.py'
        SIM_AEBS_C_SimInterfaceClassName = None   # r'C_sim_interface'
        SIM_AEBS_C_ParameterSet = None            # r'C:\KBData\DAS_eval\LDWS\LDWS_C\KBDiag_DPV\2014_10_27_NewConfigValues.DPV'
        SIM_AEBS_C_Input_Signal_Modifier = None   # axv_zero;aRef_zero
        
        print "nr_str", nr_str
        if nr_str: 
            tag = '_'+ nr_str
        else:
            tag = '' 
       
        Token_SIM_AEBS_C_ProgName              = 'SIM_AEBS_C_ProgName'+tag
        Token_SIM_AEBS_C_InterfaceFileName     = 'SIM_AEBS_C_InterfaceFileName'+tag
        Token_SIM_AEBS_C_SimInterfaceClassName = 'SIM_AEBS_C_SimInterfaceClassName'+tag
        Token_SIM_AEBS_C_ParameterSet          = 'SIM_AEBS_C_ParameterSet'+tag
        Token_SIM_AEBS_C_Input_Signal_Modifier = 'SIM_AEBS_C_Input_Signal_Modifier'+tag
        
        if Token_SIM_AEBS_C_ProgName in conf_DAS_eval:
            if isinstance(conf_DAS_eval[Token_SIM_AEBS_C_ProgName],str):
                try: 
                    SIM_AEBS_C_ProgName = str(conf_DAS_eval[Token_SIM_AEBS_C_ProgName])
                except:
                    SIM_AEBS_C_ProgName = None
                    
        if Token_SIM_AEBS_C_InterfaceFileName in conf_DAS_eval:
            if isinstance(conf_DAS_eval[Token_SIM_AEBS_C_InterfaceFileName],str):
                try: 
                    SIM_AEBS_C_InterfaceFileName = str(conf_DAS_eval[Token_SIM_AEBS_C_InterfaceFileName])
                except:
                    SIM_AEBS_C_InterfaceFileName = None

        if Token_SIM_AEBS_C_SimInterfaceClassName in conf_DAS_eval:
            if isinstance(conf_DAS_eval[Token_SIM_AEBS_C_SimInterfaceClassName],str):
                try: 
                    SIM_AEBS_C_SimInterfaceClassName = str(conf_DAS_eval[Token_SIM_AEBS_C_SimInterfaceClassName])
                except:
                    SIM_AEBS_C_SimInterfaceClassName = None
                    
        if Token_SIM_AEBS_C_ParameterSet in conf_DAS_eval:
            if isinstance(conf_DAS_eval[Token_SIM_AEBS_C_ParameterSet],str):
                try: 
                    SIM_AEBS_C_ParameterSet = str(conf_DAS_eval[Token_SIM_AEBS_C_ParameterSet])
                except:
                    SIM_AEBS_C_ParameterSet = None
                    
        if Token_SIM_AEBS_C_Input_Signal_Modifier in conf_DAS_eval:
            if isinstance(conf_DAS_eval[Token_SIM_AEBS_C_Input_Signal_Modifier],str):
                try: 
                    SIM_AEBS_C_Input_Signal_Modifier = str(conf_DAS_eval[Token_SIM_AEBS_C_Input_Signal_Modifier])
                except:
                    SIM_AEBS_C_Input_Signal_Modifier = None
        
        
        print "CSimOL_MatlabBinInterface(): nr=%s"%nr_str
        print "  SIM_AEBS_C_ProgName              :", SIM_AEBS_C_ProgName
        print "  SIM_AEBS_C_InterfaceFileName     :", SIM_AEBS_C_InterfaceFileName
        print "  SIM_AEBS_C_SimInterfaceClassName :", SIM_AEBS_C_SimInterfaceClassName
        print "  SIM_AEBS_C_ParameterSet          :", SIM_AEBS_C_ParameterSet
        print "  SIM_AEBS_C_Input_Signal_Modifier :", SIM_AEBS_C_Input_Signal_Modifier
        
        
        
        myMetaData = kbtools_user.cMetaDataIO(self.Vehicle,verbose = verbose)
        dbc_list = myMetaData.GetMetaData(category='dbc_list')
        if (SIM_AEBS_C_ProgName is not None) and (SIM_AEBS_C_InterfaceFileName is not None) and (SIM_AEBS_C_SimInterfaceClassName is not None): 
            SilAEBS_C = kbtools.CSimOL_MatlabBinInterface(SIM_AEBS_C_ProgName,SIM_AEBS_C_InterfaceFileName,SimInterfaceClassName=SIM_AEBS_C_SimInterfaceClassName,dbc_list=dbc_list,verbose=verbose)
            # quick and dirty
            SilAEBS_C.SIM_AEBS_C_ParameterSet = SIM_AEBS_C_ParameterSet
            SilAEBS_C.SIM_AEBS_C_Input_Signal_Modifier = SIM_AEBS_C_Input_Signal_Modifier
        else:
            SilAEBS_C = None
            
        return SilAEBS_C
      
    # ------------------------------------------------------------------------------------------
    def init(self,folder,conf_DAS_eval,load_event=False):     # general start
      
      
        self.src_dir_meas = conf_DAS_eval['src_dir_meas']
      
        print "EvalFLR20AEBS::Init()"
        
        # ----------------------------------------------------------------------
        # location of AEBS software-in-the-loop file  
        self.AEBS_sil_exe_FullFileName = None
        self.WorkingDir4AEBS_sil_exe =  None
        if 'AEBS_sil_exe_FullFileName' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['AEBS_sil_exe_FullFileName'],str):
                self.AEBS_sil_exe_FullFileName  = conf_DAS_eval['AEBS_sil_exe_FullFileName']
                # working dir for AEBS_sil_exe
                self.WorkingDir4AEBS_sil_exe = r".\WorkingDir4AEBS_sil_exe"
        
        # parameter ParameterChnDict for Simulation
        self.ParameterChnDict = {}
        
        if 'DAMtPrewTime' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['DAMtPrewTime'],str):
                try: 
                    self.ParameterChnDict['DAMtPrewTime'] = float(conf_DAS_eval['DAMtPrewTime'])
                except:
                    pass
                    
        if 'PCCCDAMtDriverReactTime' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['PCCCDAMtDriverReactTime'],str):
                try: 
                    self.ParameterChnDict['PCCCDAMtDriverReactTime'] = float(conf_DAS_eval['PCCCDAMtDriverReactTime'])
                except:
                    pass
                    
        if 'aComfortSwingOutYAxis' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['aComfortSwingOutYAxis'],str):
                try: 
                    self.ParameterChnDict['aComfortSwingOutYAxis'] = float(conf_DAS_eval['aComfortSwingOutYAxis'])
                except:
                    pass
          
        if 'dx_limit' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['dx_limit'],str):
                try: 
                    self.ParameterChnDict['dx_limit'] = float(conf_DAS_eval['dx_limit'])
                except:
                    pass

        if 'REPRETGaxStdPartialBraking' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['REPRETGaxStdPartialBraking'],str):
                try: 
                    self.ParameterChnDict['REPRETGaxStdPartialBraking'] = float(conf_DAS_eval['REPRETGaxStdPartialBraking'])
                except:
                    pass

        if 'axvReqActivationThreshold' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['axvReqActivationThreshold'],str):
                try: 
                    self.ParameterChnDict['axvReqActivationThreshold'] = float(conf_DAS_eval['axvReqActivationThreshold'])
                except:
                    pass
             
        
        # print ParameterChnDict
        print "ParameterChnDict"
        for key, value in self.ParameterChnDict.iteritems():    
            print key, value
        
        # ---------------------------------------------------------------
        # config -> J1939_AEBS_SA
        self.config = {}
        self.config["J1939_AEBS_SourceAddress"] = int("0x2A",16)  
        if 'J1939_AEBS_SourceAddress' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['J1939_AEBS_SourceAddress'],str):
                try:
                    J1939_AEBS_SourceAddress =  int(conf_DAS_eval['J1939_AEBS_SourceAddress'],16)  
                    self.config["J1939_AEBS_SourceAddress"] = J1939_AEBS_SourceAddress
                except:
                    pass
       
        print "  J1939_AEBS_SourceAddress = 0x%X"%self.config["J1939_AEBS_SourceAddress"]
            
                
                
        
        # ---------------------------------------------------------------
        # enable_AEBS_plots
        self.enable_AEBS_plots = False
        if 'enable_AEBS_plots' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['enable_AEBS_plots'],str):
                if conf_DAS_eval['enable_AEBS_plots'].lower() in ["yes","on","1"]:
                    self.enable_AEBS_plots = True     
                    
        # ---------------------------------------------------------------
        # Vehicle information 
        self.Vehicle = None
        if 'Vehicle' in conf_DAS_eval:
            if isinstance(conf_DAS_eval['Vehicle'],str):
                try: 
                    self.Vehicle = str(conf_DAS_eval['Vehicle'])
                except:
                    pass

      

        
        # ----------------------------------------------------------------------
        # AEBS outputs
        t_join = 0
        
        # offline Fused
        self.H4E['AEBS_warning_offline_Fused']             = kbtools.cHunt4Event('on_phase','AEBS warning offline',t_join)
        self.H4E['AEBS_partial_brake_offline_Fused']       = kbtools.cHunt4Event('on_phase','AEBS partial brake offline',t_join)
        self.H4E['AEBS_emergency_brake_offline_Fused']     = kbtools.cHunt4Event('on_phase','AEBS emergency brake offline',t_join)
      
        # offline RadarOnly
        self.H4E['AEBS_warning_offline_RadarOnly']         = kbtools.cHunt4Event('on_phase','AEBS warning offline',t_join)
        self.H4E['AEBS_partial_brake_offline_RadarOnly']   = kbtools.cHunt4Event('on_phase','AEBS partial brake offline',t_join)
        self.H4E['AEBS_emergency_brake_offline_RadarOnly'] = kbtools.cHunt4Event('on_phase','AEBS emergency brake offline',t_join)
      
        # online
        self.H4E['AEBS_warning_online']               = kbtools.cHunt4Event('on_phase','AEBS warning online',t_join)
        self.H4E['AEBS_partial_brake_online']         = kbtools.cHunt4Event('on_phase','AEBS partial brake online',t_join)
        self.H4E['AEBS_emergency_brake_online']       = kbtools.cHunt4Event('on_phase','AEBS emergency brake online',t_join)
      
        # ----------------------------------------------------------------------------------------------
        # AEBS1_AEBSState_2A 
        # 0 "Not ready" ;
        # 1 "Temporarily n/a" 
        # 2 "Deactivated by driver" 
        # 3 "Ready" 
        # 4 "Driver override" 
        # 5 "Collision warn active" 
        # 6 "Collision warn with braking" 
        # 7 "Emergency brake active" 
        # 14 "Error" 
        # 15 "Not available / not installed" 

        self.AEBS1_AEBSState_list = []
        self.AEBS1_AEBSState_list.append((0, "Not ready"))
        self.AEBS1_AEBSState_list.append((1, "Temporarily not available"))
        self.AEBS1_AEBSState_list.append((2, "Deactivated by driver"))
        self.AEBS1_AEBSState_list.append((3, "Ready"))
        self.AEBS1_AEBSState_list.append((4, "Driver override"))
        self.AEBS1_AEBSState_list.append((5, "Collision warn active"))
        self.AEBS1_AEBSState_list.append((6, "Collision warn with braking"))
        self.AEBS1_AEBSState_list.append((7, "Emergency brake active"))
        self.AEBS1_AEBSState_list.append((14, "Error"))
        self.AEBS1_AEBSState_list.append((15, "Not installed"))
      
        # ---------------------------------------------------------------------------
        # target detected
        self.H4E['target_detected']    = kbtools.cHunt4Event('switch_on_time','target detection switch-on time',t_join)
        self.H4E['target_detected_CW'] = kbtools.cHunt4Event('switch_on_time','target detection CW switch-on time',t_join)

      
        # ---------------------------------------------------------------------------
        # offline
        for k,desc in self.AEBS1_AEBSState_list:
            self.H4E['AEBSState_%d_online'%k]  = kbtools.cHunt4Event('on_phase','AEBSState %s'%desc,t_join)

        # ----------------------------------------------------------------------
        # AEBS1_AEBSState
        default_value = []
        self.H4E['AEBS1_AEBSState'] = kbtools.cHunt4Event('multi_state','AEBS1 AEBSState',default_value)


        # ----------------------------------------------------------------------
        # AEBS DM1
        default_value = 0 # no SPN
        self.H4E['AEBS_DM1'] = kbtools.cHunt4Event('multi_state','AEBS DM1',default_value)
        
        # ----------------------------------------------------------------------
        # AEBS DM1 SA=A0
        if self.do_AEBS_DM1_A0:
            default_value = 0 # no SPN
            self.H4E['AEBS_DM1_A0'] = kbtools.cHunt4Event('multi_state','AEBS DM1 A0',default_value)
        
        
        # ---------------------------------------------------------------------------
        # Autobox
        if self.enable_AUTOBOX:
            self.H4E['AEBS_warning_Autobox']              = kbtools.cHunt4Event('on_phase','AEBS warning Autobox',t_join)
            self.H4E['AEBS_partial_brake_Autobox']        = kbtools.cHunt4Event('on_phase','AEBS partial brake Autobox',t_join)
            self.H4E['AEBS_emergency_brake_Autobox']      = kbtools.cHunt4Event('on_phase','AEBS emergency brake Autobox',t_join)
      
            self.H4E['AEBSState_warning_Autobox']         = kbtools.cHunt4Event('on_phase','AEBSState warning Autobox',t_join)
            self.H4E['AEBSState_partial_brake_Autobox']   = kbtools.cHunt4Event('on_phase','AEBSState partial brake Autobox',t_join)
            self.H4E['AEBSState_emergency_brake_Autobox'] = kbtools.cHunt4Event('on_phase','AEBSState emergency brake Autobox',t_join)
       
      
        # ----------------------------------------------------------------------
        # Software-in-the-loop Simulation

        # Init LDWS Simulation
        self.init_Simulation(conf_DAS_eval)

        # ----------------------------------------------------------------------
        # SIM_AEBS_warning_xy  
        # SIM_AEBS_partial_brake_xy 
        # SIM_AEBS_emergency_brake_xy
        t_join = 0.0
        for nr_str, _ in self.SilAEBS_C_list:
            
            self.H4E['SIM_AEBS_warning'+nr_str]         = kbtools.cHunt4Event('on_phase','SIM AEBS warning'+nr_str,t_join)
            self.H4E['SIM_AEBS_partial_brake'+nr_str]   = kbtools.cHunt4Event('on_phase','SIM AEBS partial brake'+nr_str,t_join)
            self.H4E['SIM_AEBS_emergency_brake'+nr_str] = kbtools.cHunt4Event('on_phase','SIM AEBS emergency brake'+nr_str,t_join)
           
      
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
    def calc_General_Attributes_of_AEBS(self,t_start):
    
        print "calc_General_Attributes_of_AEBS()"
    
        FLR20_sig = self.FLR20_sig
       
        General_Attributes_of_AEBS = {}
    
         
        # ---------------------------------------------------------------
        # v_ego_at_t_start
        try:
            t_v_ego, v_ego = kbtools_user.cDataAC100.get_v_ego(FLR20_sig,unit='km/h')
            v_ego_at_t_start = kbtools.GetPreviousSample(t_v_ego,v_ego,t_start)  # km/h
        except:
            v_ego_at_t_start = None
       
        # ---------------------------------------------------------------
        # dx_at_t_start
        try:
            t_dx, dx = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"TO_dx","m")
            dx_at_t_start = kbtools.GetPreviousSample(t_dx,dx,t_start)
        except:
            t_dx = None
            dx = None
            dx_at_t_start = None

        # ------
        '''
        try:
            t_asso_target_index      = FLR20_sig['PosMatrix']['CW']['Time']        
            asso_target_index        = FLR20_sig['PosMatrix']['CW']['asso_target_index']
            asso_target_index_at_t_start = kbtools.GetPreviousSample(t_asso_target_index,asso_target_index,t_start, shift=1)
        except:
            asso_target_index_at_t_start = None
            
        print "asso_target_index_at_t_start",asso_target_index_at_t_start
        
        try:
            t_asso_video_ID          = FLR20_sig['PosMatrix']['CW']['Time']        
            asso_video_ID            = FLR20_sig['PosMatrix']['CW']['asso_video_ID']
            asso_video_ID_at_t_start = kbtools.GetPreviousSample(t_asso_video_ID,asso_video_ID,t_start, shift=1)
        except:
            asso_video_ID_at_t_start = None
        
        print "asso_video_ID_at_t_start",asso_video_ID_at_t_start
        '''

        # ---------------------------------------------------------------
        # is_video_associated_at_t_start
        try:
            t_is_video_associated          = FLR20_sig['PosMatrix']['CW']['Time']        
            is_video_associated            = FLR20_sig['PosMatrix']['CW']['is_video_associated']
            #is_video_associated_at_t_start = is_video_associated[t_is_video_associated>=t_start][0]
            is_video_associated_at_t_start = kbtools.GetPreviousSample(t_is_video_associated,is_video_associated,t_start)
            if is_video_associated_at_t_start:
                #is_video_associated_dt_earlier = -(kbtools.getIntervalAroundEvent(t_is_video_associated,t_start,is_video_associated, output_mode = 't')[0] - t_start)
                t_start_is_video_associated = kbtools.getIntervalAroundEvent(t_is_video_associated,t_start,is_video_associated, output_mode = 't')[0]
                is_video_associated_dt_earlier = t_start - t_start_is_video_associated
                if t_dx is not None: 
                    is_video_associated_dx_at_start = kbtools.GetPreviousSample(t_dx,dx,t_start_is_video_associated)
                else:
                    is_video_associated_dx_at_start = None
            
            else:
                is_video_associated_dt_earlier = None 
                is_video_associated_dx_at_start = None   
        except:
            is_video_associated_at_t_start = None
            is_video_associated_dt_earlier = None 
            is_video_associated_dx_at_start = None
       
        AEBS_Attr = kbtools_user.cCalcAEBSAttributes(self.FLR20_sig, input_mode = 'FLR20' , mode = 'FLR20', t_event = t_start)   
        print "  AEBS_tr_id_at_t_warning                ", AEBS_Attr.AEBS_tr_id_at_t_warning

        print "  AEBS_tr_start_time                     ", AEBS_Attr.AEBS_tr_start_time
        print "  AEBS_tr_start_dx                       ", AEBS_Attr.AEBS_tr_start_dx

        print "  AEBS_video_start_time                  ", AEBS_Attr.AEBS_video_start_time
        print "  AEBS_video_start_dx                    ", AEBS_Attr.AEBS_video_start_dx

        print "  AEBS_tr_is_video_associated_start_time ", AEBS_Attr.AEBS_tr_is_video_associated_start_time
        print "  AEBS_tr_is_video_associated_start_dx   ", AEBS_Attr.AEBS_tr_is_video_associated_start_dx

        print "  AEBS_tr_is_video_confirmed_start_time  ", AEBS_Attr.AEBS_tr_is_video_confirmed_start_time
        print "  AEBS_tr_is_video_confirmed_start_dx    ", AEBS_Attr.AEBS_tr_is_video_confirmed_start_dx
       
        print "  cw_start_time                          ", AEBS_Attr.cw_start_time
        print "  cw_start_dx                            ", AEBS_Attr.cw_start_dx
        
        
       
       

        # ---------------------------------------------------------------
        # vrel_at_t_start
        try:
            t_vRel, vRel = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"TO_vRel","km/h")
            vrel_at_t_start = kbtools.GetPreviousSample(t_vRel,vRel,t_start)
        except:
            vrel_at_t_start = None
            
        # ---------------------------------------------------------------
        # v_obst_at_t_start
        if ( v_ego_at_t_start is not None) and (vrel_at_t_start is not None):
            v_obst_at_t_start = v_ego_at_t_start + vrel_at_t_start
        else:
            v_obst_at_t_start = None
       
        # ---------------------------------------------------------------
        # Stationary_at_t_start
        try:
            t_Stationary          = FLR20_sig['PosMatrix']['CW']['Time']        
            Stationary            = FLR20_sig['PosMatrix']['CW']['Stationary']
            #Stationary_at_t_start = Stationary[t_Stationary>=t_start][0]
            Stationary_at_t_start = kbtools.GetPreviousSample(t_Stationary,Stationary,t_start)
        except:
            Stationary_at_t_start = None
    
        # ---------------------------------------------------------------
        # Time to Collision
        if (vrel_at_t_start is not None) and (dx_at_t_start is not None):
        
            print "vrel_at_t_start",vrel_at_t_start
            print "dx_at_t_start",dx_at_t_start
            
            if vrel_at_t_start >= 0.0:
                ttc_at_t_start = None
            else:
                ttc_at_t_start = -dx_at_t_start/vrel_at_t_start*3.6
        else:
            ttc_at_t_start = None
    

        General_Attributes_of_AEBS['v_ego_at_t_start']               = v_ego_at_t_start
        General_Attributes_of_AEBS['is_video_associated_at_t_start'] = is_video_associated_at_t_start
        General_Attributes_of_AEBS['is_video_associated_dt_earlier'] = is_video_associated_dt_earlier
        General_Attributes_of_AEBS['is_video_associated_dx_at_start'] = is_video_associated_dx_at_start
        General_Attributes_of_AEBS['dx_at_t_start']                  = dx_at_t_start
        General_Attributes_of_AEBS['vrel_at_t_start']                = vrel_at_t_start
        General_Attributes_of_AEBS['v_obst_at_t_start']              = v_obst_at_t_start
        General_Attributes_of_AEBS['Stationary_at_t_start']          = Stationary_at_t_start
        General_Attributes_of_AEBS['ttc_at_t_start']                 = ttc_at_t_start
       
        General_Attributes_of_AEBS['AEBS_tr_start_dx']                     = AEBS_Attr.AEBS_tr_start_dx
        General_Attributes_of_AEBS['AEBS_video_start_dx']                  = AEBS_Attr.AEBS_video_start_dx
        General_Attributes_of_AEBS['AEBS_tr_is_video_associated_start_dx'] = AEBS_Attr.AEBS_tr_is_video_associated_start_dx
        General_Attributes_of_AEBS['AEBS_tr_is_video_confirmed_start_dx']  = AEBS_Attr.AEBS_tr_is_video_confirmed_start_dx
        General_Attributes_of_AEBS['cw_start_dx']                          = AEBS_Attr.cw_start_dx
        General_Attributes_of_AEBS['speed_reduced']                        = AEBS_Attr.speed_reduced
        
        
        
            
        print "General_Attributes_of_AEBS:"
        print  "  v_ego_at_t_start",                     General_Attributes_of_AEBS['v_ego_at_t_start']
        print  "  is_video_associated_at_t_start",       General_Attributes_of_AEBS['is_video_associated_at_t_start']
        print  "  is_video_associated_dt_earlier",       General_Attributes_of_AEBS['is_video_associated_dt_earlier']
        print  "  is_video_associated_dx_at_start",      General_Attributes_of_AEBS['is_video_associated_dx_at_start']
        print  "  dx_at_t_start",                        General_Attributes_of_AEBS['dx_at_t_start'] 
        print  "  vrel_at_t_start",                      General_Attributes_of_AEBS['vrel_at_t_start'] 
        print  "  v_obst_at_t_start",                    General_Attributes_of_AEBS['v_obst_at_t_start'] 
        print  "  Stationary_at_t_start",                General_Attributes_of_AEBS['Stationary_at_t_start']
        print  "  ttc_at_t_start",                       General_Attributes_of_AEBS['ttc_at_t_start'] 
        print  "  AEBS_tr_start_dx",                     General_Attributes_of_AEBS['AEBS_tr_start_dx']                     
        print  "  AEBS_tr_is_video_associated_start_dx", General_Attributes_of_AEBS['AEBS_tr_is_video_associated_start_dx'] 
        print  "  AEBS_tr_is_video_confirmed_start_dx",  General_Attributes_of_AEBS['AEBS_tr_is_video_confirmed_start_dx']
        print  "  AEBS_video_start_dx",                  General_Attributes_of_AEBS['AEBS_video_start_dx']                  
        print  "  cw_start_dx",                          General_Attributes_of_AEBS['cw_start_dx']    
        print  "  speed_reduced",                        General_Attributes_of_AEBS['speed_reduced']    
                              
       
        return General_Attributes_of_AEBS
        
      
    # ------------------------------------------------------------------------------------------
    def calc_start_of_CW_track(self,t_start):
    
    
        FLR20_sig = self.FLR20_sig

        start_of_CW_track = {} 
        # -----------------------------------------------------        
        # start of CW track  
        #t_cw_track          = FLR20_sig['Tracks'][0]['Time']
        #cw_track            = FLR20_sig['Tracks'][0]['CW_track']

        try:
            t_cw_track          = FLR20_sig['PosMatrix']['CW']['Time']
            cw_track            = FLR20_sig['PosMatrix']['CW']['Valid']
      
            start_idx, _ = kbtools.getIntervalAroundEvent(t_cw_track,t_start,cw_track>0.5)
            t_start_cw_track    = t_cw_track[start_idx]  
        
            # 1) t_start_cw_track_before_AEBS_warning 
            t_start_cw_track_before_AEBS_warning = t_start - t_start_cw_track
        
            # 2) dx_at_cw_track_start
            #t_dx                  = FLR20_sig['Tracks'][0]['Time']
            #dx                    = FLR20_sig['Tracks'][0]['dx']
            t_dx                  = FLR20_sig['PosMatrix']['CW']['Time']
            dx                    = FLR20_sig['PosMatrix']['CW']['dx']
            dx_at_cw_track_start  = dx[t_dx>=t_start_cw_track][0]
        except:
            t_start_cw_track = None
            t_start_cw_track_before_AEBS_warning = None
            dx_at_cw_track_start = None
         
        
        start_of_CW_track['t_start_cw_track']                     = t_start_cw_track
        start_of_CW_track['t_start_cw_track_before_AEBS_warning'] = t_start_cw_track_before_AEBS_warning
        start_of_CW_track['dx_at_cw_track_start']                 = dx_at_cw_track_start
        
        return start_of_CW_track
            
    # ------------------------------------------------------------------------------------------
    def check_TRW_allow_entry_and_cancel_flags(self, t_start):
   
        FLR20_sig = self.FLR20_sig
        checkTRW_AECFlags = kbtools_user.CcheckTRW_AECFlags()
        res_collision_warning,res_partial_braking,res_emergency_braking = checkTRW_AECFlags.calc(FLR20_sig,t_start)
    
        print "res_collision_warning", res_collision_warning
        print "res_partial_braking", res_partial_braking
        print "res_emergency_braking", res_emergency_braking

        TRW_AECFlags = {}
        TRW_AECFlags['res_collision_warning'] = res_collision_warning
        TRW_AECFlags['res_partial_braking']   = res_partial_braking
        TRW_AECFlags['res_emergency_braking'] = res_emergency_braking
 
        return TRW_AECFlags
    
    # ------------------------------------------------------------------------------------------
    def callback_AEBS1_AEBSState(self,t_start,t_stop):
        
        # ----------------------------------------------------------------------------------------------
        # AEBS1_AEBSState_2A 
        # 0 "Not ready" ;
        # 1 "Temporarily n/a" 
        # 2 "Deactivated by driver" 
        # 3 "Ready" 
        # 4 "Driver override" 
        # 5 "Collision warn active" 
        # 6 "Collision warn with braking" 
        # 7 "Emergency brake active" 
        # 14 "Error" 
        # 15 "Not available / not installed" 

        
        print "callback_AEBS1_AEBSState", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
        try:
            Time_AEBSState = FLR20_sig['J1939']["Time_AEBSState"]
            AEBSState      = FLR20_sig['J1939']["AEBSState"]
    
            idx = np.argwhere(np.logical_and(t_start<=Time_AEBSState,Time_AEBSState<t_stop))
            x = AEBSState[idx]
        
            
        
            statii_list = np.unique(x)
            print "   AEBSState:", statii_list
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
                    status_str = "Collision warn active (5)"
                elif status == 6: 
                    status_str = "Collision warn with braking (6)"
                elif status == 7: 
                    status_str = "Emergency brake active (7)"
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
    def callback_AEBS_DM1(self,t_start,t_stop):
               
        print "callback_AEBS_DM1", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
        try:
            Time_DM1           = FLR20_sig['J1939']["Time_AEBS_DM1"]
            DM1_ActSPN         = FLR20_sig['J1939']["AEBS_DM1_ActSPN"]
            DM1_ActFMI         = FLR20_sig['J1939']["AEBS_DM1_ActFMI"]
            DM1_AmberWarnLStat = FLR20_sig['J1939']["AEBS_DM1_AmberWarnLStat"]
            DM1_SA             = "0x%X"%FLR20_sig['J1939']["AEBS_DM1_SA"] 
            
            #  J1939["AEBS_DM1_ActDtcOC"]  
            #  J1939["AEBS_DM1_ActDtcCM"]  
       
            idx = np.argwhere(np.logical_and(t_start<=Time_DM1,Time_DM1<t_stop))
            DM1_ActSPN         = np.unique(DM1_ActSPN[idx])
            DM1_ActFMI         = np.unique(DM1_ActFMI[idx])
            DM1_AmberWarnLStat = np.unique(DM1_AmberWarnLStat[idx])
        
                        
            DM1_ActSPN_str         = ";".join(["%d"%x for x in DM1_ActSPN])  
            DM1_ActFMI_str         = ";".join(["%d"%x for x in DM1_ActFMI])  
            DM1_AmberWarnLStat_str = ";".join(["%d"%x for x in DM1_AmberWarnLStat])  
             
        except Exception, e:
            print "error - callback_AEBS_DM1: ",e.message
            traceback.print_exc(file=sys.stdout)
            DM1_ActSPN_str = "error"
            DM1_ActFMI_str = "error"
            DM1_AmberWarnLStat_str = "error"
            DM1_SA = "error"
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["DM1_ActSPN"] = DM1_ActSPN_str  
        att["DM1_ActFMI"] = DM1_ActFMI_str  
        att["DM1_AmberWarnLStat"] = DM1_AmberWarnLStat_str 
        att["DM1_SA"]  = DM1_SA
        
        return att
    # ------------------------------------------------------------------------------------------
    def callback_AEBS_DM1_A0(self,t_start,t_stop):
               
        print "callback_AEBS_DM1 A0", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
        try:
            Time_DM1           = FLR20_sig['J1939']["Time_AEBS_DM1_sA0"]
            DM1_ActSPN         = FLR20_sig['J1939']["SPN1_sA0"]
            DM1_ActFMI         = FLR20_sig['J1939']["FailureModeIdentifier1_sA0"]
            DM1_AmberWarnLStat = FLR20_sig['J1939']["AmberWarningLampStatus_sA0"]
            #  J1939["AEBS_DM1_ActDtcOC"]  
            #  J1939["AEBS_DM1_ActDtcCM"]  
       
            idx = np.argwhere(np.logical_and(t_start<=Time_DM1,Time_DM1<t_stop))
            DM1_ActSPN         = np.unique(DM1_ActSPN[idx])
            DM1_ActFMI         = np.unique(DM1_ActFMI[idx])
            DM1_AmberWarnLStat = np.unique(DM1_AmberWarnLStat[idx])
        
                        
            DM1_ActSPN_str         = ";".join(["%d"%x for x in DM1_ActSPN])  
            DM1_ActFMI_str         = ";".join(["%d"%x for x in DM1_ActFMI])  
            DM1_AmberWarnLStat_str = ";".join(["%d"%x for x in DM1_AmberWarnLStat])  
             
        except Exception, e:
            print "error - callback_AEBS_DM1_A0: ",e.message
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
    def callback_rising_edge_offline(self,t_start,t_stop):
        print "callback_rising_edge_offline", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
       
        
        # ----------------------------------------------------- 
        # General_Attributes_of_AEBS        
        General_Attributes_of_AEBS = self.calc_General_Attributes_of_AEBS(t_start)
 
 
      
      
        # ---------------------------------------------------------------
        # AEBS cascade 1:warning; 2:partial braking; 3:emergency braking
        AEBS_cascade = 1
        t                    =  FLR20_sig['simulation_output']['t']
        #AEBS_warning         = (FLR20_sig['simulation_output']['acoacoi_SetRequest']==1.0)
        AEBS_partial_brake   = (FLR20_sig['simulation_output']['acopebp_SetRequest']==1.0)
        AEBS_emergency_brake = (FLR20_sig['simulation_output']['acopebe_SetRequest']==1.0)
   
        interval = np.logical_and(t>=t_start,t<=t_stop)
        AEBS_partial_brake_occured   = any(AEBS_partial_brake[interval])
        AEBS_emergency_brake_occured = any(AEBS_emergency_brake[interval])
        if AEBS_partial_brake_occured:
            AEBS_cascade = 2
            
        if AEBS_emergency_brake_occured:
            AEBS_cascade = 3
        
        # -----------------------------------------------------        
        # start of CW track  
        start_of_CW_track = self.calc_start_of_CW_track(t_start)
                
        # ---------------------------------------------------------------
        # TRW_allow_entry_and_cancel_flags
        TRW_AECFlags = self.check_TRW_allow_entry_and_cancel_flags(t_start) 

   
            
        # -----------------------------------------------------
        # show for debugging
        print  "  t_start", t_start
        print  "  t_stop", t_stop
        print  "  v_ego_at_t_start", General_Attributes_of_AEBS['v_ego_at_t_start']
        print  "  is_video_associated_at_t_start", General_Attributes_of_AEBS['is_video_associated_at_t_start']
        print  "  is_video_associated_dt_earlier", General_Attributes_of_AEBS['is_video_associated_dt_earlier']
        print  "  dx_at_t_start",  General_Attributes_of_AEBS['dx_at_t_start'] 
        print  "  Stationary_at_t_start", General_Attributes_of_AEBS['Stationary_at_t_start']
        print  "  ttc_at_t_start", General_Attributes_of_AEBS['ttc_at_t_start'] 
        print  "  AEBS_cascade", AEBS_cascade
        print  "  t_start_cw_track",start_of_CW_track['t_start_cw_track'] 
        print  "  t_start_cw_track_before_AEBS_warning", start_of_CW_track['t_start_cw_track_before_AEBS_warning']
        print  "  dx_at_cw_track_start", start_of_CW_track['dx_at_cw_track_start']
        #print  "  cm_allow_entry_global_conditions_at_t_start", TRW_AECFlags['cm_allow_entry_global_conditions_at_t_start']
        #print  "  cw_allow_entry_at_t_start", TRW_AECFlags['cw_allow_entry_at_t_start']
        #print  "  cmb_allow_entry_at_t_start", TRW_AECFlags['cmb_allow_entry_at_t_start'] 
        #print  "  dx_at_allow_entry_global_conditions_start", TRW_AECFlags['dx_at_allow_entry_global_conditions_start'] 

        print  "  res_collision_warning", TRW_AECFlags['res_collision_warning']
        print  "  res_partial_braking", TRW_AECFlags['res_partial_braking']
        print  "  res_emergency_braking", TRW_AECFlags['res_emergency_braking']
        
        print  "  -fin-"

         
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["v_ego_at_t_start"]                            = General_Attributes_of_AEBS['v_ego_at_t_start']
        att["is_video_associated_at_t_start"]              = General_Attributes_of_AEBS['is_video_associated_at_t_start']
        att["is_video_associated_dt_earlier"]              = General_Attributes_of_AEBS['is_video_associated_dt_earlier']
        att["is_video_associated_dx_at_start"]             = General_Attributes_of_AEBS['is_video_associated_dx_at_start']
        att["dx_at_t_start"]                               = General_Attributes_of_AEBS['dx_at_t_start'] 
        att["Stationary_at_t_start"]                       = General_Attributes_of_AEBS['Stationary_at_t_start']
        att["ttc_at_t_start"]                              = General_Attributes_of_AEBS['ttc_at_t_start']
        
        att["AEBS_cascade"]                                = AEBS_cascade
        
        att["t_start_cw_track_before_AEBS_warning"]        = start_of_CW_track['t_start_cw_track_before_AEBS_warning']
        att["dx_at_cw_track_start"]                        = start_of_CW_track['dx_at_cw_track_start']
        
        #att["cm_allow_entry_global_conditions_at_t_start"] = TRW_AECFlags['cm_allow_entry_global_conditions_at_t_start']
        #att["cw_allow_entry_at_t_start"]                   = TRW_AECFlags['cw_allow_entry_at_t_start']
        #att["cmb_allow_entry_at_t_start"]                  = TRW_AECFlags['cmb_allow_entry_at_t_start'] 
        #att["dx_at_allow_entry_global_conditions_start"]   = TRW_AECFlags['dx_at_allow_entry_global_conditions_start'] 
    
        att["AECFlags_collision_warning"] = TRW_AECFlags['res_collision_warning']
        att["AECFlags_partial_braking"]   = TRW_AECFlags['res_partial_braking']
        att["AECFlags_emergency_braking"] = TRW_AECFlags['res_emergency_braking']
        
    
        return att
    # ------------------------------------------------------------------------------------------
    def callback_rising_edge_offline2(self,t_start,t_stop, parameters=None):
        '''
           new Simulation Framework kbaebslib
        
        '''
    
        print "callback_rising_edge_offline2", t_start,t_stop
        FLR20_sig = self.FLR20_sig
        sim_out = self.FLR20_sig['sim_out']
       
        
        # ----------------------------------------------------- 
        # General_Attributes_of_AEBS        
        General_Attributes_of_AEBS = self.calc_General_Attributes_of_AEBS(t_start)
 
 
      
      
        # ---------------------------------------------------------------
        # AEBS cascade 1:warning; 2:partial braking; 3:emergency braking
        AEBS_cascade = 1
        t                    = sim_out['t']
        AEBS_partial_brake   = sim_out['AEBS1_SystemState'] == 6                 
        AEBS_emergency_brake = sim_out['AEBS1_SystemState'] == 7
       
        interval = np.logical_and(t>=t_start,t<=t_stop)
        AEBS_partial_brake_occured   = any(AEBS_partial_brake[interval])
        AEBS_emergency_brake_occured = any(AEBS_emergency_brake[interval])
        if AEBS_partial_brake_occured:
            AEBS_cascade = 2
            
        if AEBS_emergency_brake_occured:
            AEBS_cascade = 3
        
        # -----------------------------------------------------        
        # start of CW track  
        start_of_CW_track = self.calc_start_of_CW_track(t_start)
                
        # ---------------------------------------------------------------
        # TRW_allow_entry_and_cancel_flags
        TRW_AECFlags = self.check_TRW_allow_entry_and_cancel_flags(t_start) 

        # ----------------------------------------
        # plotting
        if self.enable_AEBS_plots:
            if (parameters is not None) and ('enable_AEBS_plot' in parameters) and (parameters['enable_AEBS_plot']):
                enable_png_extract = True     # snapshots from video
                show_figures = False          # open matlablib figures

                if (parameters is not None) and ('nr_str' in parameters) and (parameters['nr_str']):
                    PngFolder = r'.\AEBS_Sim_png_%s'%parameters['nr_str']
                else:
                    PngFolder = r'.\AEBS_Sim_png'
                Description = "Automatic Evaluation"
                
                PlotAEBS = kbtools_user.cPlotFLR20AEBS(FLR20_sig, t_start, xlim=None, PngFolder = PngFolder, Description=Description, show_figures=show_figures)
                PlotAEBS.PlotAll(enable_png_extract=enable_png_extract,input_mode = 'SilAEBS_C')

            
        # -----------------------------------------------------
        # show for debugging
        print  "  t_start", t_start
        print  "  t_stop", t_stop
        print  "  v_ego_at_t_start", General_Attributes_of_AEBS['v_ego_at_t_start']
        print  "  is_video_associated_at_t_start", General_Attributes_of_AEBS['is_video_associated_at_t_start']
        print  "  is_video_associated_dt_earlier", General_Attributes_of_AEBS['is_video_associated_dt_earlier']
        print  "  dx_at_t_start",  General_Attributes_of_AEBS['dx_at_t_start'] 
        print  "  Stationary_at_t_start", General_Attributes_of_AEBS['Stationary_at_t_start']
        print  "  ttc_at_t_start", General_Attributes_of_AEBS['ttc_at_t_start'] 
        print  "  AEBS_cascade", AEBS_cascade
        print  "  t_start_cw_track",start_of_CW_track['t_start_cw_track'] 
        print  "  t_start_cw_track_before_AEBS_warning", start_of_CW_track['t_start_cw_track_before_AEBS_warning']
        print  "  dx_at_cw_track_start", start_of_CW_track['dx_at_cw_track_start']
        #print  "  cm_allow_entry_global_conditions_at_t_start", TRW_AECFlags['cm_allow_entry_global_conditions_at_t_start']
        #print  "  cw_allow_entry_at_t_start", TRW_AECFlags['cw_allow_entry_at_t_start']
        #print  "  cmb_allow_entry_at_t_start", TRW_AECFlags['cmb_allow_entry_at_t_start'] 
        #print  "  dx_at_allow_entry_global_conditions_start", TRW_AECFlags['dx_at_allow_entry_global_conditions_start'] 

        print  "  res_collision_warning", TRW_AECFlags['res_collision_warning']
        print  "  res_partial_braking", TRW_AECFlags['res_partial_braking']
        print  "  res_emergency_braking", TRW_AECFlags['res_emergency_braking']
        
        print  "  -fin-"

         
        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["v_ego_at_t_start"]                            = General_Attributes_of_AEBS['v_ego_at_t_start']
        att["is_video_associated_at_t_start"]              = General_Attributes_of_AEBS['is_video_associated_at_t_start']
        att["is_video_associated_dt_earlier"]              = General_Attributes_of_AEBS['is_video_associated_dt_earlier']
        att["is_video_associated_dx_at_start"]             = General_Attributes_of_AEBS['is_video_associated_dx_at_start']
        att["dx_at_t_start"]                               = General_Attributes_of_AEBS['dx_at_t_start'] 
        att["Stationary_at_t_start"]                       = General_Attributes_of_AEBS['Stationary_at_t_start']
        att["ttc_at_t_start"]                              = General_Attributes_of_AEBS['ttc_at_t_start']
        
        att["AEBS_cascade"]                                = AEBS_cascade
        
        att["t_start_cw_track_before_AEBS_warning"]        = start_of_CW_track['t_start_cw_track_before_AEBS_warning']
        att["dx_at_cw_track_start"]                        = start_of_CW_track['dx_at_cw_track_start']
        
        #att["cm_allow_entry_global_conditions_at_t_start"] = TRW_AECFlags['cm_allow_entry_global_conditions_at_t_start']
        #att["cw_allow_entry_at_t_start"]                   = TRW_AECFlags['cw_allow_entry_at_t_start']
        #att["cmb_allow_entry_at_t_start"]                  = TRW_AECFlags['cmb_allow_entry_at_t_start'] 
        #att["dx_at_allow_entry_global_conditions_start"]   = TRW_AECFlags['dx_at_allow_entry_global_conditions_start'] 
    
        att["AECFlags_collision_warning"] = TRW_AECFlags['res_collision_warning']
        att["AECFlags_partial_braking"]   = TRW_AECFlags['res_partial_braking']
        att["AECFlags_emergency_braking"] = TRW_AECFlags['res_emergency_braking']
        
    
        return att
    # ------------------------------------------------------------------------------------------
    def callback_rising_edge_online(self,t_start,t_stop, parameters=None):
        print "callback_rising_edge_online", t_start,t_stop
        FLR20_sig = self.FLR20_sig
       
        #Autobox_processing_Delay = 0.08   # about 80ms   (2 radar cycles)
        #tmp_t_start = t_start-Autobox_processing_Delay
        tmp_t_start = t_start
        
        
        # ----------------------------------------------------- 
        # General_Attributes_of_AEBS        
        General_Attributes_of_AEBS = self.calc_General_Attributes_of_AEBS(t_start)

      
        # ----------------------------------------------------------------
        # AEBS cascade 1:warning; 2:partial braking; 3:emergency braking
        
        # a) Online
        AEBS_cascade = None
        
        t_ABESState = FLR20_sig['AEBS_SFN_OUT']['Time_ABESState']
        if t_ABESState is not None:
            #AEBS_warning         = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 5
            AEBS_partial_brake   = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 6
            AEBS_emergency_brake = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 7

            AEBS_cascade = 1
        
            interval = np.logical_and(t_ABESState>=tmp_t_start,t_ABESState<=t_stop)
            AEBS_partial_brake_occured = any(AEBS_partial_brake[interval])
            AEBS_emergency_brake_occured = any(AEBS_emergency_brake[interval])
            if AEBS_partial_brake_occured:
                AEBS_cascade = 2
            
            if AEBS_emergency_brake_occured:
                AEBS_cascade = 3
                
                
        # b) Autobox
        Autobox_AEBS_cascade = None
        if self.enable_AUTOBOX:
            t_ABESState_Autobox = FLR20_sig['AEBS_SFN_OUT']['Time_ABESState_Autobox']
            if t_ABESState_Autobox is not None:
                #AEBS_warning_Autobox         = FLR20_sig['AEBS_SFN_OUT']['ABESState_Autobox'] == 5
                AEBS_partial_brake_Autobox   = FLR20_sig['AEBS_SFN_OUT']['ABESState_Autobox'] == 6
                AEBS_emergency_brake_Autobox = FLR20_sig['AEBS_SFN_OUT']['ABESState_Autobox'] == 7

                Autobox_AEBS_cascade = 1
        
                interval = np.logical_and(t_ABESState_Autobox>=tmp_t_start,t_ABESState_Autobox<=t_stop)
                AEBS_partial_brake_occured = any(AEBS_partial_brake_Autobox[interval])
                AEBS_emergency_brake_occured = any(AEBS_emergency_brake_Autobox[interval])
                if AEBS_partial_brake_occured:
                    Autobox_AEBS_cascade = 2
            
                if AEBS_emergency_brake_occured:
                    Autobox_AEBS_cascade = 3
        
        # -----------------------------------------------------        
        # start of CW track  
        start_of_CW_track = self.calc_start_of_CW_track(t_start)
           
        
        
        # -----------------------------------------------------        
        # do we have a associated offline warning -> calculate the offset
        # t_offset_AEBS_warning_offline
        
        t_offset_AEBS_warning_offline = None
        t_AEBS_warning_offline = None
        AEBS_warning_offline = None
        if 'simulation_output' in FLR20_sig:
            t_AEBS_warning_offline =  FLR20_sig['simulation_output']['t']
            AEBS_warning_offline   = (FLR20_sig['simulation_output']['acoacoi_SetRequest']==1.0)
        elif ('sim_out' in FLR20_sig) and FLR20_sig['sim_out'] is not None:
            sim_out = FLR20_sig['sim_out']
            t_AEBS_warning_offline =  sim_out['t']
            AEBS_warning_offline   = np.logical_and(sim_out['AEBS1_SystemState'] >= 5,sim_out['AEBS1_SystemState'] <= 7)
            
        
        if t_AEBS_warning_offline is not None:
            t_gate_start = tmp_t_start - 10
            t_gate_stop  = tmp_t_start + 10
            
            gate = np.logical_and(t_gate_start<t_AEBS_warning_offline, t_AEBS_warning_offline<t_gate_stop)
            a = t_AEBS_warning_offline[np.logical_and(gate,AEBS_warning_offline>0.5 )]
            if len(a)>0:
                t_AEBS_warning_offline = a[0]
                #print "t_AEBS_warning_offline" , t_AEBS_warning_offline
                t_offset_AEBS_warning_offline = t_AEBS_warning_offline - t_start
            
        
        
        # ---------------------------------------------------------------
        # TRW_allow_entry_and_cancel_flags
        TRW_AECFlags = self.check_TRW_allow_entry_and_cancel_flags(t_start) 

        # ----------------------------------------------------------------
        # ttc for partial and emergency braking
        t_ABESState, ABESState = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"ABESState","-")
                
        #Online_AEBSState_t                 = FLR20_sig['AEBS_SFN_OUT']['Time_ABESState']
        #Online_ABESState_partial_braking   = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 6
        #Online_ABESState_emergency_braking = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 7
        
        Online_AEBSState_t                 = t_ABESState
        Online_ABESState_partial_braking   = ABESState == 6
        Online_ABESState_emergency_braking = ABESState == 7
  
        t_start_collision_warning = t_start
        # b) partial braking
        try:
            idx = (np.argwhere(np.logical_and(Online_AEBSState_t>=t_start_collision_warning,Online_ABESState_partial_braking>0.5))[0])[0]   
            t_start_partial_braking = Online_AEBSState_t[idx]
            General_Attributes_of_AEBS_at_partial_braking = self.calc_General_Attributes_of_AEBS(t_start_partial_braking)
            rel_t_start_partial_braking       = t_start_partial_braking - t_start_collision_warning
            v_ego_at_t_start_partial_braking  = General_Attributes_of_AEBS_at_partial_braking['v_ego_at_t_start'] 
            dx_at_t_start_partial_braking     = General_Attributes_of_AEBS_at_partial_braking['dx_at_t_start'] 
            vrel_at_t_start_partial_braking   = General_Attributes_of_AEBS_at_partial_braking['vrel_at_t_start'] 
            ttc_at_t_start_partial_braking    = General_Attributes_of_AEBS_at_partial_braking['ttc_at_t_start'] 
        except:
            t_start_partial_braking          = None
            rel_t_start_partial_braking      = None
            v_ego_at_t_start_partial_braking = None
            dx_at_t_start_partial_braking    = None
            vrel_at_t_start_partial_braking  = None
            ttc_at_t_start_partial_braking   = None
        
        
        # c) emergency braking    
        try:
            idx = (np.argwhere(np.logical_and(Online_AEBSState_t>=t_start_partial_braking,Online_ABESState_emergency_braking>0.5))[0])[0]   
            t_start_emergency_braking = Online_AEBSState_t[idx]
            General_Attributes_of_AEBS_at_emergency_braking = self.calc_General_Attributes_of_AEBS(t_start_emergency_braking) 
            rel_t_start_emergency_braking      =  t_start_emergency_braking - t_start_collision_warning      
            v_ego_at_t_start_emergency_braking = General_Attributes_of_AEBS_at_emergency_braking['v_ego_at_t_start'] 
            dx_at_t_start_emergency_braking    = General_Attributes_of_AEBS_at_emergency_braking['dx_at_t_start'] 
            vrel_at_t_start_emergency_braking  = General_Attributes_of_AEBS_at_emergency_braking['vrel_at_t_start'] 
            ttc_at_t_start_emergency_braking   = General_Attributes_of_AEBS_at_emergency_braking['ttc_at_t_start'] 
        except:
            t_start_emergency_braking          = None
            rel_t_start_emergency_braking      = None
            v_ego_at_t_start_emergency_braking = None
            dx_at_t_start_emergency_braking    = None
            vrel_at_t_start_emergency_braking  = None
            ttc_at_t_start_emergency_braking   = None

   
        # -----------------------------------------------------
        # show for debugging
        print  "  tmp_t_start", tmp_t_start
        print  "  t_stop", t_stop
        print  "  v_ego_at_t_start",               General_Attributes_of_AEBS['v_ego_at_t_start']
        print  "  is_video_associated_at_t_start", General_Attributes_of_AEBS['is_video_associated_at_t_start']
        print  "  is_video_associated_dt_earlier", General_Attributes_of_AEBS['is_video_associated_dt_earlier']
        print  "  dx_at_t_start",                  General_Attributes_of_AEBS['dx_at_t_start'] 
        print  "  vrel_at_t_start",                General_Attributes_of_AEBS['vrel_at_t_start'] 
        print  "  v_obst_at_t_start",              General_Attributes_of_AEBS['v_obst_at_t_start'] 
        print  "  Stationary_at_t_start",          General_Attributes_of_AEBS['Stationary_at_t_start']
        print  "  ttc_at_t_start",                 General_Attributes_of_AEBS['ttc_at_t_start'] 
        print  "  AEBS_tr_start_dx",                     General_Attributes_of_AEBS['AEBS_tr_start_dx']                     
        print  "  AEBS_video_start_dx",                  General_Attributes_of_AEBS['AEBS_video_start_dx']                  
        print  "  AEBS_tr_is_video_associated_start_dx", General_Attributes_of_AEBS['AEBS_tr_is_video_associated_start_dx'] 
        print  "  AEBS_tr_is_video_confirmed_start_dx",  General_Attributes_of_AEBS['AEBS_tr_is_video_confirmed_start_dx'] 
        print  "  cw_start_dx",                          General_Attributes_of_AEBS['cw_start_dx']   
        print  "  speed_reduced",                        General_Attributes_of_AEBS['speed_reduced']                         
   
   

        
        print  "  AEBS_cascade", AEBS_cascade
        print  "  t_start_cw_track", start_of_CW_track['t_start_cw_track']
        print  "  t_start_cw_track_before_AEBS_warning", start_of_CW_track['t_start_cw_track_before_AEBS_warning']
        print  "  dx_at_cw_track_start", start_of_CW_track['dx_at_cw_track_start']
        print  "  t_offset_AEBS_warning_offline", t_offset_AEBS_warning_offline
        #print  "  cm_allow_entry_global_conditions_at_t_start", TRW_AECFlags['cm_allow_entry_global_conditions_at_t_start']
        #print  "  cw_allow_entry_at_t_start", TRW_AECFlags['cw_allow_entry_at_t_start']
        #print  "  cmb_allow_entry_at_t_start", TRW_AECFlags['cmb_allow_entry_at_t_start'] 
        #print  "  dx_at_allow_entry_global_conditions_start", TRW_AECFlags['dx_at_allow_entry_global_conditions_start'] 

        print  "  res_collision_warning", TRW_AECFlags['res_collision_warning']
        print  "  res_partial_braking", TRW_AECFlags['res_partial_braking']
        print  "  res_emergency_braking", TRW_AECFlags['res_emergency_braking']
        
        # ttc for partial and emergency braking
        print  "  t_start_partial_braking",         t_start_partial_braking
        print  "  rel_t_start_partial_braking",     rel_t_start_partial_braking
        print  "  v_ego_at_t_start_partial_braking",v_ego_at_t_start_partial_braking
        print  "  dx_at_t_start_partial_braking",   dx_at_t_start_partial_braking
        print  "  vrel_at_t_start_partial_braking", vrel_at_t_start_partial_braking
        print  "  ttc_at_t_start_partial_braking",  ttc_at_t_start_partial_braking
 
        print  "  t_start_emergency_braking",         t_start_emergency_braking
        print  "  rel_t_start_emergency_braking",     rel_t_start_emergency_braking
        print  "  v_ego_at_t_start_emergency_braking",v_ego_at_t_start_emergency_braking
        print  "  dx_at_t_start_emergency_braking",   dx_at_t_start_emergency_braking
        print  "  vrel_at_t_start_emergency_braking", vrel_at_t_start_emergency_braking
        print  "  ttc_at_t_start_emergency_braking",  ttc_at_t_start_emergency_braking
        
        print  "  -fin-"
    
        # ----------------------------------------
        # plotting
        if self.enable_AEBS_plots:
            if (parameters is not None) and ('enable_AEBS_plot' in parameters) and (parameters['enable_AEBS_plot']):
                enable_png_extract = True     # snapshots from video
                show_figures = False          # open matlablib figures

                PngFolder = r'.\AEBS_png'
                Description = "Automatic Evaluation"

                ''' separate folder for AEBS intervention at stillstand '''
                if General_Attributes_of_AEBS['v_ego_at_t_start'] < 5.0:
                    PngFolder = os.path.join(PngFolder,"Stillstand")
                
                PlotAEBS = kbtools_user.cPlotFLR20AEBS(FLR20_sig, t_start, xlim=None, PngFolder = PngFolder, Description=Description, show_figures=show_figures)
                PlotAEBS.PlotAll(enable_png_extract=enable_png_extract)


        # -----------------------------------------------------
        # return dictionary with attributes
        att = {}
        att["v_ego_at_t_start"]                            = General_Attributes_of_AEBS['v_ego_at_t_start']
        att["is_video_associated_at_t_start"]              = General_Attributes_of_AEBS['is_video_associated_at_t_start']
        att["is_video_associated_dt_earlier"]              = General_Attributes_of_AEBS['is_video_associated_dt_earlier']
        att["is_video_associated_dx_at_start"]             = General_Attributes_of_AEBS['is_video_associated_dx_at_start']
        
        att["dx_at_t_start"]                               = General_Attributes_of_AEBS['dx_at_t_start'] 
        att["vrel_at_t_start"]                             = General_Attributes_of_AEBS['vrel_at_t_start'] 
        att["v_obst_at_t_start"]                           = General_Attributes_of_AEBS['v_obst_at_t_start'] 
        
        att["Stationary_at_t_start"]                       = General_Attributes_of_AEBS['Stationary_at_t_start']
        att["ttc_at_t_start"]                              = General_Attributes_of_AEBS['ttc_at_t_start']

        att["AEBS_tr_start_dx"]                            = General_Attributes_of_AEBS['AEBS_tr_start_dx']
        att["AEBS_video_start_dx"]                         = General_Attributes_of_AEBS['AEBS_video_start_dx']
        att["AEBS_tr_is_video_associated_start_dx"]        = General_Attributes_of_AEBS['AEBS_tr_is_video_associated_start_dx']
        att["AEBS_tr_is_video_confirmed_start_dx"]         = General_Attributes_of_AEBS['AEBS_tr_is_video_confirmed_start_dx']
        att["cw_start_dx"]                                 = General_Attributes_of_AEBS['cw_start_dx']
        att["speed_reduced"]                               = General_Attributes_of_AEBS['speed_reduced']
        
        
        
        att["AEBS_cascade"]                                = AEBS_cascade
        att["Autobox_AEBS_cascade"]                        = Autobox_AEBS_cascade
        
        att["t_start_cw_track_before_AEBS_warning"]        = start_of_CW_track['t_start_cw_track_before_AEBS_warning']
        att["dx_at_cw_track_start"]                        = start_of_CW_track['dx_at_cw_track_start']
        
        att["t_offset_AEBS_warning_offline"]               = t_offset_AEBS_warning_offline
          
        #att["cm_allow_entry_global_conditions_at_t_start"] = TRW_AECFlags['cm_allow_entry_global_conditions_at_t_start']
        #att["cw_allow_entry_at_t_start"]                   = TRW_AECFlags['cw_allow_entry_at_t_start']
        #att["cmb_allow_entry_at_t_start"]                  = TRW_AECFlags['cmb_allow_entry_at_t_start'] 
        #att["dx_at_allow_entry_global_conditions_start"]   = TRW_AECFlags['dx_at_allow_entry_global_conditions_start'] 
    
        att["AECFlags_collision_warning"] = TRW_AECFlags['res_collision_warning']
        att["AECFlags_partial_braking"]   = TRW_AECFlags['res_partial_braking']
        att["AECFlags_emergency_braking"] = TRW_AECFlags['res_emergency_braking']

        
        # ttc for partial and emergency braking
        att["rel_t_start_partial_braking"]      = rel_t_start_partial_braking
        att["v_ego_at_t_start_partial_braking"] = v_ego_at_t_start_partial_braking
        att["dx_at_t_start_partial_braking"]    = dx_at_t_start_partial_braking
        att["vrel_at_t_start_partial_braking"]  = vrel_at_t_start_partial_braking
        att["ttc_at_t_start_partial_braking"]   = ttc_at_t_start_partial_braking
 
        att["rel_t_start_emergency_braking"]      = rel_t_start_emergency_braking
        att["v_ego_at_t_start_emergency_braking"] = v_ego_at_t_start_emergency_braking
        att["dx_at_t_start_emergency_braking"]    = dx_at_t_start_emergency_braking
        att["vrel_at_t_start_emergency_braking"]  = vrel_at_t_start_emergency_braking
        att["ttc_at_t_start_emergency_braking"]   = ttc_at_t_start_emergency_braking


        
        return att
       
    # ------------------------------------------------------------------------------------------
    def _process_offline_simulation(self,Source,EnableVideoValidation = True):
        # offline - software-in-the-loop
        
        print "offline - software-in-the-loop EnableVideoValidation=%d"%EnableVideoValidation
        
        # --------------------------------------------
        # Fused oder Radar Only
        if EnableVideoValidation: 
            # Fused        
            self.ParameterChnDict['PRESSAMEnableVideoValidation_B']       = 1
            self.ParameterChnDict['PRESSASEnableVideoValidation_B']       = 1
            self.ParameterChnDict['REPPREWEnableVideoValidationSAS_B']    = 1
            self.ParameterChnDict['REPRETGEXTEnableVideoValidationSAS_B'] = 1
            self.ParameterChnDict['REPRETGSTDEnableVideoValidationSAS_B'] = 1 
        else:
            # Radar Only
            self.ParameterChnDict['PRESSAMEnableVideoValidation_B']       = 0
            self.ParameterChnDict['PRESSASEnableVideoValidation_B']       = 0
            self.ParameterChnDict['REPPREWEnableVideoValidationSAS_B']    = 0
            self.ParameterChnDict['REPRETGEXTEnableVideoValidationSAS_B'] = 0
            self.ParameterChnDict['REPRETGSTDEnableVideoValidationSAS_B'] = 0 
    
            
             
        # --------------------------------------------
        # run software-in-the-loop simulation
        FLR20_sig = self.FLR20_sig
 
        #SimKBAEBS = kbtools_user.cSimKBAEBS(FLR20_sig, AEBS_sil_exe_FullFileName=self.AEBS_sil_exe_FullFileName, WorkingDir=self.WorkingDir4AEBS_sil_exe, verbose=True)
        #FLR20_sig['simulation_output'] = SimKBAEBS.run_simulation(self.ParameterChnDict,do_remove_working_dir_b = True)
 
        
        try:
            print "before kbtools_user.cSimKBAEBS()"
            SimKBAEBS = kbtools_user.cSimKBAEBS(FLR20_sig, AEBS_sil_exe_FullFileName=self.AEBS_sil_exe_FullFileName, WorkingDir=self.WorkingDir4AEBS_sil_exe, verbose=True)
            FLR20_sig['simulation_output'] = SimKBAEBS.run_simulation(self.ParameterChnDict,do_remove_working_dir_b = True)
            print "after kbtools_user.cSimKBAEBS()"
            
            # --------------------------------------------
            # analyse the simulation results
            t                    =  FLR20_sig['simulation_output']['t']
            AEBS_warning         = (FLR20_sig['simulation_output']['acoacoi_SetRequest']==1.0)
            AEBS_partial_brake   = (FLR20_sig['simulation_output']['acopebp_SetRequest']==1.0)
            AEBS_emergency_brake = (FLR20_sig['simulation_output']['acopebe_SetRequest']==1.0)
            err_msg=None
        except:
            print "error kbtools_user.cSimKBAEBS()"
            t = None 
            AEBS_warning = None
            AEBS_partial_brake = None
            AEBS_emergency_brake = None
            err_msg='sim error'
            
       
        # --------------------------------------------
        # store results
        if EnableVideoValidation: 
            self.H4E['AEBS_warning_offline_Fused'].process(t, AEBS_warning, Source,callback_rising_edge=self.callback_rising_edge_offline,err_msg=err_msg)
            self.H4E['AEBS_partial_brake_offline_Fused'].process(t, AEBS_partial_brake, Source,err_msg=err_msg)
            self.H4E['AEBS_emergency_brake_offline_Fused'].process(t, AEBS_emergency_brake, Source,err_msg=err_msg)
        else:
            self.H4E['AEBS_warning_offline_RadarOnly'].process(t, AEBS_warning, Source,callback_rising_edge=self.callback_rising_edge_offline,err_msg=err_msg)
            self.H4E['AEBS_partial_brake_offline_RadarOnly'].process(t, AEBS_partial_brake, Source,err_msg=err_msg)
            self.H4E['AEBS_emergency_brake_offline_RadarOnly'].process(t, AEBS_emergency_brake, Source,err_msg=err_msg)
           
    # ------------------------------------------------------------------------------------------
    def DoSimulation(self, SilAEBS_C):
    
        print "DoSimulation"   
        VariationName = "sim"
        xlim = None
        gate = None
        Description = ""
        create_expected_results = False
        SimOutput_as_ExpectedResult = False
        
        # quick and dirty
        ParameterSet = SilAEBS_C.SIM_AEBS_C_ParameterSet
        ParameterChnDict = {}

        SilAEBS_C.SIM_AEBS_C_Input_Signal_Modifier
        cfg = dict([('Input_Signal_Modifier',SilAEBS_C.SIM_AEBS_C_Input_Signal_Modifier)])
        FileBaseName_MatlabBin = r'TD_aebs_01'
        SilAEBS_C.Run(self.FLR20_sig, VariationName=VariationName,xlim=xlim,gate=gate,Description=Description,create_expected_results = create_expected_results,SimOutput_as_ExpectedResult=SimOutput_as_ExpectedResult,ParameterSet=ParameterSet,ParameterChnDict=ParameterChnDict,cfg=cfg,FileBaseName_MatlabBin=FileBaseName_MatlabBin)

        ''' 
        SilAEBS_C.CreateMatlabBin(self.FLR20_sig, VariationName=VariationName,xlim=xlim,gate=gate,Description=Description,create_expected_results = create_expected_results,SimOutput_as_ExpectedResult=SimOutput_as_ExpectedResult,ParameterSet=ParameterSet,FileBaseName_MatlabBin=FileBaseName_MatlabBin)
        SilAEBS_C.RunSimulation()
        SilAEBS_C.LoadMatlabBin()
        #print "SilAEBS_C.matdata_output", SilAEBS_C.matdata_output
           
        SilAEBS_C.CleanUp()           
            # self.FLR20_sig['sim_out'] = self.SilAEBS_C.matdata_output
        '''    
           
            
        print "DoSimulation - end"   
        
        

    # ------------------------------------------------------------------------------------------
    def process(self,Source):  # evaluate recorded file

        print "============================================"
        print "EvalFLR20AEBS::process()"
        
        # --------------------------------------------
        # extract FLR20 signals from measurement (Source -> FLR20_sig)
        try:
            
            FLR20_sig = kbtools_user.cDataAC100.load_AC100_from_Source(Source,config=self.config)
            # store FLR20 signals to be used in callback function "callback_rising_edge"
            self.FLR20_sig = FLR20_sig
            
        except Exception, e:
            print "error with extract FLR20 signals from measurement: ",e.message
            traceback.print_exc(file=sys.stdout) 
            return
 
        print "process(): FileName: ", self.FLR20_sig['FileName']
        
        
        # --------------------------------------------
        # offline - software-in-the-loop
        #try:
        # Fused
        if self.do_AEBS_warnings_Offline_Fused:
            self._process_offline_simulation(Source,EnableVideoValidation=True)   
            
        # RadarOnly
        if self.do_AEBS_warnings_Offline_Radar_only:
            self._process_offline_simulation(Source,EnableVideoValidation=False)             
            
        #except:
        #    print "error with AEBS software-in-the-loop"   

        
        # --------------------------------------------------------------
        if 1:
            print "EvalFLR20AEBS: offline - SIM"
                                    
            for nr_str, SilAEBS_C in self.SilAEBS_C_list:
                try:
                    print "------------------------------"
                    print "Simulation: %s"%nr_str
                    self.DoSimulation(SilAEBS_C)
                
                    self.FLR20_sig['sim_out'] = SilAEBS_C.matdata_output
        
                    sim_out = self.FLR20_sig['sim_out']
                    t                      = sim_out['t']
                    AEBS_warning           = np.logical_and(sim_out['AEBS1_SystemState'] >= 5,sim_out['AEBS1_SystemState'] <= 7)
                    AEBS_partial_braking   = sim_out['AEBS1_SystemState'] == 6                 
                    AEBS_emergency_braking = sim_out['AEBS1_SystemState'] == 7
                    self.H4E['SIM_AEBS_warning'        +nr_str].process(t, AEBS_warning,           Source, callback_rising_edge=self.callback_rising_edge_offline2, callback_parameters={'enable_AEBS_plot':True,'nr_str':nr_str})
                    self.H4E['SIM_AEBS_partial_brake'  +nr_str].process(t, AEBS_partial_braking,   Source, callback_rising_edge=self.callback_rising_edge_offline2, callback_parameters={'enable_AEBS_plot':False})
                    self.H4E['SIM_AEBS_emergency_brake'+nr_str].process(t, AEBS_emergency_braking, Source, callback_rising_edge=self.callback_rising_edge_offline2, callback_parameters={'enable_AEBS_plot':False})

                except Exception, e:
                    print "error - simulation: ",e.message
                    traceback.print_exc(file=sys.stdout)
                    print " -> but we go on"
                    self.H4E['SIM_AEBS_warning'        +nr_str].process(None, None , Source, err_msg='sim error')
                    self.H4E['SIM_AEBS_partial_brake'  +nr_str].process(None, None , Source, err_msg='sim error')
                    self.H4E['SIM_AEBS_emergency_brake'+nr_str].process(None, None , Source, err_msg='sim error')


        
        # --------------------------------------------------------------
        # online - ECU
        if 1:
            print "--------------------"
            print "online - ECU"
            
            try:
                nr_str, SilAEBS_C = self.SilAEBS_C_list[0]
                self.FLR20_sig['sim_out'] = SilAEBS_C.matdata_output
            except Exception, e:
                self.FLR20_sig['sim_out'] = None
                print "error - simulation: ",e.message
                traceback.print_exc(file=sys.stdout)
                print " -> but we go on"

            
             
            #if 0: 
            #    Online_AEBS_warning_t           = FLR20_sig['AEBS_SFN_OUT']['Time_Warning']
            #    Online_AEBS_warning             = FLR20_sig['AEBS_SFN_OUT']['Warning']
            #    Online_AEBS_partial_braking_t   = FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand']
            #    Online_AEBS_partial_braking     = np.logical_and(FLR20_sig['AEBS_SFN_OUT']['AccelDemand'] <0.0,FLR20_sig['AEBS_SFN_OUT']['AccelDemand']>-4.0)
            #    Online_AEBS_emergency_braking_t = FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand']
            #    Online_AEBS_emergency_braking   = FLR20_sig['AEBS_SFN_OUT']['AccelDemand']<=-4.0
            #else:
            
            # AEBS system state
            # 5 collision warning
            # 6 partial braking
            # 7 emergency braking
            #Online_AEBSState_t = FLR20_sig['AEBS_SFN_OUT']['Time_ABESState']
            #Online_ABESState = FLR20_sig['AEBS_SFN_OUT']['ABESState']
            
            #Online_AEBSState_t = FLR20_sig['J1939']["Time_AEBSState"]
            #Online_ABESState = FLR20_sig['J1939']["AEBSState"]
            Online_AEBSState_t, Online_ABESState = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"ABESState","-")
            
             
            
            Online_AEBS_warning_t           = Online_AEBSState_t
            Online_AEBS_warning             = np.logical_and(Online_ABESState>=5,Online_ABESState<=7)
            Online_AEBS_partial_braking_t   = Online_AEBSState_t
            Online_AEBS_partial_braking     = Online_ABESState==6
            Online_AEBS_emergency_braking_t = Online_AEBSState_t
            Online_AEBS_emergency_braking   = Online_ABESState==7
             
            #print "Time_AEBSState", Online_AEBSState_t
            #print "AEBSState", Online_ABESState
      
            # online
            self.H4E['AEBS_warning_online'].process(Online_AEBS_warning_t, Online_AEBS_warning, Source,callback_rising_edge=self.callback_rising_edge_online,callback_parameters={'enable_AEBS_plot':True})
            self.H4E['AEBS_partial_brake_online'].process(Online_AEBS_partial_braking_t, Online_AEBS_partial_braking, Source)
            self.H4E['AEBS_emergency_brake_online'].process(Online_AEBS_emergency_braking_t, Online_AEBS_emergency_braking, Source)
      
            # AEBS system state
            # 5 collision warning
            # 6 partial braking
            # 7 emergency braking
           
            
            for k,_ in self.AEBS1_AEBSState_list:
                self.H4E['AEBSState_%d_online'%k].process(Online_AEBSState_t, Online_ABESState == k, Source,callback_rising_edge=self.callback_rising_edge_online)
           
            # ----------------------------------------------------------------------
            # AEBS1_AEBSStateS 
            self.H4E['AEBS1_AEBSState'].process(Online_AEBSState_t, Online_ABESState, Source, callback_rising_edge=self.callback_AEBS1_AEBSState)

            # ----------------------------------------------------------------------
            # AEBS DM1
            print "AEBS_DM1 - start"
            self.H4E['AEBS_DM1'].process(FLR20_sig['J1939']["Time_AEBS_DM1"], FLR20_sig['J1939']["AEBS_DM1_ActSPN"], Source, callback_rising_edge=self.callback_AEBS_DM1)
            print "AEBS_DM1 - end"
            # ----------------------------------------------------------------------
            # AEBS DM1 A0
            if self.do_AEBS_DM1_A0:
                self.H4E['AEBS_DM1_A0'].process(FLR20_sig['J1939']["Time_AEBS_DM1_sA0"], FLR20_sig['J1939']["SPN1_sA0"], Source, callback_rising_edge=self.callback_AEBS_DM1_A0)

            # self.H4E['AEBSState_warning_online'].process(Online_AEBSState_t, Online_ABESState_collision_warning, Source,callback_rising_edge=self.callback_rising_edge_online)
            #self.H4E['AEBSState_partial_brake_online'].process(Online_AEBSState_t, Online_ABESState_partial_braking, Source)
            #self.H4E['AEBSState_emergency_brake_online'].process(Online_AEBSState_t, Online_ABESState_emergency_braking, Source)

        # --------------------------------------------------------------
        # online - Autobox 
        if self.enable_AUTOBOX:
            print "online - Autobox"

            Autobox_AEBS_warning_t           = FLR20_sig['AEBS_SFN_OUT']['Time_Warning_Autobox']
            Autobox_AEBS_warning             = FLR20_sig['AEBS_SFN_OUT']['Warning_Autobox']
            Autobox_AEBS_partial_braking_t   = FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox']
            Autobox_AEBS_partial_braking     = np.logical_and(FLR20_sig['AEBS_SFN_OUT']['AccelDemand_Autobox'] <0.0,FLR20_sig['AEBS_SFN_OUT']['AccelDemand_Autobox']>-4.0)
            Autobox_AEBS_emergency_braking_t = FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand_Autobox']
            Autobox_AEBS_emergency_braking   = FLR20_sig['AEBS_SFN_OUT']['AccelDemand_Autobox']<=-4.0
      
            # Autobox
            self.H4E['AEBS_warning_Autobox'].process(Autobox_AEBS_warning_t, Autobox_AEBS_warning, Source,callback_rising_edge=self.callback_rising_edge_online)
            self.H4E['AEBS_partial_brake_Autobox'].process(Autobox_AEBS_partial_braking_t, Autobox_AEBS_partial_braking, Source)
            self.H4E['AEBS_emergency_brake_Autobox'].process(Autobox_AEBS_emergency_braking_t, Autobox_AEBS_emergency_braking, Source)
      
            # AEBS system state
            # 5 collision warning
            # 6 partial braking
            # 7 emergency braking
           
            Autobox_AEBSState_t = FLR20_sig['AEBS_SFN_OUT']['Time_ABESState_Autobox']
            Autobox_ABESState_collision_warning = FLR20_sig['AEBS_SFN_OUT']['ABESState_Autobox'] == 5
            Autobox_ABESState_partial_braking   = FLR20_sig['AEBS_SFN_OUT']['ABESState_Autobox'] == 6
            Autobox_ABESState_emergency_braking = FLR20_sig['AEBS_SFN_OUT']['ABESState_Autobox'] == 7
            
            self.H4E['AEBSState_warning_Autobox'].process(Autobox_AEBSState_t, Autobox_ABESState_collision_warning, Source,callback_rising_edge=self.callback_rising_edge_online)
            self.H4E['AEBSState_partial_brake_Autobox'].process(Autobox_AEBSState_t, Autobox_ABESState_partial_braking, Source)
            self.H4E['AEBSState_emergency_brake_Autobox'].process(Autobox_AEBSState_t, Autobox_ABESState_emergency_braking, Source)
       
        #------------------------------------------------------------------
        # target detected
        print "process target detected"

        # a) t_condition_target_detected, condition_target_detected
        t_condition_target_detected, condition_target_detected = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"relevantObjectDetected","-")
        self.H4E['target_detected'].process(t_condition_target_detected, condition_target_detected, Source,err_msg=self.err_msg_no_signal)
           
            
        # b) t_condition_target_detected_CW, condition_target_detected_CW
        t_condition_target_detected_CW, condition_target_detected_CW = kbtools_user.cDataAC100.get_AEBS(FLR20_sig,"TO_detected_CW","-")
        self.H4E['target_detected_CW'].process(t_condition_target_detected_CW, condition_target_detected_CW, Source,err_msg=self.err_msg_no_signal) 
 
       
        print "end process - EvalFLR20AEBS"
      
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
      
        self.kb_tex.tex('\n\\newpage\\section{FLR20EvalAEBS}')
    
        # online ECU   
        self.kb_tex.tex('\n\\subsection{KB AEBS Online ECU}')
        self.kb_tex.table(self.H4E['AEBS_warning_online'].table_array())
        self.kb_tex.table(self.H4E['AEBS_partial_brake_online'].table_array())
        self.kb_tex.table(self.H4E['AEBS_emergency_brake_online'].table_array())

        if self.enable_AUTOBOX:

            # online Autobox
            self.kb_tex.tex('\n\\subsection{KB AEBS Online Autobox}')
            self.kb_tex.table(self.H4E['AEBS_warning_Autobox'].table_array())
            self.kb_tex.table(self.H4E['AEBS_partial_brake_Autobox'].table_array())
            self.kb_tex.table(self.H4E['AEBS_emergency_brake_Autobox'].table_array())

        # offline Fused
        if self.do_AEBS_warnings_Offline_Fused:
            self.kb_tex.tex('\n\\subsection{KB AEBS Offline Fused}')
            self.kb_tex.table(self.H4E['AEBS_warning_offline_Fused'].table_array())
            self.kb_tex.table(self.H4E['AEBS_partial_brake_offline_Fused'].table_array())
            self.kb_tex.table(self.H4E['AEBS_emergency_brake_offline_Fused'].table_array())
        
        # offline Radar Only
        if self.do_AEBS_warnings_Offline_Radar_only:
            self.kb_tex.tex('\n\\subsection{KB AEBS Offline Radar-Only}')
            self.kb_tex.table(self.H4E['AEBS_warning_offline_RadarOnly'].table_array())
            self.kb_tex.table(self.H4E['AEBS_partial_brake_offline_RadarOnly'].table_array())
            self.kb_tex.table(self.H4E['AEBS_emergency_brake_offline_RadarOnly'].table_array())
        
        # online   
        self.kb_tex.tex('\n\\subsection{AEBS1 AEBS Status Online}')
        
        for k,desc in self.AEBS1_AEBSState_list:
            self.kb_tex.tex('\n\\subsection{%d - %s}'%(k,desc))
            self.kb_tex.table(self.H4E['AEBSState_%d_online'%k].table_array())
        #self.kb_tex.tex('\nLeft: %d entries; '% self.H4E['LDWS_warning_left'].n_entries_EventList())
        
        # ----------------------------------------------------------------------
        # AEBS1_AEBSState
        self.kb_tex.tex('\n\\subsection{AEBS1 AEBSState}')
        self.kb_tex.tex('\nAEBS1 AEBSState: %d entries; '% self.H4E['AEBS1_AEBSState'].n_entries_EventList())

        # ----------------------------------------------------------------------
        # # AEBS DM1
        self.kb_tex.tex('\n\\subsection{AEBS DM1}')
        self.kb_tex.tex('\nAEBS DM1: %d entries; '% self.H4E['AEBS_DM1'].n_entries_EventList())
        if self.do_AEBS_DM1_A0:
            self.kb_tex.tex('\nAEBS DM1 A0: %d entries; '% self.H4E['AEBS_DM1_A0'].n_entries_EventList())

                  
        #label = self.kb_tex.table(self.H4E['AEBSState_warning_online'].table_array())
        #label = self.kb_tex.table(self.H4E['AEBSState_partial_brake_online'].table_array())
        #label = self.kb_tex.table(self.H4E['AEBSState_emergency_brake_online'].table_array())
     
        # Autobox   
        if self.enable_AUTOBOX:
            self.kb_tex.tex('\n\\subsection{KB AEBS Autobox (AEBS Status)}')
            self.kb_tex.table(self.H4E['AEBSState_warning_Autobox'].table_array())
            self.kb_tex.table(self.H4E['AEBSState_partial_brake_Autobox'].table_array())
            self.kb_tex.table(self.H4E['AEBSState_emergency_brake_Autobox'].table_array())

        # ----------------------------------------------------------------------
        # AEBS Simulation
        self.kb_tex.tex('\n\\subsection{AEBS Simulation}')
        
        for nr_str, _ in self.SilAEBS_C_list:
            self.kb_tex.tex('\n\\subsubsection{%s}'%nr_str)
            self.kb_tex.tex('\nAEBS warning: %d entries; '% self.H4E['SIM_AEBS_warning'+nr_str].n_entries_EventList())
            self.kb_tex.tex('\nAEBS partial brake: %d entries; '% self.H4E['SIM_AEBS_partial_brake'+nr_str].n_entries_EventList())
            self.kb_tex.tex('\nAEBS emergency brake: %d entries; '% self.H4E['SIM_AEBS_emergency_brake'+nr_str].n_entries_EventList())
  
        # ---------------------------------------
        # target detected             
        self.kb_tex.tex('\n\\subsection{Target detected}')
        
        self.kb_tex.tex('\n\\subsubsection{Target detected}')
        self.kb_tex.table(self.H4E['target_detected'].table_array())

        self.kb_tex.tex('\n\\subsubsection{Target detected CW}')
        self.kb_tex.table(self.H4E['target_detected_CW'].table_array())
           
        # ---------------------------------------
        self.kb_tex.tex('\nEvalFLR20AEBS-finished')
      
    # ------------------------------------------------------------------------------------------
    def _build_ExcelFilename(self,ExcelBaseFilename):
        if self.src_dir_meas is not None:
            ExcelBaseFilename = "%s_%s"%(ExcelBaseFilename,os.path.basename(self.src_dir_meas))
        ExcelFilename = ExcelBaseFilename+'.xls' 
        return ExcelFilename
    # ------------------------------------------------------------------------------------------
    def excel_export(self):          # events are writte into an Excel spreadsheet
    
        print "EvalFLR20AEBS.excel_export()"
        print "src_dir_meas :",os.path.basename(self.src_dir_meas)
          
        
        # new format 
        AddColsFormat = {}
        AddColsFormat["v_ego_at_t_start"]                     = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["dx_at_t_start"]                        = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["vrel_at_t_start"]                      = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["v_obst_at_t_start"]                    = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["t_start_cw_track_before_AEBS_warning"] = ("ExcelNumFormat", '##0.00 "s"')    # "%4.2f s"
        AddColsFormat["dx_at_cw_track_start"]                 = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["t_offset_AEBS_warning_offline"]        = ("ExcelNumFormat", '##0.000 "s"')   # "%4.3f s"
        AddColsFormat["ttc_at_t_start"]                       = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        AddColsFormat["dx_at_allow_entry_global_conditions_start"] = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"

        AddColsFormat["is_video_associated_dt_earlier"]        = ("ExcelNumFormat", '##0.000 "s"')   # "%4.3f s"
        AddColsFormat["is_video_associated_dx_at_start"]       = ("ExcelNumFormat", '##0.0 "m"')   # "%4.3f s"
        
        AddColsFormat["AEBS_tr_start_dx"]                      = ("ExcelNumFormat", '##0.0 "m"')   # "%4.3f s"
        AddColsFormat["AEBS_video_start_dx"]                   = ("ExcelNumFormat", '##0.0 "m"')   # "%4.3f s"
        AddColsFormat["AEBS_tr_is_video_associated_start_dx"]  = ("ExcelNumFormat", '##0.0 "m"')   # "%4.3f s"
        AddColsFormat["AEBS_tr_is_video_confirmed_start_dx"]   = ("ExcelNumFormat", '##0.0 "m"')   # "%4.3f s"
        AddColsFormat["cw_start_dx"]                           = ("ExcelNumFormat", '##0.0 "m"')   # "%4.3f s"
        
        AddColsFormat["speed_reduced"]                         = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        

            
        # ttc for partial braking
        AddColsFormat["rel_t_start_partial_braking"]          = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        AddColsFormat["v_ego_at_t_start_partial_braking"]     = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["vrel_at_t_start_partial_braking"]      = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["dx_at_t_start_partial_braking"]        = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["ttc_at_t_start_partial_braking"]       = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        
        # ttc for emergency braking
        AddColsFormat["rel_t_start_emergency_braking"]        = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
        AddColsFormat["v_ego_at_t_start_emergency_braking"]   = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["vrel_at_t_start_emergency_braking"]    = ("ExcelNumFormat", '##0.0 "km/h"')  # "%3.1f km/h"
        AddColsFormat["dx_at_t_start_emergency_braking"]      = ("ExcelNumFormat", '##0.0 "m"')     # "%3.1f m"
        AddColsFormat["ttc_at_t_start_emergency_braking"]     = ("ExcelNumFormat", '##0.00 "s"')    # "%3.2f s"
      
        ExcelFilename = self._build_ExcelFilename("FLR20EvalAEBS_results")
        print "ExcelFilename: ",ExcelFilename

        WriteExcel = kbtools.cWriteExcel()

        
        # ----------------------------------------------------------------------
        # AEBS_DM1
        AddCols_AEBS_DM1 = ["DM1_ActSPN","DM1_ActFMI","DM1_AmberWarnLStat","DM1_SA"]
        WriteExcel.add_sheet_out_table_array('AEBS_DM1',self.H4E['AEBS_DM1'].table_array2(AddCols_AEBS_DM1,AddColsFormat))

        # ----------------------------------------------------------------------
        # AEBS_DM1 A0
        if self.do_AEBS_DM1_A0:
            AddCols_AEBS_DM1_A0 = ["DM1_ActSPN","DM1_ActFMI","DM1_AmberWarnLStat"]
            WriteExcel.add_sheet_out_table_array('AEBS_DM1_A0',self.H4E['AEBS_DM1_A0'].table_array2(AddCols_AEBS_DM1_A0,AddColsFormat))

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # AEBS_warning, AEBS_partial_brake, AEBS_emergency_brake
        
        # ---------------------------------------------------
        # online
        #AddCols_online = ["t_offset_AEBS_warning_offline","AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","cm_allow_entry_global_conditions_at_t_start","cw_allow_entry_at_t_start","cmb_allow_entry_at_t_start","dx_at_allow_entry_global_conditions_start","t_start_cw_track_before_AEBS_warning"]

        AddCols_online  = ["AEBS_cascade"]
       
        #AddCols_online += ["Stationary_at_t_start","is_video_associated_at_t_start","is_video_associated_dt_earlier","is_video_associated_dx_at_start"]
        AddCols_online += ["Stationary_at_t_start"]
       
        AddCols_online += ["v_ego_at_t_start", "dx_at_t_start", "vrel_at_t_start", "v_obst_at_t_start", "speed_reduced"]
        
        AddCols_online += ["AEBS_tr_start_dx", "AEBS_video_start_dx", "AEBS_tr_is_video_associated_start_dx", "AEBS_tr_is_video_confirmed_start_dx", "cw_start_dx"]
        
        
        # ttc for warning partial and emergency braking
        AddCols_online += ["ttc_at_t_start","ttc_at_t_start_partial_braking","ttc_at_t_start_emergency_braking"]
        AddCols_online += ["AECFlags_collision_warning","AECFlags_partial_braking","AECFlags_emergency_braking"]
        AddCols_online += ["dx_at_cw_track_start","t_start_cw_track_before_AEBS_warning"]
        AddCols_online += ["t_offset_AEBS_warning_offline"]
          
        # start of partial and emergency braking phases
        AddCols_online += ["rel_t_start_partial_braking", "v_ego_at_t_start_partial_braking","dx_at_t_start_partial_braking", "vrel_at_t_start_partial_braking"]
        AddCols_online += ["rel_t_start_emergency_braking","v_ego_at_t_start_emergency_braking","dx_at_t_start_emergency_braking","vrel_at_t_start_emergency_braking" ] 

          
        WriteExcel.add_sheet_out_table_array('AEBS_warning_online',self.H4E['AEBS_warning_online'].table_array2(AddCols_online,AddColsFormat))
        if self.braking_spreadsheets:
            WriteExcel.add_sheet_out_table_array('AEBS_partial_brake_online',self.H4E['AEBS_partial_brake_online'].table_array2())
            WriteExcel.add_sheet_out_table_array('AEBS_emergency_brake_online',self.H4E['AEBS_emergency_brake_online'].table_array2())

        # ----------------------------------------------------------------------
        # target detected   
        AddCols_target_detected = []        
        WriteExcel.add_sheet_out_table_array('target detected',self.H4E['target_detected'].table_array2(AddCols_target_detected,AddColsFormat))       
        WriteExcel.add_sheet_out_table_array('target detected CW',self.H4E['target_detected_CW'].table_array2(AddCols_target_detected,AddColsFormat))       
         
        # ----------------------------------------------------------------------
        # AEBS1_AEBSState
        AddCols_SensorStatus = ["observed_statii"]
        WriteExcel.add_sheet_out_table_array('AEBS1_AEBSState',self.H4E['AEBS1_AEBSState'].table_array2(AddCols_SensorStatus,AddColsFormat))     
         
        # ---------------------------------------------------
        # Autobox
        if self.enable_AUTOBOX:
            # AddCols_online = ["t_offset_AEBS_warning_offline","Autobox_AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","cm_allow_entry_global_conditions_at_t_start","cw_allow_entry_at_t_start","cmb_allow_entry_at_t_start","dx_at_allow_entry_global_conditions_start","t_start_cw_track_before_AEBS_warning"]
            AddCols_online = ["t_offset_AEBS_warning_offline","Autobox_AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start","is_video_associated_dt_earlier", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","AECFlags_collision_warning","AECFlags_partial_braking","AECFlags_emergency_braking","t_start_cw_track_before_AEBS_warning"]
           
            WriteExcel.add_sheet_out_table_array('AEBS_warning_Autobox',self.H4E['AEBS_warning_Autobox'].table_array2(AddCols_online,AddColsFormat))
            if self.braking_spreadsheets:
                WriteExcel.add_sheet_out_table_array('AEBS_partial_brake_Autobox',self.H4E['AEBS_partial_brake_Autobox'].table_array2())
                WriteExcel.add_sheet_out_table_array('AEBS_emergency_brake_Autobox',self.H4E['AEBS_emergency_brake_Autobox'].table_array2())

        # ---------------------------------------------------
        # offline Fused
        if self.do_AEBS_warnings_Offline_Fused:

            # AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","cm_allow_entry_global_conditions_at_t_start","cw_allow_entry_at_t_start","cmb_allow_entry_at_t_start","dx_at_allow_entry_global_conditions_start","t_start_cw_track_before_AEBS_warning"]
            AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start","is_video_associated_dt_earlier", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","AECFlags_collision_warning","AECFlags_partial_braking","AECFlags_emergency_braking","t_start_cw_track_before_AEBS_warning"]
                
            WriteExcel.add_sheet_out_table_array('Offline Fused Warning',self.H4E['AEBS_warning_offline_Fused'].table_array2(AddCols_offline,AddColsFormat))
            if self.braking_spreadsheets:
                WriteExcel.add_sheet_out_table_array('Offline Fused Part Brake',self.H4E['AEBS_partial_brake_offline_Fused'].table_array2())
                WriteExcel.add_sheet_out_table_array('Offline Fused Emerg Brake',self.H4E['AEBS_emergency_brake_offline_Fused'].table_array2())

        # ---------------------------------------------------
        # offline RadarOnly
        if self.do_AEBS_warnings_Offline_Radar_only:
           
            #AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","cm_allow_entry_global_conditions_at_t_start","cw_allow_entry_at_t_start","cmb_allow_entry_at_t_start","dx_at_allow_entry_global_conditions_start","t_start_cw_track_before_AEBS_warning"]
            AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "is_video_associated_dt_earlier", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","AECFlags_collision_warning","AECFlags_partial_braking","AECFlags_emergency_braking","t_start_cw_track_before_AEBS_warning"]
        
            WriteExcel.add_sheet_out_table_array('Offline RadarOnly Warning',self.H4E['AEBS_warning_offline_RadarOnly'].table_array2(AddCols_offline,AddColsFormat))
            if self.braking_spreadsheets:
                WriteExcel.add_sheet_out_table_array('Offline RadarOnly Part Brake',self.H4E['AEBS_partial_brake_offline_RadarOnly'].table_array2())
                WriteExcel.add_sheet_out_table_array('Offline RadarOnly Emergency',self.H4E['AEBS_emergency_brake_offline_RadarOnly'].table_array2())
        
        
        # -------------------------------------------------
        # write Excel file
        WriteExcel.save(ExcelFilename)
        print "  -> ",ExcelFilename," written"
       
       
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # AEBS1 AEBS State
        ExcelFilename = self._build_ExcelFilename("FLR20EvalAEBS_AEBS1_AEBS_Status")
        print "ExcelFilename: ",ExcelFilename

        WriteExcel = kbtools.cWriteExcel()

        AddCols_AEBSState = ["v_ego_at_t_start"]

 
        for k,desc in self.AEBS1_AEBSState_list:
            WriteExcel.add_sheet_out_table_array('%d - %s'%(k,desc),self.H4E['AEBSState_%d_online'%k].table_array2(AddCols_AEBSState,AddColsFormat))
       
        # online - AEBSState
        #WriteExcel.add_sheet_out_table_array('AEBSState_warning_online',self.H4E['AEBSState_warning_online'].table_array2(AddCols_online,AddColsFormat))
        #WriteExcel.add_sheet_out_table_array('AEBSState_par_brake_online',self.H4E['AEBSState_partial_brake_online'].table_array2())
        #WriteExcel.add_sheet_out_table_array('AEBSState_emrgcy_brake_online',self.H4E['AEBSState_emergency_brake_online'].table_array2())
            
        if self.enable_AUTOBOX:
            # Autobox - AEBSState
            WriteExcel.add_sheet_out_table_array('AEBSState_warning_Autobox',self.H4E['AEBSState_warning_Autobox'].table_array2(AddCols_online,AddColsFormat))
            WriteExcel.add_sheet_out_table_array('AEBSState_par_brake_Autobox',self.H4E['AEBSState_partial_brake_Autobox'].table_array2())
            WriteExcel.add_sheet_out_table_array('AEBSState_emrgcy_brake_Autobox',self.H4E['AEBSState_emergency_brake_Autobox'].table_array2())

        
        # ---------------------------------
        # write Excel file
        WriteExcel.save(ExcelFilename)
        print "  -> ",ExcelFilename," written"
  
  
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # offline RadarOnly
        
        if self.do_AEBS_warnings_Offline_Radar_only:
            ExcelFilename = self._build_ExcelFilename("FLR20EvalAEBS_AEBS_warnings_Offline_Radar_only")
            print "ExcelFilename: ",ExcelFilename

            WriteExcel = kbtools.cWriteExcel()
        
            #AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","cm_allow_entry_global_conditions_at_t_start","cw_allow_entry_at_t_start","cmb_allow_entry_at_t_start","dx_at_allow_entry_global_conditions_start","t_start_cw_track_before_AEBS_warning"]
            AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start","is_video_associated_dt_earlier", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","AECFlags_collision_warning","AECFlags_partial_braking","AECFlags_emergency_braking","t_start_cw_track_before_AEBS_warning"]
      

            WriteExcel.add_sheet_out_table_array('AEBS_warning_offline_RadarOnly',self.H4E['AEBS_warning_offline_RadarOnly'].table_array2(AddCols_offline,AddColsFormat))

            # ---------------------------------
            # write Excel file
            WriteExcel.save(ExcelFilename)

            print "  -> ",ExcelFilename," written"
        
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # offline Fused
        if self.do_AEBS_warnings_Offline_Fused:
            ExcelFilename = self._build_ExcelFilename("FLR20EvalAEBS_AEBS_warnings_Offline_Fused")
            print "ExcelFilename: ",ExcelFilename
           
            WriteExcel = kbtools.cWriteExcel()
           
        
            #AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","cm_allow_entry_global_conditions_at_t_start","cw_allow_entry_at_t_start","cmb_allow_entry_at_t_start","dx_at_allow_entry_global_conditions_start","t_start_cw_track_before_AEBS_warning"]
            AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "is_video_associated_dt_earlier", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","AECFlags_collision_warning","AECFlags_partial_braking","AECFlags_emergency_braking","t_start_cw_track_before_AEBS_warning"]
        
            WriteExcel.add_sheet_out_table_array('AEBS_warning_offline_Fused',self.H4E['AEBS_warning_offline_Fused'].table_array2(AddCols_offline,AddColsFormat))

            # ---------------------------------
            # write Excel file
            WriteExcel.save(ExcelFilename)

            print "  -> ",ExcelFilename," written"
      
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if self.do_Sim_AEBS_new_framework:
            ExcelFilename = self._build_ExcelFilename("FLR20EvalAEBS_sim_results")
            print "ExcelFilename: ",ExcelFilename
            
            WriteExcel_sim = kbtools.cWriteExcel()
        
            #AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","cm_allow_entry_global_conditions_at_t_start","cw_allow_entry_at_t_start","cmb_allow_entry_at_t_start","dx_at_allow_entry_global_conditions_start","t_start_cw_track_before_AEBS_warning"]
            AddCols_offline = ["AEBS_cascade","Stationary_at_t_start","is_video_associated_at_t_start","is_video_associated_dt_earlier", "v_ego_at_t_start", "dx_at_t_start","ttc_at_t_start","dx_at_cw_track_start","AECFlags_collision_warning","AECFlags_partial_braking","AECFlags_emergency_braking","t_start_cw_track_before_AEBS_warning"]
                    
            # ---------------------------------------------------------------------        
            # WriteExcel_sim: separate Excel Spreadsheet with all the simulation results 
            if self.SilAEBS_C_list:
                for nr_str, _ in self.SilAEBS_C_list:
                    WriteExcel_sim.add_sheet_out_table_array('SIM_AEBS_warning'+nr_str,self.H4E['SIM_AEBS_warning'+nr_str].table_array2(AddCols_offline,AddColsFormat))
                 
                # ---------------------------------                
                # write Excel file
                WriteExcel_sim.save(ExcelFilename)
                print "  -> ",ExcelFilename," written"
            else:
                print "self.SilAEBS_C_list is empty",self.SilAEBS_C_list
                print "  -> ",ExcelFilename," not written"

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        
        
        print "EvalFLR20AEBS.excel_export() finish"
      
#-------------------------------------------------------------------------      









