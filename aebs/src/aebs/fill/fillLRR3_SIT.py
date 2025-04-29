# -*- dataeval: init -*-

import numpy as np

import interface
import measparser

NoObjects = 33
LRR3_DEV_NAME = 'ECU'
CVR3_DEV_NAME = 'MRR1plus'

# obsolated #
AliasPattern = 'sit.RelationGraph_TC.ObjectList.i%d'
SignalGroupDict = {}
for DeviceName in LRR3_DEV_NAME, CVR3_DEV_NAME:
  SignalGroup = {}
  for i in xrange(NoObjects):
    Alias = AliasPattern %i
    SignalGroup[Alias] = DeviceName, Alias
  SignalGroupDict[DeviceName] = [SignalGroup, ]

  
LRR3_SignalGroups = SignalGroupDict[LRR3_DEV_NAME]
CVR3_SignalGroups = SignalGroupDict[CVR3_DEV_NAME]
# obsolated #

init_params = {'LRR3': dict(DeviceName='ECU'),
               'CVR3': dict(DeviceName='MRR1plus')}

class cFill(interface.iObjectFill):
  def init(self, DeviceName):
    self.DeviceName = DeviceName
    pass

  def check(self):
    Aliases = 'dxv', 'dyv', 'vxv', 'Handle', 'b.b.Stand_b'
    SignalGroups = []
    for i in xrange(NoObjects):
      SignalGroup = {}
      for Alias in Aliases:
        SignalGroup[Alias] = self.DeviceName, 'fus.ObjData_TC.FusObj.i%d.%s' %(i, Alias)
      SignalGroups.append(SignalGroup)
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, len(Aliases))

    SignalGroups = []
    for i in xrange(NoObjects):
      SignalGroup = {'ObjectList': (self.DeviceName, 'sit.RelationGraph_TC.ObjectList.i%d' %i)}
      SignalGroups.append(SignalGroup)
    Groups, Errors = interface.Source._filterSignalGroups(SignalGroups)
    measparser.signalgroup.check_allvalid(Groups, Errors, 1)
    return Groups

  def fill(self, Groups):
    Signals = measparser.signalgroup.extract_signals(Groups)
    ScaleTime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    Handles = {}
    for i in xrange(NoObjects):
      Group = Groups[i]
      DeviceName, SignalName = Group['ObjectList']
      Time, Value = interface.Source.getSignal(DeviceName, SignalName, ScaleTime=ScaleTime)
      Uniques = Handles.setdefault(DeviceName, set())
      Handles[DeviceName] = Uniques.union(Value)
    Objects=[]
    for DeviceName, Uniques in Handles.iteritems():
      for Handle in Uniques:
        o = {}
        o["dx"] = interface.Source.getSignalByHandle(DeviceName, Handle, "dxv", ScaleTime=ScaleTime)[1]
        o["dx"][np.isnan(o["dx"])] = 0
        o["dy"] = interface.Source.getSignalByHandle(DeviceName, Handle, "dyv", ScaleTime=ScaleTime)[1]
        o["dy"][np.isnan(o["dy"])] = 0
        o["dv"] = interface.Source.getSignalByHandle(DeviceName, Handle, "vxv",         ScaleTime=ScaleTime)[1]
        o["id"] = interface.Source.getSignalByHandle(DeviceName, Handle, "Handle",      ScaleTime=ScaleTime)[1]
        Stand_b = interface.Source.getSignalByHandle(DeviceName, Handle, "b.b.Stand_b", ScaleTime=ScaleTime)[1]
        #wExistProbBase = interface.Source.getSignalByHandle(DeviceName, Handle, "wExistProbBase", ScaleTime=ScaleTime)[1]
        if self.DeviceName == LRR3_DEV_NAME:
          stat_type = self.get_grouptype('LRR3_SIT_STAT')
          mov_type  = self.get_grouptype('LRR3_SIT_MOV')
          o["label"] = 'LRR3_SIT_%d'%Handle
        elif self.DeviceName == CVR3_DEV_NAME:
          stat_type = self.get_grouptype('CVR3_SIT_STAT')
          mov_type  = self.get_grouptype('CVR3_SIT_MOV')
          o["label"] = 'CVR3_SIT_%d'%Handle
        else:
          raise ValueError('Invalid parameter device name!')
          
        o["type"] = np.where( Stand_b == 1, 
                              stat_type, 
                              mov_type)
                              
        w = np.reshape(np.repeat(o["dv"] < 0, 3), (-1,3))
        o["color"] = np.where(
              w,
              [255, 255, 100],
              [0, 255, 255])
        Objects.append(o)
    return ScaleTime, Objects
