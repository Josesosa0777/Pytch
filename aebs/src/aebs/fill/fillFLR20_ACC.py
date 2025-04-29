# -*- dataeval: init -*-

import numpy as np

from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from fillFLR20 import INVALID_TRACK_ID

class cFill(iObjectFill):
  dep = 'fill_flr20_acc_track',

  def check(self):
    modules = self.get_modules()
    track = modules.fill("fill_flr20_acc_track")
    return track

  def fill(self, track):
    # create object
    o = {}
    o["id"] = np.where(track.id.mask, INVALID_TRACK_ID, track.id.data)
    o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
    o["label"] = ''
    o["dx"] = track.dx.data
    o["dy"] = track.dy.data
    o["type"] = np.where( track.id.mask,
                          self.get_grouptype('NONE_TYPE'),
                          self.get_grouptype('FLR20_ACC') )
    init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
    o["init"] = intervalsToMask(init_intervals, track.dx.size)
    objects = [o]
    return track.time, objects
