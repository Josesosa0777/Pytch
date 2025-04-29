# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from aebs.abc.search_quantity_trends import SearchQuantity

range_min = -6.4
range_max =  6.4 # 6.3500000000000005

bins_of_interest = np.linspace(-1., 1., num=21) # resolution 0.1

class Search(SearchQuantity):
  sgs  = [ {"dfil": ("General_radar_status", "dfil")} ]
  bins = np.concatenate( [[range_min], bins_of_interest, [range_max]] )
  quanamegroup = 'AC100 sensor check'
  quaname_base = 'dfil'
  quantity_setters = (
    'set_drivendistance@egoeval',
  )
