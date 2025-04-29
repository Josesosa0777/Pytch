# -*- dataeval: init -*-

import sys

from interface.Interfaces import iAnalyze

from issuegen_warning import init_params


class Analyze(iAnalyze):
  def init(self, dep):
    self.dep = dep,
    return

  def analyze(self):
    view_name, ids = self.get_modules().fill(self.dep[0])
    batch = self.get_batch()
    header = self.interval_table.getHeader()
    sys.stdout.write(batch.str_table(header[1:], ids))
    sys.stdout.flush()
    return
