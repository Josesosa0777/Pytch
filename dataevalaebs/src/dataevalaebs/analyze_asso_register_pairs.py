import sys

import numpy as np
import matplotlib.pyplot as plt

import interface

DefParam = interface.NullParam

def _plot_pie(data, labels, title):
  if not np.any(data):
    print >> sys.stderr, 'No pie data for "%s"' % title
    return
  explode = [0.05 for _ in data]
  fig = plt.figure()
  ax = fig.gca()
  ax.pie(data, labels=labels, autopct='%.1f%%', explode=explode, shadow=True)
  ax.set_title(title)
  fig.show()
  return

def get_sum_intlen_4_class(searchclass):
  q = interface.Batch.query(
    """
    SELECT TOTAL(entryintervals.end-entryintervals.start)
    FROM entryintervals
    LEFT JOIN entries ON entryintervals.entryid = entries.id
    LEFT JOIN modules ON entries.moduleid = modules.id
    WHERE modules.class = ?
    """,
    searchclass, fetchone=True)
  return int(q[0])

def pie_4_s1_pairs():
  q1 = interface.Batch.query(
    """
    SELECT TOTAL(MIN(ei1.end, ei2.end)-MAX(ei1.start, ei2.start))
    FROM entryintervals ei1
    LEFT JOIN interval2label il1 ON ei1.id = il1.entry_intervalid
    LEFT JOIN labels la1         ON il1.labelid = la1.id
    LEFT JOIN labelgroups lg1    ON la1.groupid = lg1.id
    LEFT JOIN entries en1        ON ei1.entryid = en1.id
    LEFT JOIN modules mo1        ON en1.moduleid = mo1.id
    LEFT JOIN entries en2        ON en1.measurementid = en2.measurementid
    LEFT JOIN modules mo2        ON en2.moduleid = mo2.id
    LEFT JOIN entryintervals ei2 ON en2.id = ei2.entryid
    LEFT JOIN interval2label il2 ON ei2.id = il2.entry_intervalid
    LEFT JOIN labels la2         ON il2.labelid = la2.id
    LEFT JOIN labelgroups lg2    ON la2.groupid = lg2.id
    WHERE lg1.name = "OHY object" AND
          lg2.name = "OHY object" AND
          la1.name = la2.name AND
          mo1.class = "dataevalaebs.search_asso_register_pairs.cSearch" AND
          mo2.class = "dataevalaebs.search_cvr3_ohy_pos.cSearch" AND
          mo2.param = "posname=S1" AND
          MAX(ei1.start, ei2.start) < MIN(ei1.end, ei2.end)
    """,
    fetchone=True)
  q1 = int(q1[0])

  q2 = get_sum_intlen_4_class('dataevalaebs.search_cvr3_ohy_pos.cSearch')
  q2 -= q1

  labels = ('with', 'without')
  data = (q1, q2)
  title = 'S1 object with and without association'
  _plot_pie(data, labels, title)
  return

class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    pie_4_s1_pairs()
    return
