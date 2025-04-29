# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

SignalGroups = [{'range':          ('VISION_OBSTACLE_MSG1', 'CAN_VIS_OBS_RANGE'),
                 'angle':          ('VISION_OBSTACLE_MSG1', 'CAN_VIS_OBS_ANGLE_CENTROID'),
                 'rangerate':      ('VISION_OBSTACLE_MSG1', 'CAN_VIS_OBS_RANGE_RATE'),
                 'count1':         ('VISION_OBSTACLE_MSG1', 'CAN_VIS_OBS_COUNT_MSG1'),
                 'motion':         ('VISION_OBSTACLE_MSG2', 'CAN_VIS_OBS_MOTION_TYPE'),
                 'classification': ('VISION_OBSTACLE_MSG2', 'CAN_VIS_OBS_CLASSIFICATION')}]

class cFill(interface.iObjectFill):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self, Group):
    Signals = measparser.signalgroup.extract_signals(Group)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    len_scaletime = len(scaletime)
    Objects=[]
    #multiplexed data with always 10 objects sended (value=0 for non objects)
    time_VFP , range = interface.Source.getSignalFromSignalGroup(Group, 'range')
    angle =            interface.Source.getSignalFromSignalGroup(Group, 'angle')[1]
    rangerate =        interface.Source.getSignalFromSignalGroup(Group, 'rangerate')[1]
    count1 =           interface.Source.getSignalFromSignalGroup(Group, 'count1')[1]
    motion =           interface.Source.getSignalFromSignalGroup(Group, 'motion')[1]
    classification =   interface.Source.getSignalFromSignalGroup(Group, 'classification')[1]
    for i in xrange(10):
      o={}
      len_o=len(range)/10
      o["time"]=np.zeros(len_o)
      o["dx"]=np.zeros(len_o)
      o["dy"]=np.zeros(len_o)
      o["motion"]=np.zeros(len_o)
      o["class"]=np.zeros(len_o)
      o["rangerate"]=np.zeros(len_o)
      for j in xrange(len_o):
        idx=10*j+i
        o["time"][j]=time_VFP[idx]
        o["dx"][j]=range[idx]*np.cos(angle[idx]*(np.pi/180.0))
        o["dy"][j]=-range[idx]*np.sin(angle[idx]*(np.pi/180.0))
        o["motion"][j]=motion[idx]
        o["rangerate"][j]=rangerate[idx]
        o["class"][j]=classification[idx]
      
      #rescale:
      o["dx"] = measparser.cSignalSource.rescale(o["time"], o["dx"], scaletime)[1]
      o["dy"] = measparser.cSignalSource.rescale(o["time"], o["dy"], scaletime)[1]
      o["motion"] = measparser.cSignalSource.rescale(o["time"], o["motion"], scaletime)[1]
      o["rangerate"] = measparser.cSignalSource.rescale(o["time"], o["rangerate"], scaletime)[1]
      o["class"] = measparser.cSignalSource.rescale(o["time"], o["class"], scaletime)[1]
        
      
      o["label"]="VFP_%d"%i
      
      o["type"]=np.zeros(len_scaletime)
      o["type"].fill(self.get_grouptype('VFP_STAT')) #standing
      o["type"][o["motion"]==1] = self.get_grouptype('VFP_MOV')  #moving
      o["type"][o["class"]==4] = self.get_grouptype('VFP_PEDESTRIAN')  #pedestrian
      
      w = np.reshape(np.repeat(o["rangerate"] < 0, 3), (-1,3))
      o["color"] = np.where(w,[255, 0, 0],[0, 255, 0])
      w = np.reshape(np.repeat(o["motion"]>3, 3), (-1, 3))
      o["color"] = np.where(w,[0, 0, 255],o["color"])
      o["label"] = "VFP_%d"%i
      Objects.append(o)
    return scaletime, Objects
