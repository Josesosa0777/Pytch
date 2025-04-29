# -*- dataeval: init -*-
# -*- coding: utf-8 -*-


from aebs.abc.view_quantity_hist import init_params, View

class YrsOffset(View):
  search_class = "flr20eval.yrsoffset.search_yrs_offset.Search"
  quanamegroup = "AC100 sensor check"
  quaname = "yaw rate offset min"
  base_title = "yaw rate offset"
