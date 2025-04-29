# -*- dataeval: init -*-

import numpy as np

from interface import iObjectFill

RED = 255,0,0
GREEN = 0,255,0
BLUE = 0,0,255

class cFill(iObjectFill):
  dep = 'fill_flr20_raw_targets', 'fill_flr20_raw_tracks', 'fill_flr20_aeb_track'

  def check(self):
    modules = self.get_modules()
    targets = modules.fill("fill_flr20_raw_targets")
    tracks  = modules.fill("fill_flr20_raw_tracks")
    aeb     = modules.fill("fill_flr20_aeb_track")
    assert targets.time is tracks.time is aeb.time, 'FLR20 target/track/AEB time does not agree!'
    return targets, tracks, aeb

  def fill(self, targets, tracks, aeb):
    objects = []
    # loop through all targets
    for id, target in targets.iteritems():
      # create object
      o = {}
      o["valid"] = ~target.dx.mask
      o["dx"] = target.dx.data
      o["dy"] = target.dy.data
      o["type"] = np.where( target.dx.mask,
                            self.get_grouptype('NONE_TYPE'),
                            self.get_grouptype('FLR20_TARGET')
                          )
      o["label"] = "FLR20_trg_%d" %id
      o["init"] = o["valid"]
      # color
      blue = np.array(BLUE, dtype=np.uint8)
      color = np.repeat( blue[np.newaxis,:], aeb.time.size, axis=0)
      self.colorize(id, color, tracks, GREEN)
      self.colorize(id, color, {0:aeb}, RED)
      o["color"] = color
      objects.append(o)
    return targets.time, objects

  @staticmethod
  def colorize(id, array, tracks, color):
    for track in tracks.itervalues():
      if id in track.refl_asso_masks:
        mask = track.refl_asso_masks[id]
        array[mask] = color
    return
