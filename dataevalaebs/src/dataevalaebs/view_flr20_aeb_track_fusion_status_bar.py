# -*- dataeval: init -*-

from collections import OrderedDict

import numpy as np

import datavis
from interface import iView
from view_flr20_aeb_track_fusion_status_pie import titlestr, driven_dist_query, float_query_res_to_str

fusion_st_query = """
SELECT date(me.start, '-5 hour') days, SUM(ei.end_time - ei.start_time) / 3600. AS hours
FROM entryintervals ei
JOIN interval2label il ON ei.id = il.entry_intervalid
JOIN labels la         ON il.labelid = la.id
JOIN labelgroups lg    ON la.groupid = lg.id
JOIN entries en        ON ei.entryid = en.id
JOIN modules mo        ON en.moduleid = mo.id
JOIN measurements me   ON en.measurementid = me.id
WHERE lg.name = "asso state" AND
      la.name = :asso_state AND
      mo.class = "dataevalaebs.search_flr20_aeb_track_fusion_status.SearchFlr20AebTrack"
GROUP BY days
;
"""

driven_time_query = """
SELECT date(me.start, '-5 hour') days, SUM(ei.end_time - ei.start_time) / 3600. AS hours
FROM entryintervals ei
JOIN entries en        ON ei.entryid = en.id
JOIN measurements me   ON en.measurementid = me.id
JOIN modules mo        ON en.moduleid = mo.id
WHERE mo.class = "dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch"
GROUP BY days
;
"""

titlestr = """
FLR20 AEB track fusion status in endurance drive
driven time: %s h, distance: %s km
"""

def prepare_values(values, days):
  return np.array( [values[day] if day in values else 0. for day in days] )

class View(iView):
  def check(self):
    fused = OrderedDict( self.batch.query(fusion_st_query, asso_state="fused") )
    radar_only = OrderedDict( self.batch.query(fusion_st_query, asso_state="radar only") )
    assert fused or radar_only, "incomplete information in database"
    driven_dist_sum, = self.batch.query(driven_dist_query)[0]
    driven_time = OrderedDict( self.batch.query(driven_time_query) )
    return fused, radar_only, driven_time, driven_dist_sum

  def view(self, fused, radar_only, driven_time, driven_dist_sum):
    # prepare title
    driven_time_sum = np.sum( driven_time.values() )
    driven_dist_str = float_query_res_to_str(driven_dist_sum)
    driven_time_str = float_query_res_to_str(driven_time_sum)
    title = titlestr %(driven_time_str, driven_dist_str)
    # perpare domain data
    unique_days = set( driven_time.iterkeys() )
    unique_days.update(  fused.iterkeys() )
    unique_days.update(  radar_only.iterkeys() )
    days = sorted(unique_days)
    x = np.arange( len(days) )
    # perpare values
    fused_v       = prepare_values(fused,       days)
    radar_only_v  = prepare_values(radar_only,  days)
    driven_time_v = prepare_values(driven_time, days)
    driven_time_v -= fused_v + radar_only_v
    # create navigator and axis
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.gca()
    # plot bar chart
    width = .5
    half_width = width/2.
    bar_driven_time = ax.bar(x, driven_time_v, width, color='LightGray', linewidth=0)
    bar_fused       = ax.bar(x, fused_v,       width, color='g',         linewidth=0, bottom=driven_time_v)
    bar_radar_only  = ax.bar(x, radar_only_v,  width, color='r',         linewidth=0, bottom=driven_time_v+fused_v)
    # labels and legend
    ax.set_ylabel('hours')
    ax.set_xticks(x+half_width)
    ax.set_xticklabels(days, rotation=40, horizontalalignment='right')
    ax.set_xlim(x[0]-half_width, x[-1]+width+half_width)
    leg = ax.legend( (bar_radar_only[0], bar_fused[0], bar_driven_time[0]),
               ('radar-only', 'fused', 'no AEB track') )
    leg.draggable(True)
    leg.get_frame().set_alpha(.5)
    # register client for static synchronization
    self.get_sync().addStaticClient(nav)
    return
