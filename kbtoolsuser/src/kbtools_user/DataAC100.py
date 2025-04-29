'''
   
   data source: AC100
   
   extracted data
   - track 0..9
   - vehicle speed, yaw rate, curavture, etc.
   - CW Track
   - reflected power
   
   class cDataAC100() with static methods 
   
   Ulrich Guecker 
   2013-07-19   1) introduce: AC100_sig['J1939'] 
                2) add signals 'ds', 'lateral_position' and 'vr' to AC100_sig['PosMatrix']  
   2013-07-08   1) t_threshold = 0.15           # 0.1 -> 0.15 because of "PropWarn,AudibleFeedback"
                2) added AC100_sig['Bendix_CMS'];  plot_Bendix_CMS() 
   2013-06-07   1) added: AC100_sig['General'], AC100['AEBS_SFN_OUT'], AC100_sig['VBOX_IMU'], 
                2) getIntervalAroundEvent(), calc_signal_valid(), resample() -> separate modules in kbtools
   2013-05-23   signal 'speed_over_ground' is optional because it is no longer on A087MB_V3.2_MH8_truck.dbc
   2013-03-20
   2011-12-16
    
'''

'''
todo
- loading a signal from a device name that has multiple instances
    AC100_sig['VDC2_YAW_Rate_Time'], AC100_sig['VDC2_YAW_Rate_Value'] = kbtools.GetSignal(Source,"VDC2", "YawRate") 
    Multiple device names:
    VDC2                                  VDC2--Message--Knorr_Bremse__CVR3_Prototype_1_0__ACC_J1939
                                          VDC2--Message--Knorr_Bremse__LRR3_ACC_AEBS_MANPrototype_1_1__ACC_J1939
 - ACC track


 J1939
 
 
IMU_Pitch_and_RollRate	Pitch_Rate
IMU_Pitch_and_RollRate	Roll_Rate
IMU_XAccel_and_YawRate	X_Accel
IMU_XAccel_and_YawRate	Yaw_Rate
IMU_YAccel_and_Temp	Temp
IMU_YAccel_and_Temp	Y_Accel
IMU_ZAccel	Blank
IMU_ZAccel	Z_Accel

 
 
                     
'''



# standard Python imports
import pickle
import numpy as np
import pylab as pl
import os
import sys, traceback

# KB specific imports
import kbtools


def is_same(a_nparray, b_nparray):
    # check if two numpy array are the same
    if  a_nparray is b_nparray:
        return True
    if  a_nparray.size == b_nparray.size:
        for k in xrange(a_nparray.size):
            if  not (a_nparray[k] == b_nparray[k]):
                return False
        return True
    return False

def shift_signal(x,shift):
    if x is None:
        return x
    
    if shift is not None:
        if shift > 0:
            x[shift:-1] = x[:(-1-shift)]
            x[:shift] = np.zeros(shift) 
        elif shift < 0:
            x[:shift] = x[-shift:]
            #print x_new[shift:]
            #print np.zeros(-shift) 
            x[shift:] = np.zeros(-shift) 
    return x        
    

#============================================================================================
def GetJ1939Signal(Source,DeviceName,SignalName):
    
    Time, Values = kbtools.GetSignal(Source, DeviceName, SignalName)
    
    if Time is None:
        Prefix = "J1939_"
        Time, Values = kbtools.GetSignal(Source, Prefix+DeviceName, Prefix+SignalName)
    
    return Time, Values


       
