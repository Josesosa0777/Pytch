# -*- dataeval: init -*-

import numpy as np

import interface

INVALID_TARGET_ID = -1

class cFill(interface.iObjectFill):
  dep = 'calc_mbl2_raw_targets', 'calc_mbl2_egomotion'

  def check(self):
    targets = self.modules.fill("calc_mbl2_raw_targets")
    egomotion = self.modules.fill("calc_mbl2_egomotion")
    return targets, egomotion

  def fill(self, targets, egomotion):
    objects = []
    for id, target in targets.iteritems():
      # create object
      o = {}
      o["id"] = np.where(target.range.mask, INVALID_TARGET_ID, id)
      o["label"] = np.array( ["MBL2_trg_%d" %id if id != INVALID_TARGET_ID else "" for id in o["id"]] )
      o["dx"] = target.dx.data
      o["dy"] = target.dy.data
      o["type"] = np.where(target.range.mask,
                      self.get_grouptype('NONE_TYPE'),
                      self.get_grouptype('MBL2_TARGET')
                    )
      objects.append(o)
    return targets.time, objects
