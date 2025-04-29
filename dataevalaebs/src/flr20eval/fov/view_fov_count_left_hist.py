# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc.view_quantity_hist import init_params, View

class FovCntLeft(View):
  search_class = "flr20eval.fov.search_fov_count_left.Search"
  quanamegroup = "AC100 sensor check"
  quaname = base_title = "fov count left min"
  hist_kwargs = dict(log=True)
