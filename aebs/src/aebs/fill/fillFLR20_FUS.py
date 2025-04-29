# -*- dataeval: init -*-

import numpy as np

from interface import iObjectFill
from measproc.IntervalList import intervalsToMask
from fillFLR20 import INVALID_TRACK_ID

class cFill(iObjectFill):
  dep = 'fill_flr20_raw_tracks',

  def check(self):
    modules = self.get_modules()
    tracks = modules.fill("fill_flr20_raw_tracks")
    return tracks

  def fill(self, tracks):
    objects = []
    # loop through all tracks
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.dx.mask, INVALID_TRACK_ID, id)
      o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
      o["dx"] = track.dx.data
      o["dy"] = track.dy.data
      stationary = track.mov_state.stat.data & ~track.mov_state.stat.mask
      fused = track.fused.data & ~track.fused.mask
      o["type"] = np.where( track.dx.mask,
                            self.get_grouptype('NONE_TYPE'),
                            np.where(fused,
                                     np.where( stationary,
                                               self.get_grouptype('FLR20_FUSED_STAT'),
                                               self.get_grouptype('FLR20_FUSED_MOV'),
                                             ),
                                     np.where( stationary,
                                               self.get_grouptype('FLR20_RADAR_ONLY_STAT'),
                                               self.get_grouptype('FLR20_RADAR_ONLY_MOV'),
                                             )
                                    )
                          )
      init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
      o["init"] = intervalsToMask(init_intervals, track.dx.size)
      # label
      label_fused = [ "FLR20_%d_%d" %(i,j) for i,j in zip(o["id"], track.video_id.data) ]
      label_radar_only = [ "FLR20_%d" %id for id in o["id"] ]
      o["label"] = np.where(fused, label_fused, label_radar_only)
      objects.append(o)
    return tracks.time, objects
