# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"search_f30_fused_state_KPI".
Road type based mileages and durations are also shown.
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'FLC25 fused state'
  search_class = 'mfc525eval.objecteval.search_f30_fused_state_KPI.Search'
  
  show_empties = False
  show_none = False

  base_title = "FLC25 fused state"
