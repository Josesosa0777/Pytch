# -*- dataeval: init -*-

"""
Prints a virtual Interval Table to the standard output.

The containing intervals are determined by the dependent analyze script, which
can be selected by parameter. 
"""

import sys

from interface.Interfaces import iAnalyze


init_params = {
  "all_last_entries": dict(dep="analyze_all-last_entries"),  # "analyze_all-last_entries@evaltools"
}


class Analyze(iAnalyze):
  def init(self, dep):
    self.dep = dep,
    return
  
  def analyze(self):
    header = self.interval_table.getHeader()
    ei_ids = self.modules.fill(self.dep[0])
    sys.stdout.write(self.batch.str_table(header, ei_ids))
    sys.stdout.flush()
    return
