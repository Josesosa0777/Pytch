# -*- dataeval: init -*-

import numpy as np
import interface
from measproc.IntervalList import intervalsToMask, maskToIntervals


class cFill(interface.iObjectFill):
  dep = 'calc_furukawa_targets',

  def check(self):
    furukawa_targets = self.modules.fill(self.dep[0])
    return furukawa_targets

  def fill(self, furukawa_targets):
    objects = []
    for id, target in furukawa_targets.iteritems():
      # create object
      o = {}
      o["id"] = target.id.data
      o["valid"] = ~target._mask
      o["label"] = np.where(o["valid"], "Furukawa_target_%d" % id, "")
      o["dx"] = target.dx.data
      o["dy"] = target.dy.data
      o["type"] = np.where(target._mask,
                           self.get_grouptype('NONE_TYPE'), self.get_grouptype('FURUKAWA_TARGET'))

      init_intervals = [(st, st + 1) for st, end in maskToIntervals(o['valid'])]
      o["init"] = intervalsToMask(init_intervals, target.dx.size)

      objects.append(o)
    return furukawa_targets.time, objects
