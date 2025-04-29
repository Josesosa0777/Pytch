# -*- dataeval: init -*-

from collections import OrderedDict
from itertools import chain

import numpy as np

import datavis
from datavis.figlib import argbalance
from interface import iView

init_params = {
  'all-pie' : dict(strftime='%Y',         groupby=''  , bar_chart=False),
  'all'     : dict(strftime='%Y',         groupby=''  , bar_chart=True),
  'monthly' : dict(strftime='%Y-%m',      groupby=',d', bar_chart=True),
  'weekly'  : dict(strftime='%Y-%m cw%W', groupby=',d', bar_chart=True),
  'daily'   : dict(strftime='%Y-%m-%d',   groupby=',d', bar_chart=True),
}

COLORS = [
[ 0.26934241,  0.79392134,  0.55217339],
[ 0.31008455,  0.92022359,  0.3375122 ],
[ 0.86035765,  0.18680039,  0.90128836],
[ 0.76324535,  0.15428571,  0.46919477],
[ 0.39837875,  0.98431794,  0.58291856],
[ 0.18861715,  0.24115182,  0.92536528],
[ 0.39808074,  0.75133482,  0.02371207],
[ 0.72759373,  0.34523599,  0.84995019],
[ 0.96320521,  0.00447975,  0.96505673],
[ 0.9987296 ,  0.81457375,  0.28137345],
[ 0.15891058,  0.44312221,  0.95102927],
[ 0.84494178,  0.20652189,  0.35368808],
[ 0.14796536,  0.19208111,  0.89832519],
[ 0.67872124,  0.04378053,  0.75685853],
[ 0.5996534 ,  0.00648268,  0.87056605],
]



def flush_print(msg):
  import sys
  print >> sys.stderr, msg
  sys.stderr.flush()
  return

warning_query_template = """
SELECT classif.la_name class_, strftime('%(strftime)s', me.start) d, COUNT(*) cnt
FROM %(entries)s en
JOIN entryintervals ei ON ei.entryid = en.id

JOIN modules mo ON mo.id = en.moduleid
JOIN measurements me ON me.id = en.measurementid

JOIN (
  SELECT algo_i2l.entry_intervalid ei_id, algo_la.name la_name, algo_lg.name lg_name
  FROM interval2label algo_i2l
  JOIN labels algo_la ON algo_la.id = algo_i2l.labelid
  JOIN labelgroups algo_lg ON algo_lg.id = algo_la.groupid
) algo ON algo.ei_id = ei.id
      AND algo.lg_name = "AEBS algo" AND algo.la_name = "FLR20 Warning"

LEFT JOIN (
  SELECT classif_i2l.entry_intervalid ei_id, classif_la.name la_name, classif_lg.name lg_name
  FROM interval2label classif_i2l
  JOIN labels classif_la ON classif_la.id = classif_i2l.labelid
  JOIN labelgroups classif_lg ON classif_lg.id = classif_la.groupid
) classif ON classif.ei_id = ei.id
         AND classif.lg_name = "%(classif)s"

WHERE mo.class = "dataevalaebs.search_aebs_warning.Search"
  AND strftime('%%Y-%%m-%%d', me.start) != "2013-11-26"

  AND NOT EXISTS (
    SELECT *
    FROM %(entries)s en_2
    JOIN entryintervals ei_2 ON ei_2.entryid = en_2.id

    JOIN interval2label algo_i2l_2 ON algo_i2l_2.entry_intervalid = ei_2.id
    JOIN labels algo_la_2 ON algo_la_2.id = algo_i2l_2.labelid
    JOIN labelgroups algo_lg_2 ON algo_lg_2.id = algo_la_2.groupid

    WHERE en_2.id = en.id
      AND algo_lg_2.name = "AEBS algo" AND algo_la_2.name = "FLR20 Warning"
      AND ei.start_time-ei_2.end_time BETWEEN 0 AND 2
  )
GROUP BY class_ %(groupby)s
"""

dist_dur_query = """
SELECT TOTAL(qu.value), TOTAL(ei.end_time-ei.start_time)/3600
FROM %s en
JOIN entryintervals ei ON ei.entryid = en.id

JOIN quantities qu ON qu.entry_intervalid = ei.id

JOIN modules mo1 ON mo1.id = en.moduleid

WHERE mo1.class = "dataevalaebs.searchAEBSWarnEval_RoadTypes.cSearch"
  AND en.measurementid IN (
    SELECT en2.measurementid
    FROM %s en2
    JOIN modules mo2 ON mo2.id = en2.moduleid
    WHERE mo2.class = "dataevalaebs.search_aebs_warning.Search"
      AND mo2.param LIKE "algo='FLR20 Warning'%%"
  )
"""


