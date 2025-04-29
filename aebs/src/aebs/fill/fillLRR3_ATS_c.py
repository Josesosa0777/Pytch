# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

ATS_INTERNAL_TC_ATSOBJATR_NUM = 33

Aliases = 'dxvFilt', 'dycActObjAtr', 'Handle'

SignalGroups = []
for i in xrange(ATS_INTERNAL_TC_ATSOBJATR_NUM):
  SignalGroup = {'Stand_b': ('ECU', 'fus.ObjData_TC.FusObj.i%d.b.b.Stand_b' %i)}
  for Alias in Aliases:
    SignalGroup[Alias] = 'ECU', 'ats_InternalTC.AtsObjAtr.i%d.%s' %(i, Alias)
  SignalGroups.append(SignalGroup)

class cFill(interface.iObjectFill):
  def check(self):
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases)+1)  
    return Groups
  
  def fill(self, Groups):
    Signals = measparser.signalgroup.extract_signals(Groups)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Objects=[]
    for i in xrange(ATS_INTERNAL_TC_ATSOBJATR_NUM):
      Group = Groups[i]
      o = {}
      o["dx"] = interface.Source.getSignalFromSignalGroup(Group, 'dxvFilt',      ScaleTime=scaletime)[1]
      o["dy"] = interface.Source.getSignalFromSignalGroup(Group, 'dycActObjAtr', ScaleTime=scaletime)[1]
      o["id"] = interface.Source.getSignalFromSignalGroup(Group, 'Handle',       ScaleTime=scaletime)[1]
      Stand_b = interface.Source.getSignalFromSignalGroup(Group, 'Stand_b',      ScaleTime=scaletime)[1]

      o["type"] = np.where( Stand_b == 1,
                            self.get_grouptype('LRR3_ATS_STAT'),
                            self.get_grouptype('LRR3_ATS_MOV') )
      o["label"] = "LRR3_ATS_c_%d"%i
      o["color"] = [255, 0, 0]
      Objects.append(o)
    return scaletime, Objects
