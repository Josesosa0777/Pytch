# -*- dataeval: init -*-

"""
Count AEBS events based on target moving state
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = {k: v for k, v in view_quantity_vs_status_stats.init_params.iteritems()
               if k.endswith("_mergedcount")}

class View(view_quantity_vs_status_stats.View):
  label_group = 'PAEBS moving state'
  search_class = 'paebseval.search_events_paeb.Search'
  
  base_title = "PAEBS events' moving states"
  
  show_none = False
