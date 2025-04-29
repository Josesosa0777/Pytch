# -*- dataeval: init -*-

import numpy as np
import interface

from aebs.fill.fillMB79_Target import init_params


class cFill(interface.iObjectFill):
  dep = 'calc_mb79_kb_targets',

  def init(self, xoffset=0.0, yoffset=0.0):
    self.xoffset = xoffset
    self.yoffset = yoffset
    return

  def check(self):
    kb_targets = self.modules.fill(self.dep[0])
    return kb_targets

  def fill(self, kb_targets):
    objects = []
    for id, target in kb_targets.iteritems():
      # create object
      o = {}
      o["id"] = target.id.data
      o["valid"] = ~target._mask
      o["label"] = np.where(o["valid"], "MB79_KB_target_%d" %id, "")
      o["dx"] = target.dx.data - self.xoffset
      o["dy"] = target.dy.data - self.yoffset
      o["type"] = np.where(target._mask,
                           self.get_grouptype('NONE_TYPE'), self.get_grouptype('KB_TARGET'))
      o["init"] = o["valid"]

      objects.append(o)
    return kb_targets.time, objects
