# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from aebs.abc.search_quantity_trends import SearchQuantity

range_min = 0.7 # 0.744
range_max = 1.3 # 1.254

class Search(SearchQuantity):
  sgs  = [ {"covi": ("General_radar_status", "covi")} ]
  quanamegroup = 'AC100 sensor check'
  quaname_base = 'covi'
  bins = np.linspace(range_min, range_max, num=16) # resolution 0.04, centered around 1.
  quantity_setters = (
    'set_drivendistance@egoeval',
  )
