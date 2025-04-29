# -*- dataeval: init -*-

import sys

from interface.Interfaces import iAnalyze

class Analyze(iAnalyze):
  dep = 'analyze_all-last_entries',
  
  def analyze(self):
    batch = self.get_batch()
    header = self.interval_table.getHeader()
    ei_ids = self.modules.fill(self.dep[0])
    sys.stdout.write(batch.str_table(header, ei_ids))
    sys.stdout.flush()
    return
