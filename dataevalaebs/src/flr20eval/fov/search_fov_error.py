# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc.search_quantity_trends import SearchBasedOnEvent

class Search(SearchBasedOnEvent):
  sgs  = [
    {
      "SIB1_FOV_error":   ("General_radar_status", "SIB1_FOV_error"),
      "fov count left":   ("General_radar_status", "FOV_count_left"),
      "fov count centre": ("General_radar_status", "FOV_count_centre"),
      "fov count right":  ("General_radar_status", "FOV_count_right"),
    },
  ]
  quanamegroup = 'AC100 sensor check'
  event_signame = "SIB1_FOV_error"
  title = "fov error"

  quantity_setters = (
    'set_drivendistance@egoeval',
  )
