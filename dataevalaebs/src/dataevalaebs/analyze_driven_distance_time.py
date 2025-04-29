# -*- dataeval: init -*-

"""
Sum up the driven distance [km] and time [h] using result of the script 
"dataevalaebs.searchAEBSWarnEval_RoadTypes". Duplicate runs of the search script 
on the same measurement are not considered, only the latest run.
"""

from interface.Interfaces import iAnalyze

init_params = {
  'all': dict(date=None, start_date=None, end_date=None)
}

class Analyze(iAnalyze):
  def init(self, date, start_date, end_date):
    self.date = date
    self.start_date = start_date
    self.end_date = end_date
    return

  def check(self):
    view_name = self.batch.create_table_from_last_entries(
                             date=self.date,
                             start_date=self.start_date,
                             end_date=self.end_date)

    dist, time = self.batch.query("""
      SELECT SUM(q.value) AS distance_km, SUM(ei.end_time - ei.start_time) / 3600. AS time_hours
      FROM entryintervals ei
      JOIN %s en             ON ei.entryid = en.id
      JOIN modules mo        ON en.moduleid = mo.id
      JOIN quantities q      ON ei.id = q.entry_intervalid
      JOIN quanames qn       ON qn.id = q.nameid
      JOIN quanamegroups qng ON qn.groupid = qng.id
      WHERE mo.class = :class_name      AND
            qng.name = :quanames_name   AND
            qn.name = :quantities_name
      """ % view_name,
      class_name='dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch',
      quanames_name='ego vehicle',
      quantities_name='driven distance',
      fetchone=True
    )
    if dist is None or time is None:
      raise AssertionError("Driven distance or time cannot be queried")
    return dist, time

  def analyze(self, dist, time):
    self.logger.info(
      'Driven distance: %.1f km, driven time: %.1f h' % (dist, time))
    return
