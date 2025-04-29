# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"search_lane_quality_state".
Road type based mileages and durations are also shown.
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'FLC25 lane state'
  search_class = 'mfc525eval.laneeval.search_left_lane_quality_state.Search'
  
  base_title = "FLC25 left\nlane quality"
