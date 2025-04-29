#
#  Simulation Interface for VC++ KB-AEBS
#
#  input data: FLR20 (alias AC100) and CVR3
#
#  Ulrich Guecker
#
#  2013-06-11 
#  2013-06-07 initial revision with FLR20
# ---------------------------------------------------------------------------------------------


import os
import time
import numpy as np
import pylab as pl
import subprocess

import scipy.io as sio

import kbtools



# ==========================================================
class cSimKBAEBS():

    # ==========================================================
    def __init__(self, inp_sig,AEBS_sil_exe_FullFileName=None,WorkingDir=None,verbose=False):
        
        self.verbose = verbose     
        
        # ------------------------------------------------------------------
        # input signals
        self.inp_sig                   = inp_sig
        
        # ------------------------------------------------------------------
        # location of asf_sil.exe
        if AEBS_sil_exe_FullFileName is None:
            self.AEBS_sil_exe_FullFileName = r"asf_sil.exe"  
        else:        
            self.AEBS_sil_exe_FullFileName = AEBS_sil_exe_FullFileName

        # ------------------------------------------------------------------
        # directory to run the simulation in
        if  WorkingDir is None:
            self.WorkingDir = r"./asf_sim"
        else:
            self.WorkingDir = WorkingDir
        
        # ------------------------------------------------------------------
        # Sensor Type (is included in the input signals)
        self.SensorType = None
        if 'SensorType' in self.inp_sig:
            self.SensorType = self.inp_sig['SensorType']
            
        # ------------------------------------------------------------------
        # FileName of measurement 
        if 'FileName' in self.inp_sig:
            self.FileName = os.path.basename(self.inp_sig['FileName'])
        else:
            self.FileName = ''
    
        # ------------------------------------------------------------------
        # limit range of fusion system (only for stationary objects)
        self.enable_dx_limit_b = False
        self.dx_limit = 200.0
        
        if self.verbose:
            print "cSimKBAEBS.init() okay"
       
    # ==========================================================
    def set_dx_limit(self, enable_dx_limit_b, dx_limit=200.0):
        if enable_dx_limit_b:
            self.enable_dx_limit_b = True
            self.dx_limit = dx_limit
        else:
            self.enable_dx_limit_b = False
            self.dx_limit = 200.0
               
         
    # ==========================================================
    def build_FileName(self, t_event):
        
        if t_event is None:
            FileName  = self.FileName
        else:
            FileName  = "%s@%3.1fs"%(self.FileName,t_event)
    
        return FileName
    
    # ==========================================================
    def take_a_picture(self, fig, PlotName, t_event= None):
        # create png picture
        FileName = self.FileName
        
        if t_event is None:
            PngFileName  = "%s_%s.png"%(FileName,PlotName)
        else:
            PngFileName  = "%s@%3.1fs_%s.png"%(FileName,t_event,PlotName)
        

        fig.set_size_inches(16.,12.)
        fig.savefig(PngFileName)    
                
    # ==========================================================
    def get_logdata(self):
        return self.logdata
        
    # ==========================================================
    def simulation_output(self):
        return self.simulation_output
        
        
    #=================================================================================
    def matrix2vector(self, logdata):
        # matrix to vector
        for signal in logdata.keys():
            try:
                logdata[signal] = logdata[signal][0]
            except:
                #print  logdata[signal]
                pass
        return logdata
   
    #=================================================================================
    def load_Matlab_file(self, FileName):

        # load simulation output (*.mat)    
        logdata = sio.loadmat(FileName, matlab_compatible  = True)
        
        # matrix to vector
        logdata = self.matrix2vector(logdata)
    
        return logdata

        
        
    #=================================================================================
    def save_FLR20data_as_matlab(self, FileName):
        # save signals to matlab binary         
        signal_list = self.get_FLR20data()
        sio.savemat(FileName, signal_list, oned_as='row')    
        return

    #=================================================================================
    def get_FLR20data(self,dtype_InputSignals_Cython=None):
  
        signal_list = self.local_get_FLR20data()
  
        if dtype_InputSignals_Cython is None:
            return signal_list
        else:
            self.input_data = signal_list
            return self._cnvt2Cython_AEBSInputSignals(signal_list, dtype_InputSignals_Cython)
 
    
    #=================================================================================
    def local_get_FLR20data(self):
        Markus_mode_b = True
        
        FLR20_sig = self.inp_sig
  
        print "get_FLR20data():"
  
        #  FLR20_sig['PosMatrix']['S1'] is more than IntroSAM and Introm SAS !!!
        Intro = {}
    
        # -----------------------------------------------------------------------------------
        # time
        t       =  FLR20_sig['PosMatrix']['CW']['Time']
        
        # -----------------------------------------------------------------------------------
        # vehicle state
        if FLR20_sig["General"]["actual_vehicle_speed"] is None:
            print "no actual_vehicle_speed available"
        if FLR20_sig["General"]["vehicle_reference_acceleration"] is None:
            print "no vehicle_reference_acceleration available"
 
        vxvRef  =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["actual_vehicle_speed"], t) 
        axvRef  =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["vehicle_reference_acceleration"], t)
        if Markus_mode_b:
            axvRef  = np.zeros_like(t)

        # -----------------------------------------------------------------------------------
        # driver input
        if FLR20_sig["J1939"]["Time_BrakePedalPos"] is None:
            print "no BrakePedalPos available"
        if FLR20_sig["J1939"]["Time_EBSBrakeSwitch"] is None:
            print "no EBSBrakeSwitch available"
        if FLR20_sig["J1939"]["Time_AccelPedalPos1"] is None:
            print "no AccelPedalPos1 available"
        
        BrakePedalPos   =  kbtools.resample(FLR20_sig["J1939"]["Time_BrakePedalPos"],  FLR20_sig["J1939"]["BrakePedalPos"], t) 
        EBSBrakeSwitch  =  kbtools.resample(FLR20_sig["J1939"]["Time_EBSBrakeSwitch"], FLR20_sig["J1939"]["EBSBrakeSwitch"], t) 
        AccelPedalPos1  =  kbtools.resample(FLR20_sig["J1939"]["Time_AccelPedalPos1"], FLR20_sig["J1939"]["AccelPedalPos1"], t) 
         
        GPPos              = AccelPedalPos1/100.0
        alpDtSteeringWheel = np.zeros_like(t)
        pBrake             = BrakePedalPos
        BPAct_b            = EBSBrakeSwitch
        GPKickdown_B       = AccelPedalPos1>=90.0
        DirIndL_b          = np.zeros_like(t)
        DirIndR_b          = np.zeros_like(t)
                  
        # -----------------------------------------------------------------------------------
        # Collision Object Attributes
    
        Intro['FusHandle'] =  np.zeros_like(t)
        Intro['FusObjIdx'] =  np.zeros_like(t)
        Intro['dx'] = FLR20_sig['PosMatrix']['CW']['dx']
        Intro['dy'] = FLR20_sig['PosMatrix']['CW']['dy']
        Intro['vx'] = FLR20_sig['PosMatrix']['CW']['vx']
        Intro['vy'] = FLR20_sig['PosMatrix']['CW']['vy']
        Intro['ax'] = FLR20_sig['PosMatrix']['CW']['ax_ground']-axvRef
        Intro['ay'] = np.zeros_like(t)
       
        if Markus_mode_b:
            Intro['dx'] = FLR20_sig['PosMatrix']['CW']['ds']
            Intro['dy'] = FLR20_sig['PosMatrix']['CW']['lateral_position']
            Intro['vx'] = FLR20_sig['PosMatrix']['CW']['vr']
            Intro['vy'] = np.zeros_like(t)
            Intro['ax'] = np.zeros_like(t)
            Intro['ay'] = np.zeros_like(t)
            
   
        # -----------------------------------------------------------------------------------
        # Intro['Id'], Intro['ObjectList0'], Intro['ObjectRelation']
        
        # 1) Intro['Id']
        Intro['Id']  = np.zeros_like(t)
        #Intro['Id'] +=  3.0*np.logical_and(FLR20_sig['PosMatrix']['CW']['Valid'], FLR20_sig['PosMatrix']['CW']['Stand_b'])
        #Intro['Id'] +=  1.0*np.logical_and(FLR20_sig['PosMatrix']['CW']['Valid'], np.logical_not(FLR20_sig['PosMatrix']['CW']['Stand_b']))
        Intro['Id'] +=  3.0*np.logical_and(FLR20_sig['PosMatrix']['CW']['Valid'], FLR20_sig['PosMatrix']['CW']['Stationary']) 
        Intro['Id'] +=  1.0*np.logical_and(FLR20_sig['PosMatrix']['CW']['Valid'], FLR20_sig['PosMatrix']['CW']['Same_Direction'])
        
        # range limitation of Intro['Id'] (self.enable_dx_limit_b, self.dx_limit
        if self.enable_dx_limit_b:
           print "get_FLR20data(): dx_limit%3.1fm"%self.dx_limit
           mask = np.logical_and(Intro['Id']==3.0, Intro['dx']>=self.dx_limit)
           Intro['Id'][mask]= 0.0
        
        # 2) Intro['ObjectList0'], Intro['ObjectRelation']                  
        Intro['ObjectList0'] = (Intro['Id']>0)*1.0
        Intro['ObjectRelation'] = 255*np.ones_like(t)
        Intro['ObjectRelation'][Intro['Id']==1.0] = 26.0       # moving 
        Intro['ObjectRelation'][Intro['Id']==3.0] = 22.0       # stationary
 
        # -----------------------------------------------------------------------------------
        # Driving Status        
        Intro['DriveInvDir_b']   = np.zeros_like(t)
        Intro['Drive_b']         = np.zeros_like(t)
        Intro['NotClassified_b'] = np.zeros_like(t)
        Intro['Stand_b']         = np.zeros_like(t)
        Intro['StoppedInvDir_b'] = np.zeros_like(t)
        Intro['Stopped_b']       = np.zeros_like(t)
                   
        Intro['Drive_b'][Intro['Id']==1.0] = 1  
        Intro['Stand_b'][Intro['Id']==3.0] = 1        
                   
        # -----------------------------------------------------------------------------------
        # Video associated  
        Intro['AdditionalSensorAssociated_b'] = FLR20_sig['PosMatrix']['CW']['is_video_associated']
        

        # -----------------------------------------------------------------------------------
        signal_list = {
    
                   # -------------------------------------------------------------   
                   # time
                   't'                     : t,                       # time stamp - TC cycle
                   'Envra_tAbsASF'         : np.zeros_like(t),        # time stamp - start of ASF
                   'fus_tAbsRefTime'       : np.zeros_like(t),        # time stamp - FUS data
                   'tdtTC'                 : 0.040*np.ones_like(t),   # TC interval
          
                   # -------------------------------------------------------------   
                   # ego vehicle
                   'ego_vRef'              : vxvRef,                  # ego vehicle speed
                   'ego_aRef'              : axvRef,                  # ego vehicle acceleration
                   'ego_psiDt'             : np.zeros_like(t),        # ego vehicle yaw rate
                   
                     
                   # -------------------------------------------------------------   
                   # driver override
                   'GPPos'                   : GPPos,                   # gas pedal position
                   'alpDtSteeringWheel'      : alpDtSteeringWheel,      # steering angle speed
                   'pBrake'                  : pBrake,                  # 
                                     
                   'BPAct_b'                 : BPAct_b,                 # brake pedal activation (bool)
                   'GPKickdown_B'            : GPKickdown_B,            # kickdown (gas pedal)       (bool)
                   'DirIndL_b'               : DirIndL_b,               # left directional indicator (bool)
                   'DirIndR_b'               : DirIndR_b,               # right left directional indicator (bool)
                   'SteeringWheelOverride_B' : np.zeros_like(t),        # Override via steering wheel (algorithm in simulink)
                   

                   # -------------------------------------------------------------   
                   # Intro
                   'IntroFusHandle'        : Intro['FusHandle'],          # only for information
                   'IntroFusObjIdx'        : Intro['FusObjIdx'],          # only for information // 
                                    
                   'Intro_Id'              : Intro['Id']  *1.0,            # intro id number
                   'Intro_Obj'             : Intro['ObjectList0']*1.0,      # (only for information)
                   'Intro_Rel'             : Intro['ObjectRelation']*1.0,
                
                   'Intro_dx'              : Intro['dx'],
                   'Intro_dy'              : Intro['dy'],
                   'Intro_vx'              : Intro['vx'],
                   'Intro_vy'              : Intro['vy'],
                   'Intro_ax'              : Intro['ax'],
                   'Intro_ay'              : Intro['ay'],
                   
                   'Intro_DriveInvDir_b'   : Intro['DriveInvDir_b'],
                   'Intro_Drive_b'         : Intro['Drive_b'], 
                   'Intro_NotClassified_b' : Intro['NotClassified_b'],
                   'Intro_Stand_b'         : Intro['Stand_b'],
                   'Intro_StoppedInvDir_b' : Intro['StoppedInvDir_b'],
                   'Intro_Stopped_b'       : Intro['Stopped_b'],
             
                   'Intro_AdditionalSensorAssociated_b'  :  Intro['AdditionalSensorAssociated_b'],
    
                   # -------------------------------------------------------------   
                   # ACC
                   'TORSitSubjective_b'    : np.zeros_like(t),
        
                   
                   # -------------------------------------------------------------   
                   # ACO States
                   'acooptiState_ub'       : np.zeros_like(t),
                   'acoacoiState_ub'       : np.zeros_like(t),
                   'acopebpState_ub'       : np.zeros_like(t),
                   'acopebeState_ub'       : np.zeros_like(t),
                   
    
                   # -------------------------------------------------------------   
                                    
                   
                   #'OstaskdataTc_T20_tdtTC' : CVR3_sig['OstaskdataTc_T20_tdtTC'],
                   'CountTC'                : np.zeros_like(t),
                   

                   }
    
        # check signal in signal list
    
        return signal_list
  

    #=================================================================================
    def save_CVR3data_as_matlab(self, FileName):
  
        CVR3_sig = self.inp_sig
        Intro = CVR3_sig['Intro']

        ones_vec = np.ones_like(CVR3_sig['Fus_General_TC']['Time'])
 
        # fake AdditionalSensorAssociated 
        #Intro['AdditionalSensorAssociated_b'] = np.ones_like(Intro['AdditionalSensorAssociated_b'])
  
        alpDtSteeringWheel = CVR3_sig['Sit_BasicInput_TC']['alpDtSteeringWheel']*1.0
        alpDtSteeringWheel = 0.0*ones_vec
  
        signal_list = {
    
                   # -------------------------------------------------------------   
                   # time
                   't'                     : CVR3_sig['Fus_General_TC']['Time'],
                   'Envra_tAbsASF'         : CVR3_sig['ASF']['Envra_tAbsASF'],
                   'fus_tAbsRefTime'       : CVR3_sig['Fus_General_TC']['tAbsRefTime'],
                   'tdtTC'                 : CVR3_sig['Crm_OstaskdataTc_TC']['tdtTC'],

                 
                   # -------------------------------------------------------------   
                   # ego vehicle
                   'ego_vRef'              : CVR3_sig['Fus_General_TC']['vRefSync'],
                   'ego_aRef'              : CVR3_sig['Fus_General_TC']['aRefSync'],
                   'ego_psiDt'             : CVR3_sig['Fus_General_TC']['psiDtOptSync'],
                      
                   # -------------------------------------------------------------   
                   # driver override
                   'GPPos'                 : CVR3_sig['Sit_BasicInput_TC']['GPPos']*1.0,
                   'alpDtSteeringWheel'    : alpDtSteeringWheel,
                   'pBrake'                : CVR3_sig['Asf_BasicInput_TC']['pBrake']*1.0,
                   
                   
                   
                   'BPAct_b'               : CVR3_sig['Sit_BasicInput_TC']['BPAct_b']*1.0,
                   'GPKickdown_B'          : CVR3_sig['Sit_BasicInput_TC']['GPKickdown_B']*1.0,
                   'DirIndL_b'             : CVR3_sig['Sit_BasicInput_TC']['DirIndL_b']*1.0,
                   'DirIndR_b'             : CVR3_sig['Sit_BasicInput_TC']['DirIndR_b']*1.0,
                   
            
                   # -------------------------------------------------------------   
                   # Intro
                   'IntroFusHandle'        : Intro['FusHandle'],          # only for information
                   'IntroFusObjIdx'        : Intro['FusObjIdx'],          # only for information
                   
                   'Intro_Id'              : Intro['Id']  *1.0,
                   'Intro_Obj'             : Intro['ObjectList0']*1.0,      # only for information
                   'Intro_Rel'             : Intro['ObjectRelation']*1.0,
                   
                   
                   'Intro_dx'              : Intro['dx'],
                   #'Intro_dy'              : Intro['dy'],
                   'Intro_dy'              : Intro['dyvBase'],
                                     
                   'Intro_vx'              : Intro['vx'],
                   'Intro_vy'              : Intro['vy'],
                   'Intro_ax'              : Intro['ax'],
                   'Intro_ay'              : Intro['ay'],
                   
                   'Intro_DriveInvDir_b'   : Intro['DriveInvDir_b'],
                   'Intro_Drive_b'         : Intro['Drive_b'], 
                   'Intro_NotClassified_b' : Intro['NotClassified_b'],
                   'Intro_Stand_b'         : Intro['Stand_b'],
                   'Intro_StoppedInvDir_b' : Intro['StoppedInvDir_b'],
                   'Intro_Stopped_b'       : Intro['Stopped_b'],
                   
                   'Intro_AdditionalSensorAssociated_b'  :  Intro['AdditionalSensorAssociated_b'],
    
                   # -------------------------------------------------------------   
                   # ACC
                   'TORSitSubjective_b'    : 0*ones_vec,
        
                   
                   # -------------------------------------------------------------   
                   # ACO States
                   'acooptiState_ub'       : CVR3_sig['ASF']['acooptiState'],
                   'acoacoiState_ub'       : CVR3_sig['ASF']['acoacoiState'],
                   'acopebpState_ub'       : CVR3_sig['ASF']['acopebpState'],
                   'acopebeState_ub'       : CVR3_sig['ASF']['acopebeState'],
                   
    
                   # -------------------------------------------------------------   
                                    
                   
                   #'OstaskdataTc_T20_tdtTC' : CVR3_sig['OstaskdataTc_T20_tdtTC'],
                   'CountTC'                : CVR3_sig['Crm_OstaskdataTc_TC']['CountTC'],
                   

                   }
                 
        sio.savemat(FileName, signal_list, oned_as='row')  

    #=================================================================================
    def _cnvt2Cython_AEBSInputSignals(self, inp_sig, dtype_InputSignals_Cython):
        
        t = inp_sig["t"]
  
        # number of cycles
        cycles = t.size

        # a) initialize parameter array with zeros
        AEBSInputSignals = np.zeros(cycles, dtype=dtype_InputSignals_Cython)

        # b) set input signals
        AEBSInputSignals['tAbsASF']            = inp_sig["t"]
        AEBSInputSignals['Envra_tAbsASF']      = inp_sig["Envra_tAbsASF"]
        AEBSInputSignals['fus_tAbsRefTime']    = inp_sig["fus_tAbsRefTime"]
        AEBSInputSignals['dt']                 = inp_sig["tdtTC"]
        AEBSInputSignals['vRef']               = inp_sig["ego_vRef"]
        AEBSInputSignals['aRef']               = inp_sig["ego_aRef"]
        AEBSInputSignals['psiDt']              = inp_sig["ego_psiDt"]        
        AEBSInputSignals['GPPos']              = inp_sig["GPPos"] 
        AEBSInputSignals['alpDtSteeringWheel'] = inp_sig["alpDtSteeringWheel"]
        AEBSInputSignals['pBrake']             = inp_sig["pBrake"]   #   np.zeros(cycles, dtype=np.float32)        # new!
        AEBSInputSignals['BPAct_b']            = inp_sig["BPAct_b"]      
        AEBSInputSignals['GPKickdown_B']       = inp_sig["GPKickdown_B"]
        AEBSInputSignals['DirIndL_b']          = inp_sig["DirIndL_b"]
        AEBSInputSignals['DirIndR_b']          = inp_sig["DirIndR_b"]
        AEBSInputSignals['SteeringWheelOverride_B'] = inp_sig["SteeringWheelOverride_B"]   #  np.zeros(cycles, dtype=np.uint8)      # new!
        AEBSInputSignals['iIntro_Id']          = inp_sig["Intro_Id"] 
        AEBSInputSignals['iIntro_Rel']         = inp_sig["Intro_Rel"]
        AEBSInputSignals['iFusIndex']          = np.zeros(cycles, dtype=np.uint8)
        AEBSInputSignals['iHandle']            = np.ones(cycles, dtype=np.uint8)
        AEBSInputSignals['dxv']                = inp_sig["Intro_dx"]
        AEBSInputSignals['dyv']                = inp_sig["Intro_dy"]
        AEBSInputSignals['vxv']                = inp_sig["Intro_vx"]
        AEBSInputSignals['vyv']                = inp_sig["Intro_vy"]
        AEBSInputSignals['axv']                = inp_sig["Intro_ax"]
        AEBSInputSignals['ayv']                = inp_sig["Intro_ay"]
        AEBSInputSignals['DriveInvDir_b']      = inp_sig["Intro_DriveInvDir_b"]
        AEBSInputSignals['Drive_b']            = inp_sig["Intro_Drive_b"]
        AEBSInputSignals['NotClassified_b']    = inp_sig["Intro_NotClassified_b"]
        AEBSInputSignals['Stand_b']            = inp_sig["Intro_Stand_b"]
        AEBSInputSignals['StoppedInvDir_b']    = inp_sig["Intro_StoppedInvDir_b"]
        AEBSInputSignals['Stopped_b']          = inp_sig["Intro_Stopped_b"]
        AEBSInputSignals['AdditionalSensorAssociated_b'] = inp_sig["Intro_AdditionalSensorAssociated_b"]
        AEBSInputSignals['TORSitSubjective_b'] = inp_sig["TORSitSubjective_b"]
        AEBSInputSignals['acooptiState_ub']    = inp_sig["acooptiState_ub"]
        AEBSInputSignals['acoacoiState_ub']    = inp_sig["acoacoiState_ub"]
        AEBSInputSignals['acopebpState_ub']    = inp_sig["acopebpState_ub"]
        AEBSInputSignals['acopebeState_ub']    = inp_sig["acopebeState_ub"]
 
        return AEBSInputSignals
    
        
    #=================================================================================
    def save_parameters_as_matlab(self, FileName, ParameterChnDict = {}):
   
        parameter_list = self._get_ParameterList(ParameterChnDict)
   
        sio.savemat(FileName, parameter_list, oned_as='row')  
    
    #=================================================================================
    def get_Parameters(self,ParameterChnDict = {},type_Paramters_Cython=None):
                
        parameter_list = self._get_ParameterList(ParameterChnDict)

        if 'dx_limit' in ParameterChnDict:
           self.set_dx_limit(True, ParameterChnDict['dx_limit'])
        
        if type_Paramters_Cython is None:
            return parameter_list
        else:
            return self._cnvt2Cython_AEBSParameters(parameter_list, type_Paramters_Cython)
    
    #=================================================================================
    def _get_ParameterList(self,ParameterChnDict = {}):
     
        parameter_list = {
            'Description'                                    : "AEBS/kbaebs.h",


            "take_acoStates_as_inputs_B" : 0,

            # -----------------------------
            # enable VideoValidation
            "REPPREWEnableVideoValidationSAS_B"    : 0,     
            "REPRETGSTDEnableVideoValidationSAS_B" : 0, 
            "REPRETGEXTEnableVideoValidationSAS_B" : 0,   
            "PRESSAMEnableVideoValidation_B"                 : 0,   # obsolete
            "PRESSASEnableVideoValidation_B"                 : 0,   # obsolete
                               

            # AEBS cascade
            "DAMtPrewTime"                         : 0.85,   # [s]                
            "PCCCDAMtDriverReactTime"              : 0.8,    # [s]     
            "aComfortSwingOutYAxis"                : -0.8,  # [m/s^2]
            "axvReqActivationThreshold"            : -5.5,   # [m/s^2] 
            "REPRETGaxStdPartialBraking"           : -3.0,   # [m/s^2],   
            "dxSecureReq"                          : 2.5,    # [m]              

            # Driver Override
            "REPPREWpBrakeMinStop"                 : 5.0,    # [???]    
            "REPPREWtStopDueToBP"                  : 0.2,    # [s]     
            "REPPREWvEgoMaxStart"                  : 35.0,   # [m/s]      
            "REPPREWvEgoMinStart"                  :  4.0,     
            "REPRETGpBrakeMinStop"                 :  5.0,
            "REPRETGtStopDueToBP"                  :  0.2,                
            "REPRETGtStopDueToKickdown"            :  0.02,          
                
        }
   
                
        # update parameter_list with ParameterChnDict
        for key in ParameterChnDict.keys():
          parameter_list[key] = ParameterChnDict[key]
          print "%s changed to %f"%(key, parameter_list[key])
   
        return parameter_list
        
    #=================================================================================
    def _cnvt2Cython_AEBSParameters(self, parameters, dtype_Paramters_Cython):
        # a) initialize parameter array with zeros
        AEBSParameters = np.zeros(1,dtype=dtype_Paramters_Cython)

        # b) set parameter values
        AEBSParameters['take_acoStates_as_inputs_B']            = parameters['take_acoStates_as_inputs_B']
        AEBSParameters['REPPREWEnableVideoValidationSAS_B']     = parameters['REPPREWEnableVideoValidationSAS_B'] 
        AEBSParameters['REPRETGEXTEnableVideoValidationSAS_B']  = parameters['REPRETGEXTEnableVideoValidationSAS_B'] 
        AEBSParameters['REPRETGSTDEnableVideoValidationSAS_B']  = parameters['REPRETGSTDEnableVideoValidationSAS_B'] 
        AEBSParameters['axvReqActivationThreshold']             = parameters['axvReqActivationThreshold']  
        AEBSParameters['dxSecureReq']                           = parameters['dxSecureReq'] 
        AEBSParameters['DAMtPrewTime']                          = parameters['DAMtPrewTime'] 
        AEBSParameters['PCCCDAMtDriverReactTime']               = parameters['PCCCDAMtDriverReactTime']
        AEBSParameters['REPPREWpBrakeMinStop']                  = parameters['REPPREWpBrakeMinStop'] 
        AEBSParameters['REPPREWtStopDueToBP']                   = parameters['REPPREWtStopDueToBP'] 
        AEBSParameters['REPPREWvEgoMaxStart']                   = parameters['REPPREWvEgoMaxStart']
        AEBSParameters['REPPREWvEgoMinStart']                   = parameters['REPPREWvEgoMinStart']
        AEBSParameters['REPRETGaxStdPartialBraking']            = parameters['REPRETGaxStdPartialBraking']
        AEBSParameters['REPRETGpBrakeMinStop']                  = parameters['REPRETGpBrakeMinStop'] 
        AEBSParameters['REPRETGtStopDueToBP']                   = parameters['REPRETGtStopDueToBP'] 
        AEBSParameters['REPRETGtStopDueToKickdown']             = parameters['REPRETGtStopDueToKickdown']
        AEBSParameters['aComfortSwingOutYAxis']                 = parameters['aComfortSwingOutYAxis'] 

        return AEBSParameters
        
    #=================================================================================
    def set_input_data(self, input_data):
        self.input_data = {} 
        self.input_data['t']                  = np.array(input_data['tAbsASF'])
        self.input_data['Envra_tAbsASF']      = input_data["Envra_tAbsASF"]
        self.input_data['fus_tAbsRefTime']    = input_data["fus_tAbsRefTime"]
        self.input_data['tdtTC']    = input_data['dt']
        self.input_data['ego_vRef'] = input_data['vRef']
        self.input_data['ego_aRef'] = input_data['aRef']
        self.input_data['ego_psiDt'] = input_data['psiDt']

        self.input_data['GPPos']              = input_data["GPPos"] 
        self.input_data['alpDtSteeringWheel'] = input_data["alpDtSteeringWheel"]
        self.input_data['pBrake']             = input_data["pBrake"]   #   np.zeros(cycles, dtype=np.float32)        # new!
        self.input_data['BPAct_b']            = input_data["BPAct_b"]      
        self.input_data['GPKickdown_B']       = input_data["GPKickdown_B"]
        self.input_data['DirIndL_b']          = input_data["DirIndL_b"]
        self.input_data['DirIndR_b']          = input_data["DirIndR_b"]
        self.input_data['SteeringWheelOverride_B'] = input_data["SteeringWheelOverride_B"]   #  np.zeros(cycles, dtype=np.uint8)      # new!

        
        self.input_data['Intro_Id']  = input_data['iIntro_Id']
        self.input_data['Intro_Rel'] = input_data['iIntro_Rel']

        self.input_data['Intro_dx'] = input_data['dxv']
        self.input_data['Intro_dy'] = input_data['dyv']
        self.input_data['Intro_vx'] = input_data['vxv']
        self.input_data['Intro_vy'] = input_data['vyv']
        self.input_data['Intro_ax'] = input_data['axv']
        self.input_data['Intro_ay'] = input_data['ayv']

        self.input_data['Intro_DriveInvDir_b'] = input_data['DriveInvDir_b']
        self.input_data['Intro_Drive_b'] = input_data['Drive_b']
        self.input_data['Intro_NotClassified_b'] = input_data['NotClassified_b']
        self.input_data['Intro_Stand_b'] = input_data['Stand_b']
        self.input_data['Intro_StoppedInvDir_b'] = input_data['StoppedInvDir_b']
        self.input_data['Intro_Stopped_b'] = input_data['Stopped_b']
        self.input_data['Intro_AdditionalSensorAssociated_b'] = input_data['AdditionalSensorAssociated_b']

        self.input_data['TORSitSubjective_b'] = input_data["TORSitSubjective_b"]
        self.input_data['acooptiState_ub']    = input_data["acooptiState_ub"]
        self.input_data['acoacoiState_ub']    = input_data["acoacoiState_ub"]
        self.input_data['acopebpState_ub']    = input_data["acopebpState_ub"]
        self.input_data['acopebeState_ub']    = input_data["acopebeState_ub"]
       
    #=================================================================================
    def set_simulation_output(self, out_sig, t):
  
        self.simulation_output = {}
        self.simulation_output['t'] = t 
    
        self.simulation_output['acoopti_SetRequest'] = out_sig['acoopti_SetRequest']
        self.simulation_output['acoacoi_SetRequest'] = out_sig['acoacoi_SetRequest']
        self.simulation_output['acopebp_SetRequest'] = out_sig['acopebp_SetRequest']
        self.simulation_output['acopebe_SetRequest'] = out_sig['acopebe_SetRequest']

        self.simulation_output['acoopti_RequestValue'] = out_sig['acoopti_RequestValue']
        self.simulation_output['acoacoi_RequestValue'] = out_sig['acoacoi_RequestValue']
        self.simulation_output['acopebp_RequestValue'] = out_sig['acopebp_RequestValue']
        self.simulation_output['acopebe_RequestValue'] = out_sig['acopebe_RequestValue']
 
        return self.simulation_output
 
    #=================================================================================
    def save_expected_results_as_matlab(self, FileName):
        # data for expected results - output data
        
        CVR3_sig = self.inp_sig
        signal_list = {

                   # -------------------------------------------------------------   
                   # time
                   't'                     : CVR3_sig['Fus_General_TC']['Time'],
            
                   # -------------------------------------------------------------   
                   'ASFFirstWarning'     : CVR3_sig['ASF']["FirstWarning"]  ,
                   'ASFBraking'          : CVR3_sig['ASF']["Braking"]  ,
                   
                   'acoopti_SetRequest'  : CVR3_sig['ASF']['acoopti_SetRequest']*1.0,
                   'acoacoi_SetRequest'  : CVR3_sig['ASF']['acoacoi_SetRequest']*1.0,
                   'acopebp_SetRequest'  : CVR3_sig['ASF']['acopebp_SetRequest']*1.0,
                   'acopebe_SetRequest'  : CVR3_sig['ASF']['acopebe_SetRequest']*1.0,
                   'acopebp_RequestValue': CVR3_sig['ASF']['acopebp_RequestValue'],
                   'acopebe_RequestValue': CVR3_sig['ASF']['acopebe_RequestValue'],
                   }
                
   
        sio.savemat(FileName, signal_list, oned_as='row')  
 
    #=================================================================================
    def run_simulation(self, ParameterChnDict = {},do_remove_working_dir_b = False):
        # run C++ simulation        
        
        
        if self.verbose:
            print "cSimKBAEBS.run_simulation() start"

        
        # short cut for used configuration parameters
        AEBS_sil_exe_FullFileName = self.AEBS_sil_exe_FullFileName
        WorkingDir                = self.WorkingDir
        
        
        # -----------------------------------------------------------------------
        # Specify file names of interface with AEBS_sil_exe
        # input:  signals   - (values for each sample)
        MatlabFileName_input_data       = os.path.join(WorkingDir,'AEBS_CVR3.mat')        
        # input:  parameter - (one value for all samples) 
        MatlabFileName_parameters       = os.path.join(WorkingDir,'AEBS_CVR3_parameters.mat')
        
        # output: AEBS output signals
        MatlabFileName_output_data      = os.path.join(WorkingDir,'AEBS_CVR3_out.mat')
        # expected result - to be compared with simulation out put (currently only available for CVR3)
        MatlabFileName_expected_results = os.path.join(WorkingDir,'AEBS_CVR3_expected_results.mat')
        # logdata of private class variables 
        MatlabFileName_logdata          = os.path.join(WorkingDir,'logdata.mat')
        
        # ---------------------------------------------------------
        # quick workaround
        if 'dx_limit' in ParameterChnDict:
           self.set_dx_limit(True, ParameterChnDict['dx_limit'])
           
       
   
   
        # -----------------------------------------------------------------------
        # create or purge working directory for AEBS_sil_exe
        if not os.path.exists(WorkingDir):
            os.makedirs(WorkingDir)
        else:
            extension_list = ['.mat','.dat','.txt','.out']
            kbtools.delete_files(WorkingDir,extension_list)
     
        
        # -----------------------------------------------------------------------
        # save input data for Simulation as Matlab binary file
        if "FLR20" == self.SensorType:
            # prepare inputs
            self.save_FLR20data_as_matlab(MatlabFileName_input_data)
        elif "CVR3" == self.SensorType:
            self.save_CVR3data_as_matlab(MatlabFileName_input_data)
            self.save_expected_results_as_matlab(MatlabFileName_expected_results)
           
        self.save_parameters_as_matlab(MatlabFileName_parameters,ParameterChnDict)
      
        # -----------------------------------------------------------------------
        # run simulation
        if self.verbose:
            print "cSimKBAEBS.run_simulation() run simulation"

        
        # remember the folder I am now in 
        actual_working_Folder = os.getcwd()
            
        # change to working directory 4 AEBS_sil_exe 
        os.chdir(WorkingDir)

        # run software-in-the-loop simulation
        if self.verbose:
            print "AEBS_sil_exe_FullFileName:", AEBS_sil_exe_FullFileName
        #os_output = os.system(AEBS_sil_exe_FullFileName)
        try: 
            subprocess.check_output(AEBS_sil_exe_FullFileName)
            if self.verbose:
                print "subprocess.check_output(AEBS_sil_exe_FullFileName) success"

        except subprocess.CalledProcessError, e:
            print "error: AEBS_sil_exe stdout output:\n", e.output
        except WindowsError, e:
            print "WindowsError:\n", e    
        
        # change back to folder I initial was in
        os.chdir(actual_working_Folder)
        #assert os.path.isfile(MatlabFileName_logdata), 'no logdata'
        assert os.path.isfile(MatlabFileName_output_data), 'no output'
      
        # load simulation results    
        self.input_data         = self.load_Matlab_file(MatlabFileName_input_data)
        if os.path.isfile(MatlabFileName_logdata):
           self.logdata            = self.load_Matlab_file(MatlabFileName_logdata)
        else:
           self.logdata = None
        self.simulation_output  = self.load_Matlab_file(MatlabFileName_output_data)
      
        # remove working dir (optional)
        if do_remove_working_dir_b:
            extension_list = ['.mat','.dat','.txt','.out']
            kbtools.delete_files(WorkingDir,extension_list)
            os.rmdir(WorkingDir)

        if self.verbose:
            print "cSimKBAEBS.run_simulation() end"

      
        return self.simulation_output
        
    #=================================================================================
    def plot_inputs(self, FigNr = 50, xlim = None, t_event = None):
        # input data from Matlab binary file - independent from sensor used
        
        input_data = self.input_data 
        simulation_output  = self.simulation_output 
        
        # -------------------------------------------------
        fig = pl.figure(FigNr)  
        fig.clf()

        # Suptitle
        FileName = self.build_FileName(t_event)
        text = "AEBS Sim inputs (%s)"%FileName
        fig.suptitle(text)

        t  = input_data['t']
        dx = input_data['Intro_dx']
    
   
        # ------------------------------------------------------
        # host vehicle speed
        ax = fig.add_subplot(811)
        ax.plot(t, input_data['ego_vRef']*3.6,'b')
        target_vRef = (input_data['ego_vRef'] + input_data['Intro_vx'])*(input_data['Intro_Id']>0)
        ax.plot(t,target_vRef*3.6,'r')
        ax.legend(('host','target'))
        ax.set_ylabel('km/h')
        ax.set_ylim(-5.0,100.0)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

        # ------------------------------------------------------
        # long acceleration to collision object
        ax = fig.add_subplot(812)
        ax.plot(t, input_data['ego_aRef'],'b')
        target_aRef = (input_data['ego_aRef'] + input_data['Intro_ax'])*(input_data['Intro_Id']>0)
        ax.plot(t, target_aRef,'r')
        ax.legend(('host','target'))
        ax.set_ylabel('m/s$^2$')
        ax.set_ylim(-10.5,2.5)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

    
        # ------------------------------------------------------
        # long. distance to collision target
        ax = fig.add_subplot(813)
        ax.plot(t, input_data['Intro_dx'])
        ax.legend(('dx',))
        ax.set_ylabel('m')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    

        # ------------------------------------------------------
        # lat distance to collision object
        ax = fig.add_subplot(814)
        ax.plot(t, input_data['Intro_dy'])
        ax.legend(('dy',))
        ax.set_ylabel('m')
        ax.set_ylim(-3.5,3.5)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

        
        # ------------------------------------------------------
        # driver override
        ax = fig.add_subplot(815)
           
        #ax.plot(t, input_data['GPPos'])
        #ax.plot(t, input_data['alpDtSteeringWheel'])
        ax.plot(t, input_data['pBrake'])
        
               
        #ax.legend(('GPPos','alpDtSteeringWheel','pBrake'))
        #ax.legend(('GPPos','pBrake'))
        ax.legend(('pBrake',))
        
        ax.set_ylabel('-')
        #ax.set_ylim(-0.1,5.5)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
        # ------------------------------------------------------
        # driver override
        ax = fig.add_subplot(816)
        ax.plot(t, 6.0+input_data['BPAct_b'])
        ax.plot(t, 4.0+input_data['GPKickdown_B'])
        ax.plot(t, 2.0+input_data['DirIndL_b'])
        ax.plot(t, input_data['DirIndL_b'])   
        
        ax.legend(('BPAct_b (+6)','GPKickdown_B (+4)','DirIndL_b (+2)','DirIndL_b'))
        ax.set_ylabel('-')
        ax.set_ylim(-0.1,7.5)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
        # ------------------------------------------------------
        # driving state
        ax = fig.add_subplot(817)
        ax.plot(t, 4.0+input_data['Intro_AdditionalSensorAssociated_b'])
        ax.plot(t, 2.0+input_data['Intro_Drive_b'])
        ax.plot(t, input_data['Intro_Stand_b'])
        
        ax.legend(('AdditionalSensorAssociated_b(+4)','Drive_b(+2)','Stand_b'))
        ax.set_ylabel('-')
        ax.set_ylim(-0.1,5.5)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
        
    
        # ------------------------------------------------------
        ax = fig.add_subplot(818)
    
        # Lines
        ax.plot(t, self.input_data['Intro_Id'])
        ax.legend(('Intro_Id',))
        ax.set_ylabel('m')
        ax.set_ylim(-0.1,3.5)
        ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
      
        # -------------------------------------------------------------------------
        # show on screen
        fig.show()
   
        self.take_a_picture(fig, "sim_inputs", t_event)
                
        return fig
            
    #=================================================================================
    def plot_inputs_FLR20(self, FigNr = 50, xlim = None, t_event = None):
        
        FLR20_sig = self.inp_sig
        
        # -------------------------------------------------
        fig = pl.figure(FigNr)  
        fig.clf()

        # Suptitle
        FileName = self.build_FileName(t_event)
        #text = '%s FusObj[%s]'%(FileName,FusObjIdx)
        text = "AEBS Sim inputs FLR20 (%s)"%FileName
        fig.suptitle(text)

        t  = FLR20_sig['PosMatrix']['CW']['Time']
        dx = FLR20_sig['Tracks'][0]['dx']
    
   
        # ------------------------------------------------------
        ax = fig.add_subplot(911)
        ax.plot(FLR20_sig['General']['Time'],FLR20_sig['General']['actual_vehicle_speed']*3.6)
        ax.legend(('vehicle speed',))
        ax.set_ylabel('km/h')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

    
        # ------------------------------------------------------
        ax = fig.add_subplot(912)
        #ax.plot(FLR20_sig['PosMatrix']['CW']['Time'], FLR20_sig['PosMatrix']['CW']['dx'])
        
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['dx'])
        ax.legend(('dx',))
        ax.set_ylabel('m')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    

        # ------------------------------------------------------
        ax = fig.add_subplot(913)
        #ax.plot(FLR20_sig['PosMatrix']['CW']['Time'], FLR20_sig['PosMatrix']['CW']['vx'])
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['vx'])
        ax.legend(('vx',))
        ax.set_ylabel('m/s')
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

        # ------------------------------------------------------
        ax = fig.add_subplot(914)
    
        # Lines
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['corrected_lateral_distance'])
        ax.legend(('corrected_lateral_distance',))
        ax.set_ylabel('m')
        ax.set_ylim(-3.5,3.5)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
        
        # ------------------------------------------------------
        ax = fig.add_subplot(915)
           
        ax.plot(FLR20_sig['Tracks'][0]['Time'], 4.0+FLR20_sig['Tracks'][0]['Left_Lane'])
        ax.plot(FLR20_sig['Tracks'][0]['Time'], 2.0+FLR20_sig['Tracks'][0]['In_Lane'])
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['Right_Lane'])
        
               
        ax.legend(('Left_Lane(+4)','In_Lane(+2)','Right_Lane'))
        ax.set_ylabel('-')
        ax.set_ylim(-0.1,5.5)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
        
        # ------------------------------------------------------
        ax = fig.add_subplot(916)
         # Lines
        #ax.plot(FLR20_sig['PosMatrix']['CW']['Time'], FLR20_sig['PosMatrix']['CW']['Stand_b'])
       
        
        ax.plot(FLR20_sig['Tracks'][0]['Time'], 4.0+FLR20_sig['Tracks'][0]['Opposite_Direction'])
        ax.plot(FLR20_sig['Tracks'][0]['Time'], 2.0+FLR20_sig['Tracks'][0]['Same_Direction'])
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['Stationary'])
        
        ax.legend(('Opposite_Direction(+4)','Same_Direction(+2)','Stationary'))
        ax.set_ylabel('-')
        ax.set_ylim(-0.1,5.5)
        ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
    
        # ------------------------------------------------------
        ax = fig.add_subplot(917)
    
        # Lines 
        ax.plot(FLR20_sig['Tracks'][0]['Time'], 2+FLR20_sig['Tracks'][0]['is_video_associated'],'m')
        ax.plot(FLR20_sig['Tracks'][0]['Time'], FLR20_sig['Tracks'][0]['CW_track'],'g')
        
        
        ax.legend(('is_video_associated','CW track'))
        ax.set_ylabel('-')
        ax.set_ylim(-0.0,4.1)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
        # ------------------------------------------------------
        ax = fig.add_subplot(918)
    
        # Lines
        ax.plot(self.input_data['t'], self.input_data['Intro_Id'])
        ax.legend(('Intro_Id',))
        ax.set_ylabel('m')
        ax.set_ylim(-0.1,3.5)
        #ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

        
        # ------------------------------------------------------
        ax = fig.add_subplot(919)
    
        # Lines
        '''
        ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['video_confidence'])
        ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['radar_confidence'])
        ax.legend(('video_confidence','radar_confidence'))
        ax.set_ylabel('-')
        ax.set_xlabel('time [s]')
        ax.grid()
        '''
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['angle'],'r')
        #ax.plot(FLR20_sig['PosMatrix']['CW']['Time'], FLR20_sig['PosMatrix']['CW']['angle'],'b')
  
        #ax.plot(FLR20_sig['AC100_targets'][0]['Time'], FLR20_sig['AC100_targets'][0]['range'],'b')
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['ta_range'],'r')

        ##ax.plot(FLR20_sig['AC100_targets'][0]['Time'], FLR20_sig['AC100_targets'][0]['angle_MSB']+FLR20_sig['AC100_targets'][0]['angle_LSB'],'b')
        #ax.plot(FLR20_sig['AC100_targets'][0]['Time'], FLR20_sig['AC100_targets'][0]['angle'],'b')
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['ta_angle'],'r')
    
        #ax.plot(FLR20_sig['AC100_targets'][0]['Time'], FLR20_sig['AC100_targets'][0]['power'],'b')
        #ax.plot(FLR20_sig['AC100_tracks'][0]['Time'], FLR20_sig['AC100_tracks'][0]['ta_power'],'r')

        # AEBS_SFN_Warning
        #ax.plot(FLR20_sig['AEBS_SFN_OUT']['Time_Warning'], FLR20_sig['AEBS_SFN_OUT']['Warning'],'r')
 
 
        if 'simulation_output' in FLR20_sig:
            ax.plot(FLR20_sig['simulation_output']['t'],     4.0+(FLR20_sig['simulation_output']['acoacoi_SetRequest']==1.0) ,'b' )
            ax.plot(FLR20_sig['simulation_output']['t'],     2.0+(FLR20_sig['simulation_output']['acopebp_SetRequest']==1.0) ,'g' )
            ax.plot(FLR20_sig['simulation_output']['t'],          FLR20_sig['simulation_output']['acopebe_SetRequest']==1.0 ,'r' )
        
        ax.set_ylim(-0.0,6.1) 
        ax.legend(('KB AEBS Warning','part. brake','emerg. brake'))
        
        ax.set_ylabel('-')
        ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
      
        # -------------------------------------------------------------------------
        # show on screen
        fig.show()
   
        self.take_a_picture(fig, "sim_inputs_FLR20", t_event)
        
        return fig
        
        
    #=================================================================================
    def plot_AEBS_output(self, FigNr = 50, xlim = None, t_event = None):
            
        simulation_output = self.simulation_output
    
        FileName = self.build_FileName(t_event)
        
        # offline - simulation
        Offline_t                       = simulation_output['t']
        Offline_AEBS_warning            = simulation_output['acoacoi_SetRequest']==1.0
        Offline_AEBS_partial_braking    = simulation_output['acopebp_SetRequest']==1.0
        Offline_AEBS_emergency_braking  = simulation_output['acopebe_SetRequest']==1.0
        
        
        # ---------------------------------------
        # AEBS outputs
        fig = pl.figure(FigNr); FigNr=FigNr+1  
        fig.clf()
        # Suptitle
        text = "AEBS outputs (%s)"%(FileName,)
        fig.suptitle(text)

        # ------------------------------------------------------
        # AEBS warning
        ax = fig.add_subplot(311)
        ax.plot(Offline_t, Offline_AEBS_warning ,'b' )
        ax.set_ylim(-0.1,1.1) 
        ax.set_ylabel('warning')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

            
        # ------------------------------------------------------
        # AEBS partial braking 
        ax = fig.add_subplot(312)
        ax.plot(Offline_t, Offline_AEBS_partial_braking ,'b' )
        ax.set_ylim(-0.1,1.1) 
        ax.set_ylabel('partial \n braking')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
        # ------------------------------------------------------
        # AEBS emergency braking 
        ax = fig.add_subplot(313)
        ax.plot(Offline_t, Offline_AEBS_emergency_braking ,'b' )
        ax.set_ylim(-0.1,1.1) 
        ax.set_ylabel('emergency \n braking')
        ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)


        fig.show()
   
        self.take_a_picture(fig, "sim_AEBS_outputs", t_event)
       
        return FigNr

        
    #=================================================================================
    def plot_AEBS_output_compare(self, FigNr = 50, xlim = None, t_event = None):
    
        FLR20_sig = self.inp_sig
        simulation_output = self.simulation_output
    
        FileName = self.build_FileName(t_event)
        
        # offline - simulation
        Offline_t                       = simulation_output['t']
        Offline_AEBS_warning            = simulation_output['acoacoi_SetRequest']==1.0
        Offline_AEBS_partial_braking    = simulation_output['acopebp_SetRequest']==1.0
        Offline_AEBS_emergency_braking  = simulation_output['acopebe_SetRequest']==1.0
        
        # online - ECU
        Online_AEBS_warning_t           = FLR20_sig['AEBS_SFN_OUT']['Time_Warning']
        Online_AEBS_warning             = FLR20_sig['AEBS_SFN_OUT']['Warning']
        
        Online_AEBS_partial_braking_t   = FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand']
        Online_AEBS_partial_braking     = np.logical_and(FLR20_sig['AEBS_SFN_OUT']['AccelDemand'] <0.0,FLR20_sig['AEBS_SFN_OUT']['AccelDemand']>-4.0)
        Online_AEBS_emergency_braking_t = FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand']
        Online_AEBS_emergency_braking   = FLR20_sig['AEBS_SFN_OUT']['AccelDemand']<=-4.0
        
                
        # AEBS system state
        # 5 collision warning
        # 6 partial braking
        # 7 emergency braking
        
        AEBSState_t = FLR20_sig['AEBS_SFN_OUT']['Time_ABESState']
        ABESState_collision_warning = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 5
        ABESState_partial_braking   = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 6
        ABESState_emergency_braking = FLR20_sig['AEBS_SFN_OUT']['ABESState'] == 7
        
        
        # ---------------------------------------
        # AEBS outputs
        fig = pl.figure(FigNr); FigNr=FigNr+1  
        fig.clf()
        # Suptitle
        text = "AEBS outputs (%s)"%(FileName,)
        fig.suptitle(text)

        # ------------------------------------------------------
        # AEBS warning
        ax = fig.add_subplot(311)
        
        ax.plot(Offline_t,                        4.0+(Offline_AEBS_warning) ,'b' )
        if Online_AEBS_warning_t is not None:
            ax.plot(Online_AEBS_warning_t,            2.0+(Online_AEBS_warning)  ,'r' )
        if AEBSState_t is not None:
            ax.plot(AEBSState_t,                      0.0+(ABESState_collision_warning) ,'g' )
               
        ax.set_ylim(-0.1,6.1) 
        ax.legend(('offline','online','online (System State)'))
       
        ax.set_ylabel('warning')
 
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)

            
        # ------------------------------------------------------
        # AEBS partial braking 
        ax = fig.add_subplot(312)
        ax.plot(Offline_t,                        4.0+(Offline_AEBS_partial_braking) ,'b' )
        if Online_AEBS_partial_braking_t is not None:
            ax.plot(Online_AEBS_partial_braking_t,    2.0+(Online_AEBS_partial_braking)  ,'r' )
        if AEBSState_t is not None:  
            ax.plot(AEBSState_t,                      0.0+(ABESState_partial_braking) ,'g' )
               
        ax.set_ylim(-0.1,6.1) 
        ax.legend(('offline','online','online (System State)'))
         
        ax.set_ylabel('partial braking')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)
    
        # ------------------------------------------------------
        # AEBS emergency braking 
        ax = fig.add_subplot(313)
        ax.plot(Offline_t,                        4.0+(Offline_AEBS_emergency_braking) ,'b' )
        if Online_AEBS_emergency_braking_t is not None:
            ax.plot(Online_AEBS_emergency_braking_t,  2.0+(Online_AEBS_emergency_braking)  ,'r' )
        if AEBSState_t is not None:
            ax.plot(AEBSState_t,                      0.0+(ABESState_emergency_braking)    ,'g' )
               
        ax.set_ylim(-0.1,6.1) 
        ax.legend(('offline','online','online (System State)'))
         
        ax.set_ylabel('emergency braking')
        ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)


        fig.show()
   
        self.take_a_picture(fig, "sim_AEBS_outputs_compare", t_event)
       
        return FigNr
       
    #=================================================================================
    def plot_ASF_output(self, FigNr = 60, xlim = None, t_event = None):
        # only show outputs ( no comparison)
    
        # used data
        #logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.build_FileName(t_event)
       
        
        # ---------------------------------------
        # ASF outputs
        fig = pl.figure(FigNr); FigNr=FigNr+1  
        fig.clf()
        # Suptitle
        text = "ASF outputs (%s)"%(FileName,)
        fig.suptitle(text)
        
        # 1. acoopti_SetRequest   
        ax = fig.add_subplot(611)
        #ax.set_title("acoopti_SetRequest")
        ax.plot(simulation_output["t"], simulation_output["acoopti_SetRequest"],'bx-' )
        ax.set_ylabel('acoopti \n request \n [bool]')
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
            ax.set_xlim(xlim)
        
        # 2. acoacoi_SetRequest
        ax = fig.add_subplot(612)
        #ax.set_title("acoacoi_SetRequest")
        ax.plot(simulation_output["t"], simulation_output["acoacoi_SetRequest"],'bx-' )
        ax.set_ylabel('acoacoi \n request \n [bool]')
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
           ax.set_xlim(xlim)
        
        # 3. acopebp_SetRequest
        ax = fig.add_subplot(613)
        #ax.set_title("acopebp_SetRequest")
        ax.plot(simulation_output["t"], simulation_output["acopebp_SetRequest"],'bx-' )
        ax.set_ylabel('acopebp \n request \n [bool]')
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # 4. acopebe_SetRequest
        ax = fig.add_subplot(614)
        #ax.set_title("acopebe_SetRequest")
        ax.plot(simulation_output["t"], simulation_output["acopebe_SetRequest"],'bx-' )
        ax.set_ylabel('acopebe \n request \n [bool]')
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
            ax.set_xlim(xlim)    

        # 5. acopebp_RequestValue
        ax = fig.add_subplot(615)
        #ax.set_title("acopebp_RequestValue")
        ax.plot(simulation_output["t"], simulation_output["acopebp_RequestValue"],'bx-' )
        ax.set_ylabel('acopebp \n request value \n [m/s$^2$]')
        ax.grid()
        ax.set_ylim(-10.1,1.1)
        if xlim:
            ax.set_xlim(xlim)

        # 6. acopebe_RequestValue
        ax = fig.add_subplot(616)
        #ax.set_title("acopebe_RequestValue")
        ax.plot(simulation_output["t"], simulation_output["acopebe_RequestValue"],'bx-' )
        ax.set_ylabel('acopebe \n request value \n [m/s$^2$]')
        ax.grid()
        ax.set_ylim(-10.1,1.1)
        ax.set_xlabel('time [s]')
        if xlim:
            ax.set_xlim(xlim)

    
        fig.show()

        self.take_a_picture(fig, "sim_ASF_outputs", t_event)
        
        return FigNr

    #=================================================================================
    def plot_ASF_output_compare(self, FigNr = 60, xlim = None, t_event = None):
        # compare with CVR3 online calcuations
        
        # under construction
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None
        
        
        logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.build_FileName(t_event)
        
        # ------------------------------------------------------------------
        # ASF output
        fig = pl.figure(FigNr); FigNr=FigNr+1  
        fig.clf()
    
        # Suptitle
        text = "ASF output compare (%s)"%(FileName,)
        fig.suptitle(text)
        
    
        # acoopti_SetRequest   
        ax = fig.add_subplot(611)
        ax.set_title("acoopti_SetRequest")
        ax.plot(simulation_output["t"], simulation_output["acoopti_SetRequest"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']['acoopti_SetRequest'],'rx-' )
            #ax.plot(CVR3_sig['ASF']['t_T20'], CVR3_sig['ASF']['acoopti_SetRequest_T20'],'kx-')
            ax.legend(('SIM','ECU'))   
        ax.set_ylabel('acoopti \n SetRequest')
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
            ax.set_xlim(xlim)
        
        # acoacoi_SetRequest
        ax = fig.add_subplot(612)
        ax.set_title("acoacoi_SetRequest")
        ax.plot(simulation_output["t"], simulation_output["acoacoi_SetRequest"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']['acoacoi_SetRequest'],'rx-' )
            #ax.plot(CVR3_sig['ASF']['t_T20'], CVR3_sig['ASF']['acoacoi_SetRequest_T20'],'kx-')
            ax.legend(('SIM','ECU'))   
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
           ax.set_xlim(xlim)
        
        # acopebp_SetRequest
        ax = fig.add_subplot(613)
        ax.set_title("acopebp_SetRequest")
        ax.plot(simulation_output["t"], simulation_output["acopebp_SetRequest"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']['acopebp_SetRequest'],'rx-' )
            #ax.plot(CVR3_sig['ASF']['t_T20'], CVR3_sig['ASF']['acopebp_SetRequest_T20'],'kx-')
            ax.legend(('SIM','ECU'))   
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # acopebe_SetRequest
        ax = fig.add_subplot(614)
        ax.set_title("acopebe_SetRequest")
        ax.plot(simulation_output["t"], simulation_output["acopebe_SetRequest"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']['acopebe_SetRequest'],'rx-' )
            #ax.plot(CVR3_sig['ASF']['t_T20'], CVR3_sig['ASF']['acopebe_SetRequest_T20'],'kx-')
            ax.legend(('SIM','ECU'))   
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
            ax.set_xlim(xlim)    

        # acopebp_RequestValue
        ax = fig.add_subplot(615)
        ax.set_title("acopebp_RequestValue")
        ax.plot(simulation_output["t"], simulation_output["acopebp_RequestValue"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']['acopebp_RequestValue'],'rx-' )
            ax.legend(('SIM','ECU'))   
        ax.grid()
        ax.set_ylim(-10.1,1.1)
        if xlim:
            ax.set_xlim(xlim)

        # acopebe_RequestValue
        ax = fig.add_subplot(616)
        ax.set_title("acopebe_RequestValue")
        ax.plot(simulation_output["t"], simulation_output["acopebe_RequestValue"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']['acopebe_RequestValue'],'rx-' )
            ax.legend(('SIM','ECU'))   
        ax.grid()
        ax.set_ylim(-10.1,1.1)
        ax.set_xlabel('time [s]')
        if xlim:
            ax.set_xlim(xlim)

    
        fig.show()

        self.take_a_picture(fig, "sim_ASF_outputs_compare", t_event)
    
        return FigNr
    #=================================================================================
    def plot_Master_SAS(self, FigNr = 70, xlim = None, t_event = None):
    
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None
        
        
        logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.build_FileName(t_event)


        # ---------------------------------------------------------------------
        # Master Same Approach Stationary
        fig = pl.figure(FigNr); FigNr=FigNr+1  
        fig.clf()

        # Suptitle
        text = "Master SAS - Same Approach Stationary (%s)"%(FileName,)
        fig.suptitle(text)

        # mastsas_status
        ax = fig.add_subplot(811)
        ax.set_title("mastsas_status")
        ax.plot(logdata["t"], logdata["mastsas_status"],'bx-' )
    
        ax.grid()
        ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # mastsas_activePhase
        ax = fig.add_subplot(812)
        ax.set_title("mastsas_activePhase")
        ax.plot(logdata["t"], logdata["mastsas_activePhase"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["MastSas.activePhase"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()  
        ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)

            
        # repprew_status
        ax = fig.add_subplot(813)
        ax.set_title("repprew_status")
        ax.plot(logdata["t"], logdata["repprew_status"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["repPrewStatus"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()  
        ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # repretg_status
        ax = fig.add_subplot(814)
        ax.set_title("repretg_status")
        ax.plot(logdata["t"], logdata["repretg_status"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["repRetgStatus"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()  
        ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # PSSBrakeIntervention
        ax = fig.add_subplot(815)
        ax.set_title("PSSBrakeIntervention")
        #ax.plot(logdata["t"], logdata["mastsas_PSSBrakeIntervention_B"],'bx-' )
        ax.plot(logdata["t"], logdata["pressas_PSSBrakeInterventionInProgress"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig["ASF"]["Time_pressas_PSSBrakeInterventionInProgress"], CVR3_sig["ASF"]["pressas_PSSBrakeInterventionInProgress"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # repretg ExecutionStatus
        ax = fig.add_subplot(816)
        ax.set_title("repretg ExecutionStatus")
        ax.plot(logdata["t"], logdata["repretg_ExecutionStatus"],'bx-' )  
        if CVR3_sig is not None:
            ax.plot(CVR3_sig["ASF"]["Time_repretg_ExecutionStatus"], CVR3_sig["ASF"]["repretg_ExecutionStatus"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()
        ax.set_ylim(-0.1,5.1)
        if xlim:
            ax.set_xlim(xlim)

        # acopebpState    
        ax = fig.add_subplot(817)
        ax.set_title("acopebpState")
        if CVR3_sig is not None:
            ax.plot(CVR3_sig["Time"], CVR3_sig['ASF']['acopebpState'],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()
        ax.set_ylim(-0.1,5.1)
        if xlim:
            ax.set_xlim(xlim)
        
                  
    
        # acopebeState
        ax = fig.add_subplot(818)
        ax.set_title("acopebeState")
        if CVR3_sig is not None:
            ax.plot(CVR3_sig["Time"], CVR3_sig['ASF']['acopebeState'],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()
        ax.set_ylim(-0.1,5.1)
        ax.set_xlabel('time [s]')
        if xlim:
            ax.set_xlim(xlim)

    
        fig.show()
        
        self.take_a_picture(fig, "sim_plot_Master_SAS", t_event)

        return FigNr

    #=================================================================================
    def plot_Master_SAM(self, FigNr = 70, xlim = None, t_event = None):
    
        
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None
        
        
        logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.build_FileName(t_event)

        # ---------------------------------------------------------------------
        # Master Same Approach Moving
        fig = pl.figure(FigNr); FigNr=FigNr+1  
        fig.clf()

        # Suptitle
        text = "Master SAM - Same Approach Moving (%s)"%(FileName,)
        fig.suptitle(text)
       
        
        # mastsas_status
        ax = fig.add_subplot(811)
        ax.set_title("mastsam_status")
        ax.plot(logdata["t"], logdata["mastsam_status"],'bx-' )
    
        ax.grid()
        ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # mastsas_activePhase
        ax = fig.add_subplot(812)
        ax.set_title("mastsam_activePhase")
        ax.plot(logdata["t"], logdata["mastsam_activePhase"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["MastSam.activePhase"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()  
        ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)

            
        # repprew_status
        ax = fig.add_subplot(813)
        ax.set_title("repprew_status")
        ax.plot(logdata["t"], logdata["repprew_status"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["repPrewStatus"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()  
        ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # repretg_status
        ax = fig.add_subplot(814)
        ax.set_title("repretg_status")
        ax.plot(logdata["t"], logdata["repretg_status"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["repRetgStatus"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()  
        ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # PSSBrakeIntervention
        ax = fig.add_subplot(815)
        ax.set_title("PSSBrakeIntervention")
        #ax.plot(logdata["t"], logdata["mastsas_PSSBrakeIntervention_B"],'bx-' )
        ax.plot(logdata["t"], logdata["pressas_PSSBrakeInterventionInProgress"],'bx-' )
        if CVR3_sig is not None:
            ax.plot(CVR3_sig["ASF"]["Time_pressas_PSSBrakeInterventionInProgress"], CVR3_sig["ASF"]["pressas_PSSBrakeInterventionInProgress"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()
        ax.set_ylim(-0.1,1.1)
        if xlim:
            ax.set_xlim(xlim)
    
        # repretg ExecutionStatus
        ax = fig.add_subplot(816)
        ax.set_title("repretg ExecutionStatus")
        ax.plot(logdata["t"], logdata["repretg_ExecutionStatus"],'bx-' )  
        if CVR3_sig is not None:
            ax.plot(CVR3_sig["ASF"]["Time_repretg_ExecutionStatus"], CVR3_sig["ASF"]["repretg_ExecutionStatus"],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()
        ax.set_ylim(-0.1,5.1)
        if xlim:
            ax.set_xlim(xlim)

        # acopebpState    
        ax = fig.add_subplot(817)
        ax.set_title("acopebpState")
        if CVR3_sig is not None:
            ax.plot(CVR3_sig["Time"], CVR3_sig['ASF']['acopebpState'],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()
        ax.set_ylim(-0.1,5.1)
        if xlim:
            ax.set_xlim(xlim)
        
                  
    
        # acopebeState
        ax = fig.add_subplot(818)
        ax.set_title("acopebeState")
        if CVR3_sig is not None:
            ax.plot(CVR3_sig["Time"], CVR3_sig['ASF']['acopebeState'],'rx-' )
            ax.legend(('SIM','ECU'))
        ax.grid()
        ax.set_ylim(-0.1,5.1)
        ax.set_xlabel('time [s]')
        if xlim:
            ax.set_xlim(xlim)

    
        fig.show()
        
        self.take_a_picture(fig, "sim_plot_Master_SAM", t_event)
        
        return FigNr

    #=================================================================================
    def plot_Master_SAS_Agts(self, FigNr = 80, xlim = None, t_event = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        # -------------------------------------------------------
        AgtList = ['asaxsex', 'asaslas','asasras','axasxas']
        
        self.plot_Master_Agts(FigNr, xlim, AgtList,t_event)
        
    #=================================================================================
    def plot_Master_SAM_Agts(self, FigNr = 80, xlim = None, t_event = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        # -------------------------------------------------------
        AgtList = ['asaxsex', 'asamlam','asamram','axamxam']
        
        self.plot_Master_Agts(FigNr, xlim, AgtList,t_event)
        
    #=================================================================================
    def plot_Master_Agts(self, FigNr = 80, xlim = None, AgtList = [],t_event = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        
        # Abbreviations
        logdata = self.logdata  
        simulation_output = self.simulation_output
         
        FileName = self.build_FileName(t_event)
   
        for agt in AgtList:
            fig = pl.figure(FigNr); FigNr=FigNr+1      
       
            fig.clf()  
            # Suptitle
            text = "%s (%s)"%(agt,FileName)
            fig.suptitle(text)

            # ------------------------------------------------------------------------
            # skill
            ax = fig.add_subplot(411)
            ax.plot(logdata["t"], logdata["%s_skill"%agt],'bx-' )
            ax.set_ylabel('skill')
            ax.grid() 
            ax.set_ylim(-0.1,1.1)   
            if xlim:
                ax.set_xlim(xlim)

            # ------------------------------------------------------------------------    
            # skillW
            ax = fig.add_subplot(412)
            ax.plot(logdata["t"], logdata["%s_skillW"%agt],'bx-' )
            ax.grid()  
            ax.set_ylabel('skillW')
            ax.set_ylim(-0.1,1.1)   
            if xlim:
                ax.set_xlim(xlim)
          
      
            # --------------------------------------------------------------      
            # plaus
            ax = fig.add_subplot(413)
            ax.plot(logdata["t"], logdata["%s_plaus"%agt],'bx-' )
            ax.grid()  
            ax.set_ylabel('plaus')
            ax.set_ylim(-0.1,1.1)   
            if xlim:
                ax.set_xlim(xlim)
     
            # --------------------------------------------------------------      
            # status
            ax = fig.add_subplot(414)
            ax.plot(logdata["t"], logdata["%s_status"%agt],'bx-' )
            ax.grid() 
            ax.set_ylabel('status')
            ax.set_ylim(-0.1,5.1) 
            ax.set_xlabel('time [s]')            
            if xlim:
                ax.set_xlim(xlim)
     
    
            fig.show()
            
            self.take_a_picture(fig, "sim_plot_%s"%(agt,),t_event)
            
        return FigNr
 
    #=================================================================================
    def plot_Master_SAS_Agts_compare(self, FigNr = 80, xlim = None, t_event = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        # -------------------------------------------------------
        AgtList = ['asaxsex', 'asaslas','asasras','axasxas']
        
        self.plot_Master_Agts_compare(FigNr, xlim, AgtList, t_event)
        
    #=================================================================================
    def plot_Master_SAM_Agts_compare(self, FigNr = 80, xlim = None, t_event = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        # -------------------------------------------------------
        AgtList = ['asaxsex', 'asamlam','asamram','axamxam']
        
        self.plot_Master_Agts_compare(FigNr, xlim, AgtList, t_event)
        
    #=================================================================================
    def plot_Master_Agts_compare(self, FigNr = 80, xlim = None, AgtList = [], t_event = None):
        # compare with CVR3 online calcuations
        
        # under construction
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None

        logdata = self.logdata  
        simulation_output = self.simulation_output
         
        FileName = self.build_FileName(t_event)
        
        for agt in AgtList:
            fig = pl.figure(FigNr); FigNr=FigNr+1      
       
            fig.clf()  
            # Suptitle
            text = "%s (%s)"%(agt,FileName)
            fig.suptitle(text)

            
    
            # ------------------------------------------------------------------------
            # skill
            ax = fig.add_subplot(611)
            if logdata is not None:
                ax.plot(logdata["t"], logdata["%s_skill"%agt],'bx-' )
                if CVR3_sig is not None:
                    ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["%s_skill"%agt],'rx-' )
                    if "%s_time_org"%agt in CVR3_sig['ASF']:
                        ax.plot(CVR3_sig['ASF']["%s_time_org"%agt] , CVR3_sig['ASF']["%s_skill_org"%agt],'kx-' )
                    ax.legend(('SIM','ECU'))
                else:
                    ax.legend(('SIM',))
            ax.set_ylabel('skill')
            ax.grid() 
            ax.set_ylim(-0.1,1.1)   
            if xlim:
                ax.set_xlim(xlim)

            # skill - error
            ax = fig.add_subplot(612)
            if (logdata is not None) and (CVR3_sig is not None):
                ax.plot(logdata["t"], logdata["%s_skill"%agt]-CVR3_sig['ASF']["%s_skill"%agt],'bx-' )
                ax.legend(('SIM-ECU',))
            ax.grid() 
            ax.set_ylabel('error')
            ax.set_ylim(-0.01,0.01)   
            if xlim:
                ax.set_xlim(xlim)
    
            # ------------------------------------------------------------------------    
            # skillW
            ax = fig.add_subplot(613)
            ax.plot(logdata["t"], logdata["%s_skillW"%agt],'bx-' )
            if CVR3_sig is not None:
                ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["%s_skillW"%agt],'rx-' )
                if "%s_time_org"%agt in CVR3_sig['ASF']:
                    ax.plot(CVR3_sig['ASF']["%s_time_org"%agt] , CVR3_sig['ASF']["%s_skillW_org"%agt],'kx-' )
                ax.legend(('SIM','ECU'))
            else:
                ax.legend(('SIM',))
            ax.grid()  
            ax.set_ylabel('skillW')
            ax.set_ylim(-0.1,1.1)   
            if xlim:
                ax.set_xlim(xlim)
          
      
            # skillW - error
            ax = fig.add_subplot(614)
            if CVR3_sig is not None:
                ax.plot(logdata["t"], logdata["%s_skillW"%agt]-CVR3_sig['ASF']["%s_skillW"%agt],'bx-' )
                ax.legend(('SIM-ECU',))
            ax.grid() 
            ax.set_ylabel('error')
            ax.set_ylim(-0.01,0.01)   
            if xlim:
                ax.set_xlim(xlim)    
      
            # --------------------------------------------------------------      
            # plaus
            ax = fig.add_subplot(615)
            ax.plot(logdata["t"], logdata["%s_plaus"%agt],'bx-' )
            if CVR3_sig is not None:
                ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["%s_plaus"%agt],'rx-' )
                if "%s_time_org"%agt in CVR3_sig['ASF']:
                    ax.plot(CVR3_sig['ASF']["%s_time_org"%agt] , CVR3_sig['ASF']["%s_plaus_org"%agt],'kx-' )
                ax.legend(('SIM','ECU'))
            else:
                ax.legend(('SIM',))
            ax.grid()  
            ax.set_ylabel('plaus')
            ax.set_ylim(-0.1,1.1)   
            if xlim:
                ax.set_xlim(xlim)
     
            # --------------------------------------------------------------      
            # status
            ax = fig.add_subplot(616)
            ax.plot(logdata["t"], logdata["%s_status"%agt],'bx-' )
            if CVR3_sig is not None:
                try:
                    ax.plot(CVR3_sig['ASF']['Time'], CVR3_sig['ASF']["%s_status"%agt],'rx-' )
                    if "%s_time_org"%agt in CVR3_sig['ASF']:
                        ax.plot(CVR3_sig['ASF']["%s_time_org"%agt] , CVR3_sig['ASF']["%s_plaus_org"%agt],'kx-' )
                    ax.legend(('SIM','ECU'))
                except:
                    pass
            ax.grid() 
            ax.set_ylabel('status')
            ax.set_ylim(-0.1,5.1)  
            ax.set_xlabel('time [s]')            
            if xlim:
                ax.set_xlim(xlim)
     
    
            fig.show()
            self.take_a_picture(fig, "sim_plot_%s"%(agt,),t_event)
 
        return FigNr
    #=================================================================================
    def plot_repprew(self, FigNr = 110, xlim = None, t_event = None):
    
        
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None
        
        
        logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.build_FileName(t_event)

        # ---------------------------------------------------------------------
        # Master Same Approach Moving
        fig = pl.figure(FigNr); FigNr=FigNr+1  
        fig.clf()

        # Suptitle
        text = "repprew (%s)"%(FileName,)
        fig.suptitle(text)
       
        
        # repprew_tBlockingTimer
        ax = fig.add_subplot(411)
        ax.set_title("repprew_tBlockingTimer")
        ax.plot(logdata["t"], logdata["repprew_tBlockingTimer"],'bx-' )
    
        ax.grid()
        #ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)

        # mastsas_status
        ax = fig.add_subplot(412)
        ax.set_title("repprew_AliveCounter")
        ax.plot(logdata["t"], logdata["repprew_AliveCounter"],'bx-' )
    
        ax.grid()
        #ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
        
        # repprew_ShotTheSheriff
        ax = fig.add_subplot(413)
        ax.set_title("repprew_ShotTheSheriff")
        ax.plot(logdata["t"], logdata["repprew_ShotTheSheriff"],'bx-' )
    
        ax.grid()
        #ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
        
        # repprew_aAvoid_DEBUG
        ax = fig.add_subplot(414)
        ax.set_title("repprew_aAvoid_DEBUG")
        ax.plot(logdata["t"], logdata["repprew_aAvoid_DEBUG"],'bx-' )
    
        ax.grid()
        #ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
        
        
        fig.show()
        
        self.take_a_picture(fig, "sim_plot_repprew", t_event)
        
        return FigNr
    #=================================================================================
    def plot_repretg(self, FigNr = 111, xlim = None, t_event = None):
    
        
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None
        
        
        logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.build_FileName(t_event)

        # ---------------------------------------------------------------------
        # Master Same Approach Moving
        fig = pl.figure(FigNr); FigNr=FigNr+1  
        fig.clf()

        # Suptitle
        text = "repretg (%s)"%(FileName,)
        fig.suptitle(text)
       
        
        # repretg_tBlockingTimer
        ax = fig.add_subplot(211)
        ax.set_title("repretg_tBlockingTimer")
        ax.plot(logdata["t"], logdata["repretg_tBlockingTimer"],'bx-' )
    
        ax.grid()
        #ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)

        # mastsas_status
        ax = fig.add_subplot(212)
        ax.set_title("repretg_AliveCounter")
        ax.plot(logdata["t"], logdata["repretg_AliveCounter"],'bx-' )
    
        ax.grid()
        #ax.set_ylim(-0.1,10.1)
        if xlim:
            ax.set_xlim(xlim)
        
        
        fig.show()
        
        self.take_a_picture(fig, "sim_plot_repretg", t_event)
        
        return FigNr
