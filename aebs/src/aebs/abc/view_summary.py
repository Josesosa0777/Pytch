# -*- dataeval: init -*-

"""
Plot time-based statistics about aebs warnings, driven kilometers and driven hours.
Makes a summary heatmap and a summary barchart about the driven kilometers and driven hours.
Makes barcharts for every vehicle about the driven kilometers and the occured AEBS warnings.
Time range is from the very first measurement to the most recent one, can be changed with --start-date and --end-date flags.
"""

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date, timedelta

from interface import iView
from view_quantity_trend import make_dict, groupby

init_params = {
  'all'     : dict(strftime='',           timerange=''),
  'yearly'  : dict(strftime='%Y',         timerange=', timerange'),
  'monthly' : dict(strftime='%Y-%m',      timerange=', timerange'),
  'weekly'  : dict(strftime='%Y-%m cw%W', timerange=', timerange'),
  'daily'   : dict(strftime='%Y-%m-%d',   timerange=', timerange'),
}


event_query_template = """
SELECT meastag(basename, 'vehicle') vehicle, strftime('%s', me.start, '-4 hour') timerange, count(title) event
FROM entryintervals ei
JOIN %s en             ON ei.entryid = en.id
JOIN modules mo        ON en.moduleid = mo.id
JOIN measurements me   ON en.measurementid = me.id
WHERE mo.class = :search_class
GROUP BY vehicle, timerange;
"""

distance_query_template = """
SELECT meastag(basename, 'vehicle') vehicle, strftime('%s', me.start, '-4 hour') timerange, TOTAL(qu.value) distance, TOTAL(ei.end_time - ei.start_time)/3600
FROM entryintervals ei
JOIN %s en ON ei.entryid = en.id
JOIN modules mo ON en.moduleid = mo.id
JOIN measurements me on en.measurementid = me.id
JOIN (
  SELECT quantities.entry_intervalid, quantities.value
  FROM   quantities
  JOIN quanames ON quanames.id = quantities.nameid
  JOIN quanamegroups ON quanamegroups.id = quanames.groupid
  WHERE quanamegroups.name = "ego vehicle"
    AND quanames.name = "driven distance"
) AS qu ON qu.entry_intervalid = ei.id
WHERE mo.class = :search_class
GROUP BY vehicle, timerange;
"""

def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr
        curr += delta

