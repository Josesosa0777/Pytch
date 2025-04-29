# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from aebs.abc.search_quantity_trends import SearchQuantity

range_min = 0.
range_max = 1.

class Search(SearchQuantity):
  sgs  = [ {"blindness": ("General_radar_status", "sensor_blindness")} ]
  quanamegroup = 'AC100 sensor check'
  quaname_base = 'blindness'
  bins = np.linspace(range_min, range_max, num=11) # resolution 0.1
  quantity_setters = (
    'set_drivendistance@egoeval',
  )
