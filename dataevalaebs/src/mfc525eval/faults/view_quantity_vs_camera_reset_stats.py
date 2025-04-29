# -*- dataeval: init -*-

"""
TBD
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'FLC25 events'
  search_class = 'mfc525eval.faults.search_flc25_camera_reset_events.Search'
  entry_title = 'FLC25 events'
  
  show_empties = False
  show_none = False
  
  base_title = "Camera Reset"
