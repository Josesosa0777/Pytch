# -*- dataeval: init -*-

from interface import iAnalyze

class cAnalyze(iAnalyze):
  def analyze(self):
    batch = self.get_batch()
    view = batch.create_table_from_last_start()
    self.interval_table.setViewForQueries(view)
    return
