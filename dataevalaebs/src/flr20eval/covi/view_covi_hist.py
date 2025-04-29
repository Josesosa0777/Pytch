# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc.view_quantity_hist import init_params, View

class Covi(View):
  search_class = "flr20eval.covi.search_covi.Search"
  quanamegroup = "AC100 sensor check"
  quaname = "covi min"
  base_title = "covi"
