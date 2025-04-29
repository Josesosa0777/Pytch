# -*- dataeval: init -*-

"""
Count AEBS events based on highest cascade phase
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = {k: v for k, v in view_quantity_vs_status_stats.init_params.iteritems()
               if k.endswith("_mergedcount")}

class View(view_quantity_vs_status_stats.View):
  label_group = 'AEBS cascade phase'
  search_class = 'aebseval.search_events_aeb.Search'

  labels_to_show = ('warning', 'partial\n braking', 'emergency\n braking', 'in-crash\n braking')
  
  base_title = "AEBS events' highest phases"
  
  show_none = False
