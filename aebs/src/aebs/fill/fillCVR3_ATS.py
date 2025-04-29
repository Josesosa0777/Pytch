# -*- dataeval: init -*-

import interface
import measparser
from aebs.fill.fillCVR3_POS import DeviceNames
from aebs.fill.fillCVR3_POS import Aliases as FusAliases
from aebs.fill.fillCVR3_POS import SignalGroupsDict as FusSignalGroupsDict
from aebs.fill.fillCVR3_POS import cCreateFUSMatrix
 
ATS_OBJ_NUM = 5
labelCrossTable = (("CVR3_ATS_0", (255,   0, 255)),
                   ("CVR3_ATS_1", (  0,   0, 255)),
                   ("CVR3_ATS_2", (  0, 255,   0)),
                   ("CVR3_ATS_3", (  0, 255,   0)),
                   ("CVR3_ATS_4", (  0,   0,   0))) 

SignalGroupsDict = {}
for dn in DeviceNames:
  SignalGroupsDict[dn] = []
  for i in xrange(ATS_OBJ_NUM):
    signalGroup = {'Handle' : (dn, 'ats.Po_TC.PO.i%d.Handle' %(i))}
    SignalGroupsDict[dn].append(signalGroup)

                
class cFill(interface.iObjectFill):
  def check(self):
    filtsglist = []
    filtfussglist = []
    for dn in DeviceNames:
      filtsglist.append(interface.Source._filterSignalGroups(SignalGroupsDict[dn]))
      filtfussglist.append(interface.Source._filterSignalGroups(FusSignalGroupsDict[dn]))
    groups = measparser.signalgroup.select_sgl_first_allvalid(filtsglist, 1)
    fusgroups = measparser.signalgroup.select_sgl_first_allvalid(filtfussglist, len(FusAliases))
    return groups, fusgroups
    
  def fill(self, groups, fusgroups):
    signals = measparser.signalgroup.extract_signals(groups)
    scaletime = interface.Source.selectScaleTime(signals, interface.StrictlyGrowingTimeCheck)
      
    FusMatrix = cCreateFUSMatrix(fusgroups, scaletime)
    ObjectFiller = FusMatrix.createFiller()  
    
    objects=[]
    for i in xrange(ATS_OBJ_NUM):
      group = groups[i]
      handle = interface.Source.getSignalFromSignalGroup(group, 'Handle', ScaleTime=scaletime)[1]
      o = ObjectFiller(handle)
      o["label"], o["color"] = labelCrossTable[i]
      o["type"]  = self.get_grouptype('CVR3_ATS_MOV')
      objects.append(o)
    return scaletime, objects
