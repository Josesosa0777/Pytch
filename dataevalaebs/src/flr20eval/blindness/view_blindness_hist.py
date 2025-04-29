# -*- dataeval: init -*-
# -*- coding: utf-8 -*-


from aebs.abc.view_quantity_hist import init_params, View

class Blindness(View):
  search_class = "flr20eval.blindness.search_blindness.Search"
  quanamegroup = "AC100 sensor check"
  quaname = "blindness min"
  base_title = "blindness"
