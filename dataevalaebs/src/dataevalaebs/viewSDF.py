"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis

def viewSDF(Sync, Source, FgNr):
  """
  Create PlotNavigators to illustrate the SDF. 
  
  :Parameters:
    sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `aebs.proc.cLrr3Source`
      Signal source to get mdf signals.
    FgNr : int
      Intialize the figure number of the first `datavis.cPlotNavigators`.
  :ReturnType: None
  """
  FUS_idx  = Source.getFUSIndexMode(0)  
  Intro    = Source.getSignalFromECU('sit.IntroFinder_TC.Intro.i0.ObjectList.i0')[1]
  RelGraph = Source.getSignalFromECU('sit.RelationGraph_TC.ObjectList.i%d' %(FUS_idx,))[1]
  SIT_idx  = Intro[Intro == RelGraph][0]

  " Overview dx"
  PN = datavis.cPlotNavigator('Overview dx', FgNr)
  PN.addsignal('Mobileye - Distance to Obstacle 0',
               Source.getSignal('obstacle_0_info(720)_3_', 'Distance_to_Obstacle_0'),
               'Iteris - PO target range OFC',
               Source.getSignal('Iteris_object_follow(98FF00E8)_1_', 'PO_target_range_OFC'),
               'LRR3 TO1 dxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.dxvFilt' %(0,)),
               'LRR3 TO2 dxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.dxvFilt' %(1,)),
               'LRR3 SO dxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.dxvFilt' %(4,)),
               ylabel = '[m]')
  Sync.addClient(PN)

  " --------------------------------------------------------"
  "Mobileye Valid flags"
  PN = datavis.cPlotNavigator('Mobileye - Valid flags')
  PN.addsignal('Valid 9',
               Source.getSignal('obstacle_9_info(729)_3_', 'Valid_9'),
               'Valid 8',
               Source.getSignal('obstacle_8_info(728)_3_', 'Valid_8'),
               'Valid 7',
               Source.getSignal('obstacle_7_info(727)_3_', 'Valid_7'),
               'Valid 6',
               Source.getSignal('obstacle_6_info(726)_3_', 'Valid_6'),
               'Valid 5',
               Source.getSignal('obstacle_5_info(725)_3_', 'Valid_5'),
               'Valid 4',
               Source.getSignal('obstacle_4_info(724)_3_', 'Valid_4'),
               'Valid 3',
               Source.getSignal('obstacle_3_info(723)_3_', 'Valid_3'),
               'Valid 2',
               Source.getSignal('obstacle_2_info(722)_3_', 'Valid_2'),
               'Valid 1',
               Source.getSignal('obstacle_1_info(721)_3_', 'Valid_1'),
               'Valid 0',
               Source.getSignal('obstacle_0_info(720)_3_', 'Valid_0'),
               ylabel = '[bool]',
               offset = [18.0, 16.0, 14.0, 12.0, 10.0, 8.0, 6.0, 4.0, 2.0, 0.0])
  Sync.addClient(PN)


  " --------------------------------------------------------"
  "Mobileye obstacle 0"
  PN = datavis.cPlotNavigator('Mobileye - obstacle 0')
  
  PN.addsignal('Valid 0',
               Source.getSignal('obstacle_0_info(720)_3_', 'Valid_0'),
               ylabel = '[bool]')

  PN.addsignal('Distance_to_Obstacle_0',
               Source.getSignal('obstacle_0_info(720)_3_', 'Distance_to_Obstacle_0'),
               'LRR3 TO1 dxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.dxvFilt' %(0,)),
               'LRR3 TO2 dxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.dxvFilt' %(1,)),
               ylabel = '[m]')

  PN.addsignal('Obstacle_width_0',
               Source.getSignal('obstacle_0_info(720)_3_', 'Obstacle_width_0'),
               ylabel = '[m]')

  PN.addsignal('Angle_to_obstacle_0',
               Source.getSignal('obstacle_0_info(720)_3_', 'Angle_to_obstacle_0'),
               ylabel = '[degree]')

  PN.addsignal('Relative_velocity_to_obstacle_0',
               Source.getSignal('obstacle_0_info(720)_3_', 'Relative_velocity_to_obstacle_0'),
               'LRR3 TO1 vdxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.vxvFilt' %(0,)),
               'LRR3 TO2 vxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.vxvFilt' %(1,)),

               ylabel = '[m/s]')

  PN.addsignal('Obstacle_ID_0',
               Source.getSignal('obstacle_0_info(720)_3_', 'Obstacle_ID_0'),
               ylabel = '[1]')

  PN.addsignal('CIPV_flag_0',
               Source.getSignal('obstacle_0_info(720)_3_', 'CIPV_flag_0'),
               ylabel = '[bool]')

  Sync.addClient(PN)

  " --------------------------------------------------------"
  "Mobileye obstacle 1"
  PN = datavis.cPlotNavigator('Mobileye - obstacle 1')
  
  PN.addsignal('Valid 1',
               Source.getSignal('obstacle_1_info(721)_3_', 'Valid_1'),
               ylabel = '[bool]')

  PN.addsignal('Distance_to_Obstacle_1',
               Source.getSignal('obstacle_1_info(721)_3_', 'Distance_to_Obstacle_1'),
               'LRR3 TO1 dxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.dxvFilt' %(0,)),
               'LRR3 TO2 dxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.dxvFilt' %(1,)),
               ylabel = '[m]')

  PN.addsignal('Obstacle_width_1',
               Source.getSignal('obstacle_1_info(721)_3_', 'Obstacle_width_1'),
               ylabel = '[m]')

  PN.addsignal('Angle_to_obstacle_1',
               Source.getSignal('obstacle_1_info(721)_3_', 'Angle_to_obstacle_1'),
               ylabel = '[degree]')

  PN.addsignal('Relative_velocity_to_obstacle_1',
               Source.getSignal('obstacle_1_info(721)_3_', 'Relative_velocity_to_obstacle_1'),
               'LRR3 TO1 vdxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.vxvFilt' %(0,)),
               'LRR3 TO2 vxvFilt',
               Source.getSignalFromECU('ats.Po_TC.PO.i%d.vxvFilt' %(1,)),
               ylabel = '[m/s]')

  PN.addsignal('Obstacle_ID_1',
               Source.getSignal('obstacle_1_info(721)_3_', 'Obstacle_ID_1'),
               ylabel = '[1]')

  PN.addsignal('CIPV_flag_1',
               Source.getSignal('obstacle_1_info(721)_3_', 'CIPV_flag_1'),
               ylabel = '[bool]')

  Sync.addClient(PN)

  " --------------------------------------------------------"
  "Iteris - object following"
  PN = datavis.cPlotNavigator('Iteris - object following')
  PN.addsignal('PO_track_number_OFC',
               Source.getSignal('Iteris_object_follow(98FF00E8)_1_', 'PO_track_number_OFC'),
               ylabel = '[1]')
  PN.addsignal('PO_system_state_OFC',
               Source.getSignal('Iteris_object_follow(98FF00E8)_1_', 'PO_system_state_OFC'),
               ylabel = '[1]')
  PN.addsignal('PO_target_range_OFC',
               Source.getSignal('Iteris_object_follow(98FF00E8)_1_', 'PO_target_range_OFC'),
               'range_to_target',
               Source.getSignal('OI_PO(98FF012A)_1_LRR3', 'range_to_target'),
               ylabel = '[m]')
  PN.addsignal('PO_target_width_OFC',
               Source.getSignal('Iteris_object_follow(98FF00E8)_1_', 'PO_target_width_OFC'),
               ylabel = '[m]')
  PN.addsignal('PO_right_azimuth_angle_OFC',
               Source.getSignal('Iteris_object_follow(98FF00E8)_1_', 'PO_right_azimuth_angle_OFC'),
               'PO_left_azimuth_angle_OFC',
               Source.getSignal('Iteris_object_follow(98FF00E8)_1_', 'PO_left_azimuth_angle_OFC'),
               ylabel = '[degree]')
  PN.addsignal('PO_classification_OFC',
               Source.getSignal('Iteris_object_follow(98FF00E8)_1_', 'PO_classification_OFC'),
               ylabel = '[1]')
  Sync.addClient(PN)
  pass
  
if __name__ == '__main__':
  import aebs.proc
  import sys
  import os
  
  if len(sys.argv) == 2:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source(sys.argv[1], ECU='ECU_0_0')
    Sync    = datavis.cSynchronizer()    
    
    viewSDF(Sync, Source, 300)    
    # try:
      # viewSDF(Sync, Source, 300)    
    # except KeyError, error:
      # import re
      # Devices  = Source.getDeviceNames(error.message)
      # String   = open(__file__).read()
      # ReString = re.sub("Source.getSignalFromECU\(\\s*'%s'\\s*\)" %error.message, "Source.getSignal('%s', '%s')" %(Devices[0], error.message), String)
      # open(__file__, 'w').write(ReString)
      # print String != ReString, Devices, error.message
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
    
    Sync.run()    
    raw_input("Press Enter to Exit\n")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
