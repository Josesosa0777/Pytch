# -*- dataeval: init -*-

import numpy as np

import interface

INVALID_TRACK_ID = -1

class cFill(interface.iObjectFill):
  dep = 'calc_mbl2_raw_tracks', 'calc_mbl2_egomotion'

  def check(self):
    tracks    = self.modules.fill("calc_mbl2_raw_tracks")
    egomotion = self.modules.fill("calc_mbl2_egomotion")
    return tracks, egomotion

  def fill(self, tracks, egomotion):
    objects = []
    for id, track in tracks.iteritems():
      # create object
      o = {}
      o["id"] = np.where(track.dx.mask, INVALID_TRACK_ID, id)
      o["label"] = np.array( ["MBL2_%d" %id if id != INVALID_TRACK_ID else "" for id in o["id"]] )
      o["dx"] = track.dx.data
      o["dy"] = track.dy.data
      o["type"] =  np.where( track.dx.mask,
                      self.get_grouptype('NONE_TYPE'),
                      self.get_grouptype('MBL2_TRACK')
                    )
      objects.append(o)
    return tracks.time, objects
