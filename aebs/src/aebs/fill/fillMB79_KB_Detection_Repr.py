# -*- dataeval: init -*-

import numpy as np
import interface

from aebs.fill.fillMB79_Target import init_params


class cFill(interface.iObjectFill):
  dep = 'calc_mb79_kb_detection_repr',

  def init(self, xoffset=0.0, yoffset=0.0):
    self.xoffset = xoffset
    self.yoffset = yoffset
    return

  def check(self):
    det_representants = self.modules.fill(self.dep[0])
    return det_representants

  def fill(self, det_representants):
    objects = []
    for id, det_repr in det_representants.iteritems():
      # create object
      o = {}
      o["id"] = det_repr.id.data
      o["valid"] = ~det_repr.dx.mask
      o["label"] = np.where(o["valid"], "MB79_det_repr_%d" %id, "")
      o["dx"] = det_repr.dx.data - self.xoffset
      o["dy"] = det_repr.dy.data - self.yoffset
      o["type"] = np.where(det_repr.dx.mask,
                           self.get_grouptype('NONE_TYPE'), self.get_grouptype('MB79_DET_REPR'))
      o["init"] = o["valid"]

      objects.append(o)
    return det_representants.time, objects
