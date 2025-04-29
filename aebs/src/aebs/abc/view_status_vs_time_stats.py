# -*- dataeval: init -*-

"""
Plot time-based statistics about a status signal
"""

from collections import OrderedDict
from itertools import chain

import numpy as np

import datavis
from datavis.figlib import argbalance
from interface import iView

init_params = {
  'all'     : dict(strftime='%Y',         groupby='',   bar_chart=False),
  'yearly'  : dict(strftime='%Y',         groupby=',d', bar_chart=False),
  'monthly' : dict(strftime='%Y-%m',      groupby=',d', bar_chart=True),
  'weekly'  : dict(strftime='%Y-%m cw%W', groupby=',d', bar_chart=True),
  'daily'   : dict(strftime='%Y-%m-%d',   groupby=',d', bar_chart=True),
}


status_query_template = """
SELECT la.name status, strftime('%s', me.start, '-4 hour') d, TOTAL(ei.end_time - ei.start_time) / 3600.
FROM entryintervals ei
JOIN %s en             ON ei.entryid = en.id
JOIN interval2label il ON ei.id = il.entry_intervalid
JOIN labels la         ON il.labelid = la.id
JOIN labelgroups lg    ON la.groupid = lg.id
JOIN modules mo        ON en.moduleid = mo.id
JOIN measurements me   ON en.measurementid = me.id
WHERE     lg.name = :label_group
      AND mo.class = :search_class
GROUP BY status %s;
"""

meas_days_query = """
SELECT DISTINCT date(me.start, '-4 hour') as days
-- 4 hours minus to unify recordings after midnight with start day
FROM measurements me
JOIN entries en ON en.measurementid = me.id
JOIN modules mo ON en.moduleid = mo.id
WHERE mo.class = :search_class
ORDER BY days ASC;
"""

class View(iView):
  label_group = None
  search_class = None

  colors = OrderedDict()  # color order determines how bars are stacked on top of each other (bottom-up)
  def_color = 'c'

  base_title = ""

  def init(self, strftime, groupby, bar_chart):
    self.strftime = strftime
    self.groupby = groupby
    self.bar_chart = bar_chart
    return

  def check(self):
    table_name = self.batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)
    status_query = status_query_template % \
      (self.strftime, table_name, self.groupby)
    query_kwargs = dict(
      search_class=self.search_class,
      label_group=self.label_group
    )
    res = self.batch.query(status_query, **query_kwargs)
    meas_days = list(
      chain.from_iterable( self.batch.query(meas_days_query, **query_kwargs) )
    )
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
    # align data and color definition statuses
    for status in self.colors:
      if status not in dataset:
        # drop color definition if status n/a in current dataset
        self.colors.pop(status)
    for status in dataset:
      if status not in self.colors:
        # add default color definition to unhandled status
        self.colors[status] = self.def_color
    num_days = len(meas_days)
    first_day = meas_days[0]
    last_day  = meas_days[-1]
    driven_time = np.sum( portion for status, date, portion in res )
    titlestr = "%s (between %s and %s)\ntotal: %s days, %.0f hours"
    title = titlestr %(self.base_title, first_day, last_day, num_days, driven_time)
    return dataset, unique_dates, title

  def view(self, dataset, unique_dates, title):
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax = nav.fig.gca()
    if self.bar_chart:
      self.plot_bar_chart(ax, dataset, unique_dates)
    else:
      self.plot_pie_chart(ax, dataset)
    self.sync.addStaticClient(nav)
    return

  def plot_bar_chart(self, ax, dataset, unique_dates):
    x = np.arange( len(unique_dates) )
    width = .5
    half_width = width/2.
    # plotting
    bottom = np.zeros(x.size)
    bars = []
    # loop by color order (bars stacked bottom-up)
    for status in self.colors:
      arr = dataset[status]
      bar = ax.bar(x, arr, width, color=self.colors[status], linewidth=0, bottom=bottom)
      bars.append(bar)
      bottom += arr
    # labels
    ax.set_ylabel('hours')
    ax.set_xticks(x+half_width)
    ax.set_xticklabels(unique_dates, rotation=40, horizontalalignment='right')
    ax.set_xlim(x[0]-half_width, x[-1]+width+half_width)
    # legend (in reversed plotting order)
    leg = ax.legend( (bar[0] for bar in bars[::-1]), self.colors.keys()[::-1] )
    leg.draggable(True)
    leg.get_frame().set_alpha(.5)
    return

  def plot_pie_chart(self, ax, dataset):
    data = np.array( dataset.values() )
    data /= np.sum(data)
    indices = argbalance(data)
    x = data[indices]
    labels = np.array( dataset.keys() )[indices]
    colors = [self.colors[l] for l in labels]
    explode = [0.05 for _ in x]
    patches, texts, autotexts = ax.pie(x, labels=labels, autopct='%.1f%%',
      explode=explode, shadow=True, colors=colors)
    for text in autotexts:
      text.set_color('w')
    return
