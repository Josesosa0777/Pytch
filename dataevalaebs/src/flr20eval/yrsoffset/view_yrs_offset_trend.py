# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc import view_quantity_trend
from flr20eval.yrsoffset import search_yrs_offset

init_params = view_quantity_trend.init_params

class View(view_quantity_trend.View):
  search_class = "flr20eval.yrsoffset.search_yrs_offset.Search"
  quanamegroup = "AC100 sensor check"
  quaname_min = "yaw rate offset min"
  quaname_max = "yaw rate offset max"
  base_title = "yaw rate offset"
  min = search_yrs_offset.range_min
  max = search_yrs_offset.range_max
  treshold = 0
