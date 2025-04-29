# -*- dataeval: init -*-

"""
Plot time-series of a quantity
"""
import seaborn as sns
import pandas as pd
import numpy as np

import itertools
import operator
import datavis
from interface import iView

quantity_query_template = """
SELECT meastag(basename, 'vehicle') vehicle, strftime('%s', me.start, '-4 hour') timerange, qn.name signal, %s(qu.value) value
FROM %s en
JOIN entryintervals ei on en.id = ei.entryid
JOIN quantities qu on qu.entry_intervalid = ei.id
JOIN quanames qn on qu.nameid = qn.id
JOIN measurements me on en.measurementid = me.id
JOIN modules mo on mo.id = en.moduleid
WHERE mo.class = :search_class AND signal == :quaname
GROUP BY vehicle, timerange
"""

init_params = {
  'yearly'  : dict(strftime='%Y',        ),
  'monthly' : dict(strftime='%Y-%m',     ),
  'weekly'  : dict(strftime='%Y-%m cw%W',),
  'daily'   : dict(strftime='%Y-%m-%d',  ),
}

def make_dict(group, keys, keyindex, valueindex):
  dictionary = {}
  for i,list in enumerate(group):
    data = {}
    for element in list:
      data[element[keyindex]] = element[valueindex]
    dictionary[keys[i]] = data
  return dictionary

def groupby(rawdata, keyindex=0):
  groups = []
  keys = []
  for key,group in itertools.groupby(rawdata, operator.itemgetter(keyindex)):
    groups.append(list(group))
    keys.append(key)
  return groups, keys

class View(iView):
  search_class = None
  quanamegroup = None
  quaname_min = None
  quaname_max = None
  base_title = ""
  min = None
  max = None
  treshold = None
  
  def init(self, strftime):
    self.strftime = strftime
    return
  
  def check(self):
    table_name = self.batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)
    quantity_query_min = quantity_query_template % \
      (self.strftime, 'min', table_name)
    quantity_query_max = quantity_query_template % \
      (self.strftime, 'max', table_name)
    query_kwargs_event_min = dict(
      search_class=self.search_class,
      quaname = self.quaname_min
    )
    query_kwargs_event_max = dict(
      search_class=self.search_class,
      quaname = self.quaname_max
    )
    event_min = self.batch.query(quantity_query_min, **query_kwargs_event_min)
    event_max = self.batch.query(quantity_query_max, **query_kwargs_event_max)
    return event_min, event_max

  def fill(self, event_min, event_max):
    quantity_min, vehicles_min = groupby(event_min)
    quantity_max, vehicles_max = groupby(event_max)
    
    quantity_min_dict = make_dict(quantity_min, vehicles_min, 1, 3)
    quantity_max_dict = make_dict(quantity_max, vehicles_max, 1, 3)
    
    data = {}
    for key, min in quantity_min_dict.iteritems():
      if key in quantity_max_dict:
        max = quantity_max_dict[key]
      else:
        max = {}
      d = {self.quaname_min: min, self.quaname_max: max}
      df = pd.DataFrame(d)
      df.fillna(0, inplace=True)
      data[key] = df
    d1 = {}
    d2 = {}
    for key, df in data.iteritems():
      col1 = df.pop(self.quaname_min)
      col2 = df.pop(self.quaname_max)
      d1[key] = col1
      d2[key] = col2
    df_min = pd.DataFrame(d1)
    df_max = pd.DataFrame(d2)
    d_outlier = {}
    for column in df_min:
      d_outlier[column] = (df_min[column] > self.treshold) | (df_max[column] < self.treshold) | (df_min[column] < (df_min.mean().mean() - 3*df_min.stack().std())) | (df_max[column] > (df_max.mean().mean() + 3*df_max.stack().std()))
    df_outlier = pd.DataFrame(d_outlier)
    dict_panel = {self.quaname_min: df_min, self.quaname_max: df_max, 'outlier': df_outlier}
    panel = pd.Panel(dict_panel)
    return panel

  def timeseries(self, title, panel):
    nav = datavis.MatplotlibNavigator(title=title)
    nav.setUserWindowTitle(title)
    ax1 = nav.fig.gca()
    panel.replace(0, 0.0001, inplace=True)
    df1 = panel[self.quaname_min]
    df2 = panel[self.quaname_max]
    i = 0
    colors = ['#7bc1c5', '#ffff00', '#887ecc', '#fb8072', '#80b1d3', '#fdb462', '#90b255', '#fc9fce', '#909090', '#bc80bd']
    markers = ['o',"v","^","<",">","s","p","D","h","d"]
    x = np.arange( len(df1.index) )
    for column in df1:
      outlier_min = df1[column].multiply(panel['outlier'][column])
      outlier_min.replace(0, np.nan, inplace=True)
      normal_min = df1[column].multiply(~panel['outlier'][column])
      normal_min.replace(0, np.nan, inplace=True)
      outlier_max = df2[column].multiply(panel['outlier'][column])
      outlier_max.replace(0, np.nan, inplace=True)
      normal_max = df2[column].multiply(~panel['outlier'][column])
      normal_max.replace(0, np.nan, inplace=True)
      kwargs = dict(color=colors[i], ax=ax1, interpolate=False, marker=markers[i], markersize=10, linestyle='None')
      ax1 = sns.tsplot(outlier_min, alpha=1, legend=True, condition=column, **kwargs)
      ax1 = sns.tsplot(normal_min, alpha=0.3, **kwargs)
      ax1 = sns.tsplot(outlier_max, alpha=1, **kwargs)
      ax1 = sns.tsplot(normal_max, alpha=0.3, **kwargs)
      i += 1
    ax1.set_xticks(x)
    ax1.set_xticklabels(df1.index , rotation=40, horizontalalignment='right')
    ax1.set_ybound(ax1.get_ybound()[0]-0.05, ax1.get_ybound()[1]+0.05)
    self.sync.addStaticClient(nav)
    return

  def view(self, panel):
    self.timeseries(self.base_title, panel)
    return
