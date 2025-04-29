# -*- dataeval: init -*-

import numpy as np

import interface
from fillFLR20 import INVALID_TRACK_ID
from measproc.IntervalList import intervalsToMask, maskToIntervals

init_params = {
  'FRONT_BUMPER': dict(xoffset=0.0, yoffset=0.0),
  'FRONT_RIGHT_CORNER': dict(xoffset=0.0, yoffset=-1.25),
}


class cFill(interface.iObjectFill):
  dep = 'calc_mb79_kb_warning_tracks',

  def init(self, xoffset=0.0, yoffset=0.0):
    self.xoffset = xoffset
    self.yoffset = yoffset
    return

  def check(self):
    modules = self.get_modules()
    track = modules.fill(self.dep[0])
    return track

  def fill(self, track):
    # create object
    o = {}
    # o["id"] = np.where(track.dx.mask, INVALID_TRACK_ID, track.slot.data) # TODO: implement track.id
    o["valid"] = ~track.dx.mask
    # o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask  # TODO: implement track.tr_state.meas
    o["label"] = ''
    o["dx"] = track.dx.data - self.xoffset
    o["dy"] = track.dy.data - self.yoffset
    o["type"] = np.where( track.dx.mask,
                          self.get_grouptype('NONE_TYPE'),
                          self.get_grouptype('MB79_KB_WARNING_TRACK') )
    # init_intervals = [(st, st + 1) for st, end in track.alive_intervals]  # TODO: implement track.id
    init_intervals = [(st, st + 1) for st, end in maskToIntervals(o['valid'])]
    o["init"] = intervalsToMask(init_intervals, track.dx.size)

    objects = [o]
    return track.time, objects