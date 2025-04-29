# -*- dataeval: init -*-

"""
Plot time-based statistics about the LDWSState signal
"""

from collections import OrderedDict

from aebs.abc import view_status_vs_time_stats

init_params = view_status_vs_time_stats.init_params

class View(view_status_vs_time_stats.View):
  label_group = 'LDWS state'
  search_class = 'ldwseval.systemstate.search_systemstate.Search'

  colors = OrderedDict((
    (u'Ready',                 'g'),
    (u'Temporary n/a',         'r'),
    (u'Driver override',       'm'),
    (u'Deactivated by driver', 'b'),
    (u'Not ready',             'b'),
    (u'Error',                 'k'),
    (u'Not available',         'y'),
  ))
  def_color = 'c'

  base_title = "LDWS state"
