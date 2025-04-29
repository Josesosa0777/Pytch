# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"search_daytime".
Road type based mileages and durations are also shown.
"""

from aebs.abc import view_quantity_vs_status_stats
from aebs.par import daytime

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'daytime'
  search_class = 'flc20eval.daytime.search_daytime.Search'
  
  base_title = "Daytime"
  label2color = daytime.label2color
  #show_none = False
