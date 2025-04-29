# -*- dataeval: init -*-

import sys

import datavis
import interface


checks_passed = """(
  exists(
    select 1
    from entries _en_
    join modules _mo_ on _mo_.id = _en_.moduleid
    where
      _mo_.class = 'dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch' and
      _en_.measurementid = %(measid_name)s
  ) and
  exists(
    select 1
    from entries _en_
    join modules _mo_ on _mo_.id = _en_.moduleid
    where
      _mo_.class = 'dataevalaebs.search_pathpred_higherror.Search' and
      _en_.measurementid = %(measid_name)s
  ) and
  exists(
    select 1
    from entries _en_
    join modules _mo_ on _mo_.id = _en_.moduleid
    where
      _mo_.class = 'dataevalaebs.search_aebs_candidates.Search' and
      _en_.measurementid = %(measid_name)s
  ) and
  exists(
    select 1
    from entries _en_
    join modules _mo_ on _mo_.id = _en_.moduleid
    where
      _mo_.class = 'dataevalaebs.search_lanes_visible.Search' and
      _en_.measurementid = %(measid_name)s
  )
)"""


qstr_all_meas_duration = """
  SELECT TOTAL(ei.end_time-ei.start_time)
  FROM entryintervals ei
  JOIN entries en         ON en.id = ei.entryid
  JOIN modules mo         ON mo.id = en.moduleid
  WHERE mo.class = "dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch"
"""
qstr_all_meas_duration_milage = """
  SELECT TOTAL(ei.end_time-ei.start_time), TOTAL(qu.value)
  FROM entryintervals ei
  JOIN entries en         ON en.id = ei.entryid
  JOIN modules mo         ON mo.id = en.moduleid
  JOIN quantities qu      ON qu.entry_intervalid = ei.id
  JOIN quanames qn        ON qn.id = qu.nameid
  WHERE mo.class = "dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch" AND
        qn.name = 'driven distance'
"""
qstr_meas_duration_milage = """
  select total(ei.end_time-ei.start_time), total(qu.value)
  from entryintervals ei
  join quantities qu on qu.entry_intervalid = ei.id
  join quanames qn on qn.id = qu.nameid
  join entries en on en.id = ei.entryid
  join modules mo on mo.id = en.moduleid
  where
    qn.name = 'driven distance' and
    mo.class = 'dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch' and
    %(checks_passed)s
""" % {'checks_passed': checks_passed % {'measid_name': 'en.measurementid'}}
qstr_higherror_duration = """
  SELECT TOTAL(ei.end_time-ei.start_time)
  FROM entryintervals ei
  JOIN entries en         ON en.id = ei.entryid
  JOIN modules mo         ON mo.id = en.moduleid
  WHERE mo.class = "dataevalaebs.search_pathpred_higherror.Search" AND
        %(checks_passed)s
""" % {'checks_passed': checks_passed % {'measid_name': 'en.measurementid'}}
qstr_higherror_lanevis_duration = """
  SELECT TOTAL(end_-st_)
  FROM (
    SELECT MAX(pperror.st, lanevis.st) st_, MIN(pperror.end, lanevis.end) end_
    FROM (
      SELECT ei.start_time st, ei.end_time end, en.measurementid me_id
      FROM entryintervals ei
      JOIN entries en         ON en.id = ei.entryid
      JOIN modules mo         ON mo.id = en.moduleid
      WHERE mo.class = "dataevalaebs.search_pathpred_higherror.Search"
    ) pperror
    JOIN (
      SELECT ei.start_time st, ei.end_time end, en.measurementid me_id
      FROM entryintervals ei
      JOIN entries en         ON en.id = ei.entryid
      JOIN modules mo         ON mo.id = en.moduleid
      WHERE mo.class = "dataevalaebs.search_lanes_visible.Search"
    ) lanevis ON pperror.me_id = lanevis.me_id AND
                 st_ < end_
    WHERE %(checks_passed)s
  )
""" % {'checks_passed': checks_passed % {'measid_name': 'pperror.me_id'}}
qstr_higherror_aebscand_duration = """
  SELECT TOTAL(end_-st_)
  FROM (
    SELECT MAX(pperror.st, aebscand.st) st_, MIN(pperror.end, aebscand.end) end_
    FROM (
      SELECT ei.start_time st, ei.end_time end, en.measurementid me_id
      FROM entryintervals ei
      JOIN entries en         ON en.id = ei.entryid
      JOIN modules mo         ON mo.id = en.moduleid
      WHERE mo.class = "dataevalaebs.search_pathpred_higherror.Search"
    ) pperror
    JOIN (
      SELECT ei.start_time st, ei.end_time end, en.measurementid me_id
      FROM entryintervals ei
      JOIN entries en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid

      JOIN quantities qu2 ON qu2.entry_intervalid = ei.id
      JOIN quanames qn2 ON qn2.id = qu2.nameid

      JOIN quantities qu3 ON qu3.entry_intervalid = ei.id
      JOIN quanames qn3 ON qn3.id = qu3.nameid

      WHERE mo.class = "dataevalaebs.search_aebs_candidates.Search" AND
            qu2.value < 1.5 AND
            qn2.name = "ttc min" AND
            qu3.value > 0.0 AND
            qn3.name = "aeb duty"
    ) aebscand ON pperror.me_id = aebscand.me_id AND
                  st_ < end_
    WHERE %(checks_passed)s
  )
""" % {'checks_passed': checks_passed % {'measid_name': 'pperror.me_id'}}
qstr_higherror_aebscandfus_duration = """
  SELECT TOTAL(end_-st_)
  FROM (
    SELECT MAX(pperror.st, aebscand.st) st_, MIN(pperror.end, aebscand.end) end_
    FROM (
      SELECT ei.start_time st, ei.end_time end, en.measurementid me_id
      FROM entryintervals ei
      JOIN entries en         ON en.id = ei.entryid
      JOIN modules mo         ON mo.id = en.moduleid
      WHERE mo.class = "dataevalaebs.search_pathpred_higherror.Search"
    ) pperror
    JOIN (
      SELECT ei.start_time st, ei.end_time end, en.measurementid me_id
      FROM entryintervals ei
      JOIN entries en ON en.id = ei.entryid
      JOIN modules mo ON mo.id = en.moduleid

      JOIN quantities qu2 ON qu2.entry_intervalid = ei.id
      JOIN quanames qn2 ON qn2.id = qu2.nameid

      JOIN quantities qu3 ON qu3.entry_intervalid = ei.id
      JOIN quanames qn3 ON qn3.id = qu3.nameid

      WHERE mo.class = "dataevalaebs.search_aebs_candidates.Search" AND
            qu2.value < 3.0 AND
            qn2.name = "ttc min" AND
            qu3.value > 0.0 AND
            qn3.name = "fused duty"
    ) aebscand ON pperror.me_id = aebscand.me_id AND
                  st_ < end_
    WHERE %(checks_passed)s
  )
""" % {'checks_passed': checks_passed % {'measid_name': 'pperror.me_id'}}