#classif_name = "moving state"
#classif_name = "false warning cause"
#classif_name = "AEBS event rating scale"
#classif_name = "AEBS cascade phase"
classif_name = "KB AEBS suppression phase"


# TODO: improve interval join
warning_trwsupp_query_template = """
SELECT classif.la_name class_, strftime('%(strftime)s', me.start) d, COUNT(*) cnt
FROM %(entries)s en
JOIN entryintervals ei ON ei.entryid = en.id

JOIN modules mo ON mo.id = en.moduleid
JOIN measurements me ON me.id = en.measurementid

JOIN (
  SELECT algo_i2l.entry_intervalid ei_id, algo_la.name la_name, algo_lg.name lg_name
  FROM interval2label algo_i2l
  JOIN labels algo_la ON algo_la.id = algo_i2l.labelid
  JOIN labelgroups algo_lg ON algo_lg.id = algo_la.groupid
) algo ON algo.ei_id = ei.id
      AND algo.lg_name = "AEBS algo" AND algo.la_name = "FLR20 Warning"

JOIN (
  SELECT supp_i2l.entry_intervalid ei_id, supp_la.name la_name, supp_lg.name lg_name
  FROM interval2label supp_i2l
  JOIN labels supp_la ON supp_la.id = supp_i2l.labelid
  JOIN labelgroups supp_lg ON supp_lg.id = supp_la.groupid
) supp ON supp.ei_id = ei.id
      AND supp.lg_name = "KB AEBS suppression phase" AND supp.la_name != "cancelled"

LEFT JOIN (
  SELECT classif_i2l.entry_intervalid ei_id, classif_la.name la_name, classif_lg.name lg_name
  FROM interval2label classif_i2l
  JOIN labels classif_la ON classif_la.id = classif_i2l.labelid
  JOIN labelgroups classif_lg ON classif_lg.id = classif_la.groupid
) classif ON classif.ei_id = ei.id
         AND classif.lg_name = "%(classif)s"

WHERE mo.class = "dataevalaebs.search_aebs_warning.Search"
  AND strftime('%%Y-%%m-%%d', me.start) != "2013-11-26"

  AND NOT EXISTS (
    SELECT *
    FROM %(entries)s en_2
    JOIN entryintervals ei_2 ON ei_2.entryid = en_2.id

    JOIN interval2label algo_i2l_2 ON algo_i2l_2.entry_intervalid = ei_2.id
    JOIN labels algo_la_2 ON algo_la_2.id = algo_i2l_2.labelid
    JOIN labelgroups algo_lg_2 ON algo_lg_2.id = algo_la_2.groupid

    WHERE en_2.id = en.id
      AND algo_lg_2.name = "AEBS algo" AND algo_la_2.name = "FLR20 Warning"
      AND ei.start_time-ei_2.end_time BETWEEN 0 AND 2
  )
GROUP BY class_ %(groupby)s
"""

meas_days_query = """
SELECT DISTINCT date(me.start, '-4 hour') as days
-- 4 hours minus to unify recordings after midnight with start day
FROM measurements me
JOIN entries en ON en.measurementid = me.id
JOIN modules mo ON en.moduleid = mo.id
WHERE mo.class = "dataevalaebs.search_aebs_warning.Search" --avoid later updates
ORDER BY days ASC;
"""

titlestr = """
False AEBS warnings on endurance drive
(between %s and %s)
"""
# total: %s days, %.0f hours


class View(iView):
  def init(self, strftime, groupby, bar_chart):
    self.strftime = strftime
    self.groupby = groupby
    self.bar_chart = bar_chart

    if classif_name == "moving state":
      self.colors = OrderedDict(
        (
          (u'moving',       'g'),
          (u'stopped',      'b'),
          (u'stationary',   'r'),
          (u'unclassified', 'k'),
        )
      )
    elif classif_name == "false warning cause":
      self.colors = OrderedDict(
        (
          (u'bridge', 'g'),
          (u'tunnel', 'b'),
          (u'infrastructure', 'r'),
          (u'parking car', 'k'),
          (u'road exit', 'g'),
          (u'high curvature', 'b'),
          (u'traffic island', 'r'),
          (u'approaching curve', 'k'),
          (u'straight road', 'g'),
          (u'construction site', 'b'),
          (u'braking fw vehicle', 'r'),
          (u'overtaking', 'k'),
          (u'passing by', 'g'),
          (u'sharp turn', 'b'),
          (u'overhead sign', 'r'),
          (u'crossing traffic', 'k'),
        )
      )
    elif classif_name == "AEBS event rating scale":
      self.colors = OrderedDict(
        (
          (u'1-False alarm', 'r'),
          (u'2-Questionable false alarm', 'm'),
          (u'3-Questionable', 'b'),
          (u'4-Questionable mitigation', 'y'),
          (u'5-Mitigation', 'g'),
        )
      )
    elif classif_name == "AEBS cascade phase" or classif_name == "KB AEBS suppression phase":
      self.colors = OrderedDict(
        (
          (u'warning',           'g'),
          (u'partial braking',   'y'),
          (u'emergency braking', 'r'),
        )
      )
    self.def_color = 'c'

    if classif_name == "false warning cause":
      max_color = 0xFFFFFF
      num_colors = len(self.colors)
      for i, (class_, clr) in enumerate(self.colors.iteritems()):
  #      new_clr = int(float(max_color) / num_colors * i)
  #      new_clr = np.random.randint(0, max_color)
  #      self.colors[class_] = "#%06X" % new_clr
        self.colors[class_] = COLORS[i % len(COLORS)]
    return

  def check(self):
    view_name = self.batch.create_table_from_last_entries()
    dd = {
      'strftime': self.strftime,
      'entries': view_name,
      'classif': classif_name,
      'groupby': self.groupby,
    }
