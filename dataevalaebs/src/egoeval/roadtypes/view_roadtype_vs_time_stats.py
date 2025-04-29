# -*- dataeval: init -*-

"""
Plot time-based statistics about the road types
"""

from collections import OrderedDict

from aebs.abc import view_status_vs_time_stats

init_params = view_status_vs_time_stats.init_params

class View(view_status_vs_time_stats.View):
  label_group = 'road type'
  search_class = 'egoeval.roadtypes.search_roadtypes.Search'

  colors = OrderedDict((
    (u'ego stopped', 'b'),
    (u'city',        'g'),
    (u'rural',       'm'),
    (u'highway',     'r'),
  ))
  def_color = 'c'

  base_title = "Road types"
