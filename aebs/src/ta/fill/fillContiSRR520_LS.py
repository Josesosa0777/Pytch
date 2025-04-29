# -*- dataeval: init -*-

import interface


class cFill(interface.iAreaFill):
  dep = 'calcSRR520_areas',

  def check(self):
    areas = self.modules.fill(self.dep[0])
    return areas

  def fill(self, areas):
    # create object
    o = dict()
    o["valid"] = areas.mask
    o["shape"] = 'POLYGON'
    o["type"] = self.get_grouptype('BSM_LS')
    o["vertices"] = areas.bsm_ls_vertices
    objects = [o]
    return areas.time, objects
