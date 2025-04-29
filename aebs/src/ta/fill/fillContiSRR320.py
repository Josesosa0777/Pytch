# -*- dataeval: init -*-

import numpy as np

import interface
from measproc.IntervalList import intervalsToMask

class cFill(interface.iFill):
  dep = 'calc_srr320_raw'

  def check(self):
    tracks = self.modules.fill("calc_srr320_raw")
    return tracks

  def fill(self, tracks):
    objects = []
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.mask, id, -1)
      o["valid"] = track.mask
      o["label"] = np.array( ["CONTI_SRR320_track_%d" %id if id != -1 else "" for id in o["id"] ] )
      o["dx"] = track.dx
      o["dy"] = track.dy

      o["type"] = np.where(~track.mask, self.get_grouptype('NONE_TYPE'), self.get_grouptype('CONTI_SRR320') )

      objects.append(o)
    return tracks.time, objects
