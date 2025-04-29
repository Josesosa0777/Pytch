# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc.search_quantity_trends import SearchQuantity

class Search(SearchQuantity):
  sgs = [ {"fov count left" : ("General_radar_status", "FOV_count_left")} ]
  bins = (0, 1000, 2000, 3000, 4000, 5000, 6001, 25500)
  quanamegroup = 'AC100 sensor check'
  quaname_base = 'fov count left'
  quantity_setters = (
    'set_drivendistance@egoeval',
  )
