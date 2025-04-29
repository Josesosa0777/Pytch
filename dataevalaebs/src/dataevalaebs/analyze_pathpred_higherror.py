# -*- dataeval: init -*-

from interface.Interfaces import iAnalyze

CREATE_VIEW = False

init_params = {
  "detailed": dict(query_alias='detailed'),
  "critical": dict(query_alias='critical'),
}

queries = {
  'detailed': """
    SELECT DISTINCT pperror.ei_id
    FROM (
      SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id
      FROM entryintervals ei
      JOIN %(view)s en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid

      JOIN quantities qu1 ON qu1.entry_intervalid = ei.id
      JOIN quanames qn1 ON qn1.id = qu1.nameid
      JOIN quanamegroups qg1 ON qg1.id = qn1.groupid

      JOIN quantities qu2 ON qu2.entry_intervalid = ei.id
      JOIN quanames qn2 ON qn2.id = qu2.nameid
      JOIN quanamegroups qg2 ON qg2.id = qn2.groupid

      WHERE mo.class = "dataevalaebs.search_pathpred_higherror.Search" AND
            qn1.name = "rms error avg" AND
            qg1.name = "path prediction" AND
            qn2.name = "other rms error avg" AND
            qg2.name = "path prediction" AND
            qu1.value - qu2.value > 0.5
    ) pperror
    JOIN (
      SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id
      FROM entryintervals ei
      JOIN %(view)s en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid

      JOIN quantities qu1 ON qu1.entry_intervalid = ei.id
      JOIN quanames qn1 ON qn1.id = qu1.nameid
      JOIN quanamegroups qg1 ON qg1.id = qn1.groupid

      JOIN quantities qu2 ON qu2.entry_intervalid = ei.id
      JOIN quanames qn2 ON qn2.id = qu2.nameid
      JOIN quanamegroups qg2 ON qg2.id = qn2.groupid

      JOIN quantities qu3 ON qu3.entry_intervalid = ei.id
      JOIN quanames qn3 ON qn3.id = qu3.nameid
      JOIN quanamegroups qg3 ON qg3.id = qn3.groupid

      WHERE mo.class = "dataevalaebs.search_aebs_candidates.Search" AND
            qu1.value > 0.5 AND
            qn1.name = "confidence avg" AND
            qg1.name = "target" AND
            qu2.value < 1.5 AND
            qn2.name = "ttc min" AND
            qg2.name = "target" AND
            qu3.value > 0.5 AND
            qn3.name = "aeb duty" AND
            qg3.name = "target"
    ) aebscand ON pperror.me_id = aebscand.me_id AND
                  MAX(pperror.start_time, aebscand.start_time) <=
                    MIN(pperror.end_time, aebscand.end_time)
  """,
  'critical': """
    SELECT DISTINCT pperror.ei_id
    FROM (
      SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id
      FROM entryintervals ei
      JOIN %(view)s en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid

      JOIN quantities qu1 ON qu1.entry_intervalid = ei.id
      JOIN quanames qn1 ON qn1.id = qu1.nameid
      JOIN quanamegroups qg1 ON qg1.id = qn1.groupid

      WHERE mo.class = "dataevalaebs.search_pathpred_higherror.Search" AND
            qn1.name = "rms error avg" AND
            qg1.name = "path prediction" AND
            qu1.value > 1.5
    ) pperror
    JOIN (
      SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id
      FROM entryintervals ei
      JOIN %(view)s en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid

      JOIN quantities qu2 ON qu2.entry_intervalid = ei.id
      JOIN quanames qn2 ON qn2.id = qu2.nameid
      JOIN quanamegroups qg2 ON qg2.id = qn2.groupid

      WHERE mo.class = "dataevalaebs.search_aebs_candidates.Search" AND
            qu2.value < 3.0 AND
            qn2.name = "ttc min" AND
            qg2.name = "target" AND
    ) aebscand ON pperror.me_id = aebscand.me_id AND
                  MAX(pperror.start_time, aebscand.start_time) <=
                    MIN(pperror.end_time, aebscand.end_time)
    JOIN (
      SELECT ei.id ei_id, ei.start_time, ei.end_time, en.measurementid me_id
      FROM entryintervals ei
      JOIN %(view)s en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid
      WHERE mo.class = "dataevalaebs.search_lanes_visible.Search"
    ) lanesvis ON pperror.me_id = lanesvis.me_id AND
                  MAX(pperror.start_time, lanesvis.start_time) <=
                    MIN(pperror.end_time, lanesvis.end_time)
  """,
}

class Analyze(iAnalyze):
  def init(self, query_alias):
    ###
    assert query_alias != 'critical', "'%s' query shall be corrected"  # TODO:
    ###
    self.query_str = queries[query_alias]
    return

  def check(self):
    batch = self.get_batch()
    view_name=batch.create_view_from_last_start() if CREATE_VIEW else 'entries'
    queryvars = {'view': view_name}
    q = batch.query(self.query_str % queryvars)
    if not q:
      raise AssertionError("no path prediction defect found")
    ids = (ei_id for ei_id, in q)
    return ids

  def analyze(self, ids):
    self.interval_table.addIntervals(ids)
    return
