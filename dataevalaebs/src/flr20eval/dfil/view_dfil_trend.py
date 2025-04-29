# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc import view_quantity_trend
from flr20eval.dfil import search_dfil

init_params = view_quantity_trend.init_params

class View(view_quantity_trend.View):
  search_class = "flr20eval.dfil.search_dfil.Search"
  quanamegroup = "AC100 sensor check"
  quaname_min = "dfil min"
  quaname_max = "dfil max"
  base_title = "dfil"
  min = search_dfil.range_min
  max = search_dfil.range_max
  treshold = 0
