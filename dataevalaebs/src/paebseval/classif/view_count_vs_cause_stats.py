# -*- dataeval: init -*-

"""
Count AEBS events based on causes
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = {k: v for k, v in view_quantity_vs_status_stats.init_params.iteritems()
               if k.endswith("_mergedcount")}

class View(view_quantity_vs_status_stats.View):
  label_group = 'AEBS event cause'
  search_class = 'aebseval.search_events.Search'
  
  base_title = "AEBS event causes"
  
  show_none = False
