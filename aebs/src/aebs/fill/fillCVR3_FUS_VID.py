# -*- dataeval: init -*-

import numpy as np

import interface
import measparser
from fillCVR3_FUS import VID_OBJ_NUM

VID_INVALID_HANDLE = 64

labelTemplate = "CVR3_VID_i%d_h%d"

devicenames = "RadarFC",

signalGroups = []
for dn in devicenames:
  signalGroup = {}
  for i in xrange(VID_OBJ_NUM):
    signalGroup['i%d.Handle'  %i] = dn, 'fus.SVidBasicInput_TC.VidObj.i%d.Handle'  %i
    signalGroup['i%d.dxv'     %i] = dn, 'fus.SVidBasicInput_TC.VidObj.i%d.dxv'     %i
    signalGroup['i%d.dyv'     %i] = dn, 'fus.SVidBasicInput_TC.VidObj.i%d.dyv'     %i
    signalGroup['i%d.vxv'     %i] = dn, 'fus.SVidBasicInput_TC.VidObj.i%d.vxv'     %i
    signalGroup['i%d.ObjType' %i] = dn, 'fus.SVidBasicInput_TC.VidObj.i%d.ObjType' %i
  signalGroups.append(signalGroup)

class cFill(interface.iObjectFill):
  def check(self):
    group = interface.Source.selectSignalGroup(signalGroups)
    return group
    
  def fill(self, group):
    Signals = measparser.signalgroup.extract_signals(group)
    scaletime = interface.Source.selectScaleTime(Signals, interface.StrictlyGrowingTimeCheck)
    kwargs = dict(ScaleTime=scaletime)
    objects=[]
    for i in xrange(VID_OBJ_NUM):
      o = {}
      o["id"]  = interface.Source.getSignalFromSignalGroup(group, 'i%d.Handle'  %i, **kwargs)[1]
      o["dx"]  = interface.Source.getSignalFromSignalGroup(group, 'i%d.dxv'     %i, **kwargs)[1]
      o["dy"]  = interface.Source.getSignalFromSignalGroup(group, 'i%d.dyv'     %i, **kwargs)[1]
      o["vx"]  = interface.Source.getSignalFromSignalGroup(group, 'i%d.vxv'     %i, **kwargs)[1]
      o["type"] = np.where(o["id"] == VID_INVALID_HANDLE, self.get_grouptype('NONE_TYPE'), self.get_grouptype('CVR3_FUS_VID'))
      o["label"] = np.array( [labelTemplate %(i,handle) for handle in o["id"]] )
      objects.append(o)
    return scaletime, objects
