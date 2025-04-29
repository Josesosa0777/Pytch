# -*- dataeval: init -*-

"""
TBD
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'DM1 event'
  search_class = 'flr25eval.faults.search_flr25_dm1_events.Search'
  entry_title = 'DM1 event'
  
  show_empties = False
  show_none = False
  
  base_title = "DM1 event"
