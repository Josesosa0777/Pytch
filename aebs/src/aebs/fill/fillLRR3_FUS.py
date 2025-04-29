# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

FUS_OBJ_NUM = 32

Aliases = 'dxv', 'dyv', 'vxv', 'vyv', 'Handle', 'b.b.Stand_b', 'b.b.DriveInvDir_b', 'wExistProbBase'

SignalGroups = []
for i in xrange(FUS_OBJ_NUM):
  SignalGroup = {}
  for Alias in Aliases:
    SignalGroup[Alias] = 'ECU', 'fus.ObjData_TC.FusObj.i%d.%s' %(i, Alias)
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
    for i in xrange(FUS_OBJ_NUM):
      Group = Groups[i]
      o = {}
      o["dx"]        = interface.Source.getSignalFromSignalGroup(Group, 'dxv',               ScaleTime=scaletime)[1]
      o["dy"]        = interface.Source.getSignalFromSignalGroup(Group, 'dyv',               ScaleTime=scaletime)[1]
      o["dvx"]       = interface.Source.getSignalFromSignalGroup(Group, 'vxv',               ScaleTime=scaletime)[1]
      o["dvy"]       = interface.Source.getSignalFromSignalGroup(Group, 'vyv',               ScaleTime=scaletime)[1]
      o["id"]        = interface.Source.getSignalFromSignalGroup(Group, 'Handle',            ScaleTime=scaletime)[1]
      Stand_b        = interface.Source.getSignalFromSignalGroup(Group, 'b.b.Stand_b',       ScaleTime=scaletime)[1]
      DriveInvDir_b  = interface.Source.getSignalFromSignalGroup(Group, 'b.b.DriveInvDir_b', ScaleTime=scaletime)[1]
      wExistProbBase = interface.Source.getSignalFromSignalGroup(Group, 'wExistProbBase',    ScaleTime=scaletime)[1]
      
      o["dv"] = o["dvx"]
      
      o["type"] = np.where( Stand_b==1, 
                            self.get_grouptype('LRR3_FUS_STAT'), 
                            self.get_grouptype('LRR3_FUS_MOV'))
      #########
      o["type"][wExistProbBase<0.4] = self.get_grouptype('NONE_TYPE')
      #########
      
      o["label"] = "LRR3_FUS_%d"%i # FUS index as simple label 
      
      # Set color to red or green according to relative speed
      w = np.reshape(np.repeat(o["dvx"] < 0, 3), (-1,3))
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
