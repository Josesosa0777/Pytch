import numpy as np

import datavis
import measparser

def viewMobilEye(Source,AviFile):
  '''
  view MobilEye camera objects with PN
  '''
  data=getdata(Source)
  PN = datavis.cPlotNavigator('MobilEye')
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
  
  viewoverlayMobilEye(Source,AviFile)
  
  pass
  
  
  
def viewoverlayMobilEye(Source,AviFile):
  '''
  views videooverlay of MobilEye objects
  '''
  objects=[]
  data=getdata(Source)
  scaletime=data[0]["time"]
  vidtime = Source.getSignal('Multimedia_0_0', 'Multimedia_1',ScaleTime=scaletime)[1]
  for o in data:
    scaletime, o["dx"] = measparser.cSignalSource.rescale(o["time"],o["dx"],scaletime)
    scaletime, o["dy"] = measparser.cSignalSource.rescale(o["time"],o["dy"],scaletime)
    scaletime, o["rangerate"] = measparser.cSignalSource.rescale(o["time"],o["rangerate"],scaletime)
    o["type"]=15
    w = np.reshape(np.repeat(o["rangerate"] < 0, 3), (-1,3))
    o["color"] = np.where(w,[255, 0, 0],[0, 255, 0])
    objects.append(o)
  
  VN = datavis.cVideoNavigator(AviFile, {})
  accel = Source.getSignalFromECU('evi.General_TC.axvRef', ScaleTime=scaletime)[1]
  VN.setobjects(objects, vidtime, accel / 50.)
  Sync.addClient(VN,(scaletime,vidtime))
  
def getdata(Source):
  '''
  MAIN METHOD returns MobilEye object data
  '''
  data=[]
  Source.loadParser()
  for i in xrange(10):
    Device_MobilEye_Track, = Source.Parser.getDeviceNames("Distance_to_Obstacle_%d"%i)
    time_MobilEye, range = Source.getSignal(Device_MobilEye_Track,'Distance_to_Obstacle_%d'%i)
    angle = Source.getSignal(Device_MobilEye_Track,'Angle_to_obstacle_%d'%i)[1]
    rangerate = Source.getSignal(Device_MobilEye_Track,'Relative_velocity_to_obstacle_%d'%i)[1]
    o={}
    o["time"]=time_MobilEye
    o["dx"]=range*np.cos(angle*(np.pi/180.0))
    o["dy"]=-range*np.sin(angle*(np.pi/180.0))
    o["rangerate"]=rangerate
    o["label"]="MobilEye_%d"%i
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
    
    
    viewMobilEye(Source,AviFile)
    
    Sync.run()    
    raw_input("Press Enter to Exit")
    Sync.close()
      
  else:
    sys.stderr.write('The %s needs one input argument for mdf file path!\n' %__file__)
