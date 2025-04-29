import numpy as np

import datavis
import datavis
import measparser

def viewIteris(Source,AviFile):
  '''
  view specific Iteris camera objects
  '''
  data=getdata(Source)
  PN = datavis.cPlotNavigator('Iteris')
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
  
  viewoverlayIteris(Source,AviFile)
  
  pass
  
  
  
def viewoverlayIteris(Source,AviFile):
  '''
  view Videooverlay of different Iteris Camera Objects
  '''
  objects=[]
  data=getdata(Source)
  scaletime=data[0]["time"]
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1',ScaleTime=scaletime)[1]
  for o in data:
    scaletime, o["dx"] = measparser.cSignalSource.rescale(o["time"],o["dx"],scaletime)
    scaletime, o["dy"] = measparser.cSignalSource.rescale(o["time"],o["dy"],scaletime)
    scaletime, o["rangerate"] = measparser.cSignalSource.rescale(o["time"],o["rangerate"],scaletime)
    o["type"]=14
    w = np.reshape(np.repeat(o["rangerate"] < 0, 3), (-1,3))
    o["color"] = np.where(w,[255, 0, 0],[0, 255, 0])
    objects.append(o)
  
  VN = datavis.cVideoNavigator(AviFile, {})
  accel = Source.getSignalFromECU('evi.General_TC.axvRef', ScaleTime=scaletime)[1]
  VN.setobjects(objects, vidtime, accel / 50.)
  Sync.addClient(VN,(scaletime,vidtime))
  
def getdata(Source):
  '''
  MAIN METHOD return Iteris object data
  '''
  data=[]
  Source.loadParser()
  #---data from Iteris
  Device_Iteris_Track, = Source.Parser.getDeviceNames("PO_target_range_OFC")
  time_Iteris, range = Source.getSignal(Device_Iteris_Track,'PO_target_range_OFC')
  angle = Source.getSignal(Device_Iteris_Track,'PO_right_azimuth_angle_OFC')[1]
  #----data from LRR3
  Device_Iteris_Track, = Source.Parser.getDeviceNames("target_speed")
  time_rangerate, rangerate = Source.getSignal(Device_Iteris_Track,'target_speed')
  o={}
  o["time"]=time_Iteris
  o["dx"]=range*np.cos(angle*(np.pi/180.0))
  o["dy"]=range*np.sin(angle*(np.pi/180.0))
  o["rangerate"]=rangerate
  o["time_rangerate"]=time_rangerate
  o["label"]="Iteris_PO"
  data.append(o)
  return data
  
  
if __name__ == '__main__':
  import aebs.proc
  import datavis
  import sys
  
  if len(sys.argv) > 1:
    AviFile = sys.argv[1].lower().replace('.mdf', '.avi')
    Source  = aebs.proc.cLrr3Source(sys.argv[1], ECU='ECU_0_0')
    Sync    = datavis.cSynchronizer()
    
    
    viewIteris(Source,AviFile)
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
