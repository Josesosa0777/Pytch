import sys

import numpy as np
import matplotlib.pyplot as plt

import interface
from aebs.par import labels

DefParam = interface.NullParam

LABELS = labels.default

DICT = {'availability': 'S-Cam availability'}


def fetch_sum_intervallen(label, labelgroup):
  q = interface.Batch.query("""
    SELECT TOTAL(entryintervals.end-entryintervals.start) 
    FROM entryintervals 
    LEFT OUTER JOIN interval2label ON entryintervals.id =
                                      interval2label.entry_intervalid 
    LEFT OUTER JOIN labels         ON interval2label.labelid = labels.id 
    LEFT OUTER JOIN labelgroups    ON labels.groupid = labelgroups.id 
    WHERE labels.name=? AND 
          labelgroups.name=?
    """,
    label, labelgroup, fetchone=True)
  return int(q[0])

def plot_pie_sum_intervallen(lg):
  labels = LABELS[lg][1]
  data = [fetch_sum_intervallen(label, lg) for label in labels]
  if not np.any(data):
    print >> sys.stderr, 'No pie data for "%s" labelgroup' % lg
    return
  explode = [0.05 for _ in data]
  fig = plt.figure()
  ax = fig.gca()
  ax.pie(data, labels=labels, autopct='%.1f%%', explode=explode, shadow=True)
  title = DICT[lg] if DICT.has_key(lg) else lg
  ax.set_title(title)
  fig.show()
  return

def calc_sum_intervallen_intersection(label1, label2):
  q = interface.Batch.query("""
    SELECT ei1.start, ei1.end, ei2.start, ei2.end
    FROM            entryintervals ei1
    LEFT OUTER JOIN interval2label il1 ON ei1.id = il1.entry_intervalid 
    LEFT OUTER JOIN labels l1 ON il1.labelid = l1.id 
    LEFT OUTER JOIN entries e1 ON ei1.entryid = e1.id 
    LEFT OUTER JOIN entries e2 ON e1.measurementid = e2.measurementid 
    LEFT OUTER JOIN entryintervals ei2 ON e2.id = ei2.entryid 
    LEFT OUTER JOIN interval2label il2 ON ei2.id = il2.entry_intervalid 
    LEFT OUTER JOIN labels l2 ON il2.labelid = l2.id 
    WHERE l1.name = ? AND 
          l2.name = ?
    """,
    label1, label2)
  intervalLengths = []
  for start1, end1, start2, end2 in q:
    startIntersection = max(start1, start2)
    endIntersection = min(end1, end2)
    if startIntersection < endIntersection:  # valid interval (non-empty intxn)
      intervalLengths.append(endIntersection-startIntersection)
  sumIntervals = sum(intervalLengths)
  return sumIntervals

def plot_pie_sum_intervallen_intersection(labelgroup1, labelgroup2):
  labels1 = LABELS[labelgroup1][1]
  labels2 = LABELS[labelgroup2][1]
  piedata = []
  pielabels = []
  for l2 in labels2:
    for l1 in labels1:
      pielabels.append(l1 + ' @ ' + l2)
      piedata.append(calc_sum_intervallen_intersection(l1, l2))
  if not np.any(piedata):
    print >> sys.stderr, 'No data to plot valid pie chart'
    return
  explode = [0.05 for _ in piedata]
  fig = plt.figure()
  ax = fig.gca()
  ax.pie(piedata, labels=pielabels, autopct='%.1f%%', explode=explode,
         shadow=True)
  title = 'S-Cam availability during day\'n\'night'
  ax.set_title(title)
  fig.show()

  ## hack to plot pie for day'n'night lengths during S-Cam crashes
  # pielabels = [pielabels[i] for i in (1, 3)]
  # piedata = [piedata[i] for i in (1, 3)]
  # explode = [0.05 for _ in piedata]
  # fig = plt.figure()
  # ax = fig.gca()
  # ax.pie(piedata, labels=pielabels, autopct='%.1f%%', explode=explode,
         # shadow=True)
  # title = 'Daytime during S-Cam unavailability'
  # ax.set_title(title)
  # fig.show()
  return

class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    plot_pie_sum_intervallen('availability')
    plot_pie_sum_intervallen('daytime')
    plot_pie_sum_intervallen_intersection('availability', 'daytime')
    return
