# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from aebs.abc.search_quantity_trends import SearchBasedOnEvent

class Search(SearchBasedOnEvent):
  sgs  = [
    {
      "sensor_blind_detected": ("General_radar_status", "sensor_blind_detected"),
      "blindness":             ("General_radar_status", "sensor_blindness"),
    },
  ]
  quanamegroup = 'AC100 sensor check'
  quaname_base = 'blindness'
  event_signame = "sensor_blind_detected"
  title = "blindness detected"
  quantity_setters = (
    'set_drivendistance@egoeval',
  )
