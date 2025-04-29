# -*- dataeval: init -*-

from interface.Interfaces import iAnalyze

init_params = {
  'ldw': dict(class_name='dataevalaebs.search_ldw_fake.Search',
              titles=['ldw-left', 'ldw-right'], date=None),
  'aebs': dict(class_name='dataevalaebs.search_aebs_warning.Search',
               titles=['AEBS-warnings'], date=None),
  'xls': dict(class_name='FLR20EvalAEBS_AEBS_warnings_Radar_only.xls',
              titles=['AEBS-warning-offline'], date=None),
}


class Analyze(iAnalyze):
  def init(self, class_name, titles, date):
    # register the parameters
    self.class_name = class_name
    self.titles = titles
    self.date = date
    return

  def fill(self):
    # create database access called batch
    batch = self.get_batch()
    # create a temporary view for the result of the last run
    view_name = batch.create_table_from_last_entries(date=self.date)

    # get the interval ids of the ldw module
    ids = []
    for title in self.titles:
      ids.extend(idx for idx,  in batch.query("""
        SELECT entryintervals.id FROM %s en
          JOIN entryintervals ON
               entryintervals.entryid = en.id
          JOIN modules ON
               modules.id = en.moduleid

        WHERE modules.class = :class_name
          AND en.title = :title
        """ % view_name,

      class_name=self.class_name,
      title=title))
    return view_name, ids

  def analyze(self, view_name, ids):
    # create batch navigator and register the selected intervals above
    self.interval_table.addIntervals(ids)
    return

