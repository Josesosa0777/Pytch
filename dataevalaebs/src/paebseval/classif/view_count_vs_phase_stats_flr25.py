# -*- dataeval: init -*-

"""
Count AEBS events based on highest cascade phase
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = {k: v for k, v in view_quantity_vs_status_stats.init_params.iteritems()
               if k.endswith("_mergedcount")}

class View(view_quantity_vs_status_stats.View):
  label_group = 'PAEBS cascade phase'
  search_class = 'paebseval.search_events_paeb.Search'

  labels_to_show = ('warning', 'partial braking', 'emergency braking', 'in-crash braking')
  
  base_title = "PAEBS events' highest phases"
  
  show_none = False
