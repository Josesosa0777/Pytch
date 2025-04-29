"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import numpy as np

import datavis

# TRW AC100 (24 GHz radar sensor)

# Number of targets  (0..9)   - tracks are instantaneous radar reflexions 
N_AC100_TA = 10

# Number of tracks  (0..9)    - tracks are targets with time history
N_AC100_TR = 10


# Devices in the MDF file
Device_Targets = 'Targets(662)_2_'
Device_Tracks = 'Tracks(663)_2_'

def viewAC100(Sync, Source, FigureNr):

  # -------------------------------------------------------------
  # velocity
  Client = datavis.cPlotNavigator('Vehicle Speed',FigureNr)
  Client.addsignal('VBOX_2(302)_2_VBOX_III.Velocity_Kmh', Source.getSignal('VBOX_2(302)_2_VBOX_III', 'Velocity_Kmh'),
                   'Input_1(4A0)_2_.wheel_speed_FL', Source.getSignal('Input_1(4A0)_2_', 'wheel_speed_FL'),
                   'Input_1(4A0)_2_.wheel_speed_FR', Source.getSignal('Input_1(4A0)_2_', 'wheel_speed_FR'),
                   'Input_1(4A0)_2_.wheel_speed_RL', Source.getSignal('Input_1(4A0)_2_', 'wheel_speed_RL'),
                   'Input_1(4A0)_2_.wheel_speed_RR', Source.getSignal('Input_1(4A0)_2_', 'wheel_speed_RR'),
                   'General_radar_status(661)_2_.actual_vehicle_speed', Source.getSignal('General_radar_status(661)_2_', 'actual_vehicle_speed'),
                   'ECU_0_0.evi.General_T20.vxvRef', Source.getSignal('ECU_0_0', 'evi.General_T20.vxvRef'),
                 factor=[1,1,1,1,1,3.6,3.6],
                 offset=[0,0,0,0,0,0,0],
                 color=['-','-','-','-','-','-','-'],
                 linewidth=[1,1,1,1,1,1,1],
                 ylabel = '[km/h]',
                 xlabel = 'time [s]')
  Sync.addClient(Client)

  Client = datavis.cPlotNavigator('Vehicle Speed',FigureNr)
  Client.addsignal('General_radar_status(661)_2_.actual_vehicle_speed', Source.getSignal('General_radar_status(661)_2_', 'actual_vehicle_speed'),
                   'ECU_0_0.evi.General_T20.vxvRef', Source.getSignal('ECU_0_0', 'evi.General_T20.vxvRef'),
                 factor=[3.6,3.6],
                 offset=[0.5*3.6,0],
                 color=['r-','b-'],
                 linewidth=[1,1],
                 ylabel = '[km/h]',
                 xlabel = 'time [s]')
  Sync.addClient(Client)

  # -------------------------------------------------------------
  # yawrate
  AC100_Time, AC100_cvd_yawrate    = Source.getSignal('General_radar_status(661)_2_', 'cvd_yawrate')
  AC100_Time, AC100_yawrate_offset = Source.getSignal('General_radar_status(661)_2_', 'yawrate_offset',ScaleTime=AC100_Time)
  AC100_cvd_yawrate     *= -np.pi/180.0
  AC100_yawrate_offset  *= -np.pi/180.0
 

  LRR3_Time, psiDtOptRaw   = Source.getSignal('ECU_0_0', 'evi.General_T20.psiDtOptRaw')
  LRR3_Time, psiDtOffTotal = Source.getSignal('ECU_0_0', 'evi.Rta_T20.psiDtOffTotal',ScaleTime=LRR3_Time)
  LRR3_Time, psiDtOpt      = Source.getSignal('ECU_0_0', 'evi.General_T20.psiDtOpt',ScaleTime=LRR3_Time)


  Client = datavis.cPlotNavigator('yaw rate')
  Client.addsignal('VDC2(98F0093E)_1_ESP.YAW_Rate', Source.getSignal('VDC2(98F0093E)_1_ESP', 'YAW_Rate'),
                   'General_radar_status(661)_2_.cvd_yawrate',(AC100_Time, AC100_cvd_yawrate+AC100_yawrate_offset),
                   'ECU_0_0.evi.General_T20.psiDtOpt', (LRR3_Time, psiDtOpt+psiDtOffTotal),
                   'ECU_0_0.evi.General_T20.psiDtOptRaw', (LRR3_Time, psiDtOptRaw+psiDtOffTotal),  
                   factor=[1,1,1,1],
                   offset=[0,0,0,0],
                   color=['-', '-','-','-'],
                   linewidth=[1, 1,1,1],
                   ylabel = '[rad/s]',
                   xlabel = 'time [s]')
  Sync.addClient(Client)

  # -------------------------------------------------------------
  # road curvature
  Client = datavis.cPlotNavigator('road curvature')
  Client.addsignal('General_radar_status(661)_2_.estimated_road_curvature', Source.getSignal('General_radar_status(661)_2_', 'estimated_road_curvature'),
                   'ECU_0_0.evi.MovementData_T20.kapCurvTraj', Source.getSignal('ECU_0_0', 'evi.MovementData_T20.kapCurvTraj'),
                   'ECU_0_0.evi.MovementData_T20.kapCurvTrajRaw', Source.getSignal('ECU_0_0', 'evi.MovementData_T20.kapCurvTrajRaw'),
                   factor=[-1, 1, 1],
                   offset=[ 0, 0, 0],
                   color=['-', '-', '-'],
                   linewidth=[1, 1,1],
                   ylabel = '[1/m]',
                   xlabel = 'time [s]')
  Sync.addClient(Client)