#    warning_query = warning_trwsupp_query_template % dd
    warning_query = warning_query_template % dd
    res = self.batch.query(warning_query)
    meas_days = list( chain.from_iterable( self.batch.query(meas_days_query) ) )
    dist_dur = self.batch.query(dist_dur_query % (view_name, view_name))

    print 'dist_hours_days:', dist_dur, len(meas_days)

    assert res and meas_days, "incomplete information in database"
    return res, meas_days

  def fill(self, res, meas_days):
    unique_dates = None
    if self.bar_chart:
      dataset = {} # { status<str> : portions<ndarray> }
      unique_dates = sorted( set(date for status, date, portion in res) )
      indices = dict( (date, unique_dates.index(date)) for date in unique_dates)
      xsize = len(unique_dates)
      for status, date, portion in res:
        if status not in dataset:
          dataset[status] = np.zeros(xsize)
        arr = dataset[status]
        i = indices[date]
        arr[i] = portion
    else:
      # { status<str> : portion<float> }
      dataset = dict( (status, portion) for status, date, portion in res )
    num_days = len(meas_days)
    first_day = meas_days[0]
    last_day  = meas_days[-1]
    driven_time = np.sum( portion for status, date, portion in res )
    title = titlestr %(first_day, last_day)

    ###
    print dataset
    ###

    return dataset, unique_dates, title

  def view(self, dataset, unique_dates, title):
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.gca()
    if self.bar_chart:
      self.plot_bar_chart(ax, dataset, unique_dates)
    else:
      self.plot_pie_chart(ax, dataset)
    self.get_sync().addStaticClient(nav)
    return

  def plot_bar_chart(self, ax, dataset, unique_dates):
    x = np.arange( len(unique_dates) )
    width = .5
    half_width = width/2.
    # status stacked bar ordering
    for status in dataset:
      if status not in self.colors:
        self.colors[status] = self.def_color
    # plotting
    bottom = np.zeros(x.size)
    bars = []
    for status in self.colors:
      if status in dataset:
        arr = dataset[status]
      else:
        arr = np.zeros( len(unique_dates) )
      bar = ax.bar(x, arr, width, color=self.colors[status], linewidth=0, bottom=bottom)
      bars.append(bar)
      bottom += arr
    # labels
    ax.set_ylabel('number of events')
    ax.set_xticks(x+half_width)
    ax.set_xticklabels([''])#unique_dates, rotation=40, horizontalalignment='right')
    ax.set_xlim(x[0]-half_width, x[-1]+width+half_width)

    ###
    ax.set_xlim((-1.5, 8))
    ax.set_ylim((0, 30))
    ###

    # legend (in reversed plotting order)
    leg_txts = []
    for clr in reversed(self.colors):
      num_event = int(dataset[clr][0]) if clr in dataset else 0
      leg_txts.append(str(clr) + ' (' + str(num_event) + ')')
    leg = ax.legend( (bar[0] for bar in bars[::-1]), leg_txts )
    leg.draggable(True)
    leg.get_frame().set_alpha(.5)
    return

  def plot_pie_chart(self, ax, dataset):
    data = np.array( dataset.values() )
    indices = argbalance(data)
    x = data[indices]
    labels = np.array( dataset.keys() )[indices]
    colors = [self.colors[l] if l in self.colors else self.def_color for l in labels]
    explode = [0.05 for _ in x]
    patches, texts, autotexts = ax.pie(x, labels=labels, autopct='%.1f%%',
      explode=explode, shadow=True, colors=colors)
    for text in autotexts:
      text.set_color('w')
    return