# --------------------------------------------------------------------------------------------
class cDataAC100():

  # class variables 
  N_AC100 = 10   # number of AC100 Objects
  
  N_targets_AC100 = 10 # number of AC100 targets
  
  N_FLC20_VideoObj = 10 # number of FLC20 Video objects
  
  # show comment
  verbose = False
  #verbose = True
 
  warnings_off = False  

  # -------------------------------------------------------------------------------------------
  @staticmethod
  def load_AC100_from_Source(Source, PickleFilename=None, InvertAngleSign=False, do_calc_associated_Targets_b=False, warnings_off=True, config=None):
    # load signal from SignalSource
    
    cDataAC100.warnings_off = warnings_off
    
    
    if cDataAC100.verbose:
        print "load_AC100_from_Source()"
    
    # here we want to collect the signals
    AC100_sig = None
    
    if 1:
      # here we load signal to a dict
      AC100_sig = {}
      AC100_sig['SensorType'] = "FLR20"
      AC100_sig['FileName']   = Source.FileName
      try:
          AC100_sig['FileName_org'] = Source.FileName_org
      except:
          AC100_sig['FileName_org'] = ''
      
      
      #-----------------------------------------------------
      # Yaw rate from J1939 
      AC100_sig['VDC2_YAW_Rate_Time'], AC100_sig['VDC2_YAW_Rate_Value'] = kbtools.GetSignal(Source,"VDC2", "YAW_Rate") 
      
      #-----------------------------------------------------
      # Yaw rate, vehicle speed and curvature from AC100
      AC100_sig['cvd_yawrate_Time'], AC100_sig['cvd_yawrate_Value']                           = \
            kbtools.GetSignal(Source,"General_radar_status", "cvd_yawrate")
      AC100_sig['actual_vehicle_speed_Time'], AC100_sig['actual_vehicle_speed_Value']         = \
            kbtools.GetSignal(Source,"General_radar_status","actual_vehicle_speed")
      AC100_sig['estimated_road_curvature_Time'], AC100_sig['estimated_road_curvature_Value'] = \
            kbtools.GetSignal(Source,"General_radar_status","estimated_road_curvature")
      
      #-----------------------------------------------------
      # General Time info
      AC100_sig['Time'] = AC100_sig['cvd_yawrate_Time']
      t_common= AC100_sig['Time']  # common time axis
      t_threshold = 0.15           # 0.1 -> 0.15 because of "PropWarn,AudibleFeedback"
      
      
      if t_common is not None:
          #----------------------------------------------------
          # General_radar_status
          AC100_General = cDataAC100.create_AC100_General_radar_status(Source, t_common,t_threshold)   
       
          # AC100 Targets
          AC100_targets = cDataAC100.create_AC100_targets(Source, t_common,t_threshold, InvertAngleSign)

          # AC100 Tracks
          AC100_tracks = cDataAC100.create_AC100_tracks(Source, t_common, t_threshold, AC100_targets, InvertAngleSign, do_calc_associated_Targets_b = do_calc_associated_Targets_b)
      
          # AC100 Position Matrix
          AC100_PosMatrix = cDataAC100.create_AC100_PosMatrix(t_common, t_threshold, AC100_tracks)
      
      
          # Bendix_CMS 
          Bendix_CMS = cDataAC100.create_Bendix_CMS(Source, t_common, t_threshold)
     
          # Bendix ACC S-messages
          ACC_Sxy = cDataAC100.create_Bendix_ACC_Sxy(Source, t_common, t_threshold)

          # FLC20 camera 
          FLC20 = cDataAC100.create_FLC20(Source, t_common, t_threshold)
      
      else:
          AC100_General      = None  
          AC100_targets      = None
          AC100_tracks       = None
          AC100_PosMatrix    = None
          Bendix_CMS         = None
          J1939              = None
          ACC_Sxy            = None
          FLC20              = None
      
      
      # AC100 AEBS SfN output
      AC100_AEBS_SFN_OUT =  cDataAC100.create_AC100_AEBS_SFN_OUT(Source)
          
      # VBOX_IMU    
      VBOX_IMU  =  cDataAC100.create_VBOX_IMU(Source)
      
      # J1939 Vehicle CAN bus
      J1939 = cDataAC100.create_J1939(Source,config)

      # Multimedia
      Multimedia = cDataAC100.create_Multimedia(Source)
      
      # FLR20_CAN bus  - A087
      FLR20_CAN = cDataAC100.create_FLR20_CAN(Source, InvertAngleSign)
      
      # FLC20 CAN bus
      FLC20_CAN = cDataAC100.create_FLC20_CAN(Source)

      # Bendix ACC S-messages (individual time axes)
      ACC_Sxy2 = cDataAC100.create_Bendix_ACC_Sxy2(Source)

      # Racelogic ADAS Package
      VBOX_LDWS_VCI = cDataAC100.create_VBOX_LDWS_VCI(Source)
       
      # OxTS (Ford)
      OxTS = cDataAC100.create_OxTS(Source)
      
      # register
      # old
      #AC100_sig['AC100_targets'] = AC100_targets
      #AC100_sig['AC100_tracks']  = AC100_tracks
      
      # new
      AC100_sig['General']       = AC100_General
      AC100_sig['Targets']       = AC100_targets
      AC100_sig['Tracks']        = AC100_tracks
      AC100_sig['PosMatrix']     = AC100_PosMatrix
      AC100_sig['AEBS_SFN_OUT']  = AC100_AEBS_SFN_OUT 
      AC100_sig['VBOX_IMU']      = VBOX_IMU 
      AC100_sig['Bendix_CMS']    = Bendix_CMS
      AC100_sig['J1939']         = J1939
      AC100_sig['ACC_Sxy']       = ACC_Sxy
      AC100_sig['ACC_Sxy2']      = ACC_Sxy2
      AC100_sig['FLC20']         = FLC20
      AC100_sig['Multimedia']    = Multimedia
      AC100_sig['FLR20_CAN']     = FLR20_CAN
      AC100_sig['FLC20_CAN']     = FLC20_CAN
      AC100_sig["VBOX_LDWS_VCI"] = VBOX_LDWS_VCI
      AC100_sig["OxTS"]          = OxTS
        
      AC100_sig["Source"]          = Source
 
      
      
    # ------------------------------------------------------
    # save if filename given to a pickle file
    if AC100_sig and PickleFilename:
      output = open(PickleFilename, 'wb')
      pickle.dump(AC100_sig, output,-1)     # -1: using the highest protocol available
      output.close()

    return AC100_sig
    
  #============================================================================================
  @staticmethod
  def load_AC100_from_picklefile(FileName):

    # load ego vehicle data from file (pickle)
    pkl_file = open(FileName, 'rb')
    AC100_sig  = pickle.load(pkl_file)
    pkl_file.close()
    
    return AC100_sig
    
  #============================================================================================
  @staticmethod
  def create_AC100_targets(Source, t_common,t_threshold, InvertAngleSign):
        # AC100 targets ("radar refections")
        #  no available targets are marked as AC100_target[k] = None
        
       
        if cDataAC100.verbose:
            print "create_AC100_targets"
        
        # target_signal_list: [ (short name, device name, signal name incl. %d), ()]
        target_signal_list = [
          ("angle_LSB",                 "Targets", "ta%d_angle_LSB"),
          ("angle_MSB",                 "Targets", "ta%d_angle_MSB"),
          ("relative_velocitiy",        "Targets", "ta%d_relative_velocitiy"),
          ("range",                     "Targets", "ta%d_range"),
          ("power",                     "Targets", "ta%d_power"),
  
          ("target_flags_MSB",          "Targets", "ta%d_target_flags_MSB"),         
          ("target_flags_LSB",          "Targets", "ta%d_target_flags_LSB"),
          
          ("target_status",             "Targets", "ta%d_target_status"),
          ("tracking_flags",            "Targets", "ta%d_tracking_flags"),

          # undocumented
          ("range_flags",               "Targets", "ta%d_range_flags"),
          ("FSK_relative_velocitiy",    "Targets", "ta%d_FSK_relative_velocitiy"),
          ("primary_FSK_range",         "Targets", "ta%d_primary_FSK_range"),
          ("secondary_FSK_range",       "Targets", "ta%d_secondary_FSK_range"),
        
       
          
          ]

        
        # ---------------------------------------------------------------
        # create signal dictionary AC100_targets      
        AC100_targets = {}
 
        for k in xrange(cDataAC100.N_targets_AC100):
            #print k
            AC100_targets[k] = {}
            try:
                # Time
                AC100_targets[k]['Time'] = t_common
                # Signals
                for signal in target_signal_list:
                    #print signal
                    Time, Values = kbtools.GetSignal(Source, signal[1], signal[2]%k)  
                    
                    valid = kbtools.calc_signal_valid(t_common,Time,t_threshold)
                    Values_resampled = kbtools.resample(Time,Values, t_common,'zoh')
                    AC100_targets[k][signal[0]] = Values_resampled*valid
                    AC100_targets[k]['Valid'] = valid
           
                # ----------------------------------------------------------
                # post processing
                
                # angle_MSB, LSB -> angle
                AC100_targets[k]["angle"] = AC100_targets[k]["angle_MSB"]+AC100_targets[k]["angle_LSB"]
         
                # target_flags_MSB, LSB ->  target_flags
                #     target_flags_LSB 5 Bits
                #     target_flags_MSB 2 Bits
                target_flags_MSB = np.logical_and(AC100_targets[k]["target_flags_MSB"], 0x03)*32
                target_flags_LSB = np.logical_and(AC100_targets[k]["target_flags_LSB"], 0x1F)
                AC100_targets[k]["target_flags"] = target_flags_MSB+target_flags_LSB
                    
         
           
            except:
                # no available tracks are marked as AC100_tracks[k] = None
                if cDataAC100.verbose:
                    print "target[%d] skipped"%k  
                AC100_targets[k] = None   # []

        return AC100_targets  

  #============================================================================================
  @staticmethod
  def create_AC100_tracks(Source,t_common,t_threshold, AC100_targets, InvertAngleSign, do_calc_associated_Targets_b = False ):
        # AC100 tracks
        #  no available tracks are marked as AC100_tracks[k] = None
        
        if cDataAC100.verbose:
            print "create_AC100_tracks()"
        
        
        # track_signal_list: [ (short name, device name, signal name incl. %d), ()]
        track_signal_list = [
          # frame 1
          ("credibility",                "Tracks", "tr%d_credibility",                                    True ),
          ("acc_track_info",             "Tracks", "tr%d_acc_track_info",                                 True ),   
          ("vr",                         "Tracks", "tr%d_relative_velocitiy",                             True ),
          ("ds",                         "Tracks", "tr%d_range",                                          True ),
          ("is_video_associated",        "Tracks", "tr%d_is_video_associated",                            True ),
          ("tracking_status",            "Tracks", "tr%d_tracking_status",                                True ),
          ("track_selection_status",     "Tracks", "tr%d_track_selection_status",                         True ),

          # frame 2
          ("CW_track",                   "Tracks", "tr%d_CW_track",                                       True ),
          ("forbidden",                  "Tracks", "tr%d_forbidden",                                      True ),
          ("secondary",                  "Tracks", "tr%d_secondary",                                      True ),
          ("asso_target_index",          "Tracks", "tr%d_asso_target_index",                              True ),
          ("power",                      "Tracks", "tr%d_power",                                          True ),
          ("acceleration_over_ground",   "Tracks", "tr%d_acceleration_over_ground",                       True ),
          ("angle",                      "Tracks", "tr%d_uncorrected_angle",                              True ),
          ("id",                         "Tracks", "tr%d_internal_track_index",                           True ),
          ("corrected_lateral_distance", "Tracks", "tr%d_corrected_lateral_distance",                     True ),

          # frame 3
          ("env_object_ID",              "Tracks", "tr%d_env_object_ID",                                  False ),
          ("is_env_object",              "Tracks", "tr%d_is_env_object",                                  False ),
          ("object_class",               "Tracks", "tr%d_object_class",                                   False ),
          ("width",                      "Tracks", "tr%d_width",                                          False ),
          ("video_confidence",           "Tracks", "tr%d_video_confidence",                               False ),
          ("radar_confidence",           "Tracks", "tr%d_radar_confidence",                               False ),
          ("lateral_position",           "Tracks", "tr%d_lateral_position",                               False ),
          ("asso_video_ID",              "Tracks", "tr%d_asso_video_ID",                                  False ),
     
          ]

        
        
        # ---------------------------------------------------------------
        # create signal dictionary AC100_tracks      
        AC100_tracks = {}
 
        for k in xrange(cDataAC100.N_AC100):
            if cDataAC100.verbose:
                print "track[%d]:"%k  
            
            AC100_tracks[k] = {}
            try: 
                ## ----------------------------------------------------------
                ## Time, Values
                #for signal in track_signal_list:
                #    AC100_tracks[k]['Time'], AC100_tracks[k][signal[0]] = kbtools.GetSignal(Source, signal[1], signal[2]%k)
                        
                # Time
                AC100_tracks[k]['Time'] = t_common
                # Signals
                for signal in track_signal_list:
                    #if cDataAC100.verbose:
                    #    print signal
                        
                    Time, Values = kbtools.GetSignal(Source, signal[1], signal[2]%k)  
                    
                    if Time is not None:
                        valid = kbtools.calc_signal_valid(t_common,Time,t_threshold)
                        Values_resampled = kbtools.resample(Time,Values, t_common,'zoh')
                        AC100_tracks[k][signal[0]] = Values_resampled*valid
                    else:
                        if not cDataAC100.warnings_off:
                            if signal[3]:
                                print "Mandatory signal <%s> is missing" % (signal[2]%k)
                                #raise
                            else:
                                print "Optional signal <%s> is missing" % (signal[2]%k)
                            
                # ----------------------------------------------------------
                # post processing
                if cDataAC100.verbose:
                    print "post processing"
                
                AC100_tracks[k]['corrected_lateral_distance'] = - AC100_tracks[k]['corrected_lateral_distance']
               
                if InvertAngleSign:
                    AC100_tracks[k]['angle'] = -AC100_tracks[k]['angle'] 
                
                
                # ---------------------------------------------------------------------               
                # tracking_status
                # 0 = Track is Empty.
                # 1 = Track is Initialising.
                # 2 = Track is Established.
                # 3 = Track is Sleeping.
                #tracking_status = AC100_tracks[k]['tracking_status']
                
                # ---------------------------------------------------------------------               
                # Track Selection Status
                # Bit 0: Left Lane.
                # Bit 1: Right Lane.
                # Bit 2: In Lane.
                # Bit 3: Same Direction.
                # Bit 4: Stationary.
                # Bit 5: Opposite Direction.
                # Bit 6: SVM mirror suppressed.
                # Bit 7: Overtaken.
                # Bit 8: ACC Track.
                # Bit 9: Out of ACC Lane.
                # Bit 10: Extreme Left.
                # Bit 11: Extreme Right.
                # Bit 12: (reserved).
  
                track_selection_status = AC100_tracks[k]['track_selection_status']
                AC100_tracks[k]['Left_Lane']             = kbtools.GetBitAtPos(track_selection_status,0)   #  Bit 0: Left Lane 
                AC100_tracks[k]['Right_Lane']            = kbtools.GetBitAtPos(track_selection_status,1)   #  Bit 1: Right Lane 
                AC100_tracks[k]['In_Lane']               = kbtools.GetBitAtPos(track_selection_status,2)   #  Bit 2: In Lane
                AC100_tracks[k]['Same_Direction']        = kbtools.GetBitAtPos(track_selection_status,3)   #  Bit 3: Same Direction
                AC100_tracks[k]['Stationary']            = kbtools.GetBitAtPos(track_selection_status,4)   #  Bit 4: Stationary
                AC100_tracks[k]['Opposite_Direction']    = kbtools.GetBitAtPos(track_selection_status,5)   #  Bit 5: Opposite Direction
                AC100_tracks[k]['SVM_mirror_suppressed'] = kbtools.GetBitAtPos(track_selection_status,6)   #  Bit 6: SVM mirror suppressed
                AC100_tracks[k]['Overtaken']             = kbtools.GetBitAtPos(track_selection_status,7)   #  Bit 7: Overtaken
                AC100_tracks[k]['ACC_Track']             = kbtools.GetBitAtPos(track_selection_status,8)   #  Bit 8: ACC Track
                AC100_tracks[k]['Out_of_ACC_Lane']       = kbtools.GetBitAtPos(track_selection_status,9)   #  Bit 9: Out of ACC Lane
                AC100_tracks[k]['Extreme_Left']          = kbtools.GetBitAtPos(track_selection_status,10)  #  Bit 10: Extreme Left
                AC100_tracks[k]['Extreme_Right']         = kbtools.GetBitAtPos(track_selection_status,11)  #  Bit 11: Extreme Right
                
             
                
                
                # downwards compatibility
                AC100_tracks[k]['Stand_b'] =  kbtools.GetBitAtPos(track_selection_status,4)   # Bit4: stationary 
                               
                
                #AC100_tracks[k]['dT']      = np.diff(AC100_tracks[k]['Time']);  AC100_tracks[k]['dT']  = np.hstack((0.0,AC100_tracks[k]['dT']))
                #AC100_tracks[k]['dx']      =  AC100_tracks[k]['ds']*np.cos(AC100_tracks[k]['angle']*(np.pi/180.0))     #orthogonal distance to vehicle (adjacent leg)
                #AC100_tracks[k]['dy']      =  AC100_tracks[k]['ds']*np.sin(AC100_tracks[k]['angle']*(np.pi/180.0))    #offset from vehicle (oposite leg)
                #AC100_tracks[k]['vx']      =  AC100_tracks[k]['vr']*np.cos(AC100_tracks[k]['angle']*(np.pi/180.0))     
                #AC100_tracks[k]['vy']      =  AC100_tracks[k]['vr']*np.sin(AC100_tracks[k]['angle']*(np.pi/180.0))    
          
                AC100_tracks[k]['dx']      =  np.copy(AC100_tracks[k]['ds'])
                AC100_tracks[k]['dy']      =  AC100_tracks[k]['corrected_lateral_distance']
                tmp_angle = np.arctan2(AC100_tracks[k]['dy'], AC100_tracks[k]['ds'] )
                AC100_tracks[k]['vx']      =  AC100_tracks[k]['vr']*np.cos(tmp_angle)     
                AC100_tracks[k]['vy']      =  AC100_tracks[k]['vr']*np.sin(tmp_angle)    
          
          
                # ---------------------------------------------
                # associated Targets
                if cDataAC100.verbose:
                    print "associated Targets"

                do_calc_associated_Targets_b = False    
                if do_calc_associated_Targets_b:
                    AssoTargetAttrList = [
                      ( 'ta_angle',                   "angle" ),
                      ( 'ta_relative_velocitiy',      "relative_velocitiy" ),
                      ( 'ta_range',                   "range" ),
                      ( 'ta_power',                   "power" ),
                                  
                      ]
      
                    for Attr in AssoTargetAttrList:
                        AC100_tracks[k][Attr[0]] =   np.zeros_like(AC100_tracks[k]['Time'])
                
                
                    for TargetIdx in xrange(cDataAC100.N_targets_AC100):
                        mask = np.logical_and(AC100_tracks[k]["asso_target_index"] < 30, AC100_tracks[k]["asso_target_index"] == TargetIdx)
                        for Attr in AssoTargetAttrList:
                            if AC100_targets[TargetIdx][Attr[1]] is not None:
                                temp_signal = kbtools.resample(AC100_targets[TargetIdx]['Time'],AC100_targets[TargetIdx][Attr[1]], AC100_tracks[k]['Time'],'zoh')
                                AC100_tracks[k][Attr[0]][mask] = temp_signal[mask]
                   
           
            except:
                # no available tracks are marked as AC100_tracks[k] = None
                if cDataAC100.verbose:
                    print "track[%d] skipped"%k  
                AC100_tracks[k] = None   # []

        return AC100_tracks  

  #============================================================================================
  @staticmethod
  def create_FLR20_CAN(Source, InvertAngleSign):
        # AC100 tracks
        #  no available tracks are marked as F[k] = None
        
        if cDataAC100.verbose:
            print "create_FLR20_CAN()"
        
        # ---------------------------------------------------------------------------------------
        # track_signal_list: [ (short name, device name, signal name incl. %d), ()]
        track_signal_list = [
          # frame 1
          ("credibility",                "Tracks", "tr%d_credibility",                                    True ),
          ("acc_track_info",             "Tracks", "tr%d_acc_track_info",                                 True ),   
          ("vr",                         "Tracks", "tr%d_relative_velocitiy",                             True ),
          ("ds",                         "Tracks", "tr%d_range",                                          True ),
          ("is_video_associated",        "Tracks", "tr%d_is_video_associated",                            True ),
          ("tracking_status",            "Tracks", "tr%d_tracking_status",                                True ),
          ("track_selection_status",     "Tracks", "tr%d_track_selection_status",                         True ),

          # frame 2
          ("CW_track",                   "Tracks", "tr%d_CW_track",                                       True ),
          ("forbidden",                  "Tracks", "tr%d_forbidden",                                      True ),
          ("secondary",                  "Tracks", "tr%d_secondary",                                      True ),
          ("asso_target_index",          "Tracks", "tr%d_asso_target_index",                              True ),
          ("power",                      "Tracks", "tr%d_power",                                          True ),
          ("acceleration_over_ground",   "Tracks", "tr%d_acceleration_over_ground",                       True ),
          ("angle",                      "Tracks", "tr%d_uncorrected_angle",                              True ),
          ("id",                         "Tracks", "tr%d_internal_track_index",                           True ),
          ("corrected_lateral_distance", "Tracks", "tr%d_corrected_lateral_distance",                     True ),

          # frame 3
          ("env_object_ID",              "Tracks", "tr%d_env_object_ID",                                  False ),
          ("is_env_object",              "Tracks", "tr%d_is_env_object",                                  False ),
          ("object_class",               "Tracks", "tr%d_object_class",                                   False ),
          ("width",                      "Tracks", "tr%d_width",                                          False ),
          ("video_confidence",           "Tracks", "tr%d_video_confidence",                               False ),
          ("radar_confidence",           "Tracks", "tr%d_radar_confidence",                               False ),
          ("lateral_position",           "Tracks", "tr%d_lateral_position",                               False ),
          ("asso_video_ID",              "Tracks", "tr%d_asso_video_ID",                                  False ),
     
          ]

        
        
        # ---------------------------------------------------------------
        # create signal dictionary FLR20_CAN      
        FLR20_CAN = {}
 
        # --------------------------------------------------------------
        # Tracks
        Tracks = {}
        FLR20_CAN['Tracks'] = Tracks
        
        for k in xrange(cDataAC100.N_AC100):
            if cDataAC100.verbose:
                print "track[%d]:"%k  
            
            
            Track = {}
            Tracks[k] = Track
            
            try:       
                for signal in track_signal_list:
                    #if cDataAC100.verbose:
                    #    print signal
                        
                    Track['Time_%s'%signal[0]], Track[signal[0]] = kbtools.GetSignal(Source, signal[1], signal[2]%k)  
                        
                    
                    if Track['Time_%s'%signal[0]] is None:
                        if not cDataAC100.warnings_off:
                            if signal[3]:
                                print "Mandatory signal <%s> is missing" % (signal[2]%k)
                                #raise
                            else:
                                print "Optional signal <%s> is missing" % (signal[2]%k)
                            
                # ----------------------------------------------------------
                # post processing
                if cDataAC100.verbose:
                    print "post processing"
                
                if Track['Time_corrected_lateral_distance'] is not None:
                    Track['corrected_lateral_distance'] = - Track['corrected_lateral_distance']
               
                if InvertAngleSign and (Track['Time_angle'] is not None):
                    Track['angle'] = -Track[k]['angle'] 
                
                
                # ---------------------------------------------------------------------               
                # tracking_status
                # 0 = Track is Empty.
                # 1 = Track is Initialising.
                # 2 = Track is Established.
                # 3 = Track is Sleeping.
                #tracking_status = F[k]['tracking_status']
                
                # ---------------------------------------------------------------------               
                # Track Selection Status
                # Bit 0: Left Lane.
                # Bit 1: Right Lane.
                # Bit 2: In Lane.
                # Bit 3: Same Direction.
                # Bit 4: Stationary.
                # Bit 5: Opposite Direction.
                # Bit 6: SVM mirror suppressed.
                # Bit 7: Overtaken.
                # Bit 8: ACC Track.
                # Bit 9: Out of ACC Lane.
                # Bit 10: Extreme Left.
                # Bit 11: Extreme Right.
                # Bit 12: (reserved).
                
                track_selection_status_list = [ ('Left_Lane',             0),   #  Bit 0: Left Lane 
                                                ('Right_Lane',            1),   #  Bit 1: Right Lane 
                                                ('In_Lane',               2),   #  Bit 2: In Lane
                                                ('Same_Direction',        3),   #  Bit 3: Same Direction
                                                ('Stationary',            4),   #  Bit 4: Stationary
                                                ('Opposite_Direction',    5),   #  Bit 5: Opposite Direction
                                                ('SVM_mirror_suppressed', 6),   #  Bit 6: SVM mirror suppressed
                                                ('Overtaken',             7),   #  Bit 7: Overtaken
                                                ('ACC_Track',             8),   #  Bit 8: ACC Track
                                                ('Out_of_ACC_Lane',       9),   #  Bit 9: Out of ACC Lane
                                                ('Extreme_Left',          10),  #  Bit 10: Extreme Left
                                                ('Extreme_Right',         11),  #  Bit 11: Extreme Right
                                                # downwards compatibility
                                                ('Stand_b',                4),   # Bit4: stationary 
                                             ]
                
                for (key,BitPosition) in track_selection_status_list:
                    if Track['Time_track_selection_status'] is not None:
                        Track['Time_%s'%key]   = Track['Time_track_selection_status']
                        Track[key]             = kbtools.GetBitAtPos(Track['track_selection_status'],BitPosition)
                    else:
                        Track['Time_%s'%key]   = None
                        Track[key]             = None
                                     
                # downwards compatibility
                Track['Time_dx'] =  Track['Time_ds']
                Track['dx']      =  Track['ds']
                
                Track['Time_dy'] =  Track['Time_corrected_lateral_distance']
                Track['dy']      =  Track['corrected_lateral_distance']
               
                             
            except Exception, e:
                print "error - create_FLR20_CAN(): ",e.message
                traceback.print_exc(file=sys.stdout)
                if cDataAC100.verbose:
                    print "track[%d] skipped"%k  
                Track = None   
        # -------------------------------------------------------------------
        # Tracks
        Targets = {}
        FLR20_CAN['Targets'] = Targets

        
        # target_signal_list: [ (short name, device name, signal name incl. %d), ()]
        target_signal_list = [
          ("angle_LSB",                 "Targets", "ta%d_angle_LSB"),
          ("angle_MSB",                 "Targets", "ta%d_angle_MSB"),
          ("relative_velocitiy",        "Targets", "ta%d_relative_velocitiy"),
          ("range",                     "Targets", "ta%d_range"),
          ("power",                     "Targets", "ta%d_power"),
  
          ("target_flags_MSB",          "Targets", "ta%d_target_flags_MSB"),         
          ("target_flags_LSB",          "Targets", "ta%d_target_flags_LSB"),
          
          ("target_status",             "Targets", "ta%d_target_status"),
          ("tracking_flags",            "Targets", "ta%d_tracking_flags"),

          # undocumented
          ("range_flags",               "Targets", "ta%d_range_flags"),
          ("FSK_relative_velocitiy",    "Targets", "ta%d_FSK_relative_velocitiy"),
          ("primary_FSK_range",         "Targets", "ta%d_primary_FSK_range"),
          ("secondary_FSK_range",       "Targets", "ta%d_secondary_FSK_range"),
         
          ]

        
        for k in xrange(cDataAC100.N_targets_AC100):
            
            if cDataAC100.verbose:
                print "target[%d]:"%k  
            
            
            Target = {}
            Targets[k] = Target
            
            try:
                for signal in target_signal_list:
                                      
                    Target['Time_%s'%signal[0]], Target[signal[0]] = kbtools.GetSignal(Source, signal[1], signal[2]%k)  
        
           
                # ----------------------------------------------------------
                # post processing
                
                # angle_MSB, LSB -> angle
                if ("angle_MSB" in Target) and ("angle_LSB" in Target):
                    Target["Time_angle"] = Target["Time_angle_MSB"]
                    Target["angle"] = Target["angle_MSB"]+Target["angle_LSB"]
                else:
                    Target["Time_angle"] = None
                    Target["angle"] = None
         
                # target_flags_MSB, LSB ->  target_flags
                #     target_flags_LSB 5 Bits
                #     target_flags_MSB 2 Bits
                if ("target_flags_MSB" in Target) and ("target_flags_LSB" in Target):
                    target_flags_MSB = np.logical_and(Target["target_flags_MSB"], 0x03)*32
                    target_flags_LSB = np.logical_and(Target["target_flags_LSB"], 0x1F)
                    Target["Time_target_flags"] = Target["Time_target_flags_MSB"]
                    Target["target_flags"] = target_flags_MSB+target_flags_LSB
                else:
                    Target["Time_target_flags"] = None
                    Target["target_flags"] = None
         
            except Exception, e:
                print "error - create_FLR20_CAN() Targets: ",e.message
                traceback.print_exc(file=sys.stdout)
                if cDataAC100.verbose:
                    print "target[%d] skipped"%k  
                Target = None   
            


        # -------------------------------------------------------------------
        if cDataAC100.verbose:
            print "create_FLR20_CAN() - end"


        return FLR20_CAN  


  #============================================================================================
  @staticmethod
  def create_AC100_PosMatrix(t_common, t_threshold, AC100_tracks):


      # ---------------------------------------------------------
      # Position Matrix as special tracks
      PosMatrix={}
      #PosMatrixObjListe = ('CW','ACC')
      PosMatrixObjListe = ('CW',)
      
      # Position Matrix Attribute List
      #  [ (attribute name, track signal name, mandatory),  ...] 
      PosMatrixAttrList = [
            ( 'dx',                   "dx",                           True  ),
            ( 'dy',                   "dy",                           True  ),
            ( 'ds',                   "ds",                           True  ),
            ( 'lateral_position',     "lateral_position",             True  ),         

            ( 'vx',                   "vx",                           True  ),
            ( 'vy',                   "vy",                           True  ), 
            ( 'vr',                   "vr",                           True  ), 
            
            ( 'angle',                "angle",                        True  ),
            ( 'vx_ground',            "speed_over_ground",            False ), 
            ( 'ax_ground',            "acceleration_over_ground",     True  ),
            ( 'Stand_b',              "Stand_b",                      True  ),
            ( 'is_video_associated',  "is_video_associated",          True  ),
          

            ( 'Left_Lane',            "Left_Lane",                    True  ),
            ( 'Right_Lane',           "Right_Lane",                   True  ),
            ( 'In_Lane',              "In_Lane",                      True  ),
            ( 'Extreme_Left',         "Extreme_Left",                 True  ),
            ( 'Extreme_Right',        "Extreme_Right",                True  ),

            ( 'Same_Direction',       "Same_Direction",               True  ),
            ( 'Stationary',           "Stationary",                   True  ),
            ( 'Opposite_Direction',   "Opposite_Direction",           True  ),

            ( 'SVM_mirror_suppressed',"SVM_mirror_suppressed",        True  ),

            ( 'Overtaken',             "Overtaken",                   True  ),
            ( 'ACC_Track',             "ACC_Track",                   True  ),
            ( 'Out_of_ACC_Lane',       "Out_of_ACC_Lane",             True  ),
            
         
            ( 'id',                   "id",                           True  ),
            ( 'asso_target_index',    "asso_target_index",            True  ),
            ( 'asso_video_ID',        "asso_video_ID",                False  ),
            
            
          
            ( 'power',                "power",                        True  ), 
            ( 'video_confidence',     "video_confidence",             False  ),
            ( 'radar_confidence',     "radar_confidence",             False  ),
        ]
          
   
      for ObjName in PosMatrixObjListe:
        if cDataAC100.verbose:
          print "ObjName %s"%ObjName
        
        PosMatrix[ObjName] = {}
        
        
        # initialize attributes
        PosMatrix[ObjName]['Time']    = t_common
     
        PosMatrix[ObjName]['Valid']   = 0.0*np.ones_like(t_common)
        PosMatrix[ObjName]['TrackNo'] = 255.0*np.ones_like(t_common)
        
        for Attr in PosMatrixAttrList:
            PosMatrix[ObjName][Attr[0]] = 0.0*np.ones_like(t_common)
        
        # fill signals       
        for idx in xrange(cDataAC100.N_AC100-1,-1,-1):    # from low to high important AC100 tracks
          if cDataAC100.verbose: 
            print "idx %s"%idx
          
          if AC100_tracks[idx] is not None:
            valid = kbtools.calc_signal_valid(t_common,AC100_tracks[idx]['Time'],t_threshold)
            if "CW"==ObjName:
              CW_track = kbtools.resample(AC100_tracks[idx]['Time'],AC100_tracks[idx]['CW_track'], t_common,'zoh')
              CW_track = CW_track*valid
            
              mask = CW_track > 0.5
               
            PosMatrix[ObjName]['Valid'][mask]      = valid[mask]    
            PosMatrix[ObjName]['TrackNo'][mask]    = idx*np.ones_like(t_common)[mask]
            
            # ------------------------------------------------
            for Attr in PosMatrixAttrList:
                if Attr[1] in AC100_tracks[idx]:
                    temp_signal = kbtools.resample(AC100_tracks[idx]['Time'],AC100_tracks[idx][Attr[1]], t_common,'zoh')
                    PosMatrix[ObjName][Attr[0]][mask]         = temp_signal[mask]
                else:
                    if not cDataAC100.warnings_off:
                        if Attr[2]:
                            print "%s: Mandatory signal <%s> is missing" % (ObjName, Attr[1])
                            #raise
                        else:
                            print "%s: Optional signal <%s> is missing" % (ObjName, Attr[1])
                        
                    
     
      return PosMatrix
      
  #============================================================================================
  @staticmethod
  def create_AC100_AEBS_SFN_OUT(Source):
        ''' deprecated '''
  
  
        # ----------------------------------------------------------------        
        # AEBS 
        #  Source Adress 2A - vehicle J1939 CAN
        #  Source Adress FD - output Autobox
        AEBS_SFN_OUT = {}
        AEBS_SFN_OUT['Time_Warning'],     AEBS_SFN_OUT['Warning']        = kbtools.GetSignal(Source, "PropWarn_2A", "AcousticalWarning_2A") 
        AEBS_SFN_OUT['Time_AccelDemand'], AEBS_SFN_OUT['AccelDemand']    = kbtools.GetSignal(Source, "XBR_2A", "XBR_AccelDemand_2A") 
        AEBS_SFN_OUT['Time_ABESState'],   AEBS_SFN_OUT['ABESState']      = kbtools.GetSignal(Source, "AEBS1_2A", "AEBSState_2A") 
        AEBS_SFN_OUT['Time_CollisionWarningLevel'],  AEBS_SFN_OUT['CollisionWarningLevel']      = kbtools.GetSignal(Source, "AEBS1_2A", "CollisionWarningLevel_2A") 
       
        # new dbc style
        if AEBS_SFN_OUT['Time_ABESState'] is None: 
            AEBS_SFN_OUT['Time_ABESState'],  AEBS_SFN_OUT['ABESState'] = kbtools.GetSignal(Source, "AEBS1_2A", "AEBS1_AEBSState_2A") 
        if AEBS_SFN_OUT['Time_CollisionWarningLevel'] is None: 
            AEBS_SFN_OUT['Time_CollisionWarningLevel'],  AEBS_SFN_OUT['CollisionWarningLevel'] = kbtools.GetSignal(Source, "AEBS1_2A", "AEBS1_ColisionWarningLevel_2A") 
        if AEBS_SFN_OUT['Time_CollisionWarningLevel'] is None: 
            AEBS_SFN_OUT['Time_CollisionWarningLevel'],  AEBS_SFN_OUT['CollisionWarningLevel'] = kbtools.GetSignal(Source, "AEBS1_2A", "AEBS1_CollisionWarningLevel_2A") 

        if AEBS_SFN_OUT['Time_AccelDemand'] is None: 
            AEBS_SFN_OUT['Time_AccelDemand'],  AEBS_SFN_OUT['AccelDemand'] = kbtools.GetSignal(Source, "XBR_2A", "XBR_ExtAccelDem_2A") 
      
        # Bugfix ABESState -> AEBSState
        if "ABESState" in AEBS_SFN_OUT:
            AEBS_SFN_OUT["Time_AEBSState"] = AEBS_SFN_OUT["Time_ABESState"]
            AEBS_SFN_OUT["AEBSState"]      = AEBS_SFN_OUT["ABESState"]
      
        AEBS_SFN_OUT['Time_RelevantObjectDetected'],  AEBS_SFN_OUT['RelevantObjectDetected'] = kbtools.GetSignal(Source, "AEBS1_2A", "AEBS1_RelevantObjectDetected_2A") 
       
        # TSC1
        AEBS_SFN_OUT['Time_OverrideControlMode'],  AEBS_SFN_OUT['OverrideControlMode'] = kbtools.GetSignal(Source, "TSC1_2A_00", "TSC1_OverrideControlMode_2A_00") 
        AEBS_SFN_OUT['Time_ReqTorqueLimit'],  AEBS_SFN_OUT['ReqTorqueLimit'] = kbtools.GetSignal(Source, "TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00") 

       
        #----------------------       
        if AEBS_SFN_OUT['Time_Warning'] is None:
            if AEBS_SFN_OUT['Time_CollisionWarningLevel'] is not None:
                AEBS_SFN_OUT['Time_Warning'] = AEBS_SFN_OUT['Time_CollisionWarningLevel']
                AEBS_SFN_OUT['Warning'] = AEBS_SFN_OUT['CollisionWarningLevel']>0
        
        if AEBS_SFN_OUT['Time_AccelDemand'] is None:
            AEBS_SFN_OUT['Time_AccelDemand'], AEBS_SFN_OUT['AccelDemand']    = kbtools.GetSignal(Source, "XBR_2A", "XBR_ExtAccelDem_2A") 
        
        
        
        AEBS_SFN_OUT['Time_Warning_Autobox'],     AEBS_SFN_OUT['Warning_Autobox']        = kbtools.GetSignal(Source, "PropWarn_FD", "AcousticalWarning_FD") 
        AEBS_SFN_OUT['Time_AccelDemand_Autobox'], AEBS_SFN_OUT['AccelDemand_Autobox']    = kbtools.GetSignal(Source, "XBR_FD", "XBRUS_AccelDemand_FD") 
        AEBS_SFN_OUT['Time_ABESState_Autobox'],   AEBS_SFN_OUT['ABESState_Autobox']      = kbtools.GetSignal(Source, "AEBS1_FD", "AEBSState_FD") 
           
        return AEBS_SFN_OUT
        
        
        
        # ----------------------------------------------------------------        
        # XBR
        
        # ???
        #FLR20_sig["Time_XBRAccDemand"],FLR20_sig["XBRAccDemand"] = kbtools.GetSignal(Source, "XBR", "ExtAccelerationDemand")

        # MAN 
        #FLR20_sig["Time_XBRAccDemand"],FLR20_sig["XBRAccDemand"] = kbtools.GetSignal(Source, "XBR", "Ext_Acceleration_Demand")
        
        # Bendix
        #FLR20_sig["Time_XBRAccDemand"],FLR20_sig["XBRAccDemand"] = kbtools.GetSignal(Source, "XBRUS_2A", "XBRUS_AccelDemand_2A")
        
        # Ford 
        #FLR20_sig["Time_XBRAccDemand"],FLR20_sig["XBRAccDemand"] = kbtools.GetSignal(Source, "XBR", "ExtlAccelerationDemand")

  #============================================================================================
  @staticmethod
  def create_VBOX_IMU(Source):
        
        VBOX_IMU = {}        
        # ----------------------------------------------------------------        
        # longitudinal acceleration
        VBOX_IMU["Time_IMU_X_Acc"],VBOX_IMU["IMU_X_Acc"]       = kbtools.GetSignal(Source, "IMU_XAccel_and_YawRate", "X_Accel")
        VBOX_IMU["Time_Longitudinal_acceleration"],VBOX_IMU["Longitudinal_acceleration"]       = kbtools.GetSignal(Source, "VBOX_4", "Longitudinal_acceleration")

        # vehicle speed        
        VBOX_IMU["Time_Velocity_kmh"],VBOX_IMU["Velocity_kmh"] = kbtools.GetSignal(Source, "VBOX_2", "Velocity_kmh")

        # target object attributes
        VBOX_IMU["Time_Range_tg1"], VBOX_IMU["Range_tg1"]  = kbtools.GetSignal(Source, "ADAS_VCI_T1_1", "Range_tg1")   # "Metres"
        VBOX_IMU["Time_RelSpd_tg1"],VBOX_IMU["RelSpd_tg1"] = kbtools.GetSignal(Source, "ADAS_VCI_T1_1", "RelSpd_tg1")  # "km/h"
        VBOX_IMU["Time_Accel_tg1"], VBOX_IMU["Accel_tg1"]  = kbtools.GetSignal(Source, "ADAS_VCI_T1_8", "Accel_tg1")   # "g"
                     
        return VBOX_IMU
        
  #============================================================================================
  @staticmethod
  def create_J1939(Source,config=None):
        '''
           todo: error state; signal not available 
        '''
  
        # configuration parameters 
        if config is None:
            config = {}
            config["J1939_AEBS_SourceAddress"] = int("0x2A",16)
        J1939_AEBS_SourceAddress = config["J1939_AEBS_SourceAddress"]
      
        print "create_J1939(): "
        print "  J1939_AEBS_SourceAddress = 0x%X"%J1939_AEBS_SourceAddress
      
        # output
        J1939 = {}        
  
        # ----------------------------------------------------------------        
        # turn signals  "TurnSigSw"
        # OEL_TurnSigSw_21
        #   0x0 NoTurnbeingSignaled
        #   0x1 LeftTurnSignalFlashing
        #   0x2 RightTurnSignalFlashing
        #   0xE Error
        #   0xF Not Available
        
        # Ford - SA 21
        J1939["Time_TurnSigSw"],J1939["TurnSigSw"] = GetJ1939Signal(Source, "OEL_21", "OEL_TurnSigSw_21")
        
        #print 'J1939["Time_TurnSigSw"],J1939["TurnSigSw"]', J1939["Time_TurnSigSw"],J1939["TurnSigSw"]
        
        if J1939["Time_TurnSigSw"] is None:
            # Karsan - SA E8 (wrongly implementation)
            J1939["Time_TurnSigSw"],J1939["TurnSigSw"] = GetJ1939Signal(Source, "OEL_E8", "OEL_TurnSigSw_E8")
            
            
        if J1939["Time_TurnSigSw"] is None:
            # Hyundai Bus - SA E6
            J1939["Time_TurnSigSw"],J1939["TurnSigSw"] = GetJ1939Signal(Source, "OEL_E6", "OEL_TurnSigSw_E6")

        if J1939["Time_TurnSigSw"] is None:
            # Karsan MPXL - SA 30
            J1939["Time_TurnSigSw"],J1939["TurnSigSw"] = GetJ1939Signal(Source, "OEL_30", "OEL_TurnSigSw_30")

        if J1939["Time_TurnSigSw"] is None:
            # Dennis Eagle - SA FC  (Emulator)
            J1939["Time_TurnSigSw"],J1939["TurnSigSw"] = GetJ1939Signal(Source, "OEL_FC", "OEL_TurnSigSw_FC")

        if J1939["Time_TurnSigSw"] is None:
            # Dennis Eagle - SA 17  
            J1939["Time_TurnSigSw"],J1939["TurnSigSw"] = GetJ1939Signal(Source, "OEL_17", "OEL_TurnSigSw_17")

        #print 'J1939["Time_TurnSigSw"],J1939["TurnSigSw"]', J1939["Time_TurnSigSw"],J1939["TurnSigSw"]
        
        # DirIndL_b, DirIndR_b
        J1939["Time_DirIndL_b"] = J1939["Time_TurnSigSw"]
        J1939["DirIndL_b"] = None
        J1939["Time_DirIndR_b"] = J1939["Time_TurnSigSw"]
        J1939["DirIndR_b"] = None

        if J1939["Time_TurnSigSw"] is not None:
            J1939["DirIndL_b"] = J1939["TurnSigSw"] == 1.0
            J1939["DirIndR_b"] = J1939["TurnSigSw"] == 2.0
 
        # OEL_HazardLightSw
        J1939["Time_HazardLightSw"],J1939["HazardLightSw"] = GetJ1939Signal(Source, "OEL_21", "OEL_HazardLightSw_21")
        if J1939["Time_HazardLightSw"] is None:
            J1939["Time_HazardLightSw"],J1939["HazardLightSw"] = GetJ1939Signal(Source, "OEL_E8", "OEL_HazardLightSw_E8")
        if J1939["Time_HazardLightSw"] is None:
            # Dennis Eagle - SA 17 
            J1939["Time_HazardLightSw"],J1939["HazardLightSw"] = GetJ1939Signal(Source, "OEL_17", "OEL_HazardLightSw_17")

        # OEL_HighBeamStat
        J1939["Time_HighBeamStat"],J1939["HighBeamStat"] = GetJ1939Signal(Source, "OEL_21", "OEL_HighBeamStat_21")
        if J1939["Time_HighBeamStat"] is None:
            J1939["Time_HighBeamStat"],J1939["HighBeamStat"] = GetJ1939Signal(Source, "OEL_E8", "OEL_HighBeamStat_E8")
        if J1939["Time_HighBeamStat"] is None:
            # Dennis Eagle - SA 17 
            J1939["Time_HighBeamStat"],J1939["HighBeamStat"] = GetJ1939Signal(Source, "OEL_17", "OEL_HighBeamStat_17")
 
        # OEL_WiperActive
        J1939["Time_WiperActive"],J1939["WiperActive"] = GetJ1939Signal(Source, "OEL_21", "OEL_WiperActive_21")
        if J1939["Time_WiperActive"] is None:
            J1939["Time_WiperActive"],J1939["WiperActive"] = GetJ1939Signal(Source, "OEL_E8", "OEL_WiperActive_E8")
        if J1939["Time_WiperActive"] is None:
            # Dennis Eagle - SA 17 
            J1939["Time_WiperActive"],J1939["WiperActive"] = GetJ1939Signal(Source, "OEL_17", "OEL_WiperActive_17")
     
 
        # ----------------------------------------------------------------        
        # VDC2
        J1939["Time_LatAccel"],J1939["LatAccel"]               = GetJ1939Signal(Source, "VDC2_0B", "VDC2_LatAccel_0B")
        J1939["Time_YawRate"],J1939["YawRate"]                 = GetJ1939Signal(Source, "VDC2_0B", "VDC2_YawRate_0B")
        J1939["Time_SteerWhlAngle"],J1939["SteerWhlAngle"]     = GetJ1939Signal(Source, "VDC2_0B", "VDC2_SteerWhlAngle_0B")
        J1939["Time_SteerWhlTurnCnt"],J1939["SteerWhlTurnCnt"] = GetJ1939Signal(Source, "VDC2_0B", "VDC2_SteerWhlTurnCnt_0B")

        # ----------------------------------------------------------------        
        # VDHR_HRTotVehDist_EE - milage
        J1939["Time_HRTotVehDist"],J1939["HRTotVehDist"]       = GetJ1939Signal(Source, "VDHR_EE", "VDHR_HRTotVehDist_EE")
        J1939["Time_TotVehDist"],J1939["TotVehDist"]           = GetJ1939Signal(Source, "VD_00", "VD_TotVehDist_00")
          
        if J1939["Time_HRTotVehDist"] is None:
            J1939["Time_HRTotVehDist"],J1939["HRTotVehDist"]   = GetJ1939Signal(Source, "t_VDHR_sEE", "HghRslutionTotalVehicleDistance_sEE")
          
        # ----------------------------------------------------------------        
        # Vehicle Speed
        
        # EBC2 - MeanSpdFA
        J1939["Time_MeanSpdFA"],J1939["MeanSpdFA"]               = GetJ1939Signal(Source, "EBC2_0B", "EBC2_MeanSpdFA_0B")  #km/h

        if J1939["Time_MeanSpdFA"] is None:
            J1939["Time_MeanSpdFA"],J1939["MeanSpdFA"]           = GetJ1939Signal(Source, "t_EBC2_s0B", "FrontAxleSpeed_s0B")  #km/h


        # TCO1 - VehSpd
        J1939["Time_VehSpd"],J1939["VehSpd"]                     = GetJ1939Signal(Source, "TCO1_EE", "TCO1_VehSpd_EE")   # km/h
        if J1939["Time_VehSpd"] is None:
            J1939["Time_VehSpd"],J1939["VehSpd"]                 = GetJ1939Signal(Source, "t_TCO1_sEE", "TachographVehicleSpeed_sEE")   # km/h
        
        # CCVS1 - WheelbasedVehSpd
        J1939["Time_WheelbasedVehSpd"],J1939["WheelbasedVehSpd"] = GetJ1939Signal(Source, "CCVS1_00", "CCVS_WheelbasedVehSpd_00")   # km/h
        if J1939["Time_WheelbasedVehSpd"] is None:
            J1939["Time_WheelbasedVehSpd"],J1939["WheelbasedVehSpd"] = GetJ1939Signal(Source, "t_CCVS_s00", "WheelBasedVehicleSpeed_s00")   # km/h 
                

        # ----------------------------------------------------------------        
        # AEBS1 - SA  2A
        J1939["Time_BendOffProbability"],    J1939["BendOffProbability"]     = GetJ1939Signal(Source, "AEBS1_2A", "AEBS1_BendOffProbability_2A")
        J1939["Time_TimeToCollision"],       J1939["TimeToCollision"]        = GetJ1939Signal(Source, "AEBS1_2A", "AEBS1_TimeToCollision_2A")
        J1939["Time_RelevantObjectDetected"],J1939["RelevantObjectDetected"] = GetJ1939Signal(Source, "AEBS1_2A", "AEBS1_RelevantObjectDetected_2A")
        J1939["Time_CollisionWarningLevel"], J1939["CollisionWarningLevel"]  = GetJ1939Signal(Source, "AEBS1_2A", "AEBS1_CollisionWarningLevel_2A")
        J1939["Time_AEBSState"],             J1939["AEBSState"]              = GetJ1939Signal(Source, "AEBS1_2A", "AEBS1_AEBSState_2A")

        J1939["Time_AEBSState_s2A"],         J1939["AEBSState_s2A"]          = GetJ1939Signal(Source, "t_AEBS1_s2A", "AEBSState_s2A")
        J1939["Time_AEBSState_sA0"],         J1939["AEBSState_sA0"]          = GetJ1939Signal(Source, "t_AEBS1_sA0", "AEBSState_sA0")
  
        if J1939["Time_AEBSState"] is None:
            if J1939_AEBS_SourceAddress == int("0x2A",16):
                J1939["Time_AEBSState"] = J1939["Time_AEBSState_s2A"]
                J1939["AEBSState"]      = J1939["AEBSState_s2A"] 
            if J1939_AEBS_SourceAddress == int("0xA0",16):
                J1939["Time_AEBSState"] = J1939["Time_AEBSState_sA0"]
                J1939["AEBSState"]      = J1939["AEBSState_sA0"] 
        
        # MAN_ACCsens_Sensor_CAN.dbc
        if J1939["Time_AEBSState"] is None:
            J1939["Time_AEBSState"], J1939["AEBSState"]          = GetJ1939Signal(Source, "AEBS1_BASE", "advancedEmgcyBrakingSysState_BASE")
        
        # ----------------------------------------------------------------        
        # TSC1 - SA  2A
        J1939["Time_TSC1_MsgCounter"],          J1939["TSC1_MsgCounter"]          = GetJ1939Signal(Source, "TSC1_2A_00", "TSC1_MsgCounter_2A")
        J1939["Time_TSC1_Msg_Checksum"],        J1939["TSC1_Msg_Checksum"]        = GetJ1939Signal(Source, "TSC1_2A_00", "TSC1_Msg_Checksum_2A")
        J1939["Time_TSC1_EngineReqTorqueHR"],   J1939["TSC1_EngineReqTorqueHR"]   = GetJ1939Signal(Source, "TSC1_2A_00", "TSC1_EngineReqTorqueHR_2A")
        J1939["Time_TSC1_ControlPurpose"],      J1939["TSC1_ControlPurpose"]      = GetJ1939Signal(Source, "TSC1_2A_00", "TSC1_ControlPurpose_2A_00")
        J1939["Time_TSC1_ReqTorqueLimit"],      J1939["TSC1_ReqTorqueLimit"]      = GetJ1939Signal(Source, "TSC1_2A_00", "TSC1_ReqTorqueLimit_2A_00")
        J1939["Time_TSC1_Priority"],            J1939["TSC1_Priority"]            = GetJ1939Signal(Source, "TSC1_2A_00", "TSC1_Priority_2A_00")
        J1939["Time_TSC1_OverrideControlMode"], J1939["TSC1_OverrideControlMode"] = GetJ1939Signal(Source, "TSC1_2A_00", "TSC1_OverrideControlMode_2A_00")

        # ----------------------------------------------------------------        
        # XBR - SA  2A
        J1939["Time_XBR_ExtAccelDem"], J1939["XBR_ExtAccelDem"] = GetJ1939Signal(Source, "XBR_2A", "XBR_ExtAccelDem_2A")
        J1939["Time_XBR_EBIMode"],     J1939["XBR_EBIMode"]     = GetJ1939Signal(Source, "XBR_2A", "XBR_EBIMode_2A")
        J1939["Time_XBR_Prio"],        J1939["XBR_Prio"]        = GetJ1939Signal(Source, "XBR_2A", "XBR_Prio_2A")
        J1939["Time_XBR_CtrlMode"],    J1939["XBR_CtrlMode"]    = GetJ1939Signal(Source, "XBR_2A", "XBR_CtrlMode_2A")
        J1939["Time_XBR_Urgency"],     J1939["XBR_Urgency"]     = GetJ1939Signal(Source, "XBR_2A", "XBR_Urgency_2A")
        J1939["Time_XBR_MsgCnt"],      J1939["XBR_MsgCnt"]      = GetJ1939Signal(Source, "XBR_2A", "XBR_MsgCnt_2A")
        J1939["Time_XBR_MsgChksum"],   J1939["XBR_MsgChksum"]   = GetJ1939Signal(Source, "XBR_2A", "XBR_MsgChksum_2A")

        # ------------------------------------------------
        # XBR_2A (KB AEBS/ACC, Wabco ACC)  (j1939_extension_new.dbc) t_J1939_XBR_d0B_s2A
        J1939["Time_XBR_d0B_s2A"], J1939["ExtlAccelerationDemand_d0B_s2A"] = GetJ1939Signal(Source, "t_XBR_d0B_s2A", "ExtlAccelerationDemand_d0B_s2A")
        _, J1939["XBREBIMode_d0B_s2A"]                          = GetJ1939Signal(Source, "t_XBR_d0B_s2A", "XBREBIMode_d0B_s2A")
        _, J1939["XBRPriority_d0B_s2A"]                         = GetJ1939Signal(Source, "t_XBR_d0B_s2A", "XBRPriority_d0B_s2A")
        _, J1939["XBRCtrlMode_d0B_s2A"]                         = GetJ1939Signal(Source, "t_XBR_d0B_s2A", "XBRCtrlMode_d0B_s2A")
        _, J1939["XBRUrgency_d0B_s2A"]                          = GetJ1939Signal(Source, "t_XBR_d0B_s2A", "XBRUrgency_d0B_s2A")
        _, J1939["XBRMessageCounter_d0B_s2A"]                   = GetJ1939Signal(Source, "t_XBR_d0B_s2A", "XBRMessageCounter_d0B_s2A")
        _, J1939["XBRMessageChecksum_d0B_s2A"]                  = GetJ1939Signal(Source, "t_XBR_d0B_s2A", "XBRMessageChecksum_d0B_s2A")
        
        # ------------------------------------------------
        # XBR_A0 (Wabco AEBS)  (j1939_extension_new.dbc) t_XBR_d0B_sA0
        J1939["Time_XBR_d0B_sA0"], J1939["ExtlAccelerationDemand_d0B_sA0"] = GetJ1939Signal(Source, "t_XBR_d0B_sA0", "ExtlAccelerationDemand_d0B_sA0")
        _, J1939["XBREBIMode_d0B_sA0"]                          = GetJ1939Signal(Source, "t_XBR_d0B_sA0", "XBREBIMode_d0B_sA0")
        _, J1939["XBRPriority_d0B_sA0"]                         = GetJ1939Signal(Source, "t_XBR_d0B_sA0", "XBRPriority_d0B_sA0")
        _, J1939["XBRCtrlMode_d0B_sA0"]                         = GetJ1939Signal(Source, "t_XBR_d0B_sA0", "XBRCtrlMode_d0B_sA0")
        _, J1939["XBRUrgency_d0B_sA0"]                          = GetJ1939Signal(Source, "t_XBR_d0B_sA0", "XBRUrgency_d0B_sA0")
        _, J1939["XBRMessageCounter_d0B_sA0"]                   = GetJ1939Signal(Source, "t_XBR_d0B_sA0", "XBRMessageCounter_d0B_sA0")
        _, J1939["XBRMessageChecksum__d0BsA0"]                  = GetJ1939Signal(Source, "t_XBR_d0B_sA0", "XBRMessageChecksum_d0B_sA0")
    
        J1939["XBR_ExtAccelDem_SA"] = None
        if J1939["Time_XBR_ExtAccelDem"] is None:
            if J1939_AEBS_SourceAddress == int("0x2A",16):
                J1939["Time_XBR_ExtAccelDem"]    = J1939["Time_XBR_d0B_s2A"]
                J1939["XBR_ExtAccelDem"]         = J1939["ExtlAccelerationDemand_d0B_s2A"]
                J1939["XBR_ExtAccelDem_SA"]      = int("0x2A",16)
            if J1939_AEBS_SourceAddress == int("0xA0",16):
                J1939["Time_XBR_ExtAccelDem"]    = J1939["Time_XBR_d0B_sA0"]
                J1939["XBR_ExtAccelDem"]         = J1939["ExtlAccelerationDemand_d0B_sA0"]
                J1939["XBR_ExtAccelDem_SA"]      = int("0xA0",16)
           
        #print "J1939['Time_XBR_ExtAccelDem']", J1939["Time_XBR_ExtAccelDem"]  
        #print "J1939['XBR_ExtAccelDem']", J1939["XBR_ExtAccelDem"]         
        #print "J1939['XBR_ExtAccelDem_SA']", J1939["XBR_ExtAccelDem_SA"] 
        
        
        
        
        # ----------------------------------------------------------------        
        # "DriverActDemand" AEBS Main Switch -> AEBS2
        
        # Ford - SA 21
        J1939["Time_DriverActDemand"],J1939["DriverActDemand"] = GetJ1939Signal(Source, "AEBS2_21", "AEBS2_DriverActDemand_21")
        if J1939["Time_DriverActDemand"] is None:
            # Karsan MPXL - SA 30
            J1939["Time_DriverActDemand"],J1939["DriverActDemand"] = GetJ1939Signal(Source, "AEBS2_30", "AEBS2_DriverActDemand_30")
        if J1939["Time_DriverActDemand"] is None:
            # HMC - SA E6
            J1939["Time_DriverActDemand"],J1939["DriverActDemand"] = GetJ1939Signal(Source, "AEBS2_E6", "AEBS2_DriverActDemand_E6")
        if J1939["Time_DriverActDemand"] is None:
            # Dennis Eagle - SA 17
            J1939["Time_DriverActDemand"],J1939["DriverActDemand"] = GetJ1939Signal(Source, "AEBS2_17", "AEBS2_DriverActDemand_17")
            
        # ----------------------------------------------------------------        
        # "LDW_EnableCommand" LDWS Main Switch -> FLIC
        
        # Ford - SA 21
        J1939["Time_LDW_EnableCommand"],J1939["LDW_EnableCommand"] = GetJ1939Signal(Source, "FLIC_21", "FLIC_LDW_EnableCommand_21")
        if J1939["Time_LDW_EnableCommand"] is None:
            # HMC - SA E6
            J1939["Time_LDW_EnableCommand"],J1939["LDW_EnableCommand"] = GetJ1939Signal(Source, "FLIC_E6", "FLIC_LDW_EnableCommand_E6")
        if J1939["Time_LDW_EnableCommand"] is None:
            # Dennis Eagle - SA 17
            J1939["Time_LDW_EnableCommand"],J1939["LDW_EnableCommand"] = GetJ1939Signal(Source, "FLIC_17", "FLIC_LDW_EnableCommand_17")
            
        # ----------------------------------------------------------------        
        # "FLIC_LDW_Buzzer" Buzzer State -> FLIC only Ford !!!
        # 3 "Not available" 2 "Error" 1 "Fully operational" 0 "Not operational" 
        # Ford - SA 21 
        J1939["Time_LDW_Buzzer"],J1939["LDW_Buzzer"] = GetJ1939Signal(Source, "FLIC_21", "FLIC_LDW_Buzzer_21")
        if J1939["Time_LDW_Buzzer"] is None:
            # Dennis Eagle - SA 17
            J1939["Time_LDW_Buzzer"],J1939["LDW_Buzzer"] = GetJ1939Signal(Source, "FLIC_17", "FLIC_LDW_Buzzer_17")
  
            
        # ----------------------------------------------------------------        
        # EEC2 APkickdwnSw
        J1939["Time_APkickdwnSw"],J1939["APkickdwnSw"] = GetJ1939Signal(Source, "EEC2_00", "EEC2_APkickdwnSw_00")
        
        
        # ----------------------------------------------------------------        
        # Reverse Gear -> ETC2 and TC1
        
        # ETC2
        J1939["Time_SelectGear"],J1939["SelectGear"]   = GetJ1939Signal(Source, "ETC2_03", "ETC2_SelectGear_03")
        J1939["Time_CurrentGear"],J1939["CurrentGear"] = GetJ1939Signal(Source, "ETC2_03", "ETC2_CurrentGear_03")

        # TC1
        J1939["Time_RqGear"],J1939["RqGear"] = GetJ1939Signal(Source, "TC1_21", "TC1_RqGear_21")
        
        # calculate signal "ReverseGearDetected"
        J1939["Time_ReverseGearDetected"] = None
        J1939["ReverseGearDetected"] = None
        
        if J1939["Time_CurrentGear"] is not None:
            J1939["Time_ReverseGearDetected"] = J1939["Time_CurrentGear"]
            J1939["ReverseGearDetected"] = J1939["CurrentGear"]<0            # negative means reverse
        elif  J1939["Time_RqGear"] is not None:
            # Not in reverse gear 0x00
            # Gear in reverse position 0xDF
            J1939["Time_ReverseGearDetected"] = J1939["Time_RqGear"]
            J1939["ReverseGearDetected"] = J1939["RqGear"] == 0xDF
        

        
        
        # ----------------------------------------------------------------        
        # longitudinal acceleration
        J1939["Time_BrakePedalPos"],J1939["BrakePedalPos"]         = GetJ1939Signal(Source, "EBC1", "BrakePedalPos")
        J1939["Time_EBSBrakeSwitch"],J1939["EBSBrakeSwitch"]       = GetJ1939Signal(Source, "EBC1", "EBSBrakeSwitch")
        J1939["Time_AccelPedalPos1"],J1939["AccelPedalPos1"]       = GetJ1939Signal(Source, "EEC2", "AccelPedalPos1")


        # signal names used by Bendix
        if J1939["Time_BrakePedalPos"] is None:
            J1939["Time_BrakePedalPos"],J1939["BrakePedalPos"]         = GetJ1939Signal(Source, "EBC1_0B", "EBC1_BrkPedPos_0B")
        if J1939["Time_EBSBrakeSwitch"] is None:
            J1939["Time_EBSBrakeSwitch"],J1939["EBSBrakeSwitch"]       = GetJ1939Signal(Source, "EBC1_0B", "EBC1_EBSBrkSw_0B")
        if J1939["Time_AccelPedalPos1"] is None:
            J1939["Time_AccelPedalPos1"],J1939["AccelPedalPos1"]       = GetJ1939Signal(Source, "EEC2_00", "EEC2_APPos1_00")

        # new  Lommel cw49   
        if J1939["Time_BrakePedalPos"] is None:
            J1939["Time_BrakePedalPos"],J1939["BrakePedalPos"]         = GetJ1939Signal(Source, "EBC1_0B-Brakes_System_Controller_0B", "EBC1_BrkPedPos_0B")
        if J1939["Time_EBSBrakeSwitch"] is None:
            J1939["Time_EBSBrakeSwitch"],J1939["EBSBrakeSwitch"]       = GetJ1939Signal(Source, "EBC1_0B-Brakes_System_Controller_0B", "EBC1_EBSBrkSw_0B")
        if J1939["Time_AccelPedalPos1"] is None:
            J1939["Time_AccelPedalPos1"],J1939["AccelPedalPos1"]       = GetJ1939Signal(Source, "EEC2_00-Engine_Controller_00", "EEC2_APPos1_00")
        
        # ------------------------------------------------
        # FLI1 - Lane Departure Warning
        J1939["Time_LaneDepartImminentRight"],J1939["LaneDepartImminentRight"] = GetJ1939Signal(Source, "FLI1_E8", "FLI1_LaneDepartImminentRight_E8")
        J1939["Time_LaneDepartImminentLeft"],J1939["LaneDepartImminentLeft"]   = GetJ1939Signal(Source, "FLI1_E8", "FLI1_LaneDepartImminentLeft_E8")
       
        J1939["Time_AcousticalWarningRight"],J1939["AcousticalWarningRight"]   = GetJ1939Signal(Source, "FLI1_E8", "FLI1_AcousticalWarningRight_E8")
        J1939["Time_AcousticalWarningLeft"],J1939["AcousticalWarningLeft"]     = GetJ1939Signal(Source, "FLI1_E8", "FLI1_AcousticalWarningLeft_E8")
       
        J1939["Time_OpticalWarningRight"],J1939["OpticalWarningRight"]         = GetJ1939Signal(Source, "FLI1_E8", "FLI1_OpticalWarningRight_E8")
        J1939["Time_OpticalWarningLeft"],J1939["OpticalWarningLeft"]           = GetJ1939Signal(Source, "FLI1_E8", "FLI1_OpticalWarningLeft_E8")
        
        # ------------------------------------------------
        # FLI2
        
        # FLI2 - StateOfLDWS 
        J1939["Time_StateOfLDWS"],J1939["StateOfLDWS"]           = GetJ1939Signal(Source, "FLI2_E8", "FLI2_StateOfLDWS")
        
        # FLI2 - LineType Right, Left
        J1939["Time_LineTypeRight"],J1939["LineTypeRight"]       = GetJ1939Signal(Source, "FLI2_E8", "FLI2_LineTypeRight")
        J1939["Time_LineTypeLeft"],J1939["LineTypeLeft"]         = GetJ1939Signal(Source, "FLI2_E8", "FLI2_LineTypeLeft")
        
        # FLI2 - Tracking Status Right, Left
        J1939["Time_LaneTrackingStatusRight"],J1939["LaneTrackingStatusRight"] = GetJ1939Signal(Source, "FLI2_E8", "FLI2_LaneTrackingStatusRight")
        J1939["Time_LaneTrackingStatusLeft"],J1939["LaneTrackingStatusLeft"]   = GetJ1939Signal(Source, "FLI2_E8", "FLI2_LaneTrackingStatusLeft")

        # FLI2_LaneDepartIndicationEnStat
        J1939["Time_LaneDepartIndicationEnStat"],J1939["LaneDepartIndicationEnStat"] = GetJ1939Signal(Source, "FLI2_E8", "FLI2_LaneDepartIndicationEnStat")

        # FLI2_CameraStatus
        J1939["Time_CameraStatus"],J1939["CameraStatus"]         = GetJ1939Signal(Source, "FLI2_E8", "FLI2_CameraStatus")
        
        
        # ------------------------------------------------
        # EEC1
        
        # EEC1 - EngSpd
        J1939["Time_EngSpd"],J1939["EngSpd"]           = GetJ1939Signal(Source, "EEC1_00", "EEC1_EngSpd_00")
 
        # EEC1 - DrivDemPercTrq
        J1939["Time_DrivDemPercTrq"],J1939["DrivDemPercTrq"] = GetJ1939Signal(Source, "EEC1_00", "EEC1_DrivDemPercTrq_00")

        # EEC1 - EEC1_ActEngPercTrq_00
        J1939["Time_ActEngPercTrq"],J1939["ActEngPercTrq"] = GetJ1939Signal(Source, "EEC1_00", "EEC1_ActEngPercTrq_00")
        tmp_Time, tmp_Value                                  = GetJ1939Signal(Source, "EEC1_00", "EEC1_ActEngPercTrqHR_00")
        if (J1939["Time_ActEngPercTrq"] is not None) and (tmp_Time is not None):
            if is_same(J1939["Time_ActEngPercTrq"], tmp_Time):
                J1939["ActEngPercTrq"] = J1939["ActEngPercTrq"] + tmp_Value
        
        
        # ------------------------------------------------
        # DM1_2A AEBS
        J1939["Time_AEBS_DM1"], J1939["AEBS_DM1_ActFMI"] = GetJ1939Signal(Source, "DM1_2A", "DM1_ActFMI_2A")
        _, J1939["AEBS_DM1_ActDtcOC"]          = GetJ1939Signal(Source, "DM1_2A", "DM1_ActDtcOC_2A")
        _, J1939["AEBS_DM1_ActDtcCM"]          = GetJ1939Signal(Source, "DM1_2A", "DM1_ActDtcCM_2A")
        _, DM1_ActSPN1_2A                      = GetJ1939Signal(Source, "DM1_2A", "DM1_ActSPN1_2A")
        _, DM1_ActSPN2_2A                      = GetJ1939Signal(Source, "DM1_2A", "DM1_ActSPN2_2A")
        _, DM1_ActSPN3_2A                      = GetJ1939Signal(Source, "DM1_2A", "DM1_ActSPN3_2A")
        _, J1939["AEBS_DM1_AmberWarnLStat"]    = GetJ1939Signal(Source, "DM1_2A", "DM1_AmberWarnLStat_2A")
    
        if (DM1_ActSPN1_2A is not None) and (DM1_ActSPN2_2A is not None) and (DM1_ActSPN3_2A is not None):
            J1939["AEBS_DM1_ActSPN"] = (DM1_ActSPN1_2A*256.0 + DM1_ActSPN2_2A)*256.0 + DM1_ActSPN3_2A
        else:
            J1939["AEBS_DM1_ActSPN"] = None
        J1939["AEBS_DM1_SA"] = int("0x2A",16)
 
 
        # ------------------------------------------------
        # DM1_2A AEBS  (KB AEBS, Wabco ACC)
        J1939["Time_AEBS_DM1_s2A"], J1939["FailureModeIdentifier1_s2A"] = GetJ1939Signal(Source, "t_DM1_s2A", "FailureModeIdentifier1_s2A")
        _, J1939["OccurenceCount1_s2A"]                                 = GetJ1939Signal(Source, "t_DM1_s2A", "OccurenceCount1_s2A")
        _, J1939["SPNConversionMethod1_s2A"]                            = GetJ1939Signal(Source, "t_DM1_s2A", "SPNConversionMethod1_s2A")
        _, J1939_SPN1Low_s2A                                                  = GetJ1939Signal(Source, "t_DM1_s2A", "SPN1_s2A")
        _, J1939_SPN1High_s2A                                                 = GetJ1939Signal(Source, "t_DM1_s2A", "SPN1High_s2A")
        _, J1939["AmberWarningLampStatus_s2A"]                          = GetJ1939Signal(Source, "t_DM1_s2A", "AmberWarningLampStatus_s2A")
    
        if (J1939_SPN1Low_s2A is not None) and (J1939_SPN1High_s2A is not None):
            J1939["SPN1_s2A"] = J1939_SPN1High_s2A*256.0 *256.0 + J1939_SPN1Low_s2A
        else:
            J1939["SPN1_s2A"] = None
 
        # ------------------------------------------------
        # DM1_A0   (Wabco AEBS)
        J1939["Time_AEBS_DM1_sA0"], J1939["FailureModeIdentifier1_sA0"] = GetJ1939Signal(Source, "t_DM1_sA0", "FailureModeIdentifier1_sA0")
        _, J1939["OccurenceCount1_sA0"]                                 = GetJ1939Signal(Source, "t_DM1_sA0", "OccurenceCount1_sA0")
        _, J1939["SPNConversionMethod1_sA0"]                            = GetJ1939Signal(Source, "t_DM1_sA0", "SPNConversionMethod1_sA0")
        _, J1939_SPN1Low_sA0                                                  = GetJ1939Signal(Source, "t_DM1_sA0", "SPN1_sA0")
        _, J1939_SPN1High_sA0                                                 = GetJ1939Signal(Source, "t_DM1_sA0", "SPN1High_sA0")
        _, J1939["AmberWarningLampStatus_sA0"]                          = GetJ1939Signal(Source, "t_DM1_sA0", "AmberWarningLampStatus_sA0")
    
        if (J1939_SPN1Low_sA0 is not None) and (J1939_SPN1High_sA0 is not None):
            J1939["SPN1_sA0"] = J1939_SPN1High_sA0*256.0 *256.0 + J1939_SPN1Low_sA0
        else:
            J1939["SPN1_sA0"] = None
 
        if J1939["Time_AEBS_DM1"] is None:
            if J1939_AEBS_SourceAddress == int("0x2A",16):
                J1939["Time_AEBS_DM1"]           = J1939["Time_AEBS_DM1_s2A"]
                J1939["AEBS_DM1_ActFMI"]         = J1939["FailureModeIdentifier1_s2A"]
                J1939["AEBS_DM1_ActDtcOC"]       = J1939["OccurenceCount1_s2A"]        
                J1939["AEBS_DM1_ActDtcCM"]       = J1939["SPNConversionMethod1_s2A"]        
                J1939["AEBS_DM1_AmberWarnLStat"] = J1939["AmberWarningLampStatus_s2A"]
                J1939["AEBS_DM1_ActSPN"]         = J1939["SPN1_s2A"] 
                J1939["AEBS_DM1_SA"]             = int("0x2A",16)
            if J1939_AEBS_SourceAddress == int("0xA0",16):
                J1939["Time_AEBS_DM1"]           = J1939["Time_AEBS_DM1_sA0"]
                J1939["AEBS_DM1_ActFMI"]         = J1939["FailureModeIdentifier1_sA0"]
                J1939["AEBS_DM1_ActDtcOC"]       = J1939["OccurenceCount1_sA0"]        
                J1939["AEBS_DM1_ActDtcCM"]       = J1939["SPNConversionMethod1_sA0"]        
                J1939["AEBS_DM1_AmberWarnLStat"] = J1939["AmberWarningLampStatus_sA0"]
                J1939["AEBS_DM1_ActSPN"]         = J1939["SPN1_sA0"] 
                J1939["AEBS_DM1_SA"]             = int("0xA0",16)
 
        # -------------------------------------------------------
        # DM1_E8 LDWS
        J1939["Time_LDWS_DM1"], J1939["LDWS_DM1_ActFMI"] = GetJ1939Signal(Source, "DM1_E8", "DM1_ActFMI_E8")
        _, J1939["LDWS_DM1_ActDtcOC"]          = GetJ1939Signal(Source, "DM1_E8", "DM1_ActDtcOC_E8")
        _, J1939["LDWS_DM1_ActDtcCM"]          = GetJ1939Signal(Source, "DM1_E8", "DM1_ActDtcCM_E8")
        _, DM1_ActSPN1_E8                      = GetJ1939Signal(Source, "DM1_E8", "DM1_ActSPN1_E8")
        _, DM1_ActSPN2_E8                      = GetJ1939Signal(Source, "DM1_E8", "DM1_ActSPN2_E8")
        _, DM1_ActSPN3_E8                      = GetJ1939Signal(Source, "DM1_E8", "DM1_ActSPN3_E8")
        _, J1939["LDWS_DM1_AmberWarnLStat"]    = GetJ1939Signal(Source, "DM1_E8", "DM1_AmberWarnLStat_E8")
    
        if (DM1_ActSPN1_E8 is not None) and (DM1_ActSPN2_E8 is not None) and (DM1_ActSPN3_E8 is not None):
            J1939["LDWS_DM1_ActSPN"] = (DM1_ActSPN1_E8*256.0 + DM1_ActSPN2_E8)*256.0 + DM1_ActSPN3_E8
        else:
            J1939["LDWS_DM1_ActSPN"] = None


        # ------------------------------------------------
        # ACC1
        J1939["Time_ACCDistanceAlertSignal_s2A"],J1939["ACCDistanceAlertSignal_s2A"]            = GetJ1939Signal(Source, "t_ACC1_s2A", "ACCDistanceAlertSignal_s2A")
        J1939["Time_ACCSystemShutoffWarning_s2A"],J1939["ACCSystemShutoffWarning_s2A"]          = GetJ1939Signal(Source, "t_ACC1_s2A", "ACCSystemShutoffWarning_s2A")
    
        J1939["Time_ACCTargetDetected_s2A"],J1939["ACCTargetDetected_s2A"]                      = GetJ1939Signal(Source, "t_ACC1_s2A", "ACCTargetDetected_s2A")
    
        J1939["Time_RoadCurvature_s2A"],J1939["RoadCurvature_s2A"]                              = GetJ1939Signal(Source, "t_ACC1_s2A", "RoadCurvature_s2A")
    
        J1939["Time_AdptveCruiseCtrlSetDistanceMode_s2A"],J1939["AdptveCruiseCtrlSetDistanceMode_s2A"]  = GetJ1939Signal(Source, "t_ACC1_s2A", "AdptveCruiseCtrlSetDistanceMode_s2A")
    
        J1939["Time_AdaptiveCruiseCtrlMode_s2A"],J1939["AdaptiveCruiseCtrlMode_s2A"]           = GetJ1939Signal(Source, "t_ACC1_s2A", "AdaptiveCruiseCtrlMode_s2A")
    
        J1939["Time_AdaptiveCruiseCtrlSetSpeed_s2A"],J1939["AdaptiveCruiseCtrlSetSpeed_s2A"]   = GetJ1939Signal(Source, "t_ACC1_s2A", "AdaptiveCruiseCtrlSetSpeed_s2A")
        J1939["Time_DistanceToForwardVehicle_s2A"],J1939["DistanceToForwardVehicle_s2A"]       = GetJ1939Signal(Source, "t_ACC1_s2A", "DistanceToForwardVehicle_s2A")
        J1939["Time_SpeedOfForwardVehicle_s2A"],J1939["SpeedOfForwardVehicle_s2A"]             = GetJ1939Signal(Source, "t_ACC1_s2A", "SpeedOfForwardVehicle_s2A")
        
        # ------------------------------------------------
        # CCVS
        J1939["Time_CruiseCtrlActive_s00"],J1939["CruiseCtrlActive_s00"] = GetJ1939Signal(Source, "t_CCVS_s00", "CruiseCtrlActive_s00")
        
        J1939["Time_WheelBasedVehicleSpeed_s00"],J1939["WheelBasedVehicleSpeed_s00"] = GetJ1939Signal(Source, "t_CCVS_s00", "WheelBasedVehicleSpeed_s00")
        
        '''
            SG_ ParkBrakeReleaseInhibitRq : 6|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ EngShutdownOverrideSwitch : 62|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ EngTestModeSwitch : 60|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ EngIdleDecrementSwitch : 58|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ EngIdleIncrementSwitch : 56|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ CruiseCtrlStates : 53|3@1+ (1,0) [0|7] "" Vector__XXX
            SG_ PTOState : 48|5@1+ (1,0) [0|31] "" Vector__XXX
            SG_ CruiseCtrlSetSpeed : 40|8@1+ (1,0) [0|250] "km/h" Vector__XXX
            SG_ CruiseCtrlAccelerateSwitch : 38|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ CruiseCtrlResumeSwitch : 36|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ CruiseCtrlCoastSwitch : 34|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ CruiseCtrlSetSwitch : 32|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ ClutchSwitch : 30|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ BrakeSwitch : 28|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ CruiseCtrlEnableSwitch : 26|2@1+ (1,0) [0|3] "" Vector__XXX
            
            SG_ WheelBasedVehicleSpeed : 8|16@1+ (0.00390625,0) [0|250.996] "km/h" Vector__XXX
            SG_ CruiseCtrlPauseSwitch : 4|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ ParkingBrakeSwitch : 2|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ TwoSpeedAxleSwitch : 0|2@1+ (1,0) [0|3] "" Vector__XXX
        '''
                
        # ------------------------------------------------
        # TSC1   2A -> 00 (ACC->Engine)
        J1939["Time_OverrideCtrlModePriority_d00_s2A"],J1939["OverrideCtrlModePriority_d00_s2A"] = GetJ1939Signal(Source, "t_TSC1_d00_s2A", "OverrideCtrlModePriority_d00_s2A")
        J1939["Time_EngOverrideCtrlMode_d00_s2A"],J1939["EngOverrideCtrlMode_d00_s2A"] = GetJ1939Signal(Source, "t_TSC1_d00_s2A", "EngOverrideCtrlMode_d00_s2A")
  
        J1939["Time_EngRqedTorque_TorqueLimit_d00_s2A"],J1939["EngRqedTorque_TorqueLimit_d00_s2A"] = GetJ1939Signal(Source, "t_TSC1_d00_s2A", "EngRqedTorque_TorqueLimit_d00_s2A")
  
        '''
            SG_ Tsc1MessageCounter : 56|4@1+ (1,0) [0|0] "" Vector__XXX
            SG_ Tsc1Checksum : 60|4@1+ (1,0) [0|0] "" Vector__XXX
            SG_ ControlPurpose : 35|5@1+ (1,0) [0|31] "" Vector__XXX
            SG_ TransmissionRate : 32|3@1+ (1,0) [0|7] "" Vector__XXX
            SG_ EngRqedTorque_TorqueLimit : 24|8@1+ (1,-125) [-125|125] "%" Vector__XXX
            SG_ EngRqedSpeed_SpeedLimit : 8|16@1+ (0.125,0) [0|8031.875] "rpm" Vector__XXX
            SG_ OverrideCtrlModePriority : 4|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ EngRqedSpeedCtrlConditions : 2|2@1+ (1,0) [0|3] "" Vector__XXX
            SG_ EngOverrideCtrlMode : 0|2@1+ (1,0) [0|3] "" Vector__XXX
        '''
        # ------------------------------------------------
        # TSC1   0B -> 00 (Brake -> Engine)
        J1939["Time_EngRqedTorque_TorqueLimit_d00_s0B"],J1939["EngRqedTorque_TorqueLimit_d00_s0B"] = GetJ1939Signal(Source, "t_TSC1_d00_s0B", "EngRqedTorque_TorqueLimit_d00_s0B")
  
        # ------------------------------------------------
        # TSC1   2A -> 10 (ACC -> Driveline Retarder)
        J1939["Time_EngOverrideCtrlMode_d10_s2A"],J1939["EngOverrideCtrlMode_d10_s2A"] = GetJ1939Signal(Source, "t_TSC1_d10_s2A", "EngOverrideCtrlMode_d10_s2A")
        J1939["Time_EngRqedTorque_TorqueLimit_d10_s2A"],J1939["EngRqedTorque_TorqueLimit_d10_s2A"] = GetJ1939Signal(Source, "t_TSC1_d10_s2A", "EngRqedTorque_TorqueLimit_d10_s2A")
    
        # ------------------------------------------------
        # TSC1   2A -> 29 (ACC -> Exhaust Retarder)
        J1939["Time_EngOverrideCtrlMode_d29_s2A"],J1939["EngOverrideCtrlMode_d29_s2A"] = GetJ1939Signal(Source, "t_TSC1_d29_s2A", "EngOverrideCtrlMode_d29_s2A")
        J1939["Time_EngRqedTorque_TorqueLimit_d29_s2A"],J1939["EngRqedTorque_TorqueLimit_d29_s2A"] = GetJ1939Signal(Source, "t_TSC1_d29_s2A", "EngRqedTorque_TorqueLimit_d29_s2A")

        # ------------------------------------------------
        # TSC1   10 -> 29 (Driveline Retarder -> Exhaust Retarder)
        J1939["Time_EngRqedTorque_TorqueLimit_d29_s10"],J1939["EngRqedTorque_TorqueLimit_d29_s10"] = GetJ1939Signal(Source, "t_TSC1_d29_s10", "EngRqedTorque_TorqueLimit_d29_s10")


      
      
      
        # ------------------------------------------------
        # EEC1 00
        J1939["Time_ActualEngPercentTorque_s00"],J1939["ActualEngPercentTorque_s00"] = GetJ1939Signal(Source, "t_EEC1_s00", "ActualEngPercentTorque_s00")
        J1939["Time_DriversDemandEngPercentTorque_s00"],J1939["DriversDemandEngPercentTorque_s00"] = GetJ1939Signal(Source, "t_EEC1_s00", "DriversDemandEngPercentTorque_s00")
       
        '''
        BO_ 2364540158 EEC1: 8 Vector__XXX
         SG_ EngDemandPercentTorque : 56|8@1+ (1,-125) [-125|125] "%" Vector__XXX
         SG_ EngStarterMode : 48|4@1+ (1,0) [0|15] "" Vector__XXX
         SG_ SrcAddrssOfCtrllngDvcForEngCtrl : 40|8@1+ (1,0) [0|255] "" Vector__XXX
         SG_ EngSpeed : 24|16@1+ (0.125,0) [0|8031.875] "rpm" Vector__XXX
         SG_ ActualEngPercentTorque : 16|8@1+ (1,-125) [-125|125] "%" Vector__XXX
         SG_ DriversDemandEngPercentTorque : 8|8@1+ (1,-125) [-125|125] "%" Vector__XXX
         SG_ EngTorqueMode : 0|4@1+ (1,0) [0|15] "" Vector__XXX
        '''
        
        # ------------------------------------------------
        # EEC2 00
        J1939["Time_AccelPedalPos1_s00"],J1939["AccelPedalPos1_s00"] = GetJ1939Signal(Source, "t_EEC2_s00", "AccelPedalPos1_s00")
        
        '''
        BO_ 2364539902 EEC2: 8 Vector__XXX
         SG_ ActMaxAvailEngPercentTorque : 48|8@1+ (0.4,0) [0|100] "%" Vector__XXX
         SG_ AccelPedalPos2 : 32|8@1+ (0.4,0) [0|100] "%" Vector__XXX
         SG_ VhclAccelerationRateLimitStatus : 40|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ EngPercentLoadAtCurrentSpeed : 16|8@1+ (1,0) [0|250] "%" Vector__XXX
         SG_ AccelPedal2LowIdleSwitch : 6|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ RoadSpeedLimitStatus : 4|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ AccelPedalKickdownSwitch : 2|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ AccelPedal1LowIdleSwitch : 0|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ RemoteAccelPedalPos : 24|8@1+ (0.4,0) [0|100] "%" Vector__XXX
         SG_ AccelPedalPos1 : 8|8@1+ (0.4,0) [0|100] "%" Vector__XXX
        '''
        
        # ------------------------------------------------
        # EBC1 00
        J1939["Time_BrakePedalPos_s0B"],J1939["BrakePedalPos_s0B"] = GetJ1939Signal(Source, "t_EBC1_s0B", "BrakePedalPos_s0B")
       
        '''
        BO_ 2565865982 EBC1: 8 Vector__XXX
         SG_ SrcAddrssOfCtrllngDvcFrBrkCntrl : 48|8@1+ (1,0) [0|255] "" Vector__XXX
         SG_ BrakePedalPos : 8|8@1+ (0.4,0) [0|100] "%" Vector__XXX
         SG_ TrctrMntdTrilerABSWarningSignal : 62|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ TrailerABSStatus : 60|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ HaltBrakeSwitch : 58|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ ATC_ASRInformationSignal : 46|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ ABS_EBSAmberWarningSignal : 44|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ EBSRedWarningSignal : 42|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ ABSFullyOperational : 40|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ EngRetarderSelection : 32|8@1+ (0.4,0) [0|100] "%" Vector__XXX
         SG_ RemoteAccelEnableSwitch : 30|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ EngAuxEngShutdownSwitch : 28|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ EngDerateSwitch : 26|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ AccelInterlockSwitch : 24|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ TractionCtrlOverrideSwitch : 22|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ ASRHillHolderSwitch : 20|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ ASROffroadSwitch : 18|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ ABSOffroadSwitch : 16|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ EBSBrakeSwitch : 6|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ AntiLockBrakingActive : 4|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ ASRBrakeCtrlActive : 2|2@1+ (1,0) [0|3] "" Vector__XXX
         SG_ ASREngCtrlActive : 0|2@1+ (1,0) [0|3] "" Vector__XXX
        '''
        
        return J1939
        
  #============================================================================================
  @staticmethod
  def create_AC100_General_radar_status(Source, t_common, t_threshold):
        # General_radar_status
        
        
        
        if cDataAC100.verbose:
            print "create_AC100_General_radar_status()"
        
        # signal_list: [ (short name, device name, signal name incl. %d), ()]
        signal_list = [
          ("cm_system_status",                         "General_radar_status", "cm_system_status",                   True ),
          ("vehicle_reference_acceleration",           "General_radar_status", "vehicle_reference_acceleration",     True ),
          ("environment_speed",                        "General_radar_status", "environment_speed",                  True ),
          ("actual_vehicle_speed",                     "General_radar_status", "actual_vehicle_speed",               True ),
          ("cvd_yawrate",                              "General_radar_status", "cvd_yawrate",                        True ),
          ("prefiltered_yawrate",                      "General_radar_status", "prefiltered_yawrate",                True ),
          ("estimated_road_curvature",                 "General_radar_status", "estimated_road_curvature",           True ),

          ("processor_time_used",                      "General_radar_status", "processor_time_used",                True ),
          ("number_of_tracks",                         "General_radar_status", "number_of_tracks",                   True ),
          ("number_of_targets",                        "General_radar_status", "number_of_targets",                  True ),

          ("covi",                                     "General_radar_status", "covi",                               True ),
          ("dfil",                                     "General_radar_status", "dfil",                               True ),
                   
          ("confidence_cw_track",                      "General_radar_status", "confidence_cw_track",                True ),

          ("yawrate_offset",                           "General_radar_status", "yawrate_offset",                     True ),

          ("sensor_blind_detected",                    "General_radar_status", "sensor_blind_detected",              True ),

          ("sensor_blindness",                         "General_radar_status", "sensor_blindness",                   True ),
          ("severe_misalignment_angle",                "General_radar_status", "severe_misalignment_angle",          True ),

          ("tacho_correction_factor",                  "General_radar_status", "tacho_correction_factor",            True ),
          
          ("SP_filt_antenna_blocked_prob",             "General_radar_status", "SP_filt_antenna_blocked_prob",       True ),
          ("SP_antenna_blocked",                       "General_radar_status", "SP_antenna_blocked",                 True ),
          ("SIB1_antenna_blocked",                     "General_radar_status", "SIB1_antenna_blocked",               True ),

          ("SP_inst_prob_dynamic_obstruction",         "General_radar_status", "SP_inst_prob_dynamic_obstruction",   True ),
          ("SP_inst_prob_antenna_distorted",           "General_radar_status", "SP_inst_prob_antenna_distorted",     True ),
          ("SP_inst_prob_antenna_blocked",             "General_radar_status", "SP_inst_prob_antenna_blocked",       True ),

          ("current_ramp_type",                        "General_radar_status", "current_ramp_type",                  True ),
          
         
          # ------------------------------------------------------
          # SIB1
          ("SIB1_general_status_ok",                   "General_radar_status", "SIB1_general_status_ok",             True ),
          ("SIB1_EEPROM_error",                        "General_radar_status", "SIB1_EEPROM_error",                  True ),
          ("SIB1_radar_cycle_overrun",                 "General_radar_status", "SIB1_radar_cycle_overrun",           True ),
          ("SIB1_misalignment_error",                  "General_radar_status", "SIB1_misalignment_error",            True ),
          ("SIB1_antenna_blocked",                     "General_radar_status", "SIB1_antenna_blocked",               True ),
          ("SIB1_FOV_error",                           "General_radar_status", "SIB1_FOV_error",                     True ),
          ("SIB1_spare",                               "General_radar_status", "SIB1_spare",                         True ),
          ("SIB1_ICE_detected",                        "General_radar_status", "SIB1_ICE_detected",                  True ),

          # ------------------------------------------------------
          # SIB2
          ("SIB2_linearity_error",                     "General_radar_status", "SIB2_linearity_error",               True ),
          ("SIB2_phase_error",                         "General_radar_status", "SIB2_phase_error",                   True ),
          ("SIB2_CODI_error",                          "General_radar_status", "SIB2_CODI_error",                    True ),
          ("SIB2_MMIC_power_supply_error",             "General_radar_status", "SIB2_MMIC_power_supply_error",       True ),
          ("SIB2_COVI_error",                          "General_radar_status", "SIB2_COVI_error",                    True ),
          ("SIB2_internal_fault_TRM_off",              "General_radar_status", "SIB2_internal_fault_TRM_off",        True ),
          ("SIB2_radar_jamming_detected",              "General_radar_status", "SIB2_radar_jamming_detected",        True ),
          ("SIB2_spare",                               "General_radar_status", "SIB2_spare",                         True ),

          # -------------------------------------------------------
          # Faults
          ("fault_1_ID",                               "General_radar_status", "fault_1_ID",                         True ),
          ("fault_1_ID_bit8",                          "General_radar_status", "fault_1_ID_bit8",                    True ),
          ("fault_1_snapshot",                         "General_radar_status", "fault_1_snapshot",                   True ),
          ("fault_2_ID",                               "General_radar_status", "fault_2_ID",                         True ),
          ("fault_2_ID_bit8",                          "General_radar_status", "fault_2_ID_bit8",                    True ),
          ("fault_2_snapshot",                         "General_radar_status", "fault_2_snapshot",                   True ),
          ("fault_3_ID",                               "General_radar_status", "fault_3_ID",                         True ),
          ("fault_3_ID_bit8",                          "General_radar_status", "fault_3_ID_bit8",                    True ),
          ("fault_3_snapshot",                         "General_radar_status", "fault_3_snapshot",                   True ),

          
          ]
         
        # ---------------------------------------------------------------
        # create signal dictionary 
        AC100_General = {} 
 
        # Time
        AC100_General['Time'] = t_common
        # Signals
        for signal in signal_list:
            #print signal
            Time, Values = kbtools.GetSignal(Source, signal[1], signal[2])  
            #print Time
            #print Values            
            if Time is not None:
                valid = kbtools.calc_signal_valid(t_common,Time,t_threshold)
                Values_resampled = kbtools.resample(Time,Values, t_common,'zoh')
                AC100_General[signal[0]] = Values_resampled*valid
            else:
                if not cDataAC100.warnings_off:
                    #assert not signal[3], "Mandatory signal <%s> is missing" % (signal[2])
                    print "Optional signal <%s> is missing" % (signal[2])                         
                AC100_General[signal[0]] = None
                
        return AC100_General
         
  #============================================================================================
  @staticmethod
  def create_Bendix_CMS(Source, t_common, t_threshold):
        # Bendix Collision Mitigation System
            
            
        # signal_list: [ (short name, device name, signal name incl. %d), ()]
        signal_list = [
          ("XBRAccDemand",                             "XBRUS_2A", "XBRUS_AccelDemand_2A", False ),
          ("AudibleFeedback",                          "PropWarn", "AudibleFeedback",      False ),
       
          ]
         
        # ---------------------------------------------------------------
        # create signal dictionary 
        Bendix_CMS = {} 
 
        # Time
        Bendix_CMS['Time'] = t_common
        # Signals
        for signal in signal_list:
            #print signal
            Time, Values = kbtools.GetSignal(Source, signal[1], signal[2])  
            #print Time
            #print Values            
            if Time is not None:
                valid = kbtools.calc_signal_valid(t_common,Time,t_threshold)
                Values_resampled = kbtools.resample(Time,Values, t_common,'zoh')
                Bendix_CMS[signal[0]] = Values_resampled*valid
            else:
                if not cDataAC100.warnings_off:
                    #assert not signal[3], "Mandatory signal <%s> is missing" % (signal[2])
                    print "Optional signal <%s> is missing" % (signal[2])                         
                Bendix_CMS[signal[0]] = None
        
        return Bendix_CMS
        
  #============================================================================================
  @staticmethod
  def create_Bendix_ACC_Sxy(Source, t_common, t_threshold):
        # Bendix Collision Mitigation System
            
            
        # signal_list: [ (short name, device name, signal name incl. %d), ()]
        signal_list = [
          ("ActiveFault01",   "ACC_S02", "ActiveFault01", True ),
          ("ActiveFault02",   "ACC_S02", "ActiveFault02", True ),
          ("ActiveFault03",   "ACC_S02", "ActiveFault03", True ),
          ("ActiveFault04",   "ACC_S02", "ActiveFault04", True ),
          ("ActiveFault05",   "ACC_S02", "ActiveFault05", True ),
          ("ActiveFault06",   "ACC_S02", "ActiveFault06", True ),
          ("ActiveFault07",   "ACC_S02", "ActiveFault07", True ),
          ("ActiveFault08",   "ACC_S02", "ActiveFault08", True ),

          # TRW's allow/cancel flags (ACC - S3)
          # a) global conditions
          ("cm_allow_entry_global_conditions",   "ACC_S03", "cm_allow_entry_global_conditions", True ),
          ("cm_cancel_global_conditions",        "ACC_S03", "cm_cancel_global_conditions",      True ),
          # b) cw collision warning 
          ("cw_allow_entry",                     "ACC_S03", "cw_allow_entry",                   True ),
          ("cw_cancel",                          "ACC_S03", "cw_cancel",                        True ),
          # c) cmb collision mitigation 
          ("cmb_allow_entry",                    "ACC_S03", "cmb_allow_entry",                  True ),
          ("cmb_cancel",                         "ACC_S03", "cmb_cancel",                       True ),
          ]
         
        # ---------------------------------------------------------------
        # create signal dictionary 
        ACC_Sxy = {} 
 
        # Time
        ACC_Sxy['Time'] = t_common
        # Signals
        for signal in signal_list:
            #print signal
            Time, Values = kbtools.GetSignal(Source, signal[1], signal[2])  
            #print "Time", Time
            #print "Values", Values 
            #print "t_common", t_common            
            if Time is not None:
                valid = kbtools.calc_signal_valid(t_common,Time,t_threshold)
                Values_resampled = kbtools.resample(Time,Values, t_common,'zoh')
                #print "Values_resampled", Values_resampled
                #print "valid", valid
                ACC_Sxy[signal[0]] = Values_resampled*valid
            else:
                if not cDataAC100.warnings_off:
                    #assert not signal[3], "Mandatory signal <%s> is missing" % (signal[2])
                    print "Optional signal <%s> is missing" % (signal[2])   
                ACC_Sxy[signal[0]] = None                
        
        return ACC_Sxy
          
       
  #============================================================================================
  @staticmethod
  def create_FLC20(Source, t_common, t_threshold):
        # FLC20
        
        # todo: resample on start of burst (Video Data General)     
            
            
        # signal_list: [ (short name, device name, signal name incl. %d), ()]
        signal_list = [
          ("SensorStatus",   "Video_Data_General_B", "SensorStatus", True ),
          ("LaneDepartImminentRight",   "FLI1_E8", "FLI1_LaneDepartImminentRight_E8", True ),
          ("LaneDepartImminentLeft",   "FLI1_E8", "FLI1_LaneDepartImminentLeft_E8", True ),
          
          # ------------------------------------------------
          # Video Lane Left 
          
          # old: Video_Fusion_Protocol_Released_v1.4b_Mar_27_2013_TrwDebug_mod.dbc
          ("Video_Lane_Left_Message_Counter_A",             "Video_Lane_Left_A" ,"Message_Counter_Left_A", True ),
          ("Video_Lane_Left_Message_Counter_B",             "Video_Lane_Left_B" ,"Message_Counter_Left_B", True ),
                    
          ("Video_Lane_Left_C0",                            "Video_Lane_Left_A", "Position_Left_A", True ),
          ("Video_Lane_Left_C1",                            "Video_Lane_Left_A", "Heading_Left_A", True ),
          ("Video_Lane_Left_C2",                            "Video_Lane_Left_A", "Curvature_Left_A", True ),
          ("Video_Lane_Left_C3",                            "Video_Lane_Left_A", "Curvature_Rate_Left_A", True ),
          
          ("Video_Lane_Left_View_Range",                    "Video_Lane_Left_B", "View_Range_Left_B", True ),
          ("Video_Lane_Left_Lane_TLC",                      "Video_Lane_Left_B", "TLC_Left_B", True ),
          ("Video_Lane_Left_Lane_Crossing",                 "Video_Lane_Left_B", "Lane_Crossing_Left_B", True ),
       
       
          # new: Video_Fusion_Protocol_2013-11-04.dbc           
          #("Video_Lane_Left_Message_Counter_A",             "Video_Lane_Left_A" ,"Message_Counter", True ),
          #("Video_Lane_Left_Message_Counter_B",             "Video_Lane_Left_B" ,"Message_Counter", True ),
          #("Video_Lane_Left_C0",                            "Video_Lane_Left_A", "C0", True ),
          #("Video_Lane_Left_C1",                            "Video_Lane_Left_A", "C1", True ),
          #("Video_Lane_Left_C2",                            "Video_Lane_Left_A", "C2", True ),
          #("Video_Lane_Left_C3",                            "Video_Lane_Left_A", "C3", True ),
          
          #("Video_Lane_Left_View_Range",                    "Video_Lane_Left_B", "View_Range", True ),
          #("Video_Lane_Left_Quality",                       "Video_Lane_Left_B", "Quality", True ),
          #("Video_Lane_Left_Lane_Width",                    "Video_Lane_Left_B", "Lane_Width", True ),
          #("Video_Lane_Left_Lane_Type",                     "Video_Lane_Left_A", "Lane_Type", True ),
          #("Video_Lane_Left_Lane_TLC",                      "Video_Lane_Left_B", "TLC", True ),
          #("Video_Lane_Left_Lane_Me_Line_Changed",          "Video_Lane_Left_B", "Me_Line_Changed", True ),
       
          #---------------------------------------------------
          # Video Lane Right 
          
          # old: Video_Fusion_Protocol_Released_v1.4b_Mar_27_2013_TrwDebug_mod.dbc
          ("Video_Lane_Right_Message_Counter_A",             "Video_Lane_Right_A" ,"Message_Counter_Right_A", True ),
          ("Video_Lane_Right_Message_Counter_B",             "Video_Lane_Right_B" ,"Message_Counter_Right_B", True ),
                    
          ("Video_Lane_Right_C0",                            "Video_Lane_Right_A", "Position_Right_A", True ),
          ("Video_Lane_Right_C1",                            "Video_Lane_Right_A", "Heading_Right_A", True ),
          ("Video_Lane_Right_C2",                            "Video_Lane_Right_A", "Curvature_Right_A", True ),
          ("Video_Lane_Right_C3",                            "Video_Lane_Right_A", "Curvature_Rate_Right_A", True ),
          
          ("Video_Lane_Right_View_Range",                    "Video_Lane_Right_B", "View_Range_Right_B", True ),
          ("Video_Lane_Right_Lane_TLC",                      "Video_Lane_Right_B", "TLC_Right_B", True ),
          ("Video_Lane_Right_Lane_Crossing",                 "Video_Lane_Right_B", "Lane_Crossing_Right_B", True ),

   
          
          # new: Video_Fusion_Protocol_2013-11-04.dbc 
          #("Video_Lane_Right_Message_Counter_A",            "Video_Lane_Right_A" ,"Message_Counter", True ),
          #("Video_Lane_Right_Message_Counter_B",            "Video_Lane_Right_B" ,"Message_Counter", True ),
                    
          #("Video_Lane_Right_C0",                           "Video_Lane_Right_A", "C0", True ),
          #("Video_Lane_Right_C1",                           "Video_Lane_Right_A", "C1", True ),
          #("Video_Lane_Right_C2",                           "Video_Lane_Right_A", "C2", True ),
          #("Video_Lane_Right_C3",                           "Video_Lane_Right_A", "C3", True ),
          
          #("Video_Lane_Right_View_Range",                   "Video_Lane_Right_B", "View_Range", True ),
          #("Video_Lane_Right_Quality",                      "Video_Lane_Right_B", "Quality", True ),
          #("Video_Lane_Right_Lane_Width",                   "Video_Lane_Right_B", "Lane_Width", True ),
          #("Video_Lane_Right_Lane_Type",                    "Video_Lane_Right_A", "Lane_Type", True ),
          #("Video_Lane_Right_Lane_TLC",                     "Video_Lane_Right_B", "TLC", True ),
          #("Video_Lane_Right_Lane_Me_Line_Changed",         "Video_Lane_Right_B", "Me_Line_Changed", True ),


          
          ]
 
             
        # ---------------------------------------------------------------
        # create signal dictionary 
        FLC20 = {} 
 
        # Time
        FLC20['Time'] = t_common
        # Signals
        for signal in signal_list:
            #print signal
            Time, Values = kbtools.GetSignal(Source, signal[1], signal[2])  
            #print Time
            #print Values            
            if (Time is not None) and (t_common is not None):
                valid = kbtools.calc_signal_valid(t_common,Time,t_threshold)
                Values_resampled = kbtools.resample(Time,Values, t_common,'zoh')
                FLC20[signal[0]] = Values_resampled*valid
            else:
                if not cDataAC100.warnings_off:
                    #assert not signal[3], "Mandatory signal <%s> is missing" % (signal[2])
                    print "Optional signal <%s> is missing" % (signal[2])   
                FLC20[signal[0]] = None                
        
        
        # ------------------------------------------------
        #FLC20["Time_org_Video_Lane_Left_C0"],FLC20["org_Video_Lane_Left_C0"]   = kbtools.GetSignal(Source, "Video_Lane_Left_A", "Position_Left_A")
        #FLC20["Time_org_Video_Lane_Right_C0"],FLC20["org_Video_Lane_Right_C0"] = kbtools.GetSignal(Source, "Video_Lane_Right_A", "Position_Right_A")

        
        
        return FLC20
          
  #============================================================================================
  @staticmethod
  def create_FLC20_CAN(Source):
        # not resamples
        
        '''
        FLC20 FusionMsgArray
        
        1. Video_Data_General_A
        2. Video_Data_General_B
        
        3. Video_Object_Header
        4. 5. Video_Object_X_A Video_Object_X_B   X=0..9 -> 20 messages
            if debugEnable
                Video_Object_X_C Video_Object_X_D   X=0..9 -> 20 messages
  
        24. Video_Lane_Header
        
        25. 26. Video_Lane_Right_A, Video_Lane_Right_B
        27. 28. Video_Lane_Left_A, Video_Lane_Left_B
        
        29. 30. Video_Lane_Next_Right_A, Video_Lane_Next_Right_B
        31. 32. Video_Lane_Next_Left_A, Video_Lane_Next_Left_B
        
        33. Bendix Info1
        34. Bendix Info2
        35. Bendix Info3

        '''        
        '''
        Video_Data_General_A	Application_Version_A, Application_Version_B, Application_Version_C, Application_Version_D
        Video_Data_General_A	Debug_Msg_Tx
        Video_Data_General_A	Message_Counter
        Video_Data_General_A	Pictus_SW_Version
        Video_Data_General_A	Protocol_Version_A, Protocol_Version_B, Protocol_Version_C, Protocol_Version_D
        Video_Data_General_A	RefPoint_X, RefPoint_Y
        
        Video_Data_General_B	CAN_Delay
        Video_Data_General_B	Day_Time_Indicator
        Video_Data_General_B	Driving_Side
        Video_Data_General_B	Frame_ID
        Video_Data_General_B	Message_Counter
        Video_Data_General_B	SensorStatus
        
        Video_Lane_Header	Construction_Area
        Video_Lane_Header	LaneModuleValid
        Video_Lane_Header	Message_Counter
        Video_Lane_Header	Road_Type

        Video_Object_Header
            Right_Close_Range_Cut_In 
            Ped_In_Danger_Zone
            Ped_FCW_On
            Number_Of_Objects
            Message_Counter_Header
            Left_Close_Range_Cut_In
            ID_CIPV
            FCW_On

        Video_Object_0_A
            Right_Angle_0_A 
            Relative_Velocity_0_A 
            Message_Counter_0_A 
            Longitudinal_Distance_0_A 
            Left_Angle_0_A 
            ID_0_A 
            Class_0_A 
        Video_Object_0_B
            Width_0_B 
            Relative_Velocity_STD_0_B 
            Rate_Mean_Angle_0_B 
            Motion_Status_0_B 
            Message_Counter_0_B 
            Longitudinal_Distance_STD_0_B 
            Lane_0_B 
            Inverse_TTC_0_B 
            Indicator_0_B 
            Detection_Score_0_B 
            Brake_Light_0_B 
        Video_Object_0_C
            Message_Counter_0_C 
            Lateral_Distance_0_C 
            Lane_Movement_Type_0_C 
            ID_extended_0_C
            Angle_STD_0_C
            Acceleration_Abs_0_C 
        Video_Object_0_D
            Message_Counter_0_D 
            Upper_Right_Top_from_FOE_0_D 
            Upper_Right_Right_from_FOE_0_D
            Lower_Left_Left_from_FOE_0_D
            Lower_Left_Bottom_from_FOE_0_D
            FOE_Y_0_D 
            FOE_X_0_D

             

        '''
        
        
        if cDataAC100.verbose:
            print "create_FLC20_CAN"
        
        F = {}     # FLC20_CAN 
        
        
        # ------------------------------------------------
        # 1. Video_Data_General_A - first CAN message in burst

        F["Time_Message_Counter_Video_Data_General_A"],F["Message_Counter_Video_Data_General_A"]   = kbtools.GetSignal(Source, "Video_Data_General_A", "Message_Counter_General_A")
        if F["Time_Message_Counter_Video_Data_General_A"] is None:
            # VD_Message_Counter_General_B by intention; because VD_Message_Counter_General_A not available
            F["Time_Message_Counter_Video_Data_General_A"],F["Message_Counter_Video_Data_General_A"] = kbtools.GetSignal(Source, "t_common_time", "VD_Message_Counter_General_B")
        
        F["Time_RefPoint_X"],F["RefPoint_X"]             = kbtools.GetSignal(Source, "Video_Data_General_A", "RefPoint_X")
        F["Time_RefPoint_Y"],F["RefPoint_Y"]             = kbtools.GetSignal(Source, "Video_Data_General_A", "RefPoint_Y")

        F["Time_Pictus_SW_Version"],F["Pictus_SW_Version"] = kbtools.GetSignal(Source, "Video_Data_General_A", "Pictus_SW_Version")
        F["Time_Debug_Msg_Tx"],F["Debug_Msg_Tx"]           = kbtools.GetSignal(Source, "Video_Data_General_A", "Debug_Msg_Tx")
        
        Time_Protocol_Version_A,Protocol_Version_A = kbtools.GetSignal(Source, "Video_Data_General_A", "Protocol_Version_A")
        Time_Protocol_Version_B,Protocol_Version_B = kbtools.GetSignal(Source, "Video_Data_General_A", "Protocol_Version_B")
        Time_Protocol_Version_C,Protocol_Version_C = kbtools.GetSignal(Source, "Video_Data_General_A", "Protocol_Version_C")
        Time_Protocol_Version_D,Protocol_Version_D = kbtools.GetSignal(Source, "Video_Data_General_A", "Protocol_Version_D")
        
        try:
            F["Time_Protocol_Version"] = Time_Protocol_Version_A
            F["Protocol_Version"] = ((Protocol_Version_A*16 + Protocol_Version_B)*16+Protocol_Version_C)*16+Protocol_Version_D
        except:
            F["Time_Protocol_Version"] = None
            F["Protocol_Version"] = None
            
        Time_Application_Version_A,Application_Version_A = kbtools.GetSignal(Source, "Video_Data_General_A", "Application_Version_A")
        Time_Application_Version_B,Application_Version_B = kbtools.GetSignal(Source, "Video_Data_General_A", "Application_Version_B")
        Time_Application_Version_C,Application_Version_C = kbtools.GetSignal(Source, "Video_Data_General_A", "Application_Version_C")
        Time_Application_Version_D,Application_Version_D = kbtools.GetSignal(Source, "Video_Data_General_A", "Application_Version_D")
        
        try:
            F["Time_Application_Version"] = Time_Application_Version_A
            F["Application_Version"] = ((Protocol_Version_A*16 + Protocol_Version_B)*16+Protocol_Version_C)*16+Protocol_Version_D
        except:
            F["Time_Application_Version"] = None
            F["Application_Version"] = None
        
       
        # ------------------------------------------------
        # 2. Video_Data_General_B - second message

        F["Time_Message_Counter_Video_Data_General_B"],F["Message_Counter_Video_Data_General_B"]   = kbtools.GetSignal(Source, "Video_Data_General_B", "Message_Counter_General_B")
        if F["Time_Message_Counter_Video_Data_General_B"] is None:
            F["Time_Message_Counter_Video_Data_General_B"],F["Message_Counter_Video_Data_General_B"] = kbtools.GetSignal(Source, "t_common_time", "VD_Message_Counter_General_B")

        F["Time_SensorStatus"],F["SensorStatus"]             = kbtools.GetSignal(Source, "Video_Data_General_B", "SensorStatus")
        if F["Time_SensorStatus"] is None:
            F["Time_SensorStatus"],F["SensorStatus"] = kbtools.GetSignal(Source, "t_common_time", "VD_SensorStatus")

        F["Time_Frame_ID"],F["Frame_ID"]                     = kbtools.GetSignal(Source, "Video_Data_General_B", "Frame_ID")
        if F["Time_Frame_ID"] is None:
            F["Time_Frame_ID"],F["Frame_ID"] = kbtools.GetSignal(Source, "t_common_time", "VD_Frame_ID")

        F["Time_Driving_Side"],F["Driving_Side"]             = kbtools.GetSignal(Source, "Video_Data_General_B", "Driving_Side")
        if F["Time_Driving_Side"] is None:
            F["Time_Driving_Side"],F["Driving_Side"] = kbtools.GetSignal(Source, "t_common_time", "VD_Driving_Side")

        F["Time_Day_Time_Indicator"],F["Day_Time_Indicator"] = kbtools.GetSignal(Source, "Video_Data_General_B", "Day_Time_Indicator")
        if F["Time_Day_Time_Indicator"] is None:
            F["Time_Day_Time_Indicator"],F["Day_Time_Indicator"] = kbtools.GetSignal(Source, "t_common_time", "VD_Day_Time_Indicator")
        
        F["Time_CAN_Delay"],F["CAN_Delay"]                   = kbtools.GetSignal(Source, "Video_Data_General_B", "CAN_Delay")
        if F["Time_CAN_Delay"] is None:
            F["Time_CAN_Delay"],F["CAN_Delay"] = kbtools.GetSignal(Source, "t_common_time", "VD_CAN_Delay")
 
        # ------------------------------------------------
        # 3. Video_Object_Header - third message
        F["Time_Message_Counter_Header"],F["Message_Counter_Header"]     = kbtools.GetSignal(Source, "Video_Object_Header", "Message_Counter_Header")
        F["Time_Number_Of_Objects"],F["Number_Of_Objects"]               = kbtools.GetSignal(Source, "Video_Object_Header", "Number_Of_Objects")
        F["Time_ID_CIPV"],F["ID_CIPV"]                                   = kbtools.GetSignal(Source, "Video_Object_Header", "ID_CIPV")
        F["Time_Right_Close_Range_Cut_In"],F["Right_Close_Range_Cut_In"] = kbtools.GetSignal(Source, "Video_Object_Header", "Right_Close_Range_Cut_In")
        F["Time_Left_Close_Range_Cut_In"],F["Left_Close_Range_Cut_In"]   = kbtools.GetSignal(Source, "Video_Object_Header", "Left_Close_Range_Cut_In")
        
       
        # --------------------------------------------------------------
        # 4.1 Video_Object_Header
        F["Time_Message_Counter_Header"],F["Message_Counter_Header"]     = kbtools.GetSignal(Source, "Video_Object_Header", "Message_Counter_Header")
        
        F["Time_Number_Of_Objects"],F["Number_Of_Objects"]               = kbtools.GetSignal(Source, "Video_Object_Header", "Number_Of_Objects")
                
        F["Time_Right_Close_Range_Cut_In"],F["Right_Close_Range_Cut_In"] = kbtools.GetSignal(Source, "Video_Object_Header", "Right_Close_Range_Cut_In")
        F["Time_Left_Close_Range_Cut_In"],F["Left_Close_Range_Cut_In"]   = kbtools.GetSignal(Source, "Video_Object_Header", "Left_Close_Range_Cut_In")
        
        F["Time_ID_CIPV"],F["ID_CIPV"]                                   = kbtools.GetSignal(Source, "Video_Object_Header", "ID_CIPV")
        F["Time_Ped_In_Danger_Zone"],F["Ped_In_Danger_Zone"]             = kbtools.GetSignal(Source, "Video_Object_Header", "Ped_In_Danger_Zone")
        F["Time_Ped_FCW_On"],F["Ped_FCW_On"]                             = kbtools.GetSignal(Source, "Video_Object_Header", "Ped_FCW_On")
        F["Time_FCW_On"],F["FCW_On"]                                     = kbtools.GetSignal(Source, "Video_Object_Header", "FCW_On")


        # ------------------------------------------------
        # 4.2 Video_Object_X_A .. Video_Object_X_D  
        # todo
        VideoObjects = range(0,cDataAC100.N_FLC20_VideoObj)
        
        for k in VideoObjects:
            s = "%d"%k
            if cDataAC100.verbose:
                print "k", k,"s",s
            
            T={}
            F[k] = T
              
            # .........................................
            #  Video_Object_0_A
            T["Time_Message_Counter_Video_Object_A"],T["Message_Counter_Video_Object_A"] = kbtools.GetSignal(Source, "Video_Object_%s_A"%s, "Message_Counter_%s_A"%s)
            
            T["Time_ID"],T["ID"] = kbtools.GetSignal(Source, "Video_Object_%s_A"%s, "ID_%s_A"%s)
            
            T["Time_Longitudinal_Distance"],     T["Longitudinal_Distance"]     = kbtools.GetSignal(Source, "Video_Object_%s_A"%s, "Longitudinal_Distance_%s_A"%s)
            T["Time_Relative_Velocity"],         T["Relative_Velocity"]         = kbtools.GetSignal(Source, "Video_Object_%s_A"%s, "Relative_Velocity_%s_A"%s)
            T["Time_Right_Angle"],               T["Right_Angle"]               = kbtools.GetSignal(Source, "Video_Object_%s_A"%s, "Right_Angle_%s_A"%s)
            T["Time_Left_Angle"],                T["Left_Angle"]                = kbtools.GetSignal(Source, "Video_Object_%s_A"%s, "Left_Angle_%s_A"%s)
            T["Time_Class"],                     T["Class"]                     = kbtools.GetSignal(Source, "Video_Object_%s_A"%s, "Class_%s_A"%s)
            
            #.........................................
            #  Video_Object_0_B
            T["Time_Message_Counter_Video_Object_B"],T["Message_Counter_Video_Object_B"] = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Message_Counter_%s_B"%s)

            T["Time_Width"],                     T["Width"]                     = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Width_%s_B"%s)
            T["Time_Lane"],                      T["Lane"]                      = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Lane_%s_B"%s)
            T["Time_Rate_Mean_Angle"],           T["Rate_Mean_Angle"]           = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Rate_Mean_Angle_%s_B"%s)
            T["Time_Detection_Score"],           T["Detection_Score"]           = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Detection_Score_%s_B"%s)
            T["Time_Motion_Status"],             T["Motion_Status"]             = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Motion_Status_%s_B"%s)
            T["Time_Inverse_TTC"],               T["Inverse_TTC"]               = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Inverse_TTC_%s_B"%s)
            T["Time_Indicator"],                 T["Indicator"]                 = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Indicator_%s_B"%s)
            T["Time_Brake_Light"],               T["Brake_Light"]               = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Brake_Light_%s_B"%s)
            T["Time_Longitudinal_Distance_STD"], T["Longitudinal_Distance_STD"] = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Longitudinal_Distance_STD_%s_B"%s)
            T["Time_Relative_Velocity_STD"],     T["Relative_Velocity_STD"]     = kbtools.GetSignal(Source, "Video_Object_%s_B"%s, "Relative_Velocity_STD_%s_B"%s)
           
            # .........................................
            # Video_Object_0_C
            T["Time_Message_Counter_Video_Object_C"],T["Message_Counter_Video_Object_C"] = kbtools.GetSignal(Source, "Video_Object_%s_C"%s, "Message_Counter_%s_C"%s)

            T["Time_Lateral_Distance"],          T["Lateral_Distance"]          = kbtools.GetSignal(Source, "Video_Object_%s_C"%s, "Lateral_Distance_%s_C"%s)
            T["Time_Lane_Movement_Type"],        T["Lane_Movement_Type"]        = kbtools.GetSignal(Source, "Video_Object_%s_C"%s, "Lane_Movement_Type_%s_C"%s)
            T["Time_ID_extended"],               T["ID_extended"]               = kbtools.GetSignal(Source, "Video_Object_%s_C"%s, "ID_extended_%s_C"%s)
            T["Time_Angle_STD"],                 T["Angle_STD"]                 = kbtools.GetSignal(Source, "Video_Object_%s_C"%s, "Angle_STD_%s_C"%s)
            T["Time_Acceleration_Abs"],          T["Acceleration_Abs"]          = kbtools.GetSignal(Source, "Video_Object_%s_C"%s, "Acceleration_Abs_%s_C"%s)
                      
            # .........................................
            # Video_Object_0_D
            T["Time_Message_Counter_Video_Object_D"],T["Message_Counter_Video_Object_D"] = kbtools.GetSignal(Source, "Video_Object_%s_D"%s, "Message_Counter_%s_D"%s)


            T["Time_Upper_Right_Top_from_FOE"],  T["Upper_Right_Top_from_FOE"]  = kbtools.GetSignal(Source, "Video_Object_%s_D"%s, "Upper_Right_Top_from_FOE_%s_D"%s)
            T["Time_Upper_Right_Right_from_FOE"],T["Upper_Right_Right_from_FOE"]= kbtools.GetSignal(Source, "Video_Object_%s_D"%s, "Upper_Right_Right_from_FOE_%s_D"%s)
            T["Time_Lower_Left_Left_from_FOE"],  T["Lower_Left_Left_from_FOE"]  = kbtools.GetSignal(Source, "Video_Object_%s_D"%s, "Lower_Left_Left_from_FOE_%s_D"%s)
            T["Time_Lower_Left_Bottom_from_FOE"],T["Lower_Left_Bottom_from_FOE"]= kbtools.GetSignal(Source, "Video_Object_%s_D"%s, "Lower_Left_Bottom_from_FOE_%s_D"%s)
            T["Time_FOE_X"],  T["FOE_X"]                                        = kbtools.GetSignal(Source, "Video_Object_%s_D"%s, "FOE_X_%s_D"%s)
            T["Time_FOE_Y"],  T["FOE_Y"]                                        = kbtools.GetSignal(Source, "Video_Object_%s_D"%s, "FOE_Y_%s_D"%s)
            
    
        # -------------------------------------------------
        # Video_Lane_Header
        F["Time_Message_Counter_Lane_Header"],F["Message_Counter_Lane_Header"] = kbtools.GetSignal(Source, "Video_Lane_Header", "Message_Counter_Lane_Header")
        
        F["Time_Construction_Area"],F["Construction_Area"]                     = kbtools.GetSignal(Source, "Video_Lane_Header", "Construction_Area")
        if F["Time_Construction_Area"] is None:
            F["Time_Construction_Area"],F["Construction_Area"] = kbtools.GetSignal(Source, "t_common_time", "VLH_Construction_Area")

        F["Time_Road_Type"],F["Road_Type"]                                     = kbtools.GetSignal(Source, "Video_Lane_Header", "Road_Type")
        F["Time_LaneModuleValid"],F["LaneModuleValid"]                         = kbtools.GetSignal(Source, "Video_Lane_Header", "LaneModuleValid")

                
        # ------------------------------------------------
        # Video Lane Left and Right
        # common:
        VideoLanes = ['Left','Right']
        VideoLanes = ['Left','Right','Next_Left','Next_Right']
        
        for s in VideoLanes:
            if cDataAC100.verbose:
                print "s", s
            F["Time_Message_Counter_%s_A"%s],F["Message_Counter_%s_A"%s] = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "Message_Counter_%s_A"%s)
            if F["Time_Message_Counter_%s_A"%s] is None:
                F["Time_Message_Counter_%s_A"%s],F["Message_Counter_%s_A"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_Message_Counter_%s_A"%s)
            
            F["Time_Message_Counter_%s_B"%s],F["Message_Counter_%s_B"%s] = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "Message_Counter_%s_B"%s)
            if F["Time_Message_Counter_%s_B"%s] is None:
                F["Time_Message_Counter_%s_B"%s],F["Message_Counter_%s_B"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_Message_Counter_%s_B"%s)

            F["Time_View_Range_%s"%s],     F["View_Range_%s"%s]      = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "View_Range_%s_B"%s)
            if F["Time_View_Range_%s"%s] is None:
                F["Time_View_Range_%s"%s],F["View_Range_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_View_Range_%s_B"%s)

            F["Time_Lane_Crossing_%s"%s],  F["Lane_Crossing_%s"%s]   = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "Lane_Crossing_%s_B"%s)
         
            # old: Video_Fusion_Protocol_Released_v1.4b_Mar_27_2013_TrwDebug_mod.dbc
            F["Time_C0_%s"%s], F["C0_%s"%s]  = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "Position_%s_A"%s)
            F["Time_C1_%s"%s], F["C1_%s"%s]  = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "Heading_%s_A"%s)
            F["Time_C2_%s"%s], F["C2_%s"%s]  = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "Curvature_%s_A"%s)
            if F["C2_%s"%s] is not None:
                F["C2_%s"%s] = F["C2_%s"%s]/2.0
            F["Time_C3_%s"%s], F["C3_%s"%s]  = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "Curvature_Rate_%s_A"%s)
            if F["C3_%s"%s] is not None:
                F["C3_%s"%s] = F["C3_%s"%s]/6.0
            F["Time_TLC_%s"%s],F["TLC_%s"%s] = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "TLC_%s_B"%s)
        
            # ---------------------------------------------------------------------
            # new: Video_Fusion_Protocol_2014-03-27_Bendix_mod.dbc
            
            # initialize signals which are not already exists
            F["Time_Line_Type_%s"%s],F["Line_Type_%s"%s] = None, None
            F["Time_Quality_%s"%s],  F["Quality_%s"%s]   = None, None
            
            if F["Time_C0_%s"%s] is None:
                F["Time_C0_%s"%s],F["C0_%s"%s]   = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "C0_%s_A"%s)
                if F["Time_C0_%s"%s] is None:
                    F["Time_C0_%s"%s],F["C0_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_C0_%s_A"%s)

                F["Time_C1_%s"%s],F["C1_%s"%s]   = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "C1_%s_A"%s)
                if F["Time_C1_%s"%s] is None:
                    F["Time_C1_%s"%s],F["C1_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_C1_%s_A"%s)

                F["Time_C2_%s"%s],F["C2_%s"%s]   = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "C2_%s_A"%s)
                if F["Time_C2_%s"%s] is None:
                    F["Time_C2_%s"%s],F["C2_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_C2_%s_A"%s)

                F["Time_C3_%s"%s],F["C3_%s"%s]   = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "C3_%s_A"%s)
                if F["Time_C3_%s"%s] is None:
                    F["Time_C3_%s"%s],F["C3_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_C3_%s_A"%s)
       
                F["Time_Line_Type_%s"%s],F["Line_Type_%s"%s] = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "Line_Type_%s_A"%s)
                if F["Time_Line_Type_%s"%s] is None:
                    F["Time_Line_Type_%s"%s],F["Line_Type_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_Line_Type_%s_A"%s)
                
                F["Time_Quality_%s"%s],F["Quality_%s"%s] = kbtools.GetSignal(Source, "Video_Lane_%s_A"%s, "Quality_%s_A"%s)
                if F["Time_Quality_%s"%s] is None:
                    F["Time_Quality_%s"%s],F["Quality_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_Quality_%s_A"%s)
            
            
            
            # initialize signals which are not already exists
            F["Time_ME_TLC_%s"%s],          F["ME_TLC_%s"%s]           = None, None
            F["Time_Me_Line_Changed_%s"%s], F["Me_Line_Changed_%s"%s]  = None, None
            F["Time_Line_Width_%s"%s],      F["Line_Width_%s"%s]       = None, None
            F["Time_Lateral_Velocity_%s"%s],F["Lateral_Velocity_%s"%s] = None, None
            F["Time_C0_right_wheel_%s"%s],  F["C0_right_wheel_%s"%s]   = None, None
            F["Time_BX_TLC_%s"%s],          F["BX_TLC_%s"%s]           = None, None
            
            if F["Time_TLC_%s"%s] is None:
                F["Time_TLC_%s"%s],F["TLC_%s"%s]                           = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "ME_TLC_%s_B"%s)
                if F["Time_TLC_%s"%s] is None:
                    F["Time_TLC_%s"%s],F["TLC_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_TLC_%s_A"%s)

                F["Time_ME_TLC_%s"%s],F["ME_TLC_%s"%s]                     = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "ME_TLC_%s_B"%s)
                F["Time_Me_Line_Changed_%s"%s],F["Me_Line_Changed_%s"%s]   = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "Me_Line_Changed_%s_B"%s)
                if F["Time_Me_Line_Changed_%s"%s] is None:
                    F["Time_Me_Line_Changed_%s"%s],F["Me_Line_Changed_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_Me_Line_Changed_%s_B"%s)

                F["Time_Line_Width_%s"%s],F["Line_Width_%s"%s]             = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "Line_Width_%s_B"%s)
                if F["Time_Line_Width_%s"%s] is None:
                    F["Time_Line_Width_%s"%s],F["Line_Width_%s"%s] = kbtools.GetSignal(Source, "t_common_time", "VL_Line_Width_%s_B"%s)
                
                F["Time_Lateral_Velocity_%s"%s],F["Lateral_Velocity_%s"%s] = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "Lateral_Velocity_%s_B"%s)
                F["Time_C0_right_wheel_%s"%s],F["C0_right_wheel_%s"%s]     = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "C0_right_wheel_%s_B"%s)
                F["Time_BX_TLC_%s"%s],F["BX_TLC_%s"%s]                     = kbtools.GetSignal(Source, "Video_Lane_%s_B"%s, "BX_TLC_%s_B"%s)
        
        # -------------------------------------------------------------
        # workaround for VL_Message_Counter_Next_Left_B not available
        if F["Time_Message_Counter_Next_Left_B"] is None:
            F["Time_Message_Counter_Next_Left_B"],F["Message_Counter_Next_Left_B"] = kbtools.GetSignal(Source, "t_common_time", "VL_Message_Counter_Left_B")
        
        
        # ------------------------------------------------
        # Bendix Infos 1
  
        F["Time_Message_Counter_Bendix_Info"],F["Message_Counter_Bendix_Info"] = kbtools.GetSignal(Source, "Bendix_Info", "Message_Counter_Bendix_Info")
        if F["Time_Message_Counter_Bendix_Info"] is None:
            F["Time_Message_Counter_Bendix_Info"],F["Message_Counter_Bendix_Info"] = kbtools.GetSignal(Source, "t_common_time", "BX1_Message_Counter_Bendix_Info")
        
        F["Time_C0_left_wheel"], F["C0_left_wheel"]                            = kbtools.GetSignal(Source, "Bendix_Info", "C0_left_wheel")
        if F["Time_C0_left_wheel"] is None:
            F["Time_C0_left_wheel"],F["C0_left_wheel"] = kbtools.GetSignal(Source, "t_common_time", "BX1_C0_left_wheel")

        F["Time_C0_right_wheel"],F["C0_right_wheel"]                           = kbtools.GetSignal(Source, "Bendix_Info", "C0_right_wheel")
        if F["Time_C0_right_wheel"] is None:
            F["Time_C0_right_wheel"],F["C0_right_wheel"] = kbtools.GetSignal(Source, "t_common_time", "BX1_C0_right_wheel")
  
        F["Time_LDW_LaneDeparture_Left"], F["LDW_LaneDeparture_Left"]          = kbtools.GetSignal(Source, "Bendix_Info", "LDW_LaneDeparture_Left")
        if F["Time_LDW_LaneDeparture_Left"] is None:
            F["Time_LDW_LaneDeparture_Left"],F["LDW_LaneDeparture_Left"] = kbtools.GetSignal(Source, "t_common_time", "BX1_LDW_LaneDeparture_Left")
  
        F["Time_LDW_LaneDeparture_Right"],F["LDW_LaneDeparture_Right"]         = kbtools.GetSignal(Source, "Bendix_Info", "LDW_LaneDeparture_Right")
        if F["Time_LDW_LaneDeparture_Right"] is None:
            F["Time_LDW_LaneDeparture_Right"],F["LDW_LaneDeparture_Right"] = kbtools.GetSignal(Source, "t_common_time", "BX1_LDW_LaneDeparture_Right")
        
        F["Time_ME_LDW_LaneDeparture_Left"], F["ME_LDW_LaneDeparture_Left"]    = kbtools.GetSignal(Source, "Bendix_Info", "ME_LDW_LaneDeparture_Left")
        if F["Time_ME_LDW_LaneDeparture_Left"] is None:
            F["Time_ME_LDW_LaneDeparture_Left"],F["ME_LDW_LaneDeparture_Left"] = kbtools.GetSignal(Source, "t_common_time", "BX1_ME_LDW_LaneDeparture_Left")

        F["Time_ME_LDW_LaneDeparture_Right"],F["ME_LDW_LaneDeparture_Right"]   = kbtools.GetSignal(Source, "Bendix_Info", "ME_LDW_LaneDeparture_Right")
        if F["Time_ME_LDW_LaneDeparture_Right"] is None:
            F["Time_ME_LDW_LaneDeparture_Right"],F["ME_LDW_LaneDeparture_Right"] = kbtools.GetSignal(Source, "t_common_time", "BX1_ME_LDW_LaneDeparture_Right")

        
        F["Time_Traffic_Sign_Type"],   F["Traffic_Sign_Type"]                  = kbtools.GetSignal(Source, "Bendix_Info", "Traffic_Sign_Type")
        if F["Time_Traffic_Sign_Type"] is None:
            F["Time_Traffic_Sign_Type"],F["Traffic_Sign_Type"] = kbtools.GetSignal(Source, "t_common_time", "BX1_Traffic_Sign_Type")
        F["Time_Traffic_Sign_Warning"],F["Traffic_Sign_Warning"]               = kbtools.GetSignal(Source, "Bendix_Info", "Traffic_Sign_Warning")
        if F["Time_Traffic_Sign_Warning"] is None:
            F["Time_Traffic_Sign_Warning"],F["Traffic_Sign_Warning"] = kbtools.GetSignal(Source, "t_common_time", "BX1_Traffic_Sign_Warning")
        
        # ???
        #F["Time_TrwDebugMEState"],F["TrwDebugMEState"]           = kbtools.GetSignal(Source, "Bendix_Info", "TrwDebugMEState")
        
        # -------------------------------------------------------
        # LDW Suppression bit mask 
        F["Time_BX_LDW_Suppr"],F["BX_LDW_Suppr"]                               = kbtools.GetSignal(Source, "Bendix_Info", "BX_LDW_Suppr")
        if F["Time_BX_LDW_Suppr"] is None:
            F["Time_BX_LDW_Suppr"],F["BX_LDW_Suppr"] = kbtools.GetSignal(Source, "t_common_time", "BX1_BX_LDW_Suppr")
                 
        # reason codes for Bendix LDW warning suppressing
        #  WS_ALARM_QUIET_TIME       0x0001u
        #  WS_SYSTEM_DISABLED        0x0002u
        #  WS_LOW_SPEED              0x0004u
        #  WS_TURN_SIGNAL            0x0008u
        
        #  WS_HAZARD_LIGHTS          0x0010u
        #  WS_HIGH_DECEL             0x0020u
        #  WS_HIGH_LATVEL            0x0040u
        #  WS_BRAKE_PRESSED          0x0080u
        
        #  WS_HIGH_CURVATURE         0x0100u
        #  WS_HIGH_STEERING_RATE     0x0200u
        #  WS_CONSTRUCTION_ZONE      0x0400u
        #  WS_ACC_ALERT_ACTIVE       0x0800u
 
        if F["BX_LDW_Suppr"] is not None:
            F["BX_LDW_Suppr_ALARM_QUIET_TIME"]   = np.bitwise_and(F["BX_LDW_Suppr"],0x0001)>0  
            F["BX_LDW_Suppr_SYSTEM_DISABLED"]    = np.bitwise_and(F["BX_LDW_Suppr"],0x0002)>0  
            F["BX_LDW_Suppr_LOW_SPEED"]          = np.bitwise_and(F["BX_LDW_Suppr"],0x0004)>0  
            F["BX_LDW_Suppr_TURN_SIGNAL"]        = np.bitwise_and(F["BX_LDW_Suppr"],0x0008)>0  
        
            F["BX_LDW_Suppr_HAZARD_LIGHTS"]      = np.bitwise_and(F["BX_LDW_Suppr"],0x0010)>0  
            F["BX_LDW_Suppr_HIGH_DECEL"]         = np.bitwise_and(F["BX_LDW_Suppr"],0x0020)>0 
            F["BX_LDW_Suppr_HIGH_LATVEL"]        = np.bitwise_and(F["BX_LDW_Suppr"],0x0040)>0 
            F["BX_LDW_Suppr_BRAKE_PRESSED"]      = np.bitwise_and(F["BX_LDW_Suppr"],0x0080)>0 
        
            F["BX_LDW_Suppr_HIGH_CURVATURE"]     = np.bitwise_and(F["BX_LDW_Suppr"],0x0100)>0 
            F["BX_LDW_Suppr_HIGH_STEERING_RATE"] = np.bitwise_and(F["BX_LDW_Suppr"],0x0200)>0 
            F["BX_LDW_Suppr_CONSTRUCTION_ZONE"]  = np.bitwise_and(F["BX_LDW_Suppr"],0x0400)>0 
            F["BX_LDW_Suppr_ACC_ALERT_ACTIVE"]   = np.bitwise_and(F["BX_LDW_Suppr"],0x0800)>0 
            
        else:             
            F["BX_LDW_Suppr_ALARM_QUIET_TIME"]   = None
            F["BX_LDW_Suppr_SYSTEM_DISABLED"]    = None
            F["BX_LDW_Suppr_LOW_SPEED"]          = None  
            F["BX_LDW_Suppr_TURN_SIGNAL"]        = None  
        
            F["BX_LDW_Suppr_HAZARD_LIGHTS"]      = None  
            F["BX_LDW_Suppr_HIGH_DECEL"]         = None 
            F["BX_LDW_Suppr_HIGH_LATVEL"]        = None 
            F["BX_LDW_Suppr_BRAKE_PRESSED"]      = None 
        
            F["BX_LDW_Suppr_HIGH_CURVATURE"]     = None 
            F["BX_LDW_Suppr_HIGH_STEERING_RATE"] = None 
            F["BX_LDW_Suppr_CONSTRUCTION_ZONE"]  = None 
            F["BX_LDW_Suppr_ACC_ALERT_ACTIVE"]   = None 
    
        # ------------------------------------------------
        # Bendix Infos 2
  
        F["Time_Message_Counter_Bendix_Info2"],F["Message_Counter_Bendix_Info2"] = kbtools.GetSignal(Source, "Bendix_Info2", "Message_Counter_Bendix_Info2")
        if F["Time_Message_Counter_Bendix_Info2"] is None:
            F["Time_Message_Counter_Bendix_Info2"],F["Message_Counter_Bendix_Info2"] = kbtools.GetSignal(Source, "t_common_time", "BX2_Message_Counter_Bendix_Info2")

        F["Time_BX_TLC_B"], F["BX_TLC_B"]  = kbtools.GetSignal(Source, "Bendix_Info2", "BX_TLC_B") # [s]
        if F["Time_BX_TLC_B"] is None:
            F["Time_BX_TLC_B"],F["BX_TLC_B"] = kbtools.GetSignal(Source, "t_common_time", "BX2_BX_TLC_B")
        
        F["Time_C0_right_wheel_Right_B"],   F["C0_right_wheel_Right_B"]   = kbtools.GetSignal(Source, "Bendix_Info2", "C0_right_wheel_Right_B")
        if F["Time_C0_right_wheel_Right_B"] is None:
            F["Time_C0_right_wheel_Right_B"],F["C0_right_wheel_Right_B"] = kbtools.GetSignal(Source, "t_common_time", "BX2_C0_right_wheel_Right_B")
        F["Time_C0_left_wheel_Left_B"],     F["C0_left_wheel_Left_B"]     = kbtools.GetSignal(Source, "Bendix_Info2", "C0_left_wheel_Left_B")
        if F["Time_C0_left_wheel_Left_B"] is None:
            F["Time_C0_left_wheel_Left_B"],F["C0_left_wheel_Left_B"] = kbtools.GetSignal(Source, "t_common_time", "BX2_C0_left_wheel_Left_B")

        F["Time_Lateral_Velocity_Right_B"], F["Lateral_Velocity_Right_B"] = kbtools.GetSignal(Source, "Bendix_Info2", "Lateral_Velocity_Right_B")
        if F["Time_Lateral_Velocity_Right_B"] is None:
            F["Time_Lateral_Velocity_Right_B"],F["Lateral_Velocity_Right_B"] = kbtools.GetSignal(Source, "t_common_time", "BX2_Lateral_Velocity_Right_B")
        F["Time_Lateral_Velocity_Left_B"],  F["Lateral_Velocity_Left_B"]  = kbtools.GetSignal(Source, "Bendix_Info2", "Lateral_Velocity_Left_B")
        if F["Time_Lateral_Velocity_Left_B"] is None:
            F["Time_Lateral_Velocity_Left_B"],F["Lateral_Velocity_Left_B"] = kbtools.GetSignal(Source, "t_common_time", "BX2_Lateral_Velocity_Left_B")
       
       
       
        # ------------------------------------------------
        # Bendix Infos 3
  
        F["Time_Message_Counter_Bendix_Info3"],F["Message_Counter_Bendix_Info3"] = kbtools.GetSignal(Source, "Bendix_Info3", "Message_Counter_Bendix_Info3")
        if F["Time_Message_Counter_Bendix_Info3"] is None:
            F["Time_Message_Counter_Bendix_Info3"],F["Message_Counter_Bendix_Info3"] = kbtools.GetSignal(Source, "t_common_time", "BX3_Message_Counter_Bendix_Info3")
       
        F["Time_LNVU_isWarningLeft"], F["LNVU_isWarningLeft"]  = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_LNVU_isWarningLeft")
        if F["Time_LNVU_isWarningLeft"] is None:
            F["Time_LNVU_isWarningLeft"],F["LNVU_isWarningLeft"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_LNVU_isWarningLeft")
        F["Time_LNVU_isWarningRight"],F["LNVU_isWarningRight"] = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_LNVU_isWarningRight")
        if F["Time_LNVU_isWarningRight"] is None:
            F["Time_LNVU_isWarningRight"],F["LNVU_isWarningRight"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_LNVU_isWarningRight")

        F["Time_LNVU_TimeBased_flag"],F["LNVU_TimeBased_flag"] = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_LNVU_TimeBased_flag")
        if F["Time_LNVU_TimeBased_flag"] is None:
            F["Time_LNVU_TimeBased_flag"],F["LNVU_TimeBased_flag"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_LNVU_TimeBased_flag")
        F["Time_LNVU_Frame_Id_LSB"],F["LNVU_Frame_Id_LSB"]     = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_LNVU_Frame_Id_LSB")
        if F["Time_LNVU_Frame_Id_LSB"] is None:
            F["Time_LNVU_Frame_Id_LSB"],F["LNVU_Frame_Id_LSB"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_LNVU_Frame_Id_LSB")
            
        F["Time_LNVU_AlgoState"],F["LNVU_AlgoState"]           = kbtools.GetSignal(Source, "Bendix_Info3", "LNVU_AlgoState")
        if F["Time_LNVU_AlgoState"] is None:
            F["Time_LNVU_AlgoState"],F["LNVU_AlgoState"] = kbtools.GetSignal(Source, "t_common_time", "BX3_LNVU_AlgoState")
        F["Time_Space_mm"],F["Space_mm"]                       = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_Space_mm")
        if F["Time_Space_mm"] is None:
            F["Time_Space_mm"],F["Space_mm"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_Space_mm")

        F["Time_TLC_thresh_right_ms"],F["TLC_thresh_right_ms"] = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_TLC_thresh_right_ms")
        if F["Time_TLC_thresh_right_ms"] is None:
            F["Time_TLC_thresh_right_ms"],F["TLC_thresh_right_ms"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_TLC_thresh_right_ms")
        F["Time_TLC_thresh_left_ms"], F["TLC_thresh_left_ms"]  = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_TLC_thresh_left_ms")
        if F["Time_TLC_thresh_left_ms"] is None:
            F["Time_TLC_thresh_left_ms"],F["TLC_thresh_left_ms"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_TLC_thresh_left_ms")

        F["Time_D_margin_right_mm"], F["D_margin_right_mm"]    = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_D_margin_right_mm")
        if F["Time_D_margin_right_mm"] is None:
            F["Time_D_margin_right_mm"],F["D_margin_right_mm"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_D_margin_right_mm")
        F["Time_D_margin_left_mm"], F["D_margin_left_mm"]      = kbtools.GetSignal(Source, "Bendix_Info3", "DEBUG_D_margin_left_mm")
        if F["Time_D_margin_left_mm"] is None:
            F["Time_D_margin_left_mm"],F["D_margin_left_mm"] = kbtools.GetSignal(Source, "t_common_time", "BX3_DEBUG_D_margin_left_mm")


        
        # ------------------------------------------------
       
        return F
       
  #============================================================================================
  @staticmethod
  def create_Multimedia(Source):
        
        Multimedia = {}        
        # ----------------------------------------------------------------        
        # Multimedia Signal
        Multimedia["Time_Multimedia_1"],Multimedia["Multimedia_1"]       = kbtools.GetSignal(Source, "Multimedia", "Multimedia_1")
        if Multimedia["Time_Multimedia_1"] is None:
            Multimedia["Time_Multimedia_1"],Multimedia["Multimedia_1"]       = kbtools.GetSignal(Source, "Multimedia", "Multimedia")
        
        
        Multimedia["Time_Multimedia_2"],Multimedia["Multimedia_2"]       = kbtools.GetSignal(Source, "Multimedia", "Multimedia_2")
        
        
        return Multimedia
     

  #============================================================================================
  @staticmethod
  def create_VBOX_LDWS_VCI(Source):
        
        F = {}
        F["Time_Range_Lt"],F["Range_Lt"]     = kbtools.GetSignal(Source, "VBOX_LDWS_VCI_1", "Range_Lt")
        F["Time_Range_Rt"],F["Range_Rt"]     = kbtools.GetSignal(Source, "VBOX_LDWS_VCI_1", "Range_Rt")

        F["Time_Lat_Spd_Lt"],F["Lat_Spd_Lt"] = kbtools.GetSignal(Source, "VBOX_LDWS_VCI_2", "Lat_Spd_Lt")
        F["Time_Lat_Spd_Rt"],F["Lat_Spd_Rt"] = kbtools.GetSignal(Source, "VBOX_LDWS_VCI_3", "Lat_Spd_Rt")

        F["Time_TTLC_Lt"],F["TTLC_Lt"]       = kbtools.GetSignal(Source, "VBOX_LDWS_VCI_3", "TTLC_Lt")
        F["Time_TTLC_Rt"],F["TTLC_Rt"]       = kbtools.GetSignal(Source, "VBOX_LDWS_VCI_4", "TTLC_Rt")
  
        F["Time_Angle"],F["Angle"]           = kbtools.GetSignal(Source, "VBOX_LDWS_VCI_4", "Angle")
        F["Time_Status"],F["Status"]         = kbtools.GetSignal(Source, "VBOX_LDWS_VCI_2", "TTLC_Rt")
    
       
        
        return F
  #============================================================================================
  @staticmethod
  def create_OxTS(Source):
        
        F = {}
        #FLR20_sig["Time_RightLinePosLateral"],FLR20_sig["RightLinePosLateral"] = kbtools.GetSignal(Source, "RightLineLateral", "RightLinePosLateral")
        #FLR20_sig["Time_LeftLinePosLateral"],FLR20_sig["LeftLinePosLateral"] = kbtools.GetSignal(Source, "LeftLineLateral", "LeftLinePosLateral")
      
        F["Time_RightFromCPosLateral"],F["RightFromCPosLateral"] = kbtools.GetSignal(Source, "LinesFromC", "RightFromCPosLateral")
        F["Time_LeftFromBPosLateral"],F["LeftFromBPosLateral"] = kbtools.GetSignal(Source, "LinesFromB", "LeftFromBPosLateral")
    
        F["Time_RightLineVelLateral"],F["RightLineVelLateral"] = kbtools.GetSignal(Source, "RightLineLateral", "RightLineVelLateral")
        F["Time_LeftLineVelLateral"],F["LeftLineVelLateral"] = kbtools.GetSignal(Source, "LeftLineLateral", "LeftLineVelLateral")

        F["Time_AccelForward"],F["AccelForward"] = kbtools.GetSignal(Source, "AccelLevel", "AccelForward")   # from rt3kfull_kph.dbc
        F["Time_AccelLateral"],F["AccelLateral"] = kbtools.GetSignal(Source, "AccelLevel", "AccelLateral")

        return F
       
     
  #============================================================================================
  @staticmethod
  def create_Bendix_ACC_Sxy2(Source):
        
        
        print "create_Bendix_ACC_Sxy2()"
        
        ACC_Sxy2 = {}        
        
        # ----------------------------------------------------------------        
        # TRW's allow entry and cancel flags 
        TRW_AECF = {} 
        
        
        # ACC_S03
        # a) global conditions
        TRW_AECF["Time"],TRW_AECF["cm_allow_entry_global_conditions"] = kbtools.GetSignal(Source, "ACC_S03", "cm_allow_entry_global_conditions")
        t_tmp1,          TRW_AECF["cm_cancel_global_conditions"]      = kbtools.GetSignal(Source, "ACC_S03", "cm_cancel_global_conditions")
        # b) cw collision warning 
        t_tmp2,          TRW_AECF["cw_allow_entry"]                   = kbtools.GetSignal(Source, "ACC_S03", "cw_allow_entry")
        t_tmp3,          TRW_AECF["cw_cancel"]                        = kbtools.GetSignal(Source, "ACC_S03", "cw_cancel")
        # c) cmb collision mitigation 
        t_tmp4,          TRW_AECF["cmb_allow_entry"]                  = kbtools.GetSignal(Source, "ACC_S03", "cmb_allow_entry")
        t_tmp5,          TRW_AECF["cmb_cancel"]                       = kbtools.GetSignal(Source, "ACC_S03", "cmb_cancel")

        
        if TRW_AECF["Time"] is None:
            # ACC_S30
            print "TRW_AECF from ACC_S30"
            
            # a) global conditions
            TRW_AECF["Time"],TRW_AECF["cm_allow_entry_global_conditions"] = kbtools.GetSignal(Source, "ACC_S30", "cm_allow_entry_global_conditions")
            t_tmp1,          TRW_AECF["cm_cancel_global_conditions"]      = kbtools.GetSignal(Source, "ACC_S30", "cm_cancel_global_conditions")
            # b) cw collision warning 
            t_tmp2,          TRW_AECF["cw_allow_entry"]                   = kbtools.GetSignal(Source, "ACC_S30", "cw_allow_entry")
            t_tmp3,          TRW_AECF["cw_cancel"]                        = kbtools.GetSignal(Source, "ACC_S30", "cw_cancel")
            # c) cmb collision mitigation 
            t_tmp4,          TRW_AECF["cmb_allow_entry"]                  = kbtools.GetSignal(Source, "ACC_S30", "cmb_allow_entry")
            t_tmp5,          TRW_AECF["cmb_cancel"]                       = kbtools.GetSignal(Source, "ACC_S30", "cmb_cancel")
        
        # assert
        t = TRW_AECF["Time"]
        
        #time_axes_are_equal = (t is t_tmp1) and (t is t_tmp2) and (t is t_tmp3) and (t is t_tmp4) and (t is t_tmp5)
        time_axes_are_equal = is_same(t,t_tmp1) and is_same(t,t_tmp2) and is_same(t,t_tmp3) and is_same(t,t_tmp4) and is_same(t,t_tmp5)
        print "time_axes_are_equal:",  time_axes_are_equal
        if not time_axes_are_equal:
            print "t", id(t), t
            if not is_same(t,t_tmp1):
                print "t_tmp1", id(t_tmp1), t_tmp1 
            if not is_same(t,t_tmp2):
                print "t_tmp2", id(t_tmp2), t_tmp2 
            if not is_same(t,t_tmp3):
                print "t_tmp3", id(t_tmp3), t_tmp3 
            if not is_same(t,t_tmp4):
                print "t_tmp4", id(t_tmp4), t_tmp4
            if not is_same(t,t_tmp5):
                print "t_tmp5", id(t_tmp5), t_tmp5
                
            TRW_AECF['Time']                             = None
            TRW_AECF['cm_allow_entry_global_conditions'] = None
            TRW_AECF['cw_allow_entry']                   = None
            TRW_AECF['cmb_allow_entry']                  = None
            TRW_AECF['cm_cancel_global_conditions']      = None
            TRW_AECF['cw_cancel']                        = None
            TRW_AECF['cmb_cancel']                       = None
     
        
        ACC_Sxy2["TRW_AECF"] = TRW_AECF
        
                    
        # --------------------------------------
        # additional signal for software-in-the-loop simulation        
                    
                    
        ACC_Sxy2["Time_cw_relaccel"],  ACC_Sxy2["cw_relaccel"]   = kbtools.GetSignal(Source, "ACC_S30", "cw_relaccel")   # "m/s2"
        ACC_Sxy2["Time_cw_latspeed"],  ACC_Sxy2["cw_latspeed"]   = kbtools.GetSignal(Source, "ACC_S30", "cw_latspeed")   # "m/s"
        ACC_Sxy2["Time_cw_vidconf"],   ACC_Sxy2["cw_vidconf"]    = kbtools.GetSignal(Source, "ACC_S30", "cw_vidconf")    # flag
 
        ACC_Sxy2["Time_cw_stopped"],   ACC_Sxy2["cw_stopped"]    = kbtools.GetSignal(Source, "ACC_S30", "cw_stopped")    # flag
        ACC_Sxy2["Time_cw_stationary"],ACC_Sxy2["cw_stationary"] = kbtools.GetSignal(Source, "ACC_S30", "cw_stationary") # flag
        ACC_Sxy2["Time_cw_moving"],    ACC_Sxy2["cw_moving"]     = kbtools.GetSignal(Source, "ACC_S30", "cw_moving")     # flag

         
                
        return ACC_Sxy2

  #============================================================================================
  @staticmethod
  def calc_CW_track_performance(AC100_sig): 
      # t_center : time stamp of last uninterrupted S1 appearance
      t     = AC100_sig['PosMatrix']['CW']['Time']
      Valid = AC100_sig['PosMatrix']['CW']['Valid']
      CW_appearance_list = kbtools.scan4handles(Valid)
      if cDataAC100.verbose:
        print "No of CW segments:", len(CW_appearance_list)
        print [t[x] for x in CW_appearance_list]
    
      last_CW_appearance = CW_appearance_list[-1] 
      t_center = np.mean(t[last_CW_appearance])
      if cDataAC100.verbose:
        print t_center
  
      # Handle at t_center
      t = AC100_sig['PosMatrix']['CW']['Time']
      CW_TrackNo_at_t_center = int(AC100_sig['PosMatrix']['CW']['TrackNo'][t>t_center][0])
      
      t = AC100_sig['AC100_tracks'][CW_TrackNo_at_t_center]['Time']
      CW_TrackId_at_t_center = int(AC100_sig['AC100_tracks'][CW_TrackNo_at_t_center]["id"][t>t_center][0])
    
      if cDataAC100.verbose:
        print "CW_TrackNo_at_t_center", CW_TrackNo_at_t_center
        print "CW_TrackId_at_t_center", CW_TrackId_at_t_center
  
      t = AC100_sig['AC100_tracks'][CW_TrackNo_at_t_center]['Time']
      bool_signal = AC100_sig['AC100_tracks'][CW_TrackNo_at_t_center]["id"] == CW_TrackId_at_t_center
      start_idx, stop_idx = kbtools.getIntervalAroundEvent(t,t_center,bool_signal)
      if cDataAC100.verbose:
        print start_idx, stop_idx
        print t[start_idx], t[stop_idx]

        print "track dx ", AC100_sig['AC100_tracks'][CW_TrackNo_at_t_center]['dx'][start_idx] 
        print "CW dx max", AC100_sig['PosMatrix']['CW']['dx'][last_CW_appearance[0]]
        print "CW dx min", AC100_sig['PosMatrix']['CW']['dx'][last_CW_appearance[1]]
  
      AC100_res = {}
      AC100_res['TrackNo'] = CW_TrackNo_at_t_center
      AC100_res['max_dx_CW']   = AC100_sig['PosMatrix']['CW']['dx'][last_CW_appearance[0]]
      AC100_res['t_max_dx_CW'] = AC100_sig['PosMatrix']['CW']['Time'][last_CW_appearance[0]]
      
      AC100_res['min_dx_CW']   = AC100_sig['PosMatrix']['CW']['dx'][last_CW_appearance[1]]
      AC100_res['t_min_dx_CW'] = AC100_sig['PosMatrix']['CW']['Time'][last_CW_appearance[1]]
      
      return AC100_res

  #============================================================================================
  @staticmethod
  def plot_AC100_CW_track(sig, FigNr=200,xlim = None):
    # plot collision warning CW track
 
    AC100 = sig['PosMatrix']
    
    ObjName='CW'

    fig = pl.figure(FigNr); FigNr +=1
    fig.clear()
    fig.suptitle('%s track'%ObjName)

    #  signal availibility 
    sp = fig.add_subplot(611)
    sp.plot(AC100[ObjName]['Time'], AC100[ObjName]['Valid'] )
    sp.legend(('Valid',))
    sp.grid()
    sp.set_ylim(-0.1,1.1) 
    if xlim:
      sp.set_xlim(xlim)
      
    # longitudinal distance to CIPV
    sp = fig.add_subplot(612)
    sp.plot(AC100[ObjName]['Time'], AC100[ObjName]['dx'] )
    sp.legend(('dx',))
    sp.set_ylabel('[m]')
    sp.grid()
    if xlim:
      sp.set_xlim(xlim)

    # lateral distance to CIPV
    sp = fig.add_subplot(613)
    sp.plot(AC100[ObjName]['Time'], AC100[ObjName]['dy'] )
    sp.legend(('dy',))
    sp.set_ylabel('[m]')
    sp.grid()
    if xlim:
      sp.set_xlim(xlim)
    
    # relative velocity of CIPV
    sp = fig.add_subplot(614)
    sp.plot(AC100[ObjName]['Time'], AC100[ObjName]['vx'] )
    sp.legend(('vx',))
    sp.set_ylabel('[m/s]')
    sp.grid()
    if xlim:
      sp.set_xlim(xlim)

    # acceleration over ground of CIPV
    sp = fig.add_subplot(615)
    sp.plot(AC100[ObjName]['Time'], AC100[ObjName]['ax_ground'] )
    sp.legend(('ax_ground',))
    sp.set_ylabel('[m/s^2]')
    sp.grid()
    if xlim:
      sp.set_xlim(xlim)

    # CIPV is stationary
    sp = fig.add_subplot(616)
    sp.plot(AC100[ObjName]['Time'], AC100[ObjName]['Stand_b'] )
    sp.legend(('Stand_b',))
    sp.grid()
    sp.set_ylim(-0.1,1.1) 
    if xlim:
      sp.set_xlim(xlim)

    fig.show()
    
  #============================================================================================
  @staticmethod
  def plot_AC100_track(sig, FigNr=200, Idx=0, xlim = None):
    # plot all available AC100 track 0..9
 
    AC100 = sig['AC100_tracks']
 
    k = Idx

    if AC100[k] is not None:
      fig = pl.figure(FigNr)
      fig.clear()
      fig.suptitle('track %d'%k)

      sp = fig.add_subplot(711)
      sp.plot(AC100[k]['Time'], AC100[k]['dx'] )
      sp.legend(('dx',))
      sp.grid()
      if xlim:
        sp.set_xlim(xlim)

      sp = fig.add_subplot(712)
      sp.plot(AC100[k]['Time'], AC100[k]['dy'] )
      sp.plot(AC100[k]['Time'], AC100[k]['corrected_lateral_distance'] )
      sp.legend(('dy','corrected_lateral_distance'))
      sp.grid()
      if xlim:
        sp.set_xlim(xlim)
    
      sp = fig.add_subplot(713)
      sp.plot(AC100[k]['Time'], AC100[k]['vx'] )
      sp.legend(('vx',))
      sp.grid()
      if xlim:
        sp.set_xlim(xlim)
	
      sp = fig.add_subplot(714)
      #sp.plot(AC100[k]['Time'], AC100[k]['acceleration_over_ground'] )
      #sp.legend(('acceleration_over_ground',))
      #sp.grid()
      sp.plot(AC100[k]['Time'], AC100[k]['id'] )
      sp.legend(('id',))
      sp.grid()
      if xlim:
        sp.set_xlim(xlim)
	
      sp = fig.add_subplot(715)
      sp.plot(AC100[k]['Time'], AC100[k]['acc_track_info'] )
      sp.legend(('acc_track_info',))
      sp.grid()
      sp.set_ylim(-0.1,3.1) 
      if xlim:
        sp.set_xlim(xlim)
  
      sp = fig.add_subplot(716)
      sp.plot(AC100[k]['Time'], AC100[k]['CW_track'] )
      sp.legend(('CW_track',))
      sp.grid()
      sp.set_ylim(-0.1,1.1) 
      if xlim:
        sp.set_xlim(xlim)

      sp = fig.add_subplot(717)
      sp.plot(AC100[k]['Time'], AC100[k]['Stand_b'] )
      sp.legend(('Stand_b',))
      sp.grid()
      sp.set_ylim(-0.1,1.1) 
      if xlim:
        sp.set_xlim(xlim)
	
      fig.show()

  #============================================================================================
  @staticmethod
  def plot_AC100_tracks(sig, FigNr=200,xlim = None):
    # plot all available AC100 track 0..9
 
    AC100 = sig['AC100_tracks']
 
    for k in xrange(cDataAC100.N_AC100):
      cDataAC100.plot_AC100_track(sig, FigNr, k, xlim)
      FigNr +=1

  #============================================================================================
  @staticmethod
  def plot_ego_vehicle_speed_and_yaw_rate(sig, FigNr=200,xlim = None): 
    # plot of:
    #  ego vehicle speed : actual_vehicle_speed
    #  yaw rate          : cvd_yawrate,VDC2_YAW_Rate

    # just the input signal
    fig=pl.figure(FigNr)
    fig.clear()
    fig.suptitle('ego vehicle speed and yaw rate AC100')

    # ego vehicle speed
    sp=fig.add_subplot(211)
    sp.grid()
    sp.plot(sig['actual_vehicle_speed_Time'],sig['actual_vehicle_speed_Value']*3.6)
    sp.legend(('velocity',))
    sp.set_ylabel('[km/h]')
    
 
    # yaw rate
    sp=fig.add_subplot(212)
    sp.grid()
    sp.plot(sig['VDC2_YAW_Rate_Time'],sig['VDC2_YAW_Rate_Value'],'b')
    sp.plot(sig['cvd_yawrate_Time'], -sig['cvd_yawrate_Value']*np.pi/180.0,'r')
    sp.set_ylim(-0.05,0.05)
    sp.legend(('yaw rate (VDC2)','yaw rate (AC100)'))
    sp.set_ylabel('[rad/s]')
    sp.set_xlabel('time [s]')
 
    fig.show()
 
  #============================================================================================
  @staticmethod
  def plot_ego_vehicle_speed_yaw_rate_and_curvature(sig, FigNr=200,xlim = None): 
    # plot of:
    #  ego vehicle speed : actual_vehicle_speed
    #  yaw rate          : cvd_yawrate,VDC2_YAW_Rate
    #  road_curvature    : estimated_road_curvature

    # just the input signal
    fig=pl.figure(FigNr);   FigNr += 1
    fig.clear()
    fig.suptitle('ego vehicle speed and yaw rate AC100')

    # ego vehicle speed
    sp=fig.add_subplot(311)
    sp.grid()
    sp.plot(sig['actual_vehicle_speed_Time'],sig['actual_vehicle_speed_Value']*3.6)
    sp.legend(('velocity',))
    sp.set_ylabel('[km/h]')
    
 
    # yaw rate
    sp=fig.add_subplot(312)
    sp.grid()
    sp.plot(sig['VDC2_YAW_Rate_Time'],sig['VDC2_YAW_Rate_Value'],'b')
    sp.plot(sig['cvd_yawrate_Time'], -sig['cvd_yawrate_Value']*np.pi/180.0,'r')
    sp.set_ylim(-0.05,0.05)
    sp.legend(('yaw rate (VDC2)','yaw rate (AC100)'))
    sp.set_ylabel('[rad/s]')
    
    # yaw rate
    sp=fig.add_subplot(313)
    sp.grid()
    
    sp.plot(sig['estimated_road_curvature_Time'], sig['estimated_road_curvature_Value'],'r')
    sp.set_ylim(-0.05,0.05)
    sp.legend(('road_curvature',))
    sp.set_ylabel('[rad/s]')
    sp.set_xlabel('time [s]')
 
 
    fig.show()
    
  #============================================================================================
  @staticmethod
  def plot_Bendix_CMS(sig, FigNr=400, xlim = None):
  
    # -------------------------------------------------
    fig = pl.figure(FigNr)  
    fig.clf()
    fig.clear()
    fig.suptitle('Bendix_CMS')
    
    # ------------------------------------------------------
    ax = fig.add_subplot(311)
    ax.plot( sig['General']['Time'] ,sig['General']["cm_system_status"])
    ax.legend(('cm_system_status',))
    ax.set_ylabel('bool')
    #ax.set_xlabel('time [s]')
    ax.grid()
    
    # ------------------------------------------------------
    ax = fig.add_subplot(312)
    ax.plot(sig['Bendix_CMS']["Time"],sig['Bendix_CMS']["AudibleFeedback"])
    ax.legend(('AudibleFeedback',))
    ax.set_ylabel('bool')
    #ax.set_xlabel('time [s]')
    ax.grid()
    ax.set_ylim(-0.0,7.1) 
    
    # ------------------------------------------------------
    ax = fig.add_subplot(313)
    ax.plot(sig['Bendix_CMS']["Time"],sig['Bendix_CMS']["XBRAccDemand"])
    ax.legend(('XBR',))
    ax.set_ylabel('m/s$^2$')
    ax.set_xlabel('time [s]')
    ax.grid()
    
        
    # -------------------------------------------------------------------------
    # show on screen
    fig.show()
    
  #============================================================================================
  # following methods are under construction !!!
  #============================================================================================
  
  #============================================================================================
  @staticmethod  
  def create_track_list(sig):
    # under construction !!!
  
    track_list = [];
   
    AC100 = sig['AC100_tracks']
   
   
    for k in xrange(cDataAC100.N_AC100):
      if len(AC100[k]['Time'])>0:
        # internal_track_index keeps constant but track is changing
        x = AC100[k]['id']
        #x[(AC100[k]['status']==0).nonzero()] = -1  # status ==0 Track is empty (end of a track)
        # separate handles
        handle_list = kbtools.scan4handles(x,0)
  
        print len(handle_list)
 
        # create tracks from handle list and append to track list
        for k_handle_list in xrange(len(handle_list)):
          idx = range(handle_list[k_handle_list][0],handle_list[k_handle_list][1]+1,1)
          current_track = {'idx':idx,
                           't'  :AC100[k]['Time'][idx],
                           'tr' :k,
                           'id' :AC100[k]['id'][idx],
                           'dx' :AC100[k]['dx'][idx],
                           'dy' :AC100[k]['dy'][idx],
                           'vx' :AC100[k]['vx'][idx],
                           'vy' :AC100[k]['vy'][idx],
                           #'vyv':vyv[idx],
                           #'axv':axv[idx],
                           #'ayv':ayv[idx],
                           'Stand_b':AC100[k]['Stand_b'][idx],
                          }

          track_list.append(current_track)

    print len(track_list)
    # ................................................    
    # pickle track_list to 
    #output = open('track_list_AC100.pkl', 'wb')
    #pickle.dump(track_list, output,-1) # -1: using the highest protocol available
    #output.close()

    return track_list
    
  #============================================================================================
  @staticmethod
  def plot_AC100_acc_track_info(sig, FigNr=200):
    
    AC100 = sig['AC100_tracks']
 
   
    k = 1
    print AC100[k]['Time']
    
    t = np.arange(0,400,0.02)
    t1 = AC100[k]['Time']
    t_threshold=0.1
    valid = kbtools.calc_signal_valid(t,t1,t_threshold)
    
    
    fig = pl.figure(FigNr); FigNr+=1
    fig.suptitle('acc_track_info')
    sp = fig.add_subplot(211)
    sp.plot(AC100[k]['Time'],AC100[k]['Time'],'x')

    sp = fig.add_subplot(212)
    sp.plot(t,valid,'-')
    sp.set_ylim(-0.1,1.1) 
    
    
    
    fig.show()
    
    
     
    fig = pl.figure(FigNr); FigNr+=1
    fig.suptitle('acc_track_info')
    
    # ------------------------------------
    sp = fig.add_subplot(411)
    s_legend = []
    for k in xrange(cDataAC100.N_AC100):
      if len(AC100[k]['Time'])>0:  
        sp.plot(AC100[k]['Time'], (AC100[k]['acc_track_info']==1.0)+0.1*k)
        s_legend.append("%d"%k)	
	  
    sp.legend(s_legend)
    sp.grid()
    sp.set_ylim(-0.1,4.1) 
    sp.set_ylabel('ACC track')
    
    # ------------------------------------
    sp = fig.add_subplot(412)
    s_legend = []
    for k in xrange(cDataAC100.N_AC100):
      if len(AC100[k]['Time'])>0:  
        sp.plot(AC100[k]['Time'], (AC100[k]['acc_track_info']==2.0)+0.1*k)
        s_legend.append("%d"%k)	
	  
    sp.legend(s_legend)
    sp.grid()
    sp.set_ylim(-0.1,4.1) 
    sp.set_ylabel('IIV')
    
    # ------------------------------------
    sp = fig.add_subplot(413)
    s_legend = []
    for k in xrange(cDataAC100.N_AC100):
      if len(AC100[k]['Time'])>0:  
        sp.plot(AC100[k]['Time'], (AC100[k]['acc_track_info']>=3.0)+0.1*k)
        s_legend.append("%d"%k)	
	  
    sp.legend(s_legend)
    sp.grid()
    sp.set_ylim(-0.1,4.1) 
    sp.set_ylabel('NIV')

    # ------------------------------------
    sp = fig.add_subplot(414)
    #sp.title('CW_track')
    s_legend = []
    for k in xrange(cDataAC100.N_AC100):
      if len(AC100[k]['Time'])>0:  
        sp.plot(AC100[k]['Time'], (AC100[k]['CW_track']>0.0)+0.1*k)
        s_legend.append("%d"%k)	
	  
    sp.legend(s_legend)
    sp.grid()
    sp.set_ylim(-0.1,4.1) 
    sp.set_ylabel('CW track')

    fig.show()
  
  #============================================================================================
  @staticmethod
  def get_v_ego(FLR20_sig, unit='km/h'):
        '''
            get vehicle velocity from J1939 CAN messages

                "EBC2:  MeanSpdFA", FLR20_sig['J1939']["MeanSpdFA"]
                "CCVS1: WheelbasedVehSpd", FLR20_sig['J1939']["WheelbasedVehSpd"]
                "TCO1:  VehSpd", FLR20_sig['J1939']["VehSpd"]
                
            unit : 'km/h' or 'm/s'
        '''
         
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

        elif ('General' in FLR20_sig) and (FLR20_sig['General']) is not None:
            t_v_ego          = FLR20_sig['General']['Time']        
            v_ego            = FLR20_sig['General']['actual_vehicle_speed']*3.6
            #v_ego_at_t_start, v_ego_at_t_stop = kbtools.GetValuesAtStartAndStop(t_v_ego, v_ego, t_start,t_stop)  
           
        
        # MAN EBA2
        if t_v_ego is None:
            Source = FLR20_sig["Source"]
            t_v_ego, v_ego = kbtools.GetSignal(Source, "ACCrefInfo_BASE", "vehicleSpeedFromRadar_BASIS")
        
        print "v_ego", v_ego
        
        if t_v_ego is not None:
            if unit=='km/h':
               pass
            elif unit=='m/s':
               v_ego = v_ego/3.6
        
        return t_v_ego, v_ego
  
  #============================================================================================
  @staticmethod
  def get_ax_ego(FLR20_sig, unit='m/s^2', mode='v_ego', smooth_filter=False, f_g=1.0):
        '''
            get vehicle acceleration from J1939 CAN messages
            unit : 'm/s^2'

            a) 'v_ego'
            b) 'VBOX_GPS'
            c) 'VBOX_IMU'            
                
        '''
         
        t_ax_ego = None
        ax_ego = None

        if mode=='v_ego':
            Time_v_ego, v_ego =  cDataAC100.get_v_ego(FLR20_sig, unit='m/s')
            t_ax_ego = Time_v_ego
            ax_ego = kbtools.ugdiff(Time_v_ego,v_ego)
        elif mode=='VBOX_GPS':    
            try:
                t_ax_ego = FLR20_sig["VBOX_IMU"]["Time_Longitudinal_acceleration"]
                ax_ego = FLR20_sig["VBOX_IMU"]["Longitudinal_acceleration"]*9.81
            except:
                t_ax_ego = None
                ax_ego = None
        elif mode=='VBOX_IMU':    
            try:
                t_ax_ego = FLR20_sig['VBOX_IMU']["Time_IMU_X_Acc"]
                ax_ego = FLR20_sig['VBOX_IMU']["IMU_X_Acc"]*9.81
            except:
                t_ax_ego = None
                ax_ego = None
     
        print "ax_ego", ax_ego
        
        
        
        if smooth_filter:
            if t_ax_ego is not None:
                ax_ego = kbtools.smooth_filter(t_ax_ego, ax_ego,f_g = f_g, filtertype = 'acausal')
       
        
        return t_ax_ego, ax_ego
  
        
  
  #============================================================================================
  @staticmethod
  def get_yawrate(FLR20_sig, unit='rad/s'):
    '''    
        t_yawrate = self.FLR20_sig['J1939']['Time_YawRate']
        yawrate   = self.FLR20_sig['J1939']["YawRate"]       
    '''
    t_yawrate = None
    yawrate = None            
    if ("Time_YawRate" in FLR20_sig['J1939']) and FLR20_sig['J1939']["Time_YawRate"] is not None:
        t_yawrate = FLR20_sig['J1939']['Time_YawRate']
        yawrate   = FLR20_sig['J1939']["YawRate"] 
    
    return t_yawrate, yawrate
    
  #============================================================================================
  @staticmethod
  def get_AEBS(FLR20_sig, attribute, unit):
    '''    
              
    '''
    
    
    t_sig = None
    sig = None   
    
    try:
        if attribute in ["TO_dx"]:
            t_sig, sig = cDataAC100._get_AEBS_TO_dx(FLR20_sig, unit)
        elif attribute in ["TO_dy"]:
            t_sig, sig = cDataAC100._get_AEBS_TO_dy(FLR20_sig, unit)
        elif attribute in ["TO_vx","TO_vRel"]:
            t_sig, sig = cDataAC100._get_AEBS_TO_vRel(FLR20_sig, unit)
        elif attribute in ["TO_aRel"]:
            t_sig, sig = cDataAC100._get_AEBS_TO_aRel(FLR20_sig, unit)
        elif attribute in ["ABESState"]:
            t_sig, sig = cDataAC100._get_AEBSState(FLR20_sig, unit)
        elif attribute in ["TO_detected","relevantObjectDetected"]:
            t_sig, sig = cDataAC100._get_TO_detected(FLR20_sig, unit)
        elif attribute in ["TO_detected_CW"]:
            t_sig, sig = cDataAC100._get_TO_detected_CW(FLR20_sig, unit)
        elif attribute in ["XBR_ExtAccelDem"]:
            t_sig, sig = cDataAC100._get_XBR_ExtAccelDem(FLR20_sig, unit)

    except Exception, e:
        print "error - get_AEBS(%s): "%attribute,e.message
        traceback.print_exc(file=sys.stdout)
        t_sig = None
        sig = None      
      
    
    #print attribute, "- time: ", t_sig
    #print attribute, "- signal: ", sig
    
    return t_sig, sig
  #============================================================================================
  @staticmethod
  def _get_AEBS_TO_dx(FLR20_sig, unit):
    '''    
        unit='m'     
    '''
    
    Source = FLR20_sig["Source"]
    
    t_dx = None
    dx = None   
    
    try:
        t_dx = FLR20_sig['PosMatrix']['CW']['Time']        
        dx   = FLR20_sig['PosMatrix']['CW']['dx']
    except:
        t_dx = None
        dx = None
    
    # MAN EBA2
    if t_dx is None:
        t_dx, dx  = kbtools.GetSignal(Source, "AEBSvehicle1_BASE", "Distance2vehicleAEBS1_BASE")
    
    
    return t_dx, dx

  #============================================================================================
  @staticmethod
  def _get_AEBS_TO_dy(FLR20_sig, unit):
    '''    
        unit='m'     
    '''
    
    Source = FLR20_sig["Source"]
    
    t_dy = None
    dy = None   
    
    try:
        t_dy = FLR20_sig['PosMatrix']['CW']['Time']        
        dy   = FLR20_sig['PosMatrix']['CW']['dy']
    except:
        t_dy = None
        dy = None
    
    # MAN EBA2
    if t_dy is None:
        t_dx, dx  = kbtools.GetSignal(Source, "AEBSvehicle1_BASE", "Distance2vehicleAEBS1_BASE")
        _, trackCorrectedAzimuth  = kbtools.GetSignal(Source, "AEBSvehicle1_BASE", "trackCorrectedAzimuthAEBS1_BASE")
        t_dy = t_dx
        dy  = dx * trackCorrectedAzimuth*np.pi/180.0
    
    return t_dy, dy

    
  #============================================================================================
  @staticmethod
  def _get_AEBS_TO_vRel(FLR20_sig, unit):
    '''    
        unit='m/s'      
    '''
    
    Source = FLR20_sig["Source"]
    
    t_vRel = None
    vRel = None   
    
    try:
       t_vRel          = FLR20_sig['PosMatrix']['CW']['Time']        
       vRel            = FLR20_sig['PosMatrix']['CW']['vx']
    except:
       t_vRel = None
       vRel = None
    
    
    
    # MAN EBA2
    if t_vRel is None:
        t_vRel, vRel          = kbtools.GetSignal(Source, "AEBSvehicle1_BASE", "relSpeedOfvehicleAEBS1_BASE")
        if t_vRel is not None:
           vRel = vRel/3.6

    if t_vRel is not None:
        if unit=='km/h':
            vRel = vRel*3.6
        elif unit=='m/s':
            pass 

    
    
    return t_vRel, vRel
    
    
  #============================================================================================
  @staticmethod
  def _get_AEBS_TO_aRel(FLR20_sig, unit):
    '''    
        unit='m/s^2'      
    '''
    
    Source = FLR20_sig["Source"]
    
    t_aRel = None
    aRel = None   
    
    try:
        if FLR20_sig['ACC_Sxy2']['Time_cw_relaccel'] is not None:
            t_aRel  =  FLR20_sig['ACC_Sxy2']['Time_cw_relaccel']
            aRel    =  FLR20_sig['ACC_Sxy2']['cw_relaccel']      # "m/s2"
        else:
            print "warning FLR20_sig['ACC_Sxy2']['cw_relaccel'] not available -> use FLR20_sig['PosMatrix']['CW']['ax_ground']-aRef instead"
            t_aRel = FLR20_sig['PosMatrix']['CW']['Time']
            aRef = kbtools.resample(FLR20_sig["General"]["Time"], FLR20_sig["General"]["vehicle_reference_acceleration"], t_aRel)
            aRel  = FLR20_sig['PosMatrix']['CW']['ax_ground']-aRef
    except:
       t_aRel = None
       aRel = None
    
    
    
    # MAN EBA2
    if t_aRel is None:
        t_aRel, aRel          = kbtools.GetSignal(Source, "AEBSvehicle1_BASE", "vehicleAccelAEBS1_BASE")
        

    
    
    return t_aRel, aRel

  #============================================================================================
  @staticmethod
  def _get_AEBSState(FLR20_sig, unit):
    '''    
              
    ''' 
    Source = FLR20_sig["Source"]
    
    t_AEBSState = None
    AEBSState = None   
    
    try:
       t_AEBSState = FLR20_sig['AEBS_SFN_OUT']['Time_ABESState']   
       AEBSState = FLR20_sig['AEBS_SFN_OUT']['ABESState']       
    except:
       t_AEBSState = None
       AEBSState = None
    
    if t_AEBSState is None:
        try:
            t_AEBSState = FLR20_sig['J1939']["Time_AEBSState"]
            AEBSState = FLR20_sig['J1939']["AEBSState"]
        except:
            t_AEBSState = None
            AEBSState = None
    
    return t_AEBSState, AEBSState

  #============================================================================================
  @staticmethod
  def _get_XBR_ExtAccelDem(FLR20_sig, unit):
    '''    
       unit = m/s^2      
    '''
    print "_get_XBR_ExtAccelDem"
    Source = FLR20_sig["Source"]
    
    t_XBR_ExtAccelDem = None
    XBR_ExtAccelDem = None   
    
    try:
        #t_XBR_ExtAccelDem = FLR20_sig['AEBS_SFN_OUT']['Time_AccelDemand'] 
        #XBR_ExtAccelDem   = FLR20_sig['AEBS_SFN_OUT']['AccelDemand']  
            
        t_XBR_ExtAccelDem = FLR20_sig['J1939']['Time_XBR_ExtAccelDem']
        XBR_ExtAccelDem   = FLR20_sig['J1939']['XBR_ExtAccelDem']   
        
    except:
        print "error t_XBR_ExtAccelDem"
        t_XBR_ExtAccelDem = None
        XBR_ExtAccelDem = None
    
    print "t_XBR_ExtAccelDem", t_XBR_ExtAccelDem
    
    if t_XBR_ExtAccelDem is None:
        t_XBR_ExtAccelDem, XBR_ExtAccelDem = kbtools.GetSignal(Source, "XBR_VAR4", "externalAccelerationDemand_BASIS")
          
    if t_XBR_ExtAccelDem is None:
        t_XBR_ExtAccelDem, XBR_ExtAccelDem = kbtools.GetSignal(Source, "XBR_prop", "ExtAccDemand")
    
              
            
    return t_XBR_ExtAccelDem, XBR_ExtAccelDem
    

  
  #============================================================================================
  @staticmethod
  def _get_TO_detected(FLR20_sig, unit):
    '''    
              
    '''
    #print "_get_TO_detected"
    Source = FLR20_sig["Source"]
    
    t_TO_detected = None
    TO_detected = None   
    
    try:
       t_TO_detected = FLR20_sig['Tracks'][0]['Time']   
       TO_detected = FLR20_sig['Tracks'][0]['In_Lane']       
    except:
       t_TO_detected = None
       TO_detected = None
    
    # MAN EBA2
    if t_TO_detected is None:
        t_TO_detected, TO_detected  = kbtools.GetSignal(Source, "AEBS1_BASE", "relevantObjectDetectedAEBS_BASE")
        
    return t_TO_detected, TO_detected
    
  #============================================================================================
  @staticmethod
  def _get_TO_detected_CW(FLR20_sig, unit):
    '''    
              
    '''
    #print "_get_TO_detected_CW"
    Source = FLR20_sig["Source"]
    
    t_TO_detected_CW = None
    TO_detected_CW = None   
    
    try:
       t_TO_detected_CW = FLR20_sig['Tracks'][0]['Time']   
       TO_detected_CW = FLR20_sig['Tracks'][0]['CW_track']       
    except:
       t_TO_detected_CW = None
       TO_detected_CW = None
    
    # MAN EBA2 
    #  no signal available
        
    return t_TO_detected_CW, TO_detected_CW

  #============================================================================================
  @staticmethod
  def get_SteerWhlAngle(FLR20_sig, unit='degree'):
    '''    
        t_SteerWhlAngle = self.FLR20_sig["J1939"]["Time_SteerWhlAngle"]
        SteerWhlAngle  = self.FLR20_sig["J1939"]["SteerWhlAngle"]*180.0/np.pi

    '''
    t_SteerWhlAngle = None
    SteerWhlAngle = None            
    if ("Time_SteerWhlAngle" in FLR20_sig['J1939']) and FLR20_sig['J1939']["Time_SteerWhlAngle"] is not None:
        t_SteerWhlAngle = FLR20_sig['J1939']['Time_SteerWhlAngle']
        SteerWhlAngle   = FLR20_sig['J1939']["SteerWhlAngle"]*180.0/np.pi 
    
    return t_SteerWhlAngle, SteerWhlAngle

        
  #============================================================================================
  @staticmethod
  def get_road_curvature(FLR20_sig):
        '''
           get vehicle road curvature (predicted path)
        '''
    
        print "get_road_curvature()"
    
        
    
        t_road_curvature = None
        road_curvature = None
        
        # take signals from J1939
        if ('J1939' in FLR20_sig) and (FLR20_sig['J1939']) is not None:  
        
            # get vehicle speed
            t_v_ego, v_ego = cDataAC100.get_v_ego(FLR20_sig)
        
            # yaw rate 
            t_yawrate, yawrate = cDataAC100.get_yawrate(FLR20_sig)
            
            # calculate road curvature            
            if (t_v_ego is not None) and (t_yawrate is not None):
                t_road_curvature = t_yawrate
                v_ego2    = kbtools.resample(t_v_ego, v_ego, t_road_curvature, method='zoh')
                yawrate2  = kbtools.resample(t_yawrate, yawrate, t_road_curvature, method='zoh')
                road_curvature = (v_ego2/3.6) * np.where(np.fabs(yawrate2)>(1e-5),1.0/yawrate2,1e-5)  # Unit 'm'    (it's a radius)
      
        # A087
        elif ('General' in FLR20_sig) and (FLR20_sig['General']) is not None:
            t_road_curvature          = FLR20_sig['General']['Time']        
            road_curvature            = FLR20_sig['General']['estimated_road_curvature']

        print "road_curvature", road_curvature
        
        return t_road_curvature, road_curvature
        
  #============================================================================================
  @staticmethod
  def get_ay(FLR20_sig):
        '''
           get vehicle lateral acceleration
        '''
    
        print "get_ay()"
    
       
    
        t_ay = None
        ay = None
        
        # take signals from J1939
        if ('J1939' in FLR20_sig) and (FLR20_sig['J1939']) is not None:  
        
            # get vehicle speed
            t_v_ego, v_ego = cDataAC100.get_v_ego(FLR20_sig)
        
            # yaw rate 
            t_yawrate, yawrate = cDataAC100.get_yawrate(FLR20_sig)
            
            # calculate road curvature            
            if (t_v_ego is not None) and (t_yawrate is not None):
                t_ay = t_yawrate
                v_ego2    = kbtools.resample(t_v_ego, v_ego, t_ay, method='zoh')
                yawrate2  = kbtools.resample(t_yawrate, yawrate, t_ay, method='zoh')
                ay = (v_ego2/3.6) * yawrate2  # Unit 'm/s^2'
      
       
        print "ay", ay
        
        return t_ay, ay

  #============================================================================================
  @staticmethod
  def get_TrackById(FLR20_sig,track_ID,verbose=False):
        '''
            Provide track , radar detections and video object detections to a given track_ID 
        
            Track['Time']                 common time axis
            
            Track['Track']['xxx']         track attributes
            
            Track['Target']['xxx']        radar detection attributes (TRW: Target)
            
            Track['VideoObj']['xxx']      video object attributes
                 
        '''
      
        # cDataAC100.verbose overrides local verbose
        if cDataAC100.verbose:  
            verbose = True
        
        t_threshold = 0.15 
    
        if verbose: 
            print "DataAC100.get_TrackById() - start"
            print "  track_ID:", track_ID
    
    
        # main data structure
        AEBS_Track = {}
        
        # common time axis
        AEBS_Track['Time'] = FLR20_sig['Time']
        
        # fused track 
        Track = {}
        AEBS_Track['Track'] = Track
        
        # radar detections 
        Target = {}
        AEBS_Track['Target'] = Target
        
        # video objects
        VideoObj ={}
        AEBS_Track['VideoObj'] = VideoObj
            
            
        initial_value_for_signals = np.NAN   
                     
        # -------------------------------------------------------------
        # Track attributes (fused track of radar and camera)
        if verbose:
            print "Track attributes (fused track of radar and camera):"
        '''
        for k_track in range(0,cDataAC100.N_FLC20_VideoObj): # high priority overrides low priority
            if cDataAC100.verbose: 
                print "k_track %s"%k_track
                
            x = FLR20_sig['Tracks'][k_track]
            if (x is not None) and isinstance(x, dict) and ('id' in x):
                keys = [key for key in x.keys() if not key in ['Time','Valid']]   # filter out 'Time'
                
                
                for key in keys:
                    if not key in Track:
                        Track[key]    = np.zeros_like(Track['Time'])
                        Track[key][:] = initial_value_for_signals 
                    mask = np.logical_and(track_ID==x['id'],x['Valid'])
                    Track[key][mask]  = x[key][mask]
        
        '''
        for k_track in range(0,cDataAC100.N_FLC20_VideoObj):  
            if verbose: 
                print "  k_track %s"%k_track
                
            x = FLR20_sig['FLR20_CAN']['Tracks'][k_track]
            if (x is not None) and isinstance(x, dict) and ('Time_id' in x)  and  ('id' in x):
                                 
                id_resampled = kbtools.resample(x['Time_id'], x['id'], AEBS_Track['Time'],'zoh')
                
                keys = [ key for key in x.keys() if not key.startswith('Time_')]
                #print "keys", keys
                                       
                for key in keys:
                    #print key
                    #if x['Time_%s'%key] is not None:
                    #    print "Time",len(x['Time_%s'%key]), x['Time_%s'%key]
                    #    print "Value",len(x[key]), x[key]
                        
                    if not key in Track:
                        Track[key]    = np.zeros_like(AEBS_Track['Time'])
                        Track[key][:] = initial_value_for_signals  
                        
                    if x['Time_%s'%key] is not None:                       
                        valid = kbtools.calc_signal_valid(AEBS_Track['Time'],x['Time_%s'%key],t_threshold)
                        Value_resampled = kbtools.resample(x['Time_%s'%key], x[key], AEBS_Track['Time'],'zoh')
                        
                        mask = np.logical_and(id_resampled == track_ID,valid)                       
                        
                        Track[key][mask]  = Value_resampled[mask]
         
        
         
        # -------------------------------------------------------------
        # Targets = radar detections
        if verbose:
            print "Targets = radar detections:"

        '''
        if 'asso_target_index' in Track:
            asso_target_index = Track['asso_target_index']
            
            unique_asso_target_index = np.unique(asso_target_index)
            # remove nan
            unique_asso_target_index = unique_asso_target_index[~np.isnan(unique_asso_target_index)]
            unique_asso_target_index = unique_asso_target_index[unique_asso_target_index<31]
            if cDataAC100.verbose:
                print "unique_asso_target_index", unique_asso_target_index
            
            for k_target in unique_asso_target_index:
                keys = FLR20_sig['Targets'][k_target].keys()
                if 'Time' in keys:
                    keys.remove('Time')
                for key in keys:
                    if not key in Target:
                        Target[key]    = np.zeros_like(Track['Time'])
                        Target[key][:] = initial_value_for_signals
                    mask = k_target==asso_target_index
                    Target[key][mask]  = FLR20_sig['Targets'][k_target][key][mask]
        '''
            
        if 'asso_target_index' in Track:
            asso_target_index = Track['asso_target_index']
            
            unique_asso_target_index = np.unique(asso_target_index)
            # remove nan
            unique_asso_target_index = unique_asso_target_index[~np.isnan(unique_asso_target_index)]
            unique_asso_target_index = unique_asso_target_index[unique_asso_target_index<31]
            if verbose:
                print "unique_asso_target_index", unique_asso_target_index
            
            for k_target in unique_asso_target_index:
                if verbose: 
                    print "k_target", k_target
                
                if k_target in FLR20_sig['FLR20_CAN']['Targets']:
                    x = FLR20_sig['FLR20_CAN']['Targets'][k_target]
                  
                    keys = [ key for key in x.keys() if not key.startswith('Time_')]
                    
                    for key in keys:
                        if not key in Target:
                            Target[key]    = np.zeros_like(AEBS_Track['Time'])
                            Target[key][:] = initial_value_for_signals
                        
                        #print "x['Time_%s']"%key, x['Time_%s'%key].size
                        if (x['Time_%s'%key] is not None) and (x['Time_%s'%key].size>1):   # 1d numpy array lead to errors                   
                            valid = kbtools.calc_signal_valid(AEBS_Track['Time'],x['Time_%s'%key],t_threshold)          # determine when signal is valid
                            Value_resampled = kbtools.resample(x['Time_%s'%key], x[key], AEBS_Track['Time'],'zoh')      # resample to the common time base
                            mask = np.logical_and(k_target==asso_target_index,valid)                                    # mask for copying
                            Target[key][mask]  = Value_resampled[mask]                                                  # copy mask elements   
                    
             
        # -------------------------------------------------------------
        # Video Objects
        if verbose:
            print "Video Objects:"

        if 'asso_video_ID' in Track:
            asso_video_ID = Track['asso_video_ID'] 
            
            unique_asso_video_ID = np.unique(asso_video_ID)
            # remove nan
            unique_asso_video_ID = unique_asso_video_ID[~np.isnan(unique_asso_video_ID)]
            unique_asso_video_ID = unique_asso_video_ID[0<unique_asso_video_ID]
            if verbose:
                print "unique_asso_video_ID", unique_asso_video_ID
            
            for k_video_ID in unique_asso_video_ID:
                for k_VideoObj in range(cDataAC100.N_FLC20_VideoObj-1,-1,-1): # high priority overrides low priority 
                    x = FLR20_sig['FLC20_CAN'][k_VideoObj]
                    if (x is not None) and (isinstance(x, dict)) and ('Time_ID' in x) and ('ID' in x):
                                           
                        ID_resampled = kbtools.resample(x['Time_ID'], x['ID'], AEBS_Track['Time'],'zoh')
                          
                        for key in [ key for key in x.keys() if not key.startswith('Time_')]:   # the values and not the time axes
                            if not key in VideoObj:
                                VideoObj[key]    = np.zeros_like(AEBS_Track['Time'])
                                VideoObj[key][:] = initial_value_for_signals
                
                            #print "key",key
                            #print x['Time_%s'%key], x[key]
                            if x['Time_%s'%key] is not None:
                                valid = kbtools.calc_signal_valid(AEBS_Track['Time'],x['Time_%s'%key],t_threshold)          # determine when signal is valid
                                Value_resampled = kbtools.resample(x['Time_%s'%key], x[key], AEBS_Track['Time'],'zoh')      # resample to the common time base
                                mask = np.logical_and(ID_resampled==k_video_ID,valid)                                       # mask for copying
                                VideoObj[key][mask]  = Value_resampled[mask]                                                # copy mask elements 
                 
        # -----------------------------------------------------
        # shift signals - this has to be done after all conversion
        for key in Track.keys():               
            Track[key] = shift_signal(Track[key],shift=-1)
        
        for key in Target.keys():               
            Target[key] = shift_signal(Target[key],shift=-1)     
        
        for key in VideoObj.keys():               
            VideoObj[key] = shift_signal(VideoObj[key],shift=-1)   
    
        
        # -----------------------------------------------------
        if verbose: 
            print "DataAC100.get_TrackById() - end"
    
        return AEBS_Track

    #============================================================================================



