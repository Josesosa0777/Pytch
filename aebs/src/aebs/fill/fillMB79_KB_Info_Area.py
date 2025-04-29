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
    o["valid"] = areas.info_mask
    o["shape"] = 'POLYGON'
    o["type"] = self.get_grouptype('KB_INFO_AREA')
    o["vertices"] = areas.info_area_vertices
    objects = [o]
    return areas.time, objects
