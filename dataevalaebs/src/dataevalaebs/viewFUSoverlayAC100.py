"""
 Plot LRR3 and AC100 objects in one plot

:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
import sys
import os

import numpy as np

import aebs.proc
import datavis

def calcByHandle(Source, Name):
  """
  :Parameters:
    Source : `aebs.proc.cLrr3Source`
    Name : str
  :ReturnType: numpy.ndarray, numpy.ndarray
  :Return:
    time
    value
  """
  # Indicate SIT intro object  
  device_name, = Source.getExtendedDeviceNames('ECU')
  handle = Source.getSignal(device_name, 'sit.IntroFinder_TC.Intro.i0.ObjectList.i0')[1]
  signal = np.zeros(len(handle))
  for h in np.unique(handle):
    time, value = Source.getSignalByHandle(device_name, h, Name)
    mask = handle == h
    signal[mask] = value[mask]
  return time, signal

def calcByHandle2(Source, Name, time):
  """
  :Parameters:
    Source : `aebs.proc.cLrr3Source`
    Name : str
  :ReturnType: numpy.ndarray, numpy.ndarray
  :Return:
    time
    value
  """
  # Indicate SIT intro object  
  device_name, = Source.getExtendedDeviceNames('ECU')
  handle = Source.getSignal(device_name, 'sit.IntroFinder_TC.Intro.i0.ObjectList.i0',ScaleTime = time)[1]
  signal = np.zeros(len(handle))
  for h in np.unique(handle):
    value = Source.getSignalByHandle(device_name, h, Name,ScaleTime = time)[1]
    mask = handle == h
    signal[mask] = value[mask]
  return time, signal
  
def viewFUSlist(Sync, Source):
  """
  :Parameters:
    Sync : `datavis.cSynchronizer`
    Source : `aebs.proc.cLrr3Source`
  """
  # Get data time domain and velocity
  tc,vdis = Source.getSignalFromECU('csi.VelocityData_TC.vDis')
  
  # List navigator to display distance values
  Client = datavis.cListNavigator()
  for i in range(0,33):
    dx = Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dxv'%i)[1]
    Client.addsignal('fus.ObjData_TC.FusObj.i%d.dxv'%i, (tc, dx))
  
  # Add list navigator to the synchronizer
  Sync.addClient(Client)
  pass

def fillObjects(Source):
  """
  :Parameters:
    Source : `aebs.proc.cLrr3Source`
  :ReturnType: list
  :Return: [{'dx':<numpy.ndarray>, 'dy':<numpy.ndarray>, 'label':<str>, 
             'type':<numpy.ndarray>, 'color':<numpy.ndarray>},]
  """

  print 'AC100 fillObjects()'


  N_AC100_TR = 10

  Source.loadParser()
  Device_Tracks, =   Source.Parser.getDeviceNames('tr1_range')
  print 'Device_Tracks = "%s"' % Device_Tracks
  time = Source.getSignal(Device_Tracks,('tr1_range'))[0]

  Device_General_radar_status, = Source.Parser.getDeviceNames('actual_vehicle_speed')
  actual_vehicle_speed         = Source.getSignal(Device_General_radar_status, 'actual_vehicle_speed',ScaleTime = time)[1]
  
  objects = []

  # ["type"]
  #  0: rectangular;            circles       -> moving objects
  #  1: edges of rectangular;   rectangualr   -> intro
  #  2: X                       X             -> stationary objects
  #  3: diamonds                X             -> intervention
  #  4: left and right markers  rectangular   -> warning
  
  # Add AC100 objects to object list 
  for tr_no in xrange(N_AC100_TR):
    o = {}
    t = Source.getSignal(Device_Tracks,('tr%d_range'%tr_no))[0]
    if t.size > 0:
      internal_track_index   = Source.getSignal(Device_Tracks,'tr%d_internal_track_index'%tr_no,ScaleTime = time)[1]
      track_selection_status = Source.getSignal(Device_Tracks,('tr%d_track_selection_status'%tr_no),ScaleTime = time)[1]
      dx_range               = Source.getSignal(Device_Tracks,'tr%d_range'%tr_no,ScaleTime = time)[1]
      angle                  = Source.getSignal(Device_Tracks,('tr%d_uncorrected_angle'%tr_no),ScaleTime = time)[1]
      rel_v                  = Source.getSignal(Device_Tracks,'tr%d_relative_velocitiy'%tr_no,ScaleTime = time)[1]
     


      dxv      = dx_range*np.cos(-angle*(np.pi/180.0))
      dyv      = dx_range*np.sin(-angle*(np.pi/180.0))

      CW_track = Source.getSignal(Device_Tracks,'tr%d_CW_track'%tr_no,ScaleTime = time)[1]

#      print rel_v
#      print actual_vehicle_speed
      DriveInvDir_b = (rel_v<0) & (rel_v < -actual_vehicle_speed)

      # calculate signal used for selection
      Stand_b = (track_selection_status & (2**4))>0   # Bit4: stationary

      o["dx"] = dxv
      o["dy"] = dyv
      o["label"] = "%d"%tr_no # FUS index as simple label 
      # o["label"] = np.array(o["dx"], dtype=("a6")) # dx as ndarray label
      # o["type"] = 0 # set type to 0
      o["type"] = 5 + Stand_b # set type of stationary objects to 2 (draw simple X)
      #o["type"] = 0

      # color
      # a) relative speed
      # Set color to red or green according to relative speed
      w = np.reshape(np.repeat(rel_v < 0, 3), (-1,3))
      o["color"] = np.where(
        w,
        [255, 0, 0],
        [0, 255, 0])

      # Set color of inverse dir objects to blue
      w = np.reshape(np.repeat(DriveInvDir_b == 1, 3), (-1, 3))
      o["color"] = np.where(
        w,
        [0, 0, 255],
        o["color"])

      # b) Collision Warning Track (purple)
      w = np.reshape(np.repeat(CW_track > 0.5, 3), (-1,3))
      o["color"] = np.where(
        w,
        [220, 0, 220],
        o["color"])

      # c) stationary objects (purple)
      w = np.reshape(np.repeat(Stand_b > 0.5, 3), (-1,3))
      o["color"] = np.where(
        w,
        [0, 200, 150],
        o["color"])


        # Set color of inverse dir objects to blue
        #w = np.reshape(np.repeat(Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.b.b.DriveInvDir_b"%i)[1] == 1, 3), (-1, 3))
        #o["color"] = np.where(
        #  w,
        #  [0, 0, 255],
        #  o["color"])
        # Darken object color where exist probability or obstacle probability is less than 0.1
        #w = np.reshape(np.repeat(np.logical_or(Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.wExistProb"%i)[1] < 0.1, Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.wObstacle"%i)[1] < 0.1), 3), (-1, 3))
        #o["color"] = np.where(
        #  w,
        #  o["color"] / 2,
        #  o["color"])
        # Add object to the object list
        
      objects.append(o)

      
  # Add FUS objects to object list 
  if 1:    
    for i in range(0,33):
      o = {}
      
      # object position: dx, dy
      o["dx"] = Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dxv'%i,ScaleTime = time)[1]
      o["dy"] = Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dyv'%i,ScaleTime = time)[1]

      # object label 
      o["label"] = "%d"%i # FUS index as simple label 
      # o["label"] = np.array(o["dx"], dtype=("a6")) # dx as ndarray label

      # object type (0 : Moving; 1 : Intro; 2 : Stationary)
      o["type"] = 2 * Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.b.b.Stand_b"%i,ScaleTime = time)[1] # set type of stationary objects to 2 (draw simple X)

      # object color
      # o["color"] = (255, 0, 0) # Set Color to simple Red 
      # Set color to red or green according to relative speed
      w = np.reshape(np.repeat(Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.vxv"%i,ScaleTime = time)[1] < 0, 3), (-1,3))
      o["color"] = np.where(
        w,
        [255, 0, 0],
        [0, 255, 0])
      # Set color of inverse dir objects to blue
      w = np.reshape(np.repeat(Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.b.b.DriveInvDir_b"%i,ScaleTime = time)[1] == 1, 3), (-1, 3))
      o["color"] = np.where(
        w,
        [0, 0, 255],
        o["color"])
      
      # Darken object color where exist probability or obstacle probability is less than 0.1
      #  w = np.reshape(np.repeat(np.logical_or(Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.wExistProb"%i,ScaleTime = time)[1] < 0.1, Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.wObstacle"%i,ScaleTime = time))[1] < 0.1), 3), (-1, 3))
      #  o["color"] = np.where(
      #    w,
      #    o["color"] / 2,
      #    o["color"])
      # Add object to the object list
      objects.append(o)
     
  return time, objects

def indicateIntro(Source,time):
  """
  :Parameters:
    Source : `aebs.proc.cLrr3Source`
  :ReturnType: numpy.ndarray, dict
  :Return:
    time  
    {'dx':<numpy.ndarray>, 'dy':<numpy.ndarray>, 'label':<str>, 'type':<int>, 
    'color':<tuple>}
  """
  o = {}
  o["dx"] = calcByHandle2(Source, 'dxv',time)[1]
  o["dy"] = calcByHandle2(Source, 'dyv',time)[1]
  o["label"] = ""
  o["type"] = 1
  o["color"] = (255, 0, 255)

  print 'o["dx"]', len(o["dx"])
  print 'o["dy"]', len(o["dy"])

  return time, o
  
def viewFUSoverlay(Sync, Source, VideoFile):
  """
  :Parameters:
    Sync : `datavis.cSynchronizer`
    Source : `aebs.proc.cLrr3Source`
    VideoFile : str
  """
  # Get data time domain and velocity
  #tc,vdis = Source.getSignalFromECU('csi.VelocityData_TC.vDis')
  # Get the video time in the data time base
  #vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime=tc)[1]
  # Get acceleration
  #accel = Source.getSignalFromECU('evi.General_TC.axvRef')[1]
  
  # object list 
  time, objects = fillObjects(Source)

  print 'time', len(time)
  
  # Indicate intro
  
  time, o = indicateIntro(Source,time)
  
  # Add object to the object list
  objects.append(o)
    
  # Indicate ATS target object
  # o = {}
  # o["dx"] = Source.getSignalFromECU('ats.Po_TC.PO.i0.dxvFilt')[1]
  # o["dy"] = Source.getSignalFromECU('ats.Po_TC.PO.i0.dyv')[1]
  # o["type"] = 1
  # o["color"] =  (255, 255, 255)
  # # Add object to the object list
  # objects.append(o)
  
  # Indicate acoustic warning
  #o = {}
  #o["dx"] = calcByHandle(Source, 'dxv')
  #o["dx"] = np.where(
  #  Source.getSignalFromECU("acoacoi.__b_AcoNoFb.__b_Aco.request_B")[1] > 0, 
  #  o["dx"],
  #  0)
  #o["dy"] = calcByHandle(Source, 'dyv')
  #o["dy"] = np.where(
  #  Source.getSignalFromECU("acoacoi.__b_AcoNoFb.__b_Aco.request_B")[1] > 0, 
  #  o["dy"],
  #  0)
  #o["type"] = 4
  #o["color"] = [255, 255, 0]
  #objects.append(o)
  
  # Indicate brake intervention
  #o = {}
  #o["dx"] = calcByHandle(Source, 'dxv')
  #o["dx"] = np.where(
  #  Source.getSignalFromECU("acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B")[1] > 0, 
  #  o["dx"],
  #  0)
  #o["dy"] = calcByHandle(Source, 'dyv')
  #o["dy"] = np.where(
  #  Source.getSignalFromECU("acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B")[1] > 0, 
  #  o["dy"],
  #  0)
  #o["type"] = 3
  #w = Source.getSignalFromECU("acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.requestCharacteristic")[1]
  #o["color"] = np.transpose([np.ones(np.shape(w), dtype=int)*255, np.maximum(0.01 * w + 255,0).astype(int), np.zeros(np.shape(w), dtype=int)])
  #objects.append(o)

  # Video overlay player
  Client = datavis.cVideoNavigator(VideoFile, {})
  # Set the overlay objects of the player, for simplicity acceleration compensation is 1/50 of the acceleration value
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime=time)[1]
  # Get acceleration
  accel = Source.getSignalFromECU('evi.General_TC.axvRef', ScaleTime=time)[1]


  Client.setobjects(objects, vidtime, accel / 50.)

  # Get the video time in the data time base
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime=time)[1]
  # Add the video overlay player to the synchronizer
  Sync.addClient(Client, (time, vidtime))
  pass

def vieFUSplot(Sync, Source, FgNr):
  """
  :Parameters:
    Sync : `datavis.cSynchronizer`
    Source : `aebs.proc.cLrr3Source`
    FgNr : int
  """
  # Get data time domain and velocity
  tc,vdis = Source.getSignalFromECU('csi.VelocityData_TC.vDis')
  # Get the video time in the data time base
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime=tc)[1]
  # Get acceleration
  accel = Source.getSignalFromECU('evi.General_TC.axvRef')[1]


  # Plot1
  Client = datavis.cPlotNavigator('General velocity data', FgNr)
  Client.addsignal('csi.VelocityData_TC.vDis', (tc, vdis), color="o-")
  Client.addsignal('evi.General_TC.axvRef', (tc, accel))
  Client.addsignal('Multimedia_1', (tc, vidtime))
  Sync.addClient(Client)
  
  # Plot2
  Client = datavis.cPlotNavigator('Intro details')
  Client.addsignal("intro.dx", calcByHandle(Source, 'dxv'))
  Client.addsignal("intro.dy", calcByHandle(Source, 'dyv'))
  Client.addsignal("reqChar", Source.getSignalFromECU("acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.requestCharacteristic"))
  Sync.addClient(Client)
  pass
  
if __name__ == '__main__':  
  VideoFile = "e:/DAS/PEB/2010_04_23_release__LRR3_for_MAN_AEBS_v2010-04-21__SAXadv_last_paramchanges/AEBS_H05.2604_2010-04-23_06-14_72.avi"
  MeasFile = "e:/DAS/PEB/2010_04_23_release__LRR3_for_MAN_AEBS_v2010-04-21__SAXadv_last_paramchanges/AEBS_H05.2604_2010-04-23_06-14_72.MDF"
  # VideoFile = "d:/temp/data/AEBS_H05.2604_2010-04-23_06-46_74.avi"
  # MeasFile = "d:/temp/data/AEBS_H05.2604_2010-04-23_06-46_74.MDF"
  # VideoFile = "d:/temp/data/AEBS_Bendix_H05.2604_2010-04-14_15-57_43.avi"
  # MeasFile = "d:/temp/data/AEBS_Bendix_H05.2604_2010-04-14_15-57_43.MDF"
  # VideoFile = "d:/temp/data/AEBS_H05.2604_2010-04-22_14-58_38.avi"
  # MeasFile = "d:/temp/data/AEBS_H05.2604_2010-04-22_14-58_38.MDF"
  # VideoFile = 'e:/DAS/ACC3_Bendix/2009-11-24_SOW_Endurance_on_EngRoute_CP1.5/moni_scu_DIAB_BSAMPLE_E200Z6V_2009-11-24_11-21_0014.avi'
  # MeasFile = 'e:/DAS/ACC3_Bendix/2009-11-24_SOW_Endurance_on_EngRoute_CP1.5/moni_scu_DIAB_BSAMPLE_E200Z6V_2009-11-24_11-21_0014.MDF'
  # VideoFile = 'e:/DAS/LRR3/2009_11_13_release__LRR3_for_Scania_v2009_11_12_LHT_on_dMaxFollowPO_disabled_(250m)_no_curveness_dependance/LRR3_H052604_C2SAMPLE_SCANIA_20091113_10.31_13.avi'
  # MeasFile = 'e:/DAS/LRR3/2009_11_13_release__LRR3_for_Scania_v2009_11_12_LHT_on_dMaxFollowPO_disabled_(250m)_no_curveness_dependance/LRR3_H052604_C2SAMPLE_SCANIA_20091113_10.31_13.MDF'

  if len(sys.argv) > 1:
    MeasFile   = sys.argv[1]
    Head, Tail = os.path.splitext(sys.argv[1])
    VideoFile  = Head + '.avi'
    # Data source
    Source = aebs.proc.cLrr3Source(MeasFile, ECU='ECU_0_0')
    # Synchronizer for visualization  
    Sync = datavis.cSynchronizer()

    viewFUSoverlay(Sync, Source, VideoFile)
    viewFUSlist(   Sync, Source)
    vieFUSplot(    Sync, Source, 100)

    # Run the whole stuff
    Sync.run()    
    raw_input("Press Enter to Exit\r\n")
    Sync.close()
  else:
    print "usage: %s filename.mdf"%sys.argv[0]
    
