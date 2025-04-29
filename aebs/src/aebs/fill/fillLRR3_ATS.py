# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

ATS_PO_T20_PO_LEN = 5

Aliases = 'dxvFilt', 'dyv', 'vxvFilt', 'Handle', 'flags.flags.Standing_b'

SignalGroups = []
for i in xrange(ATS_PO_T20_PO_LEN):
  SignalGroup = {}
  for Alias in Aliases:
    SignalGroup[Alias] = 'ECU', 'ats.Po_T20.PO.i%d.%s' %(i, Alias)
  SignalGroups.append(SignalGroup)

class cFill(interface.iObjectFill):
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases))
    return Groups

  def fill(self, Groups):
    Objects=[]
    Signals = measparser.signalgroup.extract_signals(Groups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    for i in xrange(ATS_PO_T20_PO_LEN):
      Group = Groups[i]
      o = {}
      o["dx"] = interface.Source.getSignalFromSignalGroup(Group, 'dxvFilt',                ScaleTime=scaletime)[1]
      o["dy"] = interface.Source.getSignalFromSignalGroup(Group, 'dyv',                    ScaleTime=scaletime)[1]
      o["dv"] = interface.Source.getSignalFromSignalGroup(Group, 'vxvFilt',                ScaleTime=scaletime)[1]
      o["id"] = interface.Source.getSignalFromSignalGroup(Group, 'Handle',                 ScaleTime=scaletime)[1]
      Stand_b = interface.Source.getSignalFromSignalGroup(Group, 'flags.flags.Standing_b', ScaleTime=scaletime)[1]
      
      o["type"] = np.where( Stand_b == 1,
                            self.get_grouptype('LRR3_ATS_STAT'),
                            self.get_grouptype('LRR3_ATS_MOV') )
      o["label"] = "LRR3_ATS_%d"%i
      # Set color to red or green according to relative speed
      if i!=4:
        w = np.reshape(np.repeat(o["dv"] < 0, 3), (-1,3))
        o["color"] = np.where(
          w,
          [255, 255, 100],
          [0, 255, 255])
      else:
        o["color"]=[0,0,0]
      Objects.append(o)
    return scaletime, Objects
