# -*- dataeval: init -*-

"""
Plot time-based statistics about a status signal
"""

from collections import OrderedDict

from aebs.abc import view_status_vs_time_stats

init_params = view_status_vs_time_stats.init_params

class View(view_status_vs_time_stats.View):
  label_group = 'camera status'
  search_class = 'flc20eval.sensorstatus.search_sensorstatus.Search'

  colors = OrderedDict((
    (u'Fully Operational',         'g'),
    (u'Warming up / Initializing', 'b'),
    (u'Partially Blocked',         'r'),
    (u'Slightly Blocked',          'b'),
    (u'Error',                     'k'),
    (u'Blocked',                   'm'),
    (u'Misaligned',                'y'),
  ))
  def_color = 'c'

  base_title = "FLC20 sensor status"
