# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

OHL_OBJ_NUM = 40

Aliases = 'dx', 'dy', 'vx', 'vy', 'internal.Index', 'c.c.Stand_b', 'c.c.DriveInvDir_b'

SignalGroups = []
for i in xrange(OHL_OBJ_NUM):
  SignalGroup = {}
  for Alias in Aliases:
    SignalGroup[Alias] = 'ECU', 'ohl.ObjData_TC.OhlObj.i%d.%s' %(i, Alias)
  SignalGroups.append(SignalGroup)

class cFill(interface.iObjectFill):
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases))
    return Groups

  def fill(self, Groups):
    Signals = measparser.signalgroup.extract_signals(Groups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Objects=[]
    for i in xrange(OHL_OBJ_NUM):
      Group = Groups[i]
      o = {}
      o["dx"]       = interface.Source.getSignalFromSignalGroup(Group, 'dx',                ScaleTime=scaletime)[1]
      o["dy"]       = interface.Source.getSignalFromSignalGroup(Group, 'dy',                ScaleTime=scaletime)[1]
      o["dvx"]      = interface.Source.getSignalFromSignalGroup(Group, 'vx',                ScaleTime=scaletime)[1]
      o["dvy"]      = interface.Source.getSignalFromSignalGroup(Group, 'vy',                ScaleTime=scaletime)[1]
      o["id"]       = interface.Source.getSignalFromSignalGroup(Group, 'internal.Index',    ScaleTime=scaletime)[1]
      Stand_b       = interface.Source.getSignalFromSignalGroup(Group, 'c.c.Stand_b',       ScaleTime=scaletime)[1]
      DriveInvDir_b = interface.Source.getSignalFromSignalGroup(Group, 'c.c.DriveInvDir_b', ScaleTime=scaletime)[1]
      o["dv"]       = o["dvx"]
      
      o["type"] = np.where( Stand_b==1,
                            self.get_grouptype('LRR3_OHL_STAT'),
                            self.get_grouptype('LRR3_OHL_MOV'))
      
      o["label"] = "LRR3_OHL_%d"%i # OHL index as simple label 
      # Set color to red or green according to relative speed
      w = np.reshape(np.repeat(o["dv"] < 0, 3), (-1,3))
      o["color"] = np.where(
        w,
        [255, 255, 100],
        [0, 255, 255])
      # Set color of inverse dir objects to blue
      w = np.reshape(np.repeat(DriveInvDir_b == 1, 3), (-1, 3))
      o["color"] = np.where(
        w,
        [255, 0, 255],
        o["color"])
      Objects.append(o)
    return scaletime, Objects
