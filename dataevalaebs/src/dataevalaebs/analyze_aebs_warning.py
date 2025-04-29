# -*- dataeval: init -*-

from interface.Interfaces import iAnalyze

init_params = {
  'all': dict(date=None)
}

class Analyze(iAnalyze):
  def init(self, date):
    self.date = date
    return

  def fill(self):
    batch = self.get_batch()
    view_name = batch.create_table_from_last_entries(date=self.date)

    ids = [idx for idx,  in batch.query("""
      SELECT entryintervals.id FROM %s en
        JOIN entryintervals ON
             entryintervals.entryid = en.id
        JOIN modules ON
             modules.id = en.moduleid

        JOIN measurements ON measurements.id = en.measurementid

      WHERE modules.class = :class_name
        AND en.title = :title
      """ % view_name,
      class_name='dataevalaebs.search_aebs_warning.Search',
      title='AEBS-warnings',
    )]
    return view_name, ids

  def analyze(self, view_name, ids):
    self.interval_table.addIntervals(ids)
    return

