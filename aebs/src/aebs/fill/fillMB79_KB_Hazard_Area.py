# -*- dataeval: init -*-

import interface


class cFill(interface.iAreaFill):
  dep = 'calc_mb79_kb_areas',

  def check(self):
    areas = self.modules.fill(self.dep[0])
    return areas

  def fill(self, areas):
    # create object
    o = dict()
    o["valid"] = areas.hazard_mask
    o["shape"] = 'POLYGON'
    o["type"] = self.get_grouptype('KB_HAZARD_AREA')
    o["vertices"] = areas.hazard_area_vertices
    objects = [o]
    return areas.time, objects
