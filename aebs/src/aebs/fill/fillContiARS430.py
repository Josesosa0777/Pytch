# -*- dataeval: init -*-

import numpy as np

import interface
from measproc.IntervalList import intervalsToMask

class cFill(interface.iObjectFill):
  dep = 'calc_conti_ars430'

  def check(self):
    tracks = self.modules.fill("calc_conti_ars430")
    return tracks

  def fill(self, tracks):
    objects = []
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.range.mask, -1, id)
      o["valid"] = ~track.range.mask
      o["label"] = np.array( ["CONTI_track_%d_%c" %(id,letter) if id != -1 else "" for (id,letter) in zip(o["id"],track.which)] )
      o["dx"] = track.dx
      o["dy"] = track.dy

      o["type"] = np.where(track.dx.mask,
                           self.get_grouptype('NONE_TYPE'),
                           np.where(track.mov_state.moving,
                                    self.get_grouptype('CONTI_ARS430_MOVING'),
                                    np.where(track.mov_state.stopped,
                                        self.get_grouptype('CONTI_ARS430_STOPPED'),
                                        self.get_grouptype('CONTI_ARS430_STAT'))
                                    )
                           )

      init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
      o["init"] = intervalsToMask(init_intervals, track.dx.size)

      objects.append(o)
    return tracks.time, objects
