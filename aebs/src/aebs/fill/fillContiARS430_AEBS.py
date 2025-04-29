# -*- dataeval: init -*-

import numpy as np

import interface
from measproc.IntervalList import intervalsToMask

class cFill(interface.iFill):
  dep = 'calc_conti_ars430_aebs'

  def check(self):
    tracks = self.modules.fill(self.dep)
    return tracks

  def fill(self, track):
    o = {}
    o["valid"] = track.valid.data
    o["id"] = np.where(o["valid"], 1, -1)
    o["label"] = np.array( [""  for id in o["id"]] )
    o["dx"] = track.dx.data
    o["dy"] = track.dy.data

    o["type"] = np.where(o["valid"],
                         self.get_grouptype('CONTI_AEBS_WARNING'),
                         self.get_grouptype('NONE_TYPE')
                         )
    return track.time, [o]
