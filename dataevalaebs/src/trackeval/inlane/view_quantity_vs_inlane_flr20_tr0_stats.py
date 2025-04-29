# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"search_inlane_flr20_tr0".
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  search_class = 'trackeval.inlane.search_inlane_flr20_tr0.Search'
  
  base_title = "In-lane obstacle presence"