class View(iView):
  event_search_class = None
  distance_search_class = None
  base_title = ""

  def init(self, strftime, timerange):
    self.strftime = strftime
    self.timerange = timerange
    return

  def check(self):
    table_name = self.batch.create_table_from_last_entries(
      start_date=self.start_date, end_date=self.end_date)
    event_query = event_query_template % \
      (self.strftime, table_name)
    query_kwargs_event = dict(
      search_class=self.event_search_class,
    )
    query_kwargs_distance = dict(
      search_class=self.distance_search_class,
    )
    event = self.batch.query(event_query, **query_kwargs_event)
    distance_query = distance_query_template % \
      (self.strftime, table_name)
    distance = self.batch.query(distance_query, **query_kwargs_distance) #TODO: check left join
    return event, distance

  def fill(self, event, distance):
    #grouping the results by vehicles (list of lists)
    dist_groups, dist_vehicles = groupby(distance)
    event_groups, event_vehicles = groupby(event)

    #making dictionaries for every type of data in {vehicle: {date:value}} format
    distance_data = make_dict(dist_groups,dist_vehicles,1,2)
    duration_data = make_dict(dist_groups,dist_vehicles,1,3)
    event_data = make_dict(event_groups,event_vehicles,1,2)

    #making a dictionary of DataFrames in {vehicle: dataframe} format
    data = {}
    for key,value in distance_data.iteritems():
      if key is None:
        continue
      if key in event_data:
        e = event_data[key]
      else:
        e = {}
      d = {'event': e, 'dist' : value, 'duration': duration_data[key]}
      df = pd.DataFrame(d)
      df.fillna(0.0001, inplace=True)
      data[key] = df

    dist_heat = {}
    for key,d in data.iteritems():
      dist_heat[key] = d['dist']

    return data, dist_heat

  def view(self, data, dist_heat):
    sum_dist = []
    sum_hrs = []
    first_date = '3000-12'
    last_date = '2000-01'
    for vehicle,dataframe in data.iteritems():
      if self.start_date is not None:
        #barchart for every vehicle
        title = self.base_title + vehicle # TODO: set figure title
        ax1,ax2 = self.draw_bar(dataframe.index,dataframe['event'],dataframe['dist'],'number of aebs warnings','driven distance [km]','r','b',title)
        max_y = max([1000*ax1.get_ybound()[1], ax2.get_ybound()[1]])
        ax1.set_ybound(upper=1.1*max_y/1000)
        ax2.set_ybound(upper=1.1*max_y)
        plt.savefig(vehicle+"_aebs_warnings.png")
      #sum driven duration and distance
      sum_dist.append(sum(dataframe['dist']))
      sum_hrs.append(sum(dataframe['duration']))
      #determine the first and last date of the measurements
      if min(dataframe.index) < first_date:
        first_date = min(dataframe.index)
      if max(dataframe.index) > last_date:
        last_date = max(dataframe.index)

    #summary barchart
    title = 'Driven kilometers and driven hours on every vehicle'
    ax1,ax2 = self.draw_bar(data.keys(),sum_hrs,sum_dist,'driven time [hours]','driven distance [km]','g','b',title,20, 15)
    ax1.set_ybound(upper=ax1.get_ybound()[1]*1.1)
    ax2.set_ybound(upper=ax2.get_ybound()[1]*1.1)
    if self.start_date is None:
      file_name = "overall_summary_plot.png"
    else:
      file_name = "yearly_summary_plot.png"
    plt.savefig(file_name)

    #drawing a summary heatmap
    title = 'Heatmap of driven kilometers'
    year1 = int(first_date[0:4])
    month1 = int(first_date[5:])
    year2 = int(last_date[0:4])
    month2 = int(last_date[5:])
    self.draw_heatmap(year1,month1,year2,month2,dist_heat,title)
    return

  def draw_bar(self,x_axis,data1,data2,label1,label2,color1,color2, title, figwidth=15, figheight=10):
    fig = plt.figure(figsize=(figwidth, figheight))
    plt.title(title)
    ax1 = fig.gca()
    x = np.arange( len(x_axis) )
    width = .4
    opacity = 1
    #first bar chart
    bar1 = ax1.bar(x, data1, width, alpha = opacity, color=color1, label = label1)
    ax1.set_ylabel(label1, color = color1)
    #x-axis labels
    ax1.set_xticks(x+width)
    ax1.set_xticklabels(x_axis, rotation=40, horizontalalignment='right')
    for t1 in ax1.get_yticklabels():
      t1.set_color(color1)
    ax2 = ax1.twinx()
    #second bar chart
    bar2 = ax2.bar(x+width, data2, width, alpha = opacity, color = color2, label = label2)
    ax2.set_ylabel(label2, color=color2)
    for t1 in ax2.get_yticklabels():
      t1.set_color(color2)
    #writing numbers to the bars
    rects1 = ax1.patches
    rects2 = ax2.patches
    labels1 = [int(i) for i in data1]
    labels2 = [int(i) for i in data2]
    for rect,label in zip(rects1,labels1):
      height = rect.get_height()
      ax1.text(rect.get_x()+width/2., height, label, ha='center', va='bottom', color=color1)
    for rect,label in zip(rects2,labels2):
      height = rect.get_height()
      ax2.text(rect.get_x()+width/2., height+5, label, ha='center', va='bottom', color=color2)
    return ax1,ax2

  def draw_heatmap(self, year1, month1, year2, month2, data, title, figwidth=20, figheight=10):
    months = []
    for result in perdelta(date(year1, month1, 15), date(year2, month2, 30), timedelta(days=30)):
      months.append(result.strftime('%Y-%m'))
    df_heatmap = pd.DataFrame(data, index=months)
    df_heatmap.fillna(0, inplace=True)
    df_heatmap=df_heatmap.transpose()
    fig = plt.figure(figsize=(figwidth, figheight))
    sns.heatmap(df_heatmap, annot=True, fmt='.0f')
    if self.start_date is None:
      file_name = "overall_heatmap.png"
    else:
      file_name = "yearly_heatmap.png"
    plt.title(title)
    plt.savefig(file_name)
    return
