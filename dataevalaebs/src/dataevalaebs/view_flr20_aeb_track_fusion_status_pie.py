# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView

fusion_st_query = """
SELECT SUM(ei.end_time - ei.start_time) / 3600. AS sum_duration
FROM entryintervals ei
JOIN interval2label il ON ei.id = il.entry_intervalid
JOIN labels la         ON il.labelid = la.id
JOIN labelgroups lg    ON la.groupid = lg.id
JOIN entries en        ON ei.entryid = en.id
JOIN modules mo        ON en.moduleid = mo.id
WHERE lg.name = "asso state" AND
      la.name = :asso_state AND
      mo.class = "dataevalaebs.search_flr20_aeb_track_fusion_status.SearchFlr20AebTrack"
;
"""

driven_dist_query = """
SELECT SUM(q.value) AS sum_distance
FROM entryintervals ei
JOIN interval2label il ON ei.id = il.entry_intervalid
JOIN entries en        ON ei.entryid = en.id
JOIN modules mo        ON en.moduleid = mo.id
JOIN quantities q      ON ei.id = q.entry_intervalid
JOIN quanames qn       ON qn.id = q.nameid
JOIN quanamegroups qng ON qn.groupid = qng.id
WHERE qng.name = 'ego vehicle'    AND
      qn.name = 'driven distance' AND
      mo.class = "dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch"
;
"""

driven_time_query = """
SELECT SUM(ei.end_time - ei.start_time) / 3600. AS sum_time_hours
FROM entryintervals ei
JOIN entries en        ON ei.entryid = en.id
JOIN modules mo        ON en.moduleid = mo.id
WHERE mo.class = "dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch"
;
"""

titlestr = """
FLR20 AEB track fusion status in endurance drive
driven time: %s h, distance: %s km
AEB track available: %s h
"""

def float_query_res_to_str(res, fmt='%.0f'):
  return 'n/a' if res is None else fmt % res

class View(iView):
  def check(self):
    fused,      = self.batch.query(fusion_st_query, asso_state="fused")[0]
    radar_only, = self.batch.query(fusion_st_query, asso_state="radar only")[0]
    assert fused or radar_only, "incomplete information in database"
    driven_dist, = self.batch.query(driven_dist_query)[0]
    driven_time, = self.batch.query(driven_time_query)[0]
    return fused, radar_only, driven_dist, driven_time

  def view(self, fused, radar_only, driven_dist, driven_time):
    driven_dist_str = float_query_res_to_str(driven_dist)
    driven_time_str = float_query_res_to_str(driven_time)
    aeb_available = float_query_res_to_str(fused + radar_only)
    title = titlestr %(driven_time_str, driven_dist_str, aeb_available)
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.gca()
    x = np.array( [fused, radar_only] )
    labels = ['fused', 'radar only']
    explode = [0.05 for _ in x]
    patches, texts, autotexts = ax.pie(x, labels=labels, autopct='%.1f%%',
      explode=explode, shadow=True, colors=['g','r'])
    for text in autotexts:
      text.set_color('w')
    self.get_sync().addStaticClient(nav)
    return
