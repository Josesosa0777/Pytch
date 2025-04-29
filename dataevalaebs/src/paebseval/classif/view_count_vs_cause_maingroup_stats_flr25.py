# -*- dataeval: init -*-

"""
Count AEBS events based on causes
"""

import view_count_vs_cause_stats_flr25
from aebs.par import paebs_classif

init_params = view_count_vs_cause_stats_flr25.init_params

class View(view_count_vs_cause_stats_flr25.View):
  labelmap = paebs_classif.label2maingroup
