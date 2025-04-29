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
  objects = []
  # Add FUS objects to object list 
  for i in range(0,33):
    o = {}
    o["dx"] = Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dxv'%i)[1]
    o["dy"] = Source.getSignalFromECU('fus.ObjData_TC.FusObj.i%d.dyv'%i)[1]
    o["label"] = "%d"%i # FUS index as simple label 
    # o["label"] = np.array(o["dx"], dtype=("a6")) # dx as ndarray label
    # o["type"] = 0 # set type to 0
    o["type"] = 2 * Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.b.b.Stand_b"%i)[1] # set type of stationary objects to 2 (draw simple X)
    # o["color"] = (255, 0, 0) # Set Color to simple Red 
    
    # Set color to red or green according to relative speed
    w = np.reshape(np.repeat(Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.vxv"%i)[1] < 0, 3), (-1,3))
    o["color"] = np.where(
      w,
      [255, 0, 0],
      [0, 255, 0])
    # Set color of inverse dir objects to blue
    w = np.reshape(np.repeat(Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.b.b.DriveInvDir_b"%i)[1] == 1, 3), (-1, 3))
    o["color"] = np.where(
      w,
      [0, 0, 255],
      o["color"])
    # Darken object color where exist probability or obstacle probability is less than 0.1
    w = np.reshape(np.repeat(np.logical_or(Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.wExistProb"%i)[1] < 0.1, Source.getSignalFromECU("fus.ObjData_TC.FusObj.i%d.wObstacle"%i)[1] < 0.1), 3), (-1, 3))
    o["color"] = np.where(
      w,
      o["color"] / 2,
      o["color"])
    # Add object to the object list
    objects.append(o)
  time, value = Source.getSignalFromECU('fus.ObjData_TC.FusObj.i0.dxv')
  return time, objects

def indicateIntro(Source):
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
  time, o["dx"] = calcByHandle(Source, 'dxv')
  time, o["dy"] = calcByHandle(Source, 'dyv')
  o["type"] = 1
  o["color"] = (255, 0, 255)
  return time, o
  
def viewFUSoverlay(Sync, Source, VideoFile):
  """
  :Parameters:
    Sync : `datavis.cSynchronizer`
    Source : `aebs.proc.cLrr3Source`
    VideoFile : str
  :ReturnType: list
  :Return: [datavis.VideoNavogator,]  
  """
  Clients = []
  # Get data time domain and velocity
  tc,vdis = Source.getSignalFromECU('csi.VelocityData_TC.vDis')
  # Get the video time in the data time base
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime=tc)[1]
  # Get acceleration
  accel = Source.getSignalFromECU('evi.General_TC.axvRef')[1]
  
  # object list 
  time, objects = fillObjects(Source)
  
  # Indicate intro
  time, o = indicateIntro(Source)
  
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
  o = {}
  time, o["dx"] = calcByHandle(Source, 'dxv')
  o["dx"] = np.where(
    Source.getSignalFromECU("acoacoi.__b_AcoNoFb.__b_Aco.request_B")[1] > 0, 
    o["dx"],
    0)
  time, o["dy"] = calcByHandle(Source, 'dyv')
  o["dy"] = np.where(
    Source.getSignalFromECU("acoacoi.__b_AcoNoFb.__b_Aco.request_B")[1] > 0, 
    o["dy"],
    0)
  o["type"] = 4
  o["color"] = [255, 255, 0]
  objects.append(o)
  
  # Indicate brake intervention
  o = {}
  time, o["dx"] = calcByHandle(Source, 'dxv')
  o["dx"] = np.where(
    Source.getSignalFromECU("acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B")[1] > 0, 
    o["dx"],
    0)
  time, o["dy"] = calcByHandle(Source, 'dyv')
  o["dy"] = np.where(
    Source.getSignalFromECU("acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B")[1] > 0, 
    o["dy"],
    0)
  o["type"] = 3
  w = Source.getSignalFromECU("acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.requestCharacteristic")[1]
  o["color"] = np.transpose([np.ones(np.shape(w), dtype=int)*255, np.maximum(0.01 * w + 255,0).astype(int), np.zeros(np.shape(w), dtype=int)])
  objects.append(o)

  # Video overlay player
  Client = datavis.cVideoNavigator(VideoFile, {})
  Clients.append(Client)
  # Set the overlay objects of the player, for simplicity acceleration compensation is 1/50 of the acceleration value
  Client.setobjects(objects, vidtime, accel / 50.)

  # Get the video time in the data time base
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1', ScaleTime=tc)[1]
  # Add the video overlay player to the synchronizer
  Sync.addClient(Client, (tc, vidtime))
  return Clients

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
    
