# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc import view_quantity_trend
from flr20eval.covi import search_covi

init_params = view_quantity_trend.init_params

class View(view_quantity_trend.View):
  search_class = "flr20eval.covi.search_covi.Search"
  quanamegroup = "AC100 sensor check"
  quaname_min = "covi min"
  quaname_max = "covi max"
  base_title = "covi"
  min = search_covi.range_min
  max = search_covi.range_max
  treshold = 1
