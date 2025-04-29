# -*- dataeval: init -*-
from interface.Interfaces import iAnalyze

init_params = {
  'search_aebs_warning': dict(
    module='dataevalaebs.search_aebs_warning.Search',
  ),
  'search_flc20_missing_aeb_track': dict(
    module='search_flc20_missing_aeb_track.Search',
  ),
  'search_flr20_aeb_track_asso_dropout': dict(
    module='dataevalaebs.search_flr20_aeb_track_asso_dropout.SearchFlr20AssoDropout',
  ),
}

class Analyze(iAnalyze):
  def init(self, module):
    self.module = module
    return

  def check(self):
    batch = self.get_batch()
    last_startid = batch.query('''
      SELECT DISTINCT starts.id FROM entries
        JOIN modules ON modules.id = entries.moduleid
        JOIN starts ON starts.id = entries.startid
      WHERE modules.class = :class_name
      ORDER BY starts.time DESC LIMIT 1
    ''', class_name=self.module, fetchone=True)
    assert last_startid is not None, 'No single run for %s' % self.module
    last_startid, = last_startid

    entries = batch.query('''
      SELECT src_entries.id, dst_entries.id
        FROM entries src_entries, entries dst_entries
        JOIN modules src_modules ON src_modules.id = src_entries.moduleid
        JOIN modules dst_modules ON dst_modules.id = dst_entries.moduleid
        JOIN starts src_starts ON src_starts.id = src_entries.startid
        JOIN starts dst_starts ON dst_starts.id = dst_entries.startid

      WHERE dst_entries.startid = :dst_start
        AND src_starts.time < dst_starts.time
        AND src_modules.class = :class_name
        AND dst_modules.class = :class_name
        AND src_entries.measurementid = dst_entries.measurementid
        AND src_modules.param = dst_modules.param

      GROUP BY src_entries.measurementid, src_modules.param, dst_starts.time
      HAVING src_starts.time = MAX(src_starts.time)
      ''', dst_start=last_startid, class_name=self.module)
    return entries

  def analyze(self, entries):
    batch = self.get_batch()
    for src_entryid, dst_entryid in entries:
      batch.update_interval_labels(src_entryid, dst_entryid)
      batch.update_interval_comment(src_entryid, dst_entryid)
      batch.update_interval_quantities(src_entryid, dst_entryid)
    return

