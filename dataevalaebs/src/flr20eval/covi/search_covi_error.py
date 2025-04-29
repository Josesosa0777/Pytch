# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc.search_quantity_trends import SearchBasedOnEvent

class Search(SearchBasedOnEvent):
  sgs  = [
    {
      "SIB2_COVI_error": ("General_radar_status", "SIB2_COVI_error"),
      "covi":            ("General_radar_status", "covi"), 
    },
  ]
  quanamegroup = 'AC100 sensor check'
  quaname_base = 'covi'
  event_signame = "SIB2_COVI_error"
  title = "covi error"
  quantity_setters = (
    'set_drivendistance@egoeval',
  )
