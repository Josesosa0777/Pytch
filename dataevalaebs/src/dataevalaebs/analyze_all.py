# -*- dataeval: init -*-

from interface.Interfaces import iAnalyze

init_params = {
  'default':      dict(use_last_entries=False),
  'last_entries': dict(use_last_entries=True),
}

class Analyze(iAnalyze):
  def init(self, use_last_entries):
    self.use_last_entries = use_last_entries
    return

  def fill(self):
    if self.use_last_entries:
      view_name = self.batch.create_table_from_last_entries()
    else:
      view_name = 'entries'

    ei_ids = self.batch.query("""
      SELECT ei.id FROM entryintervals AS ei JOIN %s AS en ON en.id = ei.entryid
      """ % view_name)
    ei_ids = [ei_id for ei_id, in ei_ids]
    return ei_ids

  def analyze(self, ei_ids):
    self.interval_table.addIntervals(ei_ids)
    return
