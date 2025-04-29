# -*- dataeval: init -*-

"""
Plot time-based statistics about aebs warnings and driven distances
"""

from aebs.abc import view_summary

init_params = view_summary.init_params

class View(view_summary.View):
  event_search_class = 'aebseval.search_events.Search'
  distance_search_class = 'egoeval.roadtypes.search_roadtypes.Search'
  base_title = 'number of aebs warnings and driven kilometers on '
