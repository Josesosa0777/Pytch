# -*- dataeval: init -*-

import numpy as np

from interface import iObjectFill
from measproc.Object import colorByVelocity
from measproc.IntervalList import intervalsToMask
from fill_flc20_raw_tracks import INVALID_VIDEO_ID

class cFill(iObjectFill):
  dep = 'fill_flc20_raw_tracks', 'calc_egomotion'

  def check(self):
    modules = self.get_modules()
    tracks    = modules.fill("fill_flc20_raw_tracks")
    ego_orig  = modules.fill("calc_egomotion")
    egomotion = ego_orig.rescale(tracks.time)
    return tracks, egomotion

  def fill(self, tracks, egomotion):
    objects = []
    # loop through all tracks
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.dx.mask, INVALID_VIDEO_ID, id)
      o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
      o["label"] = np.array( ["FLC20_%d" %id for id in o["id"]] )
      o["dx"]  = track.dx.data
      o["dy"]  = track.dy.data
      o["type"] = np.where( track.mov_state.stat.data & ~track.mov_state.stat.mask,
                            self.get_grouptype('FLC20_STAT'),
                            self.get_grouptype('FLC20_MOV') )
      init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
      o["init"] = intervalsToMask(init_intervals, track.dx.size)
      # ongoing: green, stationary: red, oncoming: blue
      o["color"] = colorByVelocity(egomotion.vx, track.vx.data,
                                   [0, 255, 0],  [255, 0, 0], [0, 0, 255])
      objects.append(o)
    return tracks.time, objects
