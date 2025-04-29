# -*- dataeval: init -*-

import numpy as np

import datavis
from interface import iView


query_template = """
SELECT ei1.id AS ei_id,
       la1.name AS mov_state,
       qu11.value AS dx_start_exp, qu12.value AS dx_end_exp,
       qu21.value AS dx_start_fact, qu22.value AS dx_end_fact

FROM entryintervals ei1
JOIN %s en1             ON ei1.entryid = en1.id
JOIN modules mo1        ON en1.moduleid = mo1.id
JOIN measurements me1   ON en1.measurementid = me1.id

JOIN interval2label il1 ON il1.entry_intervalid = ei1.id
JOIN labels la1         ON la1.id = il1.labelid
JOIN labelgroups lg1    ON lg1.id = la1.groupid

JOIN quantities qu11 ON qu11.entry_intervalid = ei1.id
JOIN quanames qn11 ON qn11.id = qu11.nameid
JOIN quanamegroups qg11 ON qg11.id = qn11.groupid

JOIN quantities qu12 ON qu12.entry_intervalid = ei1.id
JOIN quanames qn12 ON qn12.id = qu12.nameid
JOIN quanamegroups qg12 ON qg12.id = qn12.groupid


JOIN entryintervals ei2
JOIN %s en2             ON ei2.entryid = en2.id
JOIN modules mo2        ON en2.moduleid = mo2.id
JOIN measurements me2   ON en2.measurementid = me2.id

JOIN interval2label il2 ON il2.entry_intervalid = ei2.id
JOIN labels la2         ON la2.id = il2.labelid
JOIN labelgroups lg2    ON lg2.id = la2.groupid

JOIN quantities qu21 ON qu21.entry_intervalid = ei2.id
JOIN quanames qn21 ON qn21.id = qu21.nameid
JOIN quanamegroups qg21 ON qg21.id = qn21.groupid

JOIN quantities qu22 ON qu22.entry_intervalid = ei2.id
JOIN quanames qn22 ON qn22.id = qu22.nameid
JOIN quanamegroups qg22 ON qg22.id = qn22.groupid

WHERE 
      mo1.class = "dataevalaebs.search_aeb_classif.Search"
  AND en1.title LIKE "%%expected%%"
  AND lg1.name = "moving state"
  AND qn11.name = "dx start"
  AND qn12.name = "dx end"

  AND mo2.class = "dataevalaebs.search_aeb_classif.Search"
  AND en2.title LIKE "%%factual%%"
  AND lg2.name = "moving state"
  AND qn21.name = "dx start"
  AND qn22.name = "dx end"
  
  AND MAX(ei1.start_time, ei2.start_time) <= MIN(ei1.end_time, ei2.end_time)
  
  --AND ei1.end_time - ei1.start_time > 1.0
  --AND la2.name == "stationary"

ORDER BY dx_start_fact, dx_start_exp
"""


class View(iView):
  def check(self):
    view_name = self.batch.create_table_from_last_start()
    query = query_template % (view_name, view_name)
    res = self.batch.query(query)
    assert res, "incomplete information in database"
    return res
  
  def view(self, res):
    title = "overall"
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.gca()
    ax.set_xlabel("distance [m]")
    ax.set_ylabel("#event")
    
    ei_ids = set((row[0] for row in res))
    ys = dict(zip(ei_ids, xrange(len(ei_ids))))
    
    for ei_id, mov_state, dx_start_exp, dx_end_exp, dx_start_fact, dx_end_fact in res:
      l_exp,  = ax.plot( (dx_start_exp,  dx_end_exp),  (ys[ei_id], ys[ei_id]), 'b-' )
    for ei_id, mov_state, dx_start_exp, dx_end_exp, dx_start_fact, dx_end_fact in res:
      l_fact, = ax.plot( (dx_start_fact, dx_end_fact), (ys[ei_id], ys[ei_id]), 'r-' )
    
    ax.legend([l_exp, l_fact], ["expected", "factual"])
    
    self.sync.addStaticClient(nav)
    return
