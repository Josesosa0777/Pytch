# -*- dataeval: init -*-

import numpy as np

import interface
#from measproc.Object import colorByVelocity

INVALID_TARGET_ID = -1

init_params = {
  'FRONT_BUMPER': dict(xoffset=0.0, yoffset=0.0),
  'FRONT_RIGHT_CORNER': dict(xoffset=0.0, yoffset=-1.25),
}

class cFill(interface.iObjectFill):
  dep = 'calc_mb79_raw_targets' #, 'calc_mb79_egomotion'

  def init(self, xoffset=0.0, yoffset=0.0):
    self.xoffset = xoffset
    self.yoffset = yoffset
    return

  def check(self):
    targets = self.modules.fill("calc_mb79_raw_targets")
    #egomotion = self.modules.fill("calc_mb79_egomotion")
    return targets #, egomotion

  def fill(self, targets): #, egomotion):
    objects = []
    #c = [0, 255, 0]
    for id, target in targets.iteritems():
      # create object
      o = {}
      o["id"] = np.where(target.range.mask, INVALID_TARGET_ID, id)
      o["valid"] = ~target.dx.mask
      o["label"] = np.array( ["MB79_det_%d" %id if id != INVALID_TARGET_ID else "" for id in o["id"]] )
      o["dx"] = target.dx.data - self.xoffset
      o["dy"] = target.dy.data - self.yoffset

      #TODO: create mov states
      o["type"] = self.get_grouptype('MB79_TARGET')

      o["init"] = o["valid"]

      #o["color"] = colorByVelocity(egomotion.vx, target.range_rate.data, c, c, c)  # TODO: without colorByVelocity
      objects.append(o)
    return targets.time, objects
