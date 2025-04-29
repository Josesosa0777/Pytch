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

import scipy.io as sio

import kbtools


# ==========================================================
class cSimTRWTracking():

    # ==========================================================
    def __init__(self, inp_sig,AEBS_sil_exe_FullFileName=None,WorkingDir=None):
        
                   
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
            self.WorkingDir = r"./tracking_dll"
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
    
    # ==========================================================
    def take_a_picture(self, fig, PngFileName):
        # create png picture
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
        
        
        FLR20_sig = self.inp_sig
  
           
        # -----------------------------------------------------------------------------------
        # common time axis
        t =  FLR20_sig['PosMatrix']['CW']['Time']
        
        # -----------------------------------------------------------------------------------
        # radar 
        current_ramp_type         =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["current_ramp_type"], t) 
        
        # -----------------------------------------------------------------------------------
        # vehicle state
        actual_vehicle_speed      =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["actual_vehicle_speed"], t) 
        cvd_yawrate               =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["cvd_yawrate"], t) 
        prefiltered_yawrate       =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["prefiltered_yawrate"], t) 
        yawrate_offset            =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["yawrate_offset"], t) 
        covi                      =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["covi"], t) 
        dfil                      =  kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["dfil"], t) 
       
        # -----------------------------------------------------------------------------------
        # driver input
        BrakePedalPos   =  kbtools.resample(FLR20_sig["J1939"]["Time_BrakePedalPos"],  FLR20_sig["J1939"]["BrakePedalPos"], t) 
        EBSBrakeSwitch  =  kbtools.resample(FLR20_sig["J1939"]["Time_EBSBrakeSwitch"], FLR20_sig["J1939"]["EBSBrakeSwitch"], t) 
        AccelPedalPos1  =  kbtools.resample(FLR20_sig["J1939"]["Time_AccelPedalPos1"], FLR20_sig["J1939"]["AccelPedalPos1"], t) 

        # -----------------------------------------------------------------------------------
        signal_list = {
    
                   # -------------------------------------------------------------   
                   # time
                   't'                     : t,
                   
                   # -------------------------------------------------------------   
                   # expected results
                   'cw_track_Valid'        : FLR20_sig['PosMatrix']['CW']['Valid'],
                   'cw_track_ds'           : FLR20_sig['PosMatrix']['CW']['ds'],
                                 
                   # -------------------------------------------------------------   
                   # GeneralStatusData_t
                   'cvd_yaw_f32'             : cvd_yawrate,                 # filtered and corrected yaw rate from A087 [degree/s]
                   'unfiltered_yaw_rate_f32' : prefiltered_yawrate,         # unfiltered and uncorrected yaw rate from vehicle CAN or A087 [degree/s] 
                   'yaw_sensor_offset_f32'   : yawrate_offset,              # measured filtered yawrate-sensor offset [degree/s] 
                   'speed_cor_factor_f32'    : covi,                        # speed correction factor (0..1)
                   'misalignment_angle_f32'  : dfil,                        # sensor mis-alignment in azimuth [degree]
                   'actual_vehicle_speed_f32': actual_vehicle_speed,        # speed of the host vehicle [m/s]
                   'ems_pedal_position_f32'  : AccelPedalPos1,              # position of the accelerator pedal [%]
                   'current_ramp_type_u8'    : current_ramp_type,           # Radar ramp type 0,1,2 
                   'bbc_brake_pressed_b'     : EBSBrakeSwitch,              # indicating if brake is pressed [bool]
                   

                   }
        
        # add tracks
        N_targets_AC100 = len(FLR20_sig['Targets'])
        for k in xrange(N_targets_AC100):
            # synchronize
            angle              = kbtools.resample(FLR20_sig['Targets'][k]["Time"], FLR20_sig["Targets"][k]["angle"], t) ;
            relative_velocitiy = kbtools.resample(FLR20_sig['Targets'][k]["Time"], FLR20_sig["Targets"][k]["relative_velocitiy"], t) ;
            range              = kbtools.resample(FLR20_sig['Targets'][k]["Time"], FLR20_sig["Targets"][k]["range"], t) ;
            power              = kbtools.resample(FLR20_sig['Targets'][k]["Time"], FLR20_sig["Targets"][k]["power"], t) ;
            is_available_b     = k < kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["number_of_targets"], t);
            target_status      = kbtools.resample(FLR20_sig['Targets'][k]["Time"], FLR20_sig["Targets"][k]["target_status"], t) ;
            tracking_flags     = kbtools.resample(FLR20_sig['Targets'][k]["Time"], FLR20_sig["Targets"][k]["target_flags"], t) ;
            
            
            signal_list["targets_a%d__angle_f32"%k]        = angle
            signal_list["targets_a%d__speed_pl_f32"%k]     = relative_velocitiy
            signal_list["targets_a%d__distance_pl_f32"%k]  = range
            signal_list["targets_a%d__power_f32"%k]        = power
            signal_list["targets_a%d__is_available_b"%k]   = is_available_b
            signal_list["targets_a%d__status_u8"%k]        = target_status
            signal_list["targets_a%d__flags_u8"%k]         = tracking_flags

    
        # save signals to matlab binary         
        sio.savemat(FileName, signal_list, oned_as='row')    


    #=================================================================================
    def save_expected_results_as_matlab(self, FileName):
        # data for expected results - output data
        
        FLR20_sig = self.inp_sig
        signal_list = {

                   # -------------------------------------------------------------   
                   # time
                   't'                     : FLR20_sig['PosMatrix']['CW']['Time'],
            
                   # -------------------------------------------------------------   
                   # expected results
                   'cw_track_Valid'        : FLR20_sig['PosMatrix']['CW']['Valid'],
                   'cw_track_ds'           : FLR20_sig['PosMatrix']['CW']['ds'],
                   
                   }
                
   
        sio.savemat(FileName, signal_list, oned_as='row')  

     
    #=================================================================================
    def run_simulation(self, ParameterChnDict = {}):
        # run C++ simulation        
        
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
        
          
   
   
        # -----------------------------------------------------------------------
        # create or purge working directory for AEBS_sil_exe
        if not os.path.exists(WorkingDir):
            os.makedirs(WorkingDir)
        else:
            extension_list = ['.mat','.dat']
            kbtools.delete_files(WorkingDir,extension_list)
     
        
        # -----------------------------------------------------------------------
        # save input data for Simulation as Matlab binary file
        if "FLR20" == self.SensorType:
            # prepare inputs
            self.save_FLR20data_as_matlab(MatlabFileName_input_data)
              
        self.save_parameters_as_matlab(MatlabFileName_parameters,ParameterChnDict)
      
        # -----------------------------------------------------------------------
        # run simulation

        # remember the folder I am now in 
        actual_working_Folder = os.getcwd()
            
        # change to working directory 4 AEBS_sil_exe 
        os.chdir(WorkingDir)

        # run software-in-the-loop simulation
        os_output = os.system(AEBS_sil_exe_FullFileName)

        # change back to folder I initial was in
        os.chdir(actual_working_Folder)
        assert os.path.isfile(MatlabFileName_logdata), 'no logdata'
        assert os.path.isfile(MatlabFileName_output_data), 'no output'
      
        # load simulation results    
        self.input_data         = self.load_Matlab_file(MatlabFileName_input_data)
        self.logdata            = self.load_Matlab_file(MatlabFileName_logdata)
        self.simulation_output  = self.load_Matlab_file(MatlabFileName_output_data)
      
        return self.simulation_output
        
    #=================================================================================
    def plot_inputs(self, FigNr = 50, xlim = None):
        # input data from Matlab binary file - independent from sensor used
        
        input_data = self.input_data 
        simulation_output  = self.simulation_output 
        
        # -------------------------------------------------
        fig = pl.figure(FigNr)  
        fig.clf()

        # Suptitle
        FileName = self.FileName
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
        ax.legend(('GPPos','pBrake'))
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
   
        self.take_a_picture(fig, "%s_sim_inputs.png"%(FileName,))
                
        return fig
            
    #=================================================================================
    def plot_inputs_FLR20(self, FigNr = 50, xlim = None):
        
        FLR20_sig = self.inp_sig
        
        # -------------------------------------------------
        fig = pl.figure(FigNr)  
        fig.clf()

        # Suptitle
        FileName = self.FileName
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
   
        self.take_a_picture(fig, "%s_sim_inputs_FLR20.png"%(FileName,))
        
        return fig
        
        
    #=================================================================================
    def plot_AEBS_output(self, FigNr = 50, xlim = None):
            
        simulation_output = self.simulation_output
    
        FileName = self.FileName
        
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
   
        self.take_a_picture(fig, "%s_sim_AEBS_outputs.png"%(FileName,))
       
        return FigNr

        
    #=================================================================================
    def plot_AEBS_output_compare(self, FigNr = 50, xlim = None):
    
        FLR20_sig = self.inp_sig
        simulation_output = self.simulation_output
    
        FileName = self.FileName
        
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
        if Online_AEBS_warning_t:
            ax.plot(Online_AEBS_warning_t,            2.0+(Online_AEBS_warning)  ,'r' )
        if AEBSState_t:
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
        if Online_AEBS_partial_braking_t:
            ax.plot(Online_AEBS_partial_braking_t,    2.0+(Online_AEBS_partial_braking)  ,'r' )
        if AEBSState_t:  
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
        if Online_AEBS_emergency_braking_t:
            ax.plot(Online_AEBS_emergency_braking_t,  2.0+(Online_AEBS_emergency_braking)  ,'r' )
        if AEBSState_t:
            ax.plot(AEBSState_t,                      0.0+(ABESState_emergency_braking)    ,'g' )
               
        ax.set_ylim(-0.1,6.1) 
        ax.legend(('offline','online','online (System State)'))
         
        ax.set_ylabel('emergency braking')
        ax.set_xlabel('time [s]')
        ax.grid()
        if xlim:
            ax.set_xlim(xlim)


        fig.show()
   
        self.take_a_picture(fig, "%s_sim_AEBS_outputs_compare.png"%(FileName,))
       
        return FigNr
       
    #=================================================================================
    def plot_ASF_output(self, FigNr = 60, xlim = None):
        # only show outputs ( no comparison)
    
        # used data
        logdata = self.logdata  
        simulation_output = self.simulation_output

        
        FileName = self.FileName
       
        
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

        self.take_a_picture(fig, "%s_sim_ASF_outputs.png"%(FileName,))
        
        return FigNr

    #=================================================================================
    def plot_ASF_output_compare(self, FigNr = 60, xlim = None):
        # compare with CVR3 online calcuations
        
        # under construction
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None
        
        
        logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.FileName
        
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

        self.take_a_picture(fig, "%s_sim_ASF_outputs_compare.png"%(FileName,))
    
        return FigNr
    #=================================================================================
    def plot_Master_SAS(self, FigNr = 70, xlim = None):
    
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None
        
        
        logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.FileName
 

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
        
        self.take_a_picture(fig, "%s_sim_plot_Master_SAS.png"%(FileName,))

        return FigNr

    #=================================================================================
    def plot_Master_SAM(self, FigNr = 70, xlim = None):
    
        
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None
        
        
        logdata = self.logdata  
        simulation_output = self.simulation_output

        FileName = self.FileName

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
        
        self.take_a_picture(fig, "%s_sim_plot_Master_SAM.png"%(FileName,))
        
        return FigNr

    #=================================================================================
    def plot_Master_SAS_Agts(self, FigNr = 80, xlim = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        # -------------------------------------------------------
        AgtList = ['asaxsex', 'asaslas','asasras','axasxas']
        
        self.plot_Master_Agts(FigNr, xlim, AgtList)
        
    #=================================================================================
    def plot_Master_SAM_Agts(self, FigNr = 80, xlim = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        # -------------------------------------------------------
        AgtList = ['asaxsex', 'asamlam','asamram','axamxam']
        
        self.plot_Master_Agts(FigNr, xlim, AgtList)
        
    #=================================================================================
    def plot_Master_Agts(self, FigNr = 80, xlim = None, AgtList = []):
        # only show offline calculated internal signals ( no comparison with online calculated)
        
        # Abbreviations
        logdata = self.logdata  
        simulation_output = self.simulation_output
         
        FileName = self.FileName
        
    
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
            
            self.take_a_picture(fig, "%s_sim_plot_%s.png"%(FileName,agt))
            
        return FigNr
 
    #=================================================================================
    def plot_Master_SAS_Agts_compare(self, FigNr = 80, xlim = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        # -------------------------------------------------------
        AgtList = ['asaxsex', 'asaslas','asasras','axasxas']
        
        self.plot_Master_Agts_compare(FigNr, xlim, AgtList)
        
    #=================================================================================
    def plot_Master_SAM_Agts_compare(self, FigNr = 80, xlim = None):
        # only show offline calculated internal signals ( no comparison with online calculated)
        # -------------------------------------------------------
        AgtList = ['asaxsex', 'asamlam','asamram','axamxam']
        
        self.plot_Master_Agts_compare(FigNr, xlim, AgtList)
        
    #=================================================================================
    def plot_Master_Agts_compare(self, FigNr = 80, xlim = None, AgtList = []):
        # compare with CVR3 online calcuations
        
        # under construction
        if "CVR3" == self.SensorType:
           CVR3_sig = self.inp_sig
        else:
           CVR3_sig = None

        logdata = self.logdata  
        simulation_output = self.simulation_output
         
        FileName = self.FileName
        
        for agt in AgtList:
            fig = pl.figure(FigNr); FigNr=FigNr+1      
       
            fig.clf()  
            # Suptitle
            text = "%s (%s)"%(agt,FileName)
            fig.suptitle(text)

            
    
            # ------------------------------------------------------------------------
            # skill
            ax = fig.add_subplot(611)
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
            if CVR3_sig is not None:
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
            self.take_a_picture(fig, "%s_sim_plot_%s.png"%(FileName,agt))
 
        return FigNr
