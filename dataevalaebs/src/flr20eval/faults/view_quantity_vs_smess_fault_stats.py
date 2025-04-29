# -*- dataeval: init -*-

"""
TBD
"""

from aebs.abc import view_quantity_vs_status_stats

init_params = view_quantity_vs_status_stats.init_params

class View(view_quantity_vs_status_stats.View):
  label_group = 'FLR21 fault'
  search_class = 'flr20eval.faults.search_smess_faults.Search'
  entry_title = 'FLR21 faults - ACC_S02 - single'
  
  show_empties = False
  show_none = False
  
  base_title = "Occurred FLR21 faults"
