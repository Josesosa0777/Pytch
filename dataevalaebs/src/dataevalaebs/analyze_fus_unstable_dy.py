import itertools

import interface
from analyze_asso_dropout_reunion import get_entryids_from_query

class cParameter(interface.iParameter):
  def __init__(self, pos_mtx, values={
                                     'ego_speed_avg_lb' : 30, # [kph]
                                     'target_dx_min_ub' : 50, # [m]
                                     'dy_error_max_lb'  : 0,  # [m]
                                     'dy_error_max_ub'  : 20,  # [m]
                                     }):
    #self.genKeys()
    self.pos_mtx = pos_mtx
    values['pos_mtx'] = pos_mtx
    self.values = values
    self.genKeys()

# instantiation of module parameters
L1 = cParameter('L1')
S1 = cParameter('S1')
R1 = cParameter('R1')
L2 = cParameter('L2')
S2 = cParameter('S2')
R2 = cParameter('R2')

entry_id = {'select_stmt' : 'SELECT DISTINCT query_fus_dy.en_id',
            'where_stmt' : ''}

position = {'select_stmt' : 'SELECT DISTINCT query_fus_dy.ei_pos',
            'where_stmt' : 'WHERE query_fus_dy.en_id = ?'}

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
        mo.class = "dataevalaebs.search_fus_unstable_dy.cSearch"
  ) query_fus_dy
JOIN (
  SELECT ei.id ei_id
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE qng.name = "ego vehicle" AND
        qn.name = "speed" AND
        q.value > %(ego_speed_avg_lb)s
  ) query_ego_speed ON query_fus_dy.ei_id = query_ego_speed.ei_id
JOIN (
  SELECT ei.id ei_id
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE qng.name = "target" AND
        qn.name = "dx min" AND
        q.value < %(target_dx_min_ub)s
  ) query_target_distance ON query_fus_dy.ei_id = query_target_distance.ei_id
JOIN (
  SELECT ei.id ei_id, q.value dy_error_max
  FROM entryintervals ei
  JOIN quantities q      ON ei.id = q.entry_intervalid
  JOIN quanames qn       ON qn.id = q.nameid
  JOIN quanamegroups qng ON qn.groupid = qng.id
  WHERE qng.name = "target" AND
        qn.name = "dy error max" AND
        q.value BETWEEN %(dy_error_max_lb)s AND %(dy_error_max_ub)s
  ) query_dy_error ON query_fus_dy.ei_id = query_dy_error.ei_id
JOIN (
  SELECT en.id en_id, ei.id ei_id, ei.start, ei.end, la.name la_name, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN interval2label il2 ON ei.id = il2.entry_intervalid
  JOIN labels la2         ON il2.labelid = la2.id
  JOIN labelgroups lg2    ON la2.groupid = lg2.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE lg.name = "OHY object" AND
        lg2.name = "moving direction" AND
        la2.name != "oncoming" AND
        mo.class = "dataevalaebs.search_cvr3_ohy_pos.cSearch" AND
        mo.param = "posname=%(pos_mtx)s"
  ) query_s1 ON query_fus_dy.me_id = query_s1.me_id AND
              query_fus_dy.la_name = query_s1.la_name AND
              MAX(query_fus_dy.start, query_s1.start) < MIN(query_fus_dy.end, query_s1.end)
%(where_stmt)s
;
"""


class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    entry_id.update(param.values)
    position.update(param.values)
    query_pos = QUERY_TEMPLATE % position
    query_ids = QUERY_TEMPLATE % entry_id
    interface.BatchNav.BatchFrame.query = query_pos
    entryids = get_entryids_from_query(interface.Batch, query_ids)
    interface.BatchNav.BatchFrame.addEntries(entryids)
    return
