# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from view_fov_count_left_hist import init_params, FovCntLeft

class Fov(FovCntLeft):
  search_class = "flr20eval.fov.search_fov_count_centre.Search"
  quaname = base_title = "fov count centre min"
