import sys

import numpy as np
import matplotlib.pyplot as plt

import interface
from aebs.par import labels

DefParam = interface.NullParam

LABELS = labels.default  # TODO: from interface

DICT = {'asso problem main cause':     'Main causes of association break-ups',
        'asso problem detailed cause': 'Detailed causes of association break-ups\n(gate)'}

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

def get_sum_intlen_4_label(label, labelgroup, searchclass):
  q = interface.Batch.query(
    """
    SELECT COUNT(*)
    FROM
     (SELECT DISTINCT entryintervals.id
      FROM entryintervals
      LEFT JOIN interval2label ON entryintervals.id = interval2label.entry_intervalid
      LEFT JOIN labels         ON interval2label.labelid = labels.id
      LEFT JOIN labelgroups    ON labels.groupid = labelgroups.id
      LEFT JOIN entries        ON entryintervals.entryid = entries.id
      LEFT JOIN modules        ON entries.moduleid = modules.id
      WHERE labels.name = ? AND
            labelgroups.name = ? AND
            modules.class = ?)
    """,
    label, labelgroup, searchclass, fetchone=True)
  return int(q[0])

def get_sum_intlen_4_label_s1_stat(label, labelgroup, searchclass):
  q = interface.Batch.query(
    """
    SELECT COUNT(*)
    FROM
     (SELECT DISTINCT ei1.id
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
      LEFT JOIN interval2label il3 ON il1.entry_intervalid = il3.entry_intervalid
      LEFT JOIN labels la3         ON il3.labelid = la3.id
      LEFT JOIN labelgroups lg3    ON la3.groupid = lg3.id
      LEFT JOIN interval2label il4 ON il1.entry_intervalid = il4.entry_intervalid
      LEFT JOIN labels la4         ON il4.labelid = la4.id
      LEFT JOIN labelgroups lg4    ON la4.groupid = lg4.id
      WHERE lg1.name = "OHY object" AND
            lg2.name = "OHY object" AND
            la1.name = la2.name AND
            mo1.class = ? AND
            mo2.class = "dataevalaebs.search_cvr3_ohy_pos.cSearch" AND
            mo2.param = "posname=S1" AND
            MAX(ei1.start, ei2.start) < MIN(ei1.end, ei2.end) AND
            la3.name = ? AND
            lg3.name = ? AND
            la4.name = "stationary" AND
            lg4.name = "moving state")
    """,
    searchclass, label, labelgroup, fetchone=True)
  return int(q[0])

def pie_4_labelgroup(lg, searchclass, filterS1Stat):
  labels = LABELS[lg][1]
  getterfunc = get_sum_intlen_4_label_s1_stat if filterS1Stat else get_sum_intlen_4_label
  data = [getterfunc(label, lg, searchclass) for label in labels]
  title = DICT[lg] if DICT.has_key(lg) else lg
  _plot_pie(data, labels, title)
  return

class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    pie_4_labelgroup('asso problem main cause', 'dataevalaebs.search_asso_breakup_reason.cSearch', True)
    pie_4_labelgroup('asso problem detailed cause', 'dataevalaebs.search_asso_breakup_reason.cSearch', True)
    return
