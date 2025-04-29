# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

LOC_OBJ_NUM = 48
ANGLE_INDECES_NUM = 7

DeviceNames = "MRR1plus", "RadarFC"
SignalPattern = 'dsp.LocationData_TC.Location.i%d.%s'
AngleSignalPattern = 'dsp.LocationData_TC.Location.i%d.Angle.i%d.alpAng'

SuperSignalGroups = []
""":type: list
[[{Alias<str>: (ShortDeviceName<str>, SignalName<str>)}]]"""
AngleSignalGroupsDict = {}
for dn in DeviceNames:
  for Name in 'StatusFlags.Status.Valid_b', 'Measured':
    SignalGroups = []
    for i in xrange(LOC_OBJ_NUM):
      SignalGroup = {'Valid': (dn, SignalPattern %(i, Name))}
      for Name in 'dMeas', 'wProbDH1':
        SignalGroup[Name] = dn, SignalPattern %(i, Name)
      SignalGroups.append(SignalGroup)
    SuperSignalGroups.append(SignalGroups)

  for i in xrange(LOC_OBJ_NUM):
    Groups = [{'alpAng': (dn, AngleSignalPattern %(i, j))} 
              for j in xrange(ANGLE_INDECES_NUM)]
    AngleKey = dn, i
    AngleSignalGroupsDict[AngleKey] = Groups
  


class cFill(interface.iObjectFill):
  def check(self):
    filtsglist = []
    for SignalGroups in SuperSignalGroups:
      filtsglist.append(interface.Source._filterSignalGroups(SignalGroups))
    Len = len(SuperSignalGroups[0][0])
    Groups = measparser.signalgroup.select_sgl_first_allvalid(filtsglist, Len)
    AngleGroups = []
    for i in xrange(LOC_OBJ_NUM):
      filtangsglist = []
      for dn in DeviceNames:
        filtangsglist.append(interface.Source._filterSignalGroups(AngleSignalGroupsDict[(dn,i)]))
      AngleGroups.append(measparser.signalgroup.select_sgl_first_allvalid(filtangsglist, 1))
    return Groups, AngleGroups

  def fill(self, Groups, AngleGroups):
    Signals = measparser.signalgroup.extract_signals(Groups, AngleGroups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Objects=[]
    for i in xrange(LOC_OBJ_NUM):
      Group = Groups[i]
      dr          = interface.Source.getSignalFromSignalGroup(Group, 'dMeas',    ScaleTime=scaletime)[1]
      valid       = interface.Source.getSignalFromSignalGroup(Group, 'Valid',    ScaleTime=scaletime)[1]
      probability = interface.Source.getSignalFromSignalGroup(Group, 'wProbDH1', ScaleTime=scaletime)[1]
      for idx in xrange(ANGLE_INDECES_NUM):
        Group = AngleGroups[i][idx]
        angle = interface.Source.getSignalFromSignalGroup(Group, 'alpAng', ScaleTime=scaletime)[1]

        o = {}
        o["dx"] = dr * np.cos(angle)
        o["dy"] = dr * np.sin(angle)
        mask = valid==1
        o["type"] = np.where( mask, 
                              self.get_grouptype('CVR3_LOC_VALID'), 
                              self.get_grouptype('CVR3_LOC_INVALID'))
                              
        o["label"] = "CVR3_LOC_%d_%d"%(i,idx) # location and angle indeces as simple label
        
        w = np.reshape(np.repeat(mask, 3), (-1,3))
        o["color"] = np.where(
                            w,
                            [255, 0, 0],
                            [255, 200, 200])
        
        Objects.append(o)
    return scaletime, Objects