def viewAC100_2(Sync, Source, FigureNr):
  """
  Create PlotNavigators to illustrate the AC100. 
  
  :Parameters:
    sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `aebs.proc.cLrr3Source`
      Signal source to get mdf signals.
    FigureNr : int
      Intialize the figure number of the first `datavis.cPlotNavigators`.
  :ReturnType: None
  """


  # ------------------------------------------------------------------------
  # Tracks range  - distance from ego vehicle to obstacle
  PN = datavis.cPlotNavigator('TRW AC100 - Tracks range', FigureNr)
  for Idx in xrange(10):
    tmp_name = 'tr%d_range'%Idx
    PN.addsignal(tmp_name,Source.getSignal(Device_Tracks, tmp_name),ylabel = '[m]')
  Sync.addClient(PN)
  
  PN = datavis.cPlotNavigator('AC100 - Tracks range')
  PN.addsignal('tr0_range',Source.getSignal(Device_Tracks, 'tr0_range'),
               'tr1_range',Source.getSignal(Device_Tracks, 'tr1_range'),
               'tr2_range',Source.getSignal(Device_Tracks, 'tr2_range'),
               'tr3_range',Source.getSignal(Device_Tracks, 'tr3_range'),
               'tr4_range',Source.getSignal(Device_Tracks, 'tr4_range'),
               'tr5_range',Source.getSignal(Device_Tracks, 'tr5_range'),
               'tr6_range',Source.getSignal(Device_Tracks, 'tr6_range'),
               'tr7_range',Source.getSignal(Device_Tracks, 'tr7_range'),
               'tr8_range',Source.getSignal(Device_Tracks, 'tr8_range'),
               'tr9_range',Source.getSignal(Device_Tracks, 'tr9_range'),               
               ylabel = '[m]')
  Sync.addClient(PN)

  # ------------------------------------------------------------------------
  # Tracks relative velocitiy - speed of obstacle relative to ego vehicle speed
  PN = datavis.cPlotNavigator('TRW AC100 - Tracks relative velocity')
  for Idx in xrange(10):
    tmp_name = 'tr%d_relative_velocitiy'%Idx
    PN.addsignal(tmp_name,Source.getSignal(Device_Tracks, tmp_name),ylabel = '[m/s]')
  Sync.addClient(PN)
  
  PN = datavis.cPlotNavigator('AC100 - Tracks relative velocity')
  PN.addsignal('tr0_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr0_relative_velocitiy'),
               'tr1_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr1_relative_velocitiy'),
               'tr2_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr2_relative_velocitiy'),
               'tr3_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr3_relative_velocitiy'),
               'tr4_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr4_relative_velocitiy'),
               'tr5_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr5_relative_velocitiy'),
               'tr6_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr6_relative_velocitiy'),
               'tr7_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr7_relative_velocitiy'),
               'tr8_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr8_relative_velocitiy'),
               'tr9_relative_velocitiy',Source.getSignal(Device_Tracks, 'tr9_relative_velocitiy'),               
               ylabel = '[m/s]')
  Sync.addClient(PN)


  # ------------------------------------------------------------------------
  # Tracks uncorrected angle - horizontal angle refered to the ego vehicle driving axle
  #                            uncorrected in this context means it is not related the
  #                            predicted ego vehicle path

  PN = datavis.cPlotNavigator('TRW AC100 - Tracks uncorrected angle')
  for Idx in xrange(10):
    tmp_name = 'tr%d_uncorrected_angle'%Idx
    PN.addsignal(tmp_name,Source.getSignal(Device_Tracks, tmp_name),ylabel = '[degree]')
  Sync.addClient(PN)


  PN = datavis.cPlotNavigator('AC100 - Tracks uncorrected angle')
  PN.addsignal('tr0_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr0_uncorrected_angle'),
               'tr1_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr1_uncorrected_angle'),
               'tr2_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr2_uncorrected_angle'),
               'tr3_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr3_uncorrected_angle'),
               'tr4_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr4_uncorrected_angle'),
               'tr5_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr5_uncorrected_angle'),
               'tr6_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr6_uncorrected_angle'),
               'tr7_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr7_uncorrected_angle'),
               'tr8_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr8_uncorrected_angle'),
               'tr9_uncorrected_angle',Source.getSignal(Device_Tracks, 'tr9_uncorrected_angle'),               
               ylabel = '[degree]')
  Sync.addClient(PN)


  # ------------------------------------------------------------------------
  # Tracks dy (calculated) - lateral distance of the obstacle refered to the middle of the ego vehicle

  # create a dictionary AC100_dict['tr%d_uncorrected_dy'] = [t_dy,dy]  %d=0..9
  
  for k in xrange(N_AC100_TR):
    t_angle, angle = Source.getSignal(Device_Tracks,'tr%d_uncorrected_angle'%k)
    timekey        = Source.getTimeKey(Device_Tracks,'tr%d_uncorrected_angle'%k)

    angle = np.pi/180* angle
    if t_angle.size > 0:
      ds = Source.getSignal(Device_Tracks,'tr%d_range'%k,ScaleTime=t_angle)[1]
      dy = ds*np.sin(angle)
    else:
      dy = np.empty_like(angle)
    Source.addSignal(Device_Tracks, 'tr%d_uncorrected_dy' %k, timekey, dy)


  PN = datavis.cPlotNavigator('TRW AC100 - Tracks uncorrected dy (calculated)')
  for Idx in xrange(N_AC100_TR):
    tmp_name = 'tr%d_uncorrected_dy'%Idx
    PN.addsignal(tmp_name, Source.getSignal(Device_Tracks, tmp_name), ylabel = '[m]')

  Sync.addClient(PN)

  PN = datavis.cPlotNavigator('AC100 - Tracks uncorrected dy (calculated)')
  PN.addsignal('tr0_uncorrected_dy',Source.getSignal(Device_Tracks,'tr0_uncorrected_dy'),
               'tr1_uncorrected_dy',Source.getSignal(Device_Tracks,'tr1_uncorrected_dy'),
               'tr2_uncorrected_dy',Source.getSignal(Device_Tracks,'tr2_uncorrected_dy'),
               'tr3_uncorrected_dy',Source.getSignal(Device_Tracks,'tr3_uncorrected_dy'),
               'tr4_uncorrected_dy',Source.getSignal(Device_Tracks,'tr4_uncorrected_dy'),
               'tr5_uncorrected_dy',Source.getSignal(Device_Tracks,'tr5_uncorrected_dy'),
               'tr6_uncorrected_dy',Source.getSignal(Device_Tracks,'tr6_uncorrected_dy'),
               'tr7_uncorrected_dy',Source.getSignal(Device_Tracks,'tr7_uncorrected_dy'),
               'tr8_uncorrected_dy',Source.getSignal(Device_Tracks,'tr8_uncorrected_dy'),
               'tr9_uncorrected_dy',Source.getSignal(Device_Tracks,'tr9_uncorrected_dy'),               
               ylabel = '[m]')
  Sync.addClient(PN)

  pass

  # ------------------------------------------------------------------------
  # Tracks credibility - how reliable this track is
  
  PN = datavis.cPlotNavigator('TRW AC100 - Tracks credibility')
  for Idx in xrange(10):
    tmp_name = 'tr%d_credibility'%Idx
    PN.addsignal(tmp_name,Source.getSignal(Device_Tracks, tmp_name),
               ylabel = '[%%]')
  Sync.addClient(PN)


  PN = datavis.cPlotNavigator('AC100 - Tracks credibility')
  PN.addsignal('tr0_credibility',Source.getSignal(Device_Tracks, 'tr0_credibility'),
               'tr1_credibility',Source.getSignal(Device_Tracks, 'tr1_credibility'),
               'tr2_credibility',Source.getSignal(Device_Tracks, 'tr2_credibility'),
               'tr3_credibility',Source.getSignal(Device_Tracks, 'tr3_credibility'),
               'tr4_credibility',Source.getSignal(Device_Tracks, 'tr4_credibility'),
               'tr5_credibility',Source.getSignal(Device_Tracks, 'tr5_credibility'),
               'tr6_credibility',Source.getSignal(Device_Tracks, 'tr6_credibility'),
               'tr7_credibility',Source.getSignal(Device_Tracks, 'tr7_credibility'),
               'tr8_credibility',Source.getSignal(Device_Tracks, 'tr8_credibility'),
               'tr9_credibility',Source.getSignal(Device_Tracks, 'tr9_credibility'),               
               ylabel = '[%%]')
  Sync.addClient(PN)

  # ------------------------------------------------------------------------
  # Tracks acceleration_over_ground
  
  PN = datavis.cPlotNavigator('TRW AC100 - Tracks acceleration over ground')
  for Idx in xrange(10):
    tmp_name = 'tr%d_acceleration_over_ground'%Idx
    PN.addsignal(tmp_name,Source.getSignal(Device_Tracks, tmp_name),
               ylabel = '[m/s^2]')
  Sync.addClient(PN)


  PN = datavis.cPlotNavigator('AC100 - Tracks acceleration over ground')
  PN.addsignal('tr0_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr0_acceleration_over_ground'),
               'tr1_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr1_acceleration_over_ground'),
               'tr2_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr2_acceleration_over_ground'),
               'tr3_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr3_acceleration_over_ground'),
               'tr4_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr4_acceleration_over_ground'),
               'tr5_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr5_acceleration_over_ground'),
               'tr6_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr6_acceleration_over_ground'),
               'tr7_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr7_acceleration_over_ground'),
               'tr8_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr8_acceleration_over_ground'),
               'tr9_acceleration_over_ground',Source.getSignal(Device_Tracks, 'tr9_acceleration_over_ground'),               
               ylabel = '[m/^s^2]')
  Sync.addClient(PN)


  # ------------------------------------------------------------------------
  # Tracks acc track info
  
  PN = datavis.cPlotNavigator('TRW AC100 - Tracks acc track info')
  for Idx in xrange(10):
    tmp_name = 'tr%d_acc_track_info'%Idx
    PN.addsignal(tmp_name,Source.getSignal(Device_Tracks, tmp_name),
               ylabel = '[???]')
  Sync.addClient(PN)


  PN = datavis.cPlotNavigator('AC100 - Tracks acc track info')
  PN.addsignal('tr0_acc_track_info',Source.getSignal(Device_Tracks, 'tr0_acc_track_info'),
               'tr1_acc_track_info',Source.getSignal(Device_Tracks, 'tr1_acc_track_info'),
               'tr2_acc_track_info',Source.getSignal(Device_Tracks, 'tr2_acc_track_info'),
               'tr3_acc_track_info',Source.getSignal(Device_Tracks, 'tr3_acc_track_info'),
               'tr4_acc_track_info',Source.getSignal(Device_Tracks, 'tr4_acc_track_info'),
               'tr5_acc_track_info',Source.getSignal(Device_Tracks, 'tr5_acc_track_info'),
               'tr6_acc_track_info',Source.getSignal(Device_Tracks, 'tr6_acc_track_info'),
               'tr7_acc_track_info',Source.getSignal(Device_Tracks, 'tr7_acc_track_info'),
               'tr8_acc_track_info',Source.getSignal(Device_Tracks, 'tr8_acc_track_info'),
               'tr9_acc_track_info',Source.getSignal(Device_Tracks, 'tr9_acc_track_info'),               
               ylabel = '[???]')
  Sync.addClient(PN)

  # ------------------------------------------------------------------------
  # Tracks power
  
  PN = datavis.cPlotNavigator('TRW AC100 - Tracks power')
  for Idx in xrange(10):
    tmp_name = 'tr%d_power'%Idx
    PN.addsignal(tmp_name,Source.getSignal(Device_Tracks, tmp_name),
               ylabel = '[dB]')
  Sync.addClient(PN)


  PN = datavis.cPlotNavigator('AC100 - Tracks power')
  PN.addsignal('tr0_power',Source.getSignal(Device_Tracks, 'tr0_power'),
               'tr1_power',Source.getSignal(Device_Tracks, 'tr1_power'),
               'tr2_power',Source.getSignal(Device_Tracks, 'tr2_power'),
               'tr3_power',Source.getSignal(Device_Tracks, 'tr3_power'),
               'tr4_power',Source.getSignal(Device_Tracks, 'tr4_power'),
               'tr5_power',Source.getSignal(Device_Tracks, 'tr5_power'),
               'tr6_power',Source.getSignal(Device_Tracks, 'tr6_power'),
               'tr7_power',Source.getSignal(Device_Tracks, 'tr7_power'),
               'tr8_power',Source.getSignal(Device_Tracks, 'tr8_power'),
               'tr9_power',Source.getSignal(Device_Tracks, 'tr9_power'),               
               ylabel = '[dB]')
  Sync.addClient(PN)


  # ------------------------------------------------------------------------
  # Tracks Flags: _CW_track _secondary 
  
  PN = datavis.cPlotNavigator('TRW AC100 - Tracks Flags _CW_track _secondary ')
  for Idx in xrange(10):
     tmp_name1 = 'tr%d_CW_track'%Idx
     tmp_name2 = 'tr%d_secondary'%Idx
     tmp_name3 = 'tr%d_forbidden'%Idx
     tmp_name4 = 'tr%d_is_video_associated'%Idx
     PN.addsignal(tmp_name1,Source.getSignal(Device_Tracks,tmp_name1),
                  tmp_name2,Source.getSignal(Device_Tracks,tmp_name2),
                  tmp_name3,Source.getSignal(Device_Tracks,tmp_name3),
                  tmp_name4,Source.getSignal(Device_Tracks,tmp_name4),
                  ylabel = '[???]')
  Sync.addClient(PN)

  # ------------------------------------------------------------------------
  # Target range
  PN = datavis.cPlotNavigator('TRW AC100 - Target range')
  for Idx in xrange(10):
    tmp_name = 'ta%d_range'%Idx
    PN.addsignal(tmp_name,Source.getSignal(Device_Targets, tmp_name),
               ylabel = '[m]')
  Sync.addClient(PN)

  PN = datavis.cPlotNavigator('AC100 - Targets')
  PN.addsignal('ta0_range',Source.getSignal(Device_Targets, 'ta0_range'),
               'ta1_range',Source.getSignal(Device_Targets, 'ta1_range'),
               'ta2_range',Source.getSignal(Device_Targets, 'ta2_range'),
               'ta3_range',Source.getSignal(Device_Targets, 'ta3_range'),
               'ta4_range',Source.getSignal(Device_Targets, 'ta4_range'),
               'ta5_range',Source.getSignal(Device_Targets, 'ta5_range'),
               'ta6_range',Source.getSignal(Device_Targets, 'ta6_range'),
               'ta7_range',Source.getSignal(Device_Targets, 'ta7_range'),
               'ta8_range',Source.getSignal(Device_Targets, 'ta8_range'),
               'ta9_range',Source.getSignal(Device_Targets, 'ta9_range'),               
               ylabel = '[m]')
  Sync.addClient(PN)
                    
  pass

#----------------------ACC100 IntroData-----------------
def getAC100Introdata(Source):
    Source.loadParser()
    Device_ESR_Track1, = Source.Parser.getDeviceNames('tr0_range')
    time = Source.getSignal(Device_ESR_Track1, 'tr0_range')[0]
    signal_range = Source.getSignal(Device_ESR_Track1, 'tr0_range')[1]
    signal_angle = Source.getSignal(Device_ESR_Track1, 'tr0_uncorrected_angle')[1]
    signal_angle = -signal_angle
    signal_dx=signal_range*np.cos(signal_angle*(np.pi/180.0))
    signal_dy=signal_range*np.sin(signal_angle*(np.pi/180.0))
    signal_rangerate = Source.getSignal(Device_ESR_Track1, 'tr0_relative_velocitiy')[1]
    
    
    return time,signal_dx,signal_dy,signal_rangerate,signal_angle


if __name__ == '__main__':
  import aebs.proc
  import datavis
  import sys
  import os
  
  if len(sys.argv) == 2:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source(sys.argv[1], ECU='ECU_0_0')
    Sync    = datavis.cSynchronizer()    

    viewAC100(Sync, Source, 200)
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
