# -*- dataeval: init -*-

from interface.Interfaces import iAnalyze

class Analyze(iAnalyze):
  def check(self):
    batch = self.get_batch()
    view_name = batch.create_view_from_last_start()
    querystr = """
      SELECT ei.id
      FROM entryintervals ei
      JOIN %(view)s en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid
      WHERE mo.class = "dataevalaebs.search_ego_maneuver.Search"
    """
    queryvars = {'view': view_name}
    q = batch.query(querystr % queryvars)
    if not q:
      raise AssertionError("no ego maneuver found")
    ids = (ei_id for ei_id, in q)
    return ids

  def analyze(self, ids):
    self.interval_table.addIntervals(ids)
    return
