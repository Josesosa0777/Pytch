# -*- dataeval: init -*-

import numpy as np

import interface
from measproc.IntervalList import intervalsToMask

class cFill(interface.iFill):
  dep = 'calc_conti_ars440'

  def check(self):
    tracks = self.modules.fill("calc_conti_ars440")
    return tracks

  def fill(self, tracks):
    objects = []
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.range.mask, -1, id)
      o["valid"] = ~track.range.mask
      o["label"] = np.array( ["CONTI_track_%d" %id if id != -1 else "" for id in o["id"]] )
      o["dx"] = track.dx
      o["dy"] = track.dy

      o["type"] = np.where(track.dx.mask,
                           self.get_grouptype('NONE_TYPE'),
                           np.where(track.mov_state.moving,
                                    self.get_grouptype('CONTI_ARS440_MOVING'),
                                    np.where(track.mov_state.stopped,
                                        self.get_grouptype('CONTI_ARS440_STOPPED'),
                                        self.get_grouptype('CONTI_ARS440_STAT'))
                                    )
                           )
      objects.append(o)
    return tracks.time, objects
