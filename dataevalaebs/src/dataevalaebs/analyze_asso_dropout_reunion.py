# -*- dataeval: call -*-

import itertools

import interface

class cParameter(interface.iParameter):
  def __init__(self, pos_mtx, moving_state):
    self.values = {'moving_state'  : moving_state,
                   'pos_mtx'       : pos_mtx,
                   'ego_speed_avg_lb' : 30, # [kph]
                   'target_dx_min_ub' : 50, # [m]
                  }
    self.genKeys()
    return

call_params = {
  'S1_stationary' : dict(pos_mtx='S1', moving_state='stationary'),
  'S1_moving'     : dict(pos_mtx='S1', moving_state='moving'),
}

entry_id = {'select_stmt' : 'SELECT DISTINCT query_reunion.en_id, query_breakup_reason.en_id',
            'where_stmt' : ''}

position = {'select_stmt' : 'SELECT DISTINCT query_reunion.ei_pos',
            'where_stmt' : 'WHERE query_reunion.en_id = ?'}

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
  WHERE lg.name = "OHY object" AND
        mo.class = "dataevalaebs.search_asso_dropout_reunion.cSearch"
  ) query_reunion
JOIN (
  SELECT ei.id ei_id
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE qng.name = "ego vehicle" AND
        qn.name = "speed" AND
        q.value > %(ego_speed_avg_lb)s
  ) query_ego_speed ON query_reunion.ei_id = query_ego_speed.ei_id
JOIN (
  SELECT ei.id ei_id
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE qng.name = "target" AND
        qn.name = "dx min" AND
        q.value < %(target_dx_min_ub)s
  ) query_target_distance ON query_reunion.ei_id = query_target_distance.ei_id
JOIN (
  SELECT en.id en_id, ei.id ei_id, ei.start, ei.end, la.name la_name, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE lg.name = "OHY object" AND
        mo.class = "dataevalaebs.search_cvr3_ohy_pos.cSearch" AND
        mo.param = "posname=%(pos_mtx)s"
  ) query_s1 ON query_reunion.me_id = query_s1.me_id AND
              query_reunion.la_name = query_s1.la_name AND
              MAX(query_reunion.start, query_s1.start) < MIN(query_reunion.end, query_s1.end)
JOIN (
  SELECT en.id en_id, ei.id ei_id, ei.start, ei.end, la.name la_name, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE lg.name = "moving state" AND
        la.name = "%(moving_state)s" AND
        mo.class = "dataevalaebs.search_asso_breakup_reason.cSearch"
  ) query_breakup_reason ON query_reunion.me_id = query_breakup_reason.me_id AND
                            query_reunion.start = query_breakup_reason.end
%(where_stmt)s
;
"""

def get_entryids_from_query(db, query):
  q = db.query(query)
  ids = set( itertools.chain.from_iterable(q) )
  return ids

class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    entry_id.update(param.values)
    position.update(param.values)
    query_pos = QUERY_TEMPLATE % position
    query_ids = QUERY_TEMPLATE % entry_id
    interface.BatchNav.BatchFrame.queryEdit.setText(query_pos)
    interface.BatchNav.BatchFrame.editQuery()
    entryids = get_entryids_from_query(interface.Batch, query_ids)
    interface.BatchNav.BatchFrame.addEntries(entryids)
    return
