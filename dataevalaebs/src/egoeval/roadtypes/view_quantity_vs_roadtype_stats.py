# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"search_roadtypes".
Road type based mileages and durations are also shown.
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'road type'
  search_class = 'egoeval.roadtypes.search_roadtypes.Search'
  
  base_title = "Road types"
