# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"search_systemstate".
Road type based mileages and durations are also shown.
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'AEBS state'
  search_class = 'aebseval.systemstate.search_systemstate.Search'
  
  base_title = "AC100 AEBS state"
