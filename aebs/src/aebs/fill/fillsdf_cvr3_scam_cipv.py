# -*- dataeval: init -*-

import numpy as np

import interface
import measparser
from aebs.sdf import asso_cvr3_sCam_cipv, fuse_cvr3_sCam_cipv

sdfLabelTemplate = 'CIPV_h%d_id%d'

signalGroups = asso_cvr3_sCam_cipv.signalGroups

class cFill(interface.iObjectFill):
  def check(self):
    group = interface.Source.selectSignalGroup(signalGroups) 
    return group

  def fill(self, group):
    signals = measparser.signalgroup.extract_signals(group)
    scaletime = interface.Source.selectScaleTime(signals, interface.StrictlyGrowingTimeCheck)
    objects=[]
    # track-to-track association
    assoObj = asso_cvr3_sCam_cipv.AssoCvr3SCamCipv(interface.Source, scaleTime=scaletime)
    assoObj.calc()
    # # track-to-track fusion
    fuseObj = fuse_cvr3_sCam_cipv.FuseCvr3SCamCipv(assoObj)
    fuseObj.calc(isDiag=True)
    # share object references
    interface.assoObj = assoObj
    interface.fuseObj = fuseObj
    # create fused cipv object
    o = {}
    state = None
    labelDtype = '|S%d' %len(sdfLabelTemplate)
    label = np.zeros_like(scaletime, dtype=labelDtype)
    # loop through fused data
    for (i,j), timeIndices in assoObj.assoData.iteritems():
      xfus, Pfus = fuseObj.tracks[i,j]
      if state is None:
        state = np.zeros(shape=(scaletime.size,2), dtype=xfus.dtype)
      state[timeIndices] = xfus[:,0:2]
      label[timeIndices] = sdfLabelTemplate %(i,j)
    # fill object attributes
    o["dx"] = state[:,0]
    o["dy"] = state[:,1]
    o["label"] = label
    o["type"]  = np.where(o["dx"] == 0,
                          self.get_grouptype('NONE_TYPE'),
                          self.get_grouptype('SDF_CVR3_SCAM_CIPV'))
    objects.append(o)
    return scaletime, objects
