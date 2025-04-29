# -*- dataeval: init -*-

import numpy as np

import interface
from collections import namedtuple
from measproc.IntervalList import intervalsToMask

INVALID_TRACK_ID = -1
BOUNDING_BOX_SIZE = 3

init_params = {
  'FRONT_BUMPER': dict(xoffset=0.0, yoffset=0.0),
  'FRONT_RIGHT_CORNER': dict(xoffset=0.0, yoffset=-1.25),
}

BoundingBox = namedtuple('BoundingBox', ('upper_left_x', 'upper_left_y', 'width', 'height'))

class cFill(interface.iObjectFill):
  dep = 'calc_mb79_raw_tracks', 'calc_mb79_egomotion'

  def init(self, xoffset=0.0, yoffset=0.0):
    self.xoffset = xoffset
    self.yoffset = yoffset
    return

  def check(self):
    tracks = self.modules.fill("calc_mb79_raw_tracks")
    egomotion = self.modules.fill("calc_mb79_egomotion")
    return tracks, egomotion

  def fill(self, tracks, egomotion):
    objects = []
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.range.mask, INVALID_TRACK_ID, id)
      o["valid"] = track.tr_state.valid.data & ~track.tr_state.valid.mask
      o["label"] = np.array( ["MB79_track_%d" %id if id != INVALID_TRACK_ID else "" for id in o["id"]] )
      o["dx"] = track.dx.data - self.xoffset
      o["dy"] = track.dy.data - self.yoffset

      o["type"] = np.where(track.dx.mask,
                           self.get_grouptype('NONE_TYPE'),
                           np.where(track.mov_state.moving,
                                    self.get_grouptype('MB79_TRACK_MOV'),
                                    self.get_grouptype('MB79_TRACK_STAT')
                                    )
                           )

      init_intervals = [(st, st + 1) for st, end in track.alive_intervals]
      o["init"] = intervalsToMask(init_intervals, track.dx.size)

      upper_left_x = o['dx'] + BOUNDING_BOX_SIZE / 2.0
      upper_left_y = o['dy'] + BOUNDING_BOX_SIZE / 2.0
      width = np.full(track.dx.shape, BOUNDING_BOX_SIZE)
      heigth = np.full(track.dx.shape, BOUNDING_BOX_SIZE)
      o["bbox"] = BoundingBox(upper_left_x=upper_left_x, upper_left_y=upper_left_y, width=width, height=heigth)

      objects.append(o)
    return tracks.time, objects
