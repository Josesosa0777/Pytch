# -*- dataeval: init -*-

import numpy as np

import interface
from measproc.IntervalList import intervalsToMask
from aebs.fill.fillMB79_Track import init_params

INVALID_TRACK_ID = -1


class cFill(interface.iObjectFill):
  dep = 'calc_mb79_kb_track_slots', 'calc_mb79_kb_egomotion'

  def init(self, xoffset=0.0, yoffset=0.0):
    self.xoffset = xoffset
    self.yoffset = yoffset
    return

  def check(self):
    tracks = self.modules.fill(self.dep[0])
    egomotion = self.modules.fill(self.dep[1])
    return tracks, egomotion

  def fill(self, tracks, egomotion):
    objects = []
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.range.mask, INVALID_TRACK_ID, id)
      o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
      o["label"] = np.array( ["KB_track_%d" %id if id != INVALID_TRACK_ID else "" for id in o["id"]] )
      o["dx"] = track.dx.data - self.xoffset
      o["dy"] = track.dy.data - self.yoffset

      o["type"] = np.where(track.dx.mask,
                           self.get_grouptype('NONE_TYPE'),
                           np.where(track.mov_state.moving,
                                    self.get_grouptype('KB_TRACK_MOV'),
                                    np.where(track.mov_state.stat,
                                             self.get_grouptype('KB_TRACK_STAT'),
                                             np.where(track.mov_state.stopped,
                                                      self.get_grouptype('KB_TRACK_STOP'),
                                                      self.get_grouptype('KB_TRACK_UNK')
                                                      )
                                             )
                                    )
                           )

      init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
      o["init"] = intervalsToMask(init_intervals, track.dx.size)

      objects.append(o)
    return tracks.time, objects
