# -*- dataeval: init -*-

"""
Count AEBS events based on causes
"""

import view_count_vs_cause_stats
from aebs.par import aebs_classif

init_params = view_count_vs_cause_stats.init_params

class View(view_count_vs_cause_stats.View):
  labelmap = aebs_classif.label2maingroup
