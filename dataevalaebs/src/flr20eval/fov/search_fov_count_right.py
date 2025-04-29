# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import search_fov_count_left

class Search(search_fov_count_left.Search):
  sgs = [ {"fov count right": ("General_radar_status", "FOV_count_centre")} ]
  quaname_base = 'fov count right'
