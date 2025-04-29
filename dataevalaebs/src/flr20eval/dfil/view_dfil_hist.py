# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc.view_quantity_hist import init_params, View

class Dfil(View):
  search_class = "flr20eval.dfil.search_dfil.Search"
  quanamegroup = "AC100 sensor check"
  quaname = "dfil min"
  base_title = "dfil"
