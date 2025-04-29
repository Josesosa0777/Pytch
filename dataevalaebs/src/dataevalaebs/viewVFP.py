import numpy as np

import datavis
import aebs.proc
import measparser
import viewFUSoverlayLRR3_AC100_ESR

def viewVFP(Source,AviFile):
  '''
  view different obect data with PN
  '''
  #----plot
  data=getdata(Source)
  PN = datavis.cPlotNavigator('VFP')
  signal_dx=[]
  signal_dy=[]
  for o in data:
    signal_dx.append(o["label"]+"_dx")
    signal_dx.append((o["time"],o["dx"]))
    signal_dy.append(o["label"]+"_dy")
    signal_dy.append((o["time"],o["dy"]))
  PN.addsignal(ylabel="dx [m]",xlabel="time [s]",*signal_dx)
  PN.addsignal(ylabel="dy [m]",xlabel="time [s]",*signal_dy)
  Sync.addClient(PN)
  scaletime=data[0]["time"]
  viewoverlayVFP(Source,scaletime)


  
  
def viewoverlayVFP(Source,scaletime):
  '''
  view videooverlay of VFP camera objects
  '''
  objects=[]
  #------------------------------------------------------------------------------
  if 1:#-------------------------Add delphi radar objects?
    time_ESR, objects_ESR=viewFUSoverlayLRR3_AC100_ESR.fillObjects(Source,0,0,1,0,0)
    scaletime=time_ESR
  for o in objects_ESR:
    objects.append(o)
  #------------------------------------------------------------------------------
  data=getdata(Source)
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1',ScaleTime=scaletime)[1]
  for o in data:
    scaletime, o["dx"] = measparser.cSignalSource.rescale(o["time"],o["dx"],scaletime)
    scaletime, o["dy"] = measparser.cSignalSource.rescale(o["time"],o["dy"],scaletime)
    scaletime, o["motion"] = measparser.cSignalSource.rescale(o["time"],o["motion"],scaletime)
    scaletime, o["class"] = measparser.cSignalSource.rescale(o["time"],o["class"],scaletime)
    scaletime, o["rangerate"] = measparser.cSignalSource.rescale(o["time"],o["rangerate"],scaletime)
    o["type"]=np.zeros(len(o["motion"]))
    for i in xrange(len(o["motion"])):
      if o["motion"][i]==1:
        o["type"][i]=12
      else:
        o["type"][i]=11
      if o["class"][i]==4:
        o["type"][i]=13
    w = np.reshape(np.repeat(o["rangerate"] < 0, 3), (-1,3))
    o["color"] = np.where(w,[255, 0, 0],[0, 255, 0])
    w = np.reshape(np.repeat(o["motion"]>3, 3), (-1, 3))
    o["color"] = np.where(w,[0, 0, 255],o["color"])
    objects.append(o)
  
  
  
  VN = datavis.cVideoNavigator(AviFile, {})
  accel = Source.getSignalFromECU('evi.General_TC.axvRef', ScaleTime=scaletime)[1]
  VN.setobjects(objects, vidtime, accel / 50.)
  Sync.addClient(VN,(scaletime,vidtime))
  
  
  
  
def getdata(Source):
  '''
  MAIN METHOD returns VFP object data
  '''
  #multiplexed data with always 10 objects sended (value=0 for non objects)
  Source.loadParser()
  Device_VFP_Track, = Source.Parser.getDeviceNames("CAN_VIS_OBS_RANGE")
  time_VFP, range = Source.getSignal(Device_VFP_Track,'CAN_VIS_OBS_RANGE')
  angle = Source.getSignal(Device_VFP_Track,'CAN_VIS_OBS_ANGLE_CENTROID')[1]
  rangerate = Source.getSignal(Device_VFP_Track,'CAN_VIS_OBS_RANGE_RATE')[1]
  Device_VFP_Track, = Source.Parser.getDeviceNames("CAN_VIS_OBS_COUNT_MSG1")
  count1 = Source.getSignal(Device_VFP_Track,'CAN_VIS_OBS_COUNT_MSG1')[1]
  Device_VFP_Track, = Source.Parser.getDeviceNames("CAN_VIS_OBS_MOTION_TYPE")
  motion = Source.getSignal(Device_VFP_Track,'CAN_VIS_OBS_MOTION_TYPE')[1]
  Device_VFP_Track, = Source.Parser.getDeviceNames("CAN_VIS_OBS_CLASSIFICATION")
  classification = Source.getSignal(Device_VFP_Track,'CAN_VIS_OBS_CLASSIFICATION')[1]
  data=[]
  for i in xrange(10):
    o={}
    len_o=len(range)/10
    o["dx"]=np.zeros(len_o)
    o["dy"]=np.zeros(len_o)
    o["time"]=np.zeros(len_o)
    o["motion"]=np.zeros(len_o)
    o["class"]=np.zeros(len_o)
    o["rangerate"]=np.zeros(len_o)
    o["class"]=np.zeros(len_o)
    for j in xrange(len_o):
      idx=10*j+i
      o["dx"][j]=range[idx]*np.cos(angle[idx]*(np.pi/180.0))
      o["dy"][j]=-range[idx]*np.sin(angle[idx]*(np.pi/180.0))
      o["time"][j]=time_VFP[idx]
      o["motion"][j]=motion[idx]
      o["rangerate"][j]=rangerate[idx]
      o["class"][j]=classification[idx]
    o["label"]="VFP_%d"%i
    data.append(o)
  return data
  
  
  
if __name__ == '__main__':
  import sys
  import aebs.proc
  import datavis
  
  if len(sys.argv) > 1:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source('ECU_0_0', sys.argv[1])
    Sync    = datavis.cSynchronizer()
    
    
    #viewVFP(Source,AviFile)
    viewoverlayVFP(Source,[])
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
