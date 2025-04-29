# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from aebs.abc.search_quantity_trends import SearchQuantity

range_min = -3.2
range_max =  3.2 # 3.175

class Search(SearchQuantity):
  sgs  = [ {"yaw rate offset": ("General_radar_status", "yawrate_offset")} ]
  bins = np.linspace(range_min, range_max, num=17) # resolution 0.4
  quanamegroup = 'AC100 sensor check'
  quaname_base = 'yaw rate offset'
  quantity_setters = (
    'set_drivendistance@egoeval',
  )