def _get_nav(title, data, labels, **kwargs):
  nav = datavis.MatplotlibNavigator(title=title)
  ax = nav.fig.add_subplot(111)
  explode = [0.05 for _ in data]
  ax.pie(data, labels=labels, autopct='%.1f%%', explode=explode, shadow=True, **kwargs)
  return nav

def get_plot_02(batch):
  title = "Lane visibility at low performance"
  higherror_lanevis_duration, = batch.query(qstr_higherror_lanevis_duration, fetchone=True)
  higherror_duration, = batch.query(qstr_higherror_duration, fetchone=True)
  data = [higherror_lanevis_duration, higherror_duration-higherror_lanevis_duration]
  labels = ['good visibility', 'untrustable lane info']
  nav = _get_nav(title, data, labels)
  return nav

def get_plot_03a(batch):
  title = "Relevant track at poor performance"
  higherror_aebscand_duration, = batch.query(qstr_higherror_aebscand_duration, fetchone=True)
  higherror_duration, = batch.query(qstr_higherror_duration, fetchone=True)
  data = [higherror_aebscand_duration, higherror_duration-higherror_aebscand_duration]
  labels = ['present', 'not present']
  nav = _get_nav(title, data, labels, colors=('r', 'g'))
  return nav

def get_plot_03b(batch):
  title = "Relevant track at poor performance"
  higherror_aebscandfus_duration, = batch.query(qstr_higherror_aebscandfus_duration, fetchone=True)
  higherror_duration, = batch.query(qstr_higherror_duration, fetchone=True)
  data = [higherror_aebscandfus_duration, higherror_duration-higherror_aebscandfus_duration]
  labels = ['present', 'not present']
  nav = _get_nav(title, data, labels, colors=('r', 'g'))
  return nav

def get_plot_04(batch):
  meas_duration, meas_milage = batch.query(qstr_meas_duration_milage, fetchone=True)
  title = "Overall performance\nDuration: %d hours, Milage: %d km" % \
    (int(meas_duration / 3600.0), int(meas_milage))
  higherror_lanevis_duration, = batch.query(qstr_higherror_lanevis_duration, fetchone=True)
  higherror_duration, = batch.query(qstr_higherror_duration, fetchone=True)
  data = [meas_duration-higherror_duration, higherror_lanevis_duration, higherror_duration-higherror_lanevis_duration]
  labels = ['decent', 'poor (improvable)', 'poor (acceptable)']
  nav = _get_nav(title, data, labels, colors=('g',(1,0,0),(0.5,0.5,0)))
  return nav


class View(interface.iView):
  def view(self):
    sync = self.get_sync()
    batch = self.get_batch()

    # print TOTAL durations and milages
    meas_duration, meas_milage = batch.query(qstr_all_meas_duration_milage, fetchone=True)
    print >> sys.stderr, "TOTAL duration: %d, milage: %d" % \
      (int(meas_duration / 3600.0), int(meas_milage))
    # print USED durations and milages
    meas_duration, meas_milage = batch.query(qstr_meas_duration_milage, fetchone=True)
    print >> sys.stderr, "USED duration: %d, milage: %d" % \
      (int(meas_duration / 3600.0), int(meas_milage))

    # create plots
#    sync.addStaticClient(get_plot_02(batch))
#    sync.addStaticClient(get_plot_03a(batch))
    sync.addStaticClient(get_plot_03b(batch))
    sync.addStaticClient(get_plot_04(batch))
    return
