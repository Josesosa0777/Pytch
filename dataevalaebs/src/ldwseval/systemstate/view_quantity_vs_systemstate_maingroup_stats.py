# -*- dataeval: init -*-

"""
TBD
"""

import view_quantity_vs_systemstate_stats
from aebs.par import ldws_state

init_params = view_quantity_vs_systemstate_stats.init_params

class View(view_quantity_vs_systemstate_stats.View):
  labelmap = ldws_state.label2maingroup
  show_none = False
  label2color = ldws_state.maingroup2color
