# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

LOC_OBJ_NUM = 48
ANGLE_INDECES_NUM = 6

Aliases = 'dMeas', 'StatusFlags.Status.Valid_b', 'wPorbDH1'

SignalGroups =  []
AngleSignalGroups = []
for i in xrange(LOC_OBJ_NUM):
  SignalGroup = {}
  for Alias in Aliases:
    SignalGroup[Alias] = 'ECU', 'rmp.D2lLocationData_TC.Location.i%d.%s' %(i, Alias)
  SignalGroups.append(SignalGroup)

  for idx in xrange(ANGLE_INDECES_NUM):
    Groups = [{'alpAng': ('ECU', 'rmp.D2lLocationData_TC.Location.i%d.Angle.i%d.alpAng' %(i,idx))}]
  AngleSignalGroups.append(Groups)

class cFill(interface.iObjectFill):
  def check(self):
    AngleGroups = [] 
    for Groups in AngleSignalGroups:
      Groups, Errors = interface.Source._filterSignalGroups(Groups)
      measparser.signalgroup.check_allvalid(Groups, Errors, 1)
      AngleGroups.append(Groups)
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases))
    return Groups, AngleGroups

  def fill(self, Groups, AngleGroups):
    Signals = measparser.signalgroup.extract_signals(AngleGroups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Objects=[]
    for i in xrange(LOC_OBJ_NUM):
      Group = Groups[i]
      dr          = interface.Source.getSignalFromSignalGroup(Group, 'dMeas',                     ScaleTime=scaletime)[1]
      valid       = interface.Source.getSignalFromSignalGroup(Group, 'StatusFlag.Status.Valid_b', ScaleTime=scaletime)[1]
      probability = interface.Source.getSignalFromSignalGroup(Group, 'wProbDH1',                  ScaleTime=scaletime)[1]
      for idx in xrange(ANGLE_INDECES_NUM):
        Group = AngleGroups[i][idx]
        o = {}
        angle = interface.Source.getSignalFromSignalGroup(Group, 'alpAng', ScaleTime=scaletime)[1]
        o["dx"] = dr * np.cos(angle)
        o["dy"] = dr * np.sin(angle) 
        o["type"] = np.where( valid == 1,
                              self.get_grouptype('LRR3_LOC_VALID'),
                              self.get_grouptype('LRR3_LOC_INVALID') )
        
        o["label"] = "LRR3_LOC_%d_%d"%(i,idx) # location and angle indeces as simple label 
        w = np.reshape(np.repeat(valid == 1, 3), (-1,3))
        o["color"] = np.where(
                            w,
                            [255, 255, 0],
                            [255, 255, 200])
        Objects.append(o)
    return scaletime, Objects
