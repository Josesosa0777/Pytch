# -*- dataeval: init -*-

import interface
from analyze_asso_dropout_reunion import get_entryids_from_query

entry_id = {'select_stmt' : 'SELECT DISTINCT late_subquery.en_id',
            'where_stmt' : ''}

position = {'select_stmt' : 'SELECT DISTINCT late_subquery.ei_pos',
            'where_stmt' : 'WHERE late_subquery.en_id = ?'}

QUERY_TEMPLATE = """
%(select_stmt)s
FROM (
  SELECT en.id en_id, ei.id ei_id, ei.position ei_pos, ei.start, ei.end, la.name la_name, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE     mo.class = "dataevalaebs.search_asso_late_flr20.SearchFlr20AssoLate"
        AND lg.name = "AC100 track"
        AND ei.end - ei.start > 10
  ) late_subquery
JOIN (
  SELECT ei.id ei_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "asso problem"
        AND la.name = "late"
  ) late_2_subquery ON late_subquery.ei_id = late_2_subquery.ei_id
JOIN (
  SELECT ei.id ei_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "moving state"
        AND la.name = "stationary"
  ) mov_state_subquery ON late_subquery.ei_id = mov_state_subquery.ei_id
JOIN (
  SELECT en.id en_id, en.measurementid me_id, la.name la_name, ei.start, ei.end
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE lg.name = "AC100 track" AND
        mo.class = "dataevalaebs.search_flr20_aeb_track.SearchFlr20aebTrack"
  ) aeb_subquery ON
                    late_subquery.me_id = aeb_subquery.me_id AND
                    late_subquery.la_name = aeb_subquery.la_name AND
                    MAX(late_subquery.start, aeb_subquery.start) < MIN(late_subquery.end, aeb_subquery.end)
%(where_stmt)s
;
"""

class cAnalyze(interface.iAnalyze):
  def analyze(self):
    query_pos = QUERY_TEMPLATE % position
    query_ids = QUERY_TEMPLATE % entry_id
    interface.BatchNav.BatchFrame.queryEdit.setText(query_pos)
    interface.BatchNav.BatchFrame.editQuery()
    entryids = get_entryids_from_query(interface.Batch, query_ids)
    interface.BatchNav.BatchFrame.addEntries(entryids)
    return
