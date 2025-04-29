"""
This module shows the 5 different obstacle classification probability signals of the relevant intro. 
Since all the 5 signals are only present on ohl level, the fus handles of the relevant 
intro (one handle at a specific time) are transformed into ohl object indices as follows:
fus handle -> fus index -> ohl index
The transformation may be unique (1-by-1) for the same fus handles at different time.
However, since the intro is strongly filtered (by certain obstacle probability), this approach 
result in the 'obstacle' class dominating the probability value.
"""
import numpy as np

import datavis
import measparser
import interface

DefParam = interface.NullParam

OBS_CLASSIF_TYPES = ('OBSTACLE', 
                     'UNDERPASSABLE', 
                     'OVERRUNABLE', 
                     'INTERFERENCE', 
                     'UNKNOWN')
INVALID_FUS_HANDLE = 0
INVALID_FUS_INDEX  = 255
INVALID_OHL_INDEX  = 255
INVALID_FUS_2_OHL_ASSOC = 255
FUS_ASSOC_NUM = 32
OHL_OBJ_NUM = 40

ShortDeviceName = 'MRR1plus'
# ShortDeviceName = 'ECU'

SignalGroup = {'introFUShandle':   (ShortDeviceName, 'sit.IntroFinder_TC.Intro.i0.ObjectList.i0'),}
for k in xrange(FUS_ASSOC_NUM):
  SignalGroup['fus.i%d_to_ohl_assoc'%k] = (ShortDeviceName, 'fus_asso_mat.LrrObjIdx.i%d'%k)
for m in xrange(OHL_OBJ_NUM):
  SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[0])] = (ShortDeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i0' %m)
  SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[1])] = (ShortDeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i1' %m)
  SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[2])] = (ShortDeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i2' %m)
  SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[3])] = (ShortDeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i3' %m)
  SignalGroup['OhlObj.i%d.probClass.%s' %(m, OBS_CLASSIF_TYPES[4])] = (ShortDeviceName, 'ohl.ObjData_TC.OhlObj.i%d.probClass.i4' %m)

SignalGroups = [SignalGroup, ]

def findUniqueValues(array, exceptValue=None):
  uniqueValues = list(np.unique(array))
  if exceptValue is not None and exceptValue in uniqueValues:
    uniqueValues.remove(exceptValue)
  return uniqueValues

class cIntroObstacleClassif1by1(interface.iView):
  def check(self):
    Group = interface.Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self,Group):
    return Group

  def view(cls, Param, Group):
    try:
      scaletime=  interace.Objects.ScaleTime
    except AttributeError:
      Time, handles = interface.Source.getSignalFromSignalGroup(Group, 'introFUShandle')
      scaleTime = Time
    else:
      Time, handles = interface.Source.getSignalFromSignalGroup(Group, 'introFUShandle', ScaleTime=scaletime)
    kwargs = dict(ScaleTime=scaletime)
    
    # fus handle to fus index
    ExtendedDeviceName, = interface.Source.getExtendedDeviceNames(ShortDeviceName)
    uniqueHandles = findUniqueValues(handles, exceptValue=INVALID_FUS_HANDLE)
    Time, DummyIndex = interface.Source.getFUSindicesFromHandle(ExtendedDeviceName, INVALID_FUS_HANDLE, 
                                                                InvalidValue=INVALID_FUS_INDEX, **kwargs)
    fusIndex = np.ones_like(DummyIndex) * INVALID_FUS_INDEX
    for handle in uniqueHandles:
      Time, indexValue = interface.Source.getFUSindicesFromHandle(ExtendedDeviceName, handle,
                                                                  InvalidValue=INVALID_FUS_INDEX, **kwargs)
      mask             = handles==handle
      fusIndex[mask]   = indexValue[mask]
    # fus index to ohl index
    uniqueFusIndices = findUniqueValues(fusIndex, exceptValue=INVALID_FUS_INDEX)
    ohlIndex = np.ones_like(fusIndex) * INVALID_OHL_INDEX
    for fus_index in uniqueFusIndices:
      Time, fus2ohlAssoc = interface.Source.getSignalFromSignalGroup(Group, 'fus.i%d_to_ohl_assoc'%fus_index, **kwargs)
      mask               = fusIndex==fus_index
      ohlIndex[mask]     = fus2ohlAssoc[mask]
    uniqueOhlIndices = findUniqueValues(ohlIndex, exceptValue=INVALID_OHL_INDEX)
    # ohl obstacle classification signals
    ohlObjects = {}
    for i in uniqueOhlIndices:
      ohlObjects[i] = {}
      for classifType in OBS_CLASSIF_TYPES:
        ohlObjects[i][classifType] = interface.Source.getSignalFromSignalGroup(Group, 'OhlObj.i%d.probClass.%s' %(i,classifType), **kwargs)[1]
    outSignals = {}
    for index in uniqueOhlIndices:
      mask = index==ohlIndex
      for classifType in OBS_CLASSIF_TYPES:
        signal    = ohlObjects[index][classifType]
        out       = outSignals.setdefault( classifType, np.zeros_like(signal) )
        out[mask] = signal[mask]
        
    # display result
    PN = datavis.cPlotNavigator(title='Obstacle classification signals of relevant SIT intro')
    interface.Sync.addClient(PN)
    Axis1 = PN.addAxis()
    PN.addSignal2Axis(Axis1, 'Relevant intro FUS handles', scaletime, handles, unit="")
    Axis2 = PN.addAxis()
    for classifType, signal in outSignals.iteritems():
      PN.addSignal2Axis(Axis2, classifType, scaletime, signal, unit="")
    
    # # DEBUG
    # print 'unique handles', uniqueHandles
    # print 'unique fus indices', uniqueFusIndices
    # print 'unique ohl indices', uniqueOhlIndices
    return 
