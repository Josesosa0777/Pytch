"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import datavis

def viewIbeoLux(Sync, Source, FgNr):
  """
  Create PlotNavigators to illustrate the SIT. 
  
  :Parameters:
    sync : `datavis.cSynchronizer`
      Synchronizer instance to connect the `datavis.cPlotNavigators`s.
    Source : `aebs.proc.cLrr3Source`
      Signal source to get mdf signals.
    FgNr : int
      Intialize the figure number of the first `datavis.cPlotNavigators`.
  :ReturnType: None
  """
  # Message:    List_header
  # Identifier: 500h
  # Signals:    Version 
  #             Number_of_objects 
  #             Sensor_view_range 
  #             Sensor_temperature 
  #             Object_data_info_flags

  PN = datavis.cPlotNavigator('Ibeo Lux - List_header', FgNr)
  PN.addsignal('Version',
               Source.getSignal('List_header(500)_4_', 'Version'),
               ylabel = '[]')
  PN.addsignal('Number_of_objects',
               Source.getSignal('List_header(500)_4_', 'Number_of_objects'),
               ylabel = '[]')
  PN.addsignal('Sensor_view_range',
               Source.getSignal('List_header(500)_4_', 'Sensor_view_range'),
               ylabel = '[]')
  PN.addsignal('Sensor_temperature',
               Source.getSignal('List_header(500)_4_', 'Sensor_temperature'),
               ylabel = '[]')
  PN.addsignal('Object_data_info_flags',
               Source.getSignal('List_header(500)_4_', 'Object_data_info_flags'),
               ylabel = '[]')
  Sync.addClient(PN)

  # Message:    Time_stamp
  # Identifier: 501h
  # Signals:    NTP_seconds
  #             NTP_fractional_seconds
  PN = datavis.cPlotNavigator('Ibeo Lux - Time_stamp')
  PN.addsignal('NTP_seconds',
               Source.getSignal('Time_stamp(501)_4_', 'NTP_seconds'),
               ylabel = '[s]')
  # error: long int too large to convert to int
  #PN.addsignal('NTP_fractional_seconds',
  #             Source.getSignalFromECU('NTP_fractional_seconds'),
  #             ylabel = '[s]')
  Sync.addClient(PN)


  # Message:    Tracking_1
  # Identifier: 502h
  # Signals:    Object_ID 
  #             Position_x 
  #             Position_y 
  #             Velocity_x 
  #             Velocity_y 

  PN = datavis.cPlotNavigator('Ibeo Lux - Tracking_1')
  PN.addsignal('Object_ID',
               Source.getSignal('Tracking_1(502)_4_', 'Object_ID'),
               ylabel = '[]')
  PN.addsignal('Position_x',
               Source.getSignal('Tracking_1(502)_4_', 'Position_x'),
               ylabel = '[cm]')
  PN.addsignal('Position_y',
               Source.getSignal('Tracking_1(502)_4_', 'Position_y'),
               ylabel = '[cm]')
  PN.addsignal('Velocity x',
               Source.getSignal('Tracking_1(502)_4_', 'Velocity_x'),
               ylabel = '[]')
  PN.addsignal('Velocity_y',
               Source.getSignal('Tracking_1(502)_4_', 'Velocity_y'),
               ylabel = '[]')
  Sync.addClient(PN)

  # Message:    Tracking_2
  # Identifier: 503h
  # Signals:    Object_ID 
  #             Object_age
  #             Object_prediction_age 
  #             Object_time_offset
  #             Position_x_sigma
  #             Position_y_sigma
  #             Velocity_x_sigma 
  #             Velocity_y_sigma
  PN = datavis.cPlotNavigator('Ibeo Lux - Tracking_2')
  PN.addsignal('Object_ID',
               Source.getSignal('Tracking_2(503)_4_', 'Object_ID'),
               ylabel = '[]')
  PN.addsignal('Object_age',
               Source.getSignal('Tracking_2(503)_4_', 'Object_age'),
               ylabel = '[cm]')
  PN.addsignal('Object_prediction_age',
               Source.getSignal('Tracking_2(503)_4_', 'Object_prediction_age'),
               ylabel = '[cm]')
  PN.addsignal('Object_time_offset x',
               Source.getSignal('Tracking_2(503)_4_', 'Object_time_offset'),
               ylabel = '[]')
  PN.addsignal('Position_x_sigma',
               Source.getSignal('Tracking_2(503)_4_', 'Position_x_sigma'),
               ylabel = '[]')
  PN.addsignal('Position_y_sigma',
               Source.getSignal('Tracking_2(503)_4_', 'Position_y_sigma'),
               ylabel = '[]')
  PN.addsignal('Velocity_x_sigma',
               Source.getSignal('Tracking_2(503)_4_', 'Velocity_x_sigma'),
               ylabel = '[]')
  PN.addsignal('Velocity_y_sigma',
               Source.getSignal('Tracking_2(503)_4_', 'Velocity_y_sigma'),
               ylabel = '[]')
  Sync.addClient(PN)

  # Message:    Class_and_box_1
  # Identifier: 504h
  # Signals:    Object_ID 
  #             Object_classification
  #             Object_classification_certainty
  #             Object_classification_age
  #             Box_center_x
  #             Box_center_y
  PN = datavis.cPlotNavigator('Ibeo Lux - Class_and_box_1')
  PN.addsignal('Object_ID',
               Source.getSignal('Class_and_box_1(504)_4_', 'Object_ID'),
               ylabel = '[]')
  PN.addsignal('Object_classification',
               Source.getSignal('Class_and_box_1(504)_4_', 'Object_classification'),
               ylabel = '[cm]')
  PN.addsignal('Object_classification_certainty',
               Source.getSignal('Class_and_box_1(504)_4_', 'Object_classification_certainty'),
               ylabel = '[cm]')
  PN.addsignal('Object_classification_age x',
               Source.getSignal('Class_and_box_1(504)_4_', 'Object_classification_age'),
               ylabel = '[]')
  PN.addsignal('Box_center_x',
               Source.getSignal('Class_and_box_1(504)_4_', 'Box_center_x'),
               ylabel = '[]')
  PN.addsignal('Box_center_y',
               Source.getSignal('Class_and_box_1(504)_4_', 'Box_center_y'),
               ylabel = '[]')
  Sync.addClient(PN)

  # Message:    Box_2
  # Identifier: 505h
  # Signals:    Object_ID 
  #             Box_size_x 
  #             Box_size_y 
  #             Box_orientation 
  PN = datavis.cPlotNavigator('Ibeo Lux - Box_2')
  PN.addsignal('Object_ID',
               Source.getSignal('Box_2(505)_4_', 'Object_ID'),
               ylabel = '[]')
  PN.addsignal('Box_size_x',
               Source.getSignal('Box_2(505)_4_', 'Box_size_x'),
               ylabel = '[cm]')
  PN.addsignal('Box_size_y',
               Source.getSignal('Box_2(505)_4_', 'Box_size_y'),
               ylabel = '[cm]')
  PN.addsignal('Box_orientation x',
               Source.getSignal('Box_2(505)_4_', 'Box_orientation'),
               ylabel = '[]')
  PN.addsignal('Box_center_x',
               Source.getSignal('Class_and_box_1(504)_4_', 'Box_center_x'),
               ylabel = '[]')
  Sync.addClient(PN)

  # Message:    Contour_header 
  # Identifier: 506h
  # Signals:    Object_ID
  #             Number_of_contour_points
  #             Start_point_x
  #             Start_point_y 
  #             Closest_contour_point_number
  PN = datavis.cPlotNavigator('Ibeo Lux - Contour_header')
  PN.addsignal('Object_ID',
               Source.getSignal('Contour_header(506)_4_', 'Object_ID'),
               ylabel = '[]')
  PN.addsignal('Number_of_contour_points',
               Source.getSignal('Contour_header(506)_4_', 'Number_of_contour_points'),
               ylabel = '[cm]')
  PN.addsignal('Start_point_x',
               Source.getSignal('Contour_header(506)_4_', 'Start_point_x'),
               ylabel = '[cm]')
  PN.addsignal('Start_point_y x',
               Source.getSignal('Contour_header(506)_4_', 'Start_point_y'),
               ylabel = '[]')
  PN.addsignal('Closest_contour_point_number',
               Source.getSignal('Contour_header(506)_4_', 'Closest_contour_point_number'),
               ylabel = '[]')
  Sync.addClient(PN)

  # Message:    Contour_points 
  # Identifier: 507h
  # Signals:    Object_ID
  #             Countour_message_number
  #             x_offset_point_1
  #             y_offset_point_1
  #             x_offset_point_2
  #             y_offset_point_2
  #             x_offset_point_3
  #             y_offset_point_3
 
  PN = datavis.cPlotNavigator('Ibeo Lux - Contour_points')
  PN.addsignal('Object_ID',
               Source.getSignal('Contour_points(507)_4_', 'Object_ID'),
               ylabel = '[]')
  PN.addsignal('Countour_message_number',
               Source.getSignal('Contour_points(507)_4_', 'Countour_message_number'),
               ylabel = '[cm]')
  PN.addsignal('x_offset_point_1',
               Source.getSignal('Contour_points(507)_4_', 'x_offset_point_1'),
               ylabel = '[cm]')
  PN.addsignal('y_offset_point_1',
               Source.getSignal('Contour_points(507)_4_', 'y_offset_point_1'),
               ylabel = '[]')
  PN.addsignal('x_offset_point_2',
               Source.getSignal('Contour_points(507)_4_', 'x_offset_point_2'),
               ylabel = '[cm]')
  PN.addsignal('y_offset_point_2',
               Source.getSignal('Contour_points(507)_4_', 'y_offset_point_2'),
               ylabel = '[]')
  PN.addsignal('x_offset_point_3',
               Source.getSignal('Contour_points(507)_4_', 'x_offset_point_3'),
               ylabel = '[cm]')
  PN.addsignal('y_offset_point_3',
               Source.getSignal('Contour_points(507)_4_', 'y_offset_point_3'),
               ylabel = '[]')
  
  Sync.addClient(PN)

  # Message:    Error_warning 
  # Identifier: 50Fh
  # Signals:    Error_1 
  #             Error_2 
  #             Warning_1 
  #             Warning_2 

  PN = datavis.cPlotNavigator('Ibeo Lux - Error_warning')
  PN.addsignal('Error_1',
               Source.getSignal('Error_warning(50F)_4_', 'Error_1'),
               ylabel = '[]')
  PN.addsignal('Error_2',
               Source.getSignal('Error_warning(50F)_4_', 'Error_2'),
               ylabel = '[cm]')
  PN.addsignal('Warning_1',
               Source.getSignal('Error_warning(50F)_4_', 'Warning_1'),
               ylabel = '[cm]')
  PN.addsignal('Warning_2 x',
               Source.getSignal('Error_warning(50F)_4_', 'Warning_2'),
               ylabel = '[]')
  Sync.addClient(PN)



  
  pass

if __name__ == '__main__':
  import aebs.proc
  import datavis
  import sys
  import os
  
  if len(sys.argv) == 2:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source(sys.argv[1], ECU='ECU_0_0')
    Sync    = datavis.cSynchronizer()    

    viewIbeoLux(Sync, Source, 200)
    if os.path.isfile(AviFile):
      Sync.addClient(datavis.cVideoNavigator(AviFile, {}), Source.getSignal('Multimedia_0_0', 'Multimedia_1'))
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
