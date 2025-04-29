# -*- dataeval: init -*-

import numpy as np
import matplotlib as mpl

import datavis
from interface import iView

init_params = { 'stationary' : {'mov_state':'stationary'},
                'moving'     : {'mov_state':'moving'},
}

aeb_dropout_reunion_query = """
SELECT DISTINCT dropout_subquery.ei_id, dropout_subquery.end - dropout_subquery.start AS cycles
FROM (
  SELECT en.id en_id, ei.id ei_id, ei.position ei_pos, ei.start, ei.end, ei.start_time, ei.end_time, la.name la_name, en.measurementid me_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE lg.name = "AC100 track" AND
        mo.class = "dataevalaebs.search_asso_dropout_reunion_flr20.SearchFlr20AssoReunion"
  ) dropout_subquery
JOIN (
  SELECT ei.id ei_id
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  WHERE     lg.name = "moving state"
        AND la.name = :mov_state
  ) mov_state_subquery ON dropout_subquery.ei_id = mov_state_subquery.ei_id
JOIN (
  SELECT en.measurementid me_id, la.name la_name, ei.start_time, ei.end_time
  FROM entryintervals ei
  JOIN interval2label il ON ei.id = il.entry_intervalid
  JOIN labels la         ON il.labelid = la.id
  JOIN labelgroups lg    ON la.groupid = lg.id
  JOIN entries en        ON ei.entryid = en.id
  JOIN modules mo        ON en.moduleid = mo.id
  WHERE lg.name = "AC100 track" AND
        mo.class = "dataevalaebs.search_flr20_aeb_track.SearchFlr20aebTrack"
  ) aeb_subquery ON
                    dropout_subquery.me_id = aeb_subquery.me_id AND
                    dropout_subquery.la_name = aeb_subquery.la_name AND
                    MAX(dropout_subquery.start_time, aeb_subquery.start_time) <= MIN(dropout_subquery.end_time, aeb_subquery.end_time)
;
"""

class View(iView):
  def init(self, mov_state):
    self.mov_state = mov_state
    return

  def check(self):
    # query from db
    dropouts = self.batch.query(aeb_dropout_reunion_query, mov_state=self.mov_state)
    # convert to 1D array
    assert dropouts, 'Empty dropouts'
    dropouts  = np.array(dropouts)[:,1]
    assert dropouts.size, "incomplete information in database"
    return dropouts

  def view(self, x):
    titlestr = """
    FLR20 AEB track fusion dropout-reunion in detection cycles (below 100m)
    %d events, %s object
    """
    title = titlestr %(x.size, self.mov_state.upper())
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.gca()
    bins = [1,2,5,20,50,100]
    max_bin = np.max(x)
    if max_bin <= bins[-1]:
      max_bin = bins[-1] + 1
    bins.append(max_bin)
    # levels
    names = ('single', 'light', 'moderate', 'significant', 'long', 'extreme')
    edges = [ '(%d-%d)'%(st,end-1) for st,end in zip(bins, bins[1:]) ]
    edges[0] = '(%d)' %bins[0]
    labels = [ '%s %s' %(name,edge) for name,edge in zip(names,edges) ]
    # calculate histogram
    hist, bin_edges = np.histogram(x, bins=bins)
    # cut zero values from the end of the array
    nonzeros, = hist.nonzero()
    last_nonzero_idx = nonzeros[-1]
    idx = last_nonzero_idx + 1
    # color map
    cm = mpl.cm.get_cmap(name='RdYlGn')
    colors = [ cm(i) for i in np.linspace(0,1,hist.size)[::-1] ]
    explode = [0.05 for _ in hist]
    ax.pie(hist[:idx], labels=labels[:idx], autopct='%.1f%%', explode=explode[:idx], shadow=True, colors=colors[:idx])
    self.get_sync().addStaticClient(nav)
    return
