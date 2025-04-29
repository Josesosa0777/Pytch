# -*- dataeval: init -*-

"""
TBD
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'FLR25 events'
  search_class = 'flr25eval.faults.search_flr25_radar_reset_events.Search'
  entry_title = 'FLR25 events'
  
  show_empties = False
  show_none = False
  
  base_title = "Radar Reset"
