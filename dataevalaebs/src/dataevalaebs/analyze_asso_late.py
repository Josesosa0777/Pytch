import sys

import numpy as np
import matplotlib.pyplot as plt

import interface
from aebs.par import labels

DefParam = interface.NullParam

LABELS = labels.default  # TODO: from interface

DICT = {'asso problem main cause':     'Main causes of late associations',
        'asso problem detailed cause': 'Detailed causes of late associations\n(gate)',
        'late':                        'Association latency'}

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

def count_multilabels(labelgroup):
  q = interface.Batch.query(
    """
    SELECT COUNT(*)
    FROM entryintervals
    LEFT JOIN interval2label ON entryintervals.id = interval2label.entry_intervalid
    LEFT JOIN labels         ON interval2label.labelid = labels.id
    LEFT JOIN labelgroups    ON labels.groupid = labelgroups.id
    WHERE labelgroups.name=?
    GROUP BY interval2label.entry_intervalid
    """,
    labelgroup)
  q = np.array(q)
  print '*%s* 0: %d; 1: %d; 2: %d; 3: %d; >3: %d' % \
    (labelgroup,
     np.count_nonzero(q==0),
     np.count_nonzero(q==1),
     np.count_nonzero(q==2),
     np.count_nonzero(q==3),
     np.count_nonzero(q>3))
  return

def get_entryids_4_label(label, labelgroup):
  q = interface.Batch.query(
    """
    SELECT entryintervals.entryid
    FROM entryintervals
    LEFT JOIN interval2label ON entryintervals.id = interval2label.entry_intervalid
    LEFT JOIN labels         ON interval2label.labelid = labels.id
    LEFT JOIN labelgroups    ON labels.groupid = labelgroups.id
    WHERE labels.name = ? AND
          labelgroups.name = ?
    """,
    label, labelgroup)
  q = [item[0] for item in q]
  return q

def get_entryids_4_intlen(lower, upper):
  q = interface.Batch.query(
    """
    SELECT entryid
    FROM entryintervals
    WHERE end-start BETWEEN ? AND ?
    """,
    lower, upper)
  q = [item[0] for item in q]
  return q

def get_sum_intlen_4_label(label, labelgroup, searchclass):
  q = interface.Batch.query(
    """
    SELECT TOTAL(entryintervals.end-entryintervals.start)
    FROM entryintervals
    LEFT JOIN interval2label ON entryintervals.id = interval2label.entry_intervalid
    LEFT JOIN labels         ON interval2label.labelid = labels.id
    LEFT JOIN labelgroups    ON labels.groupid = labelgroups.id
    LEFT JOIN entries        ON entryintervals.entryid = entries.id
    LEFT JOIN modules        ON entries.moduleid = modules.id
    WHERE labels.name = ? AND
          labelgroups.name = ? AND
          modules.class = ?
    """,
    label, labelgroup, searchclass, fetchone=True)
  return int(q[0])

def get_sum_intlen_4_label_s1_stat(label, labelgroup, searchclass):
  q = interface.Batch.query(
    """
    SELECT TOTAL(ei1.end-ei1.start)
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
          lg4.name = "moving state"
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

def hist_4_tag(tag, dataMax):
  q = interface.Batch.query(
    """
    SELECT entryintervals.end-entryintervals.start AS len
    FROM entryintervals
    LEFT JOIN entry2tag ON entryintervals.entryid = entry2tag.entryid
    LEFT JOIN tags      ON entry2tag.tagid = tags.id
    WHERE tags.name = ? AND
          len <= ?
    """,
    tag, dataMax)
  q = np.array(q)
  if not q.size:
    print >> sys.stderr, 'No histogram data for "%s" tag' % tag
    return
  nBins = np.max(q)-np.min(q)
  fig = plt.figure()
  ax = fig.gca()
  ax.hist(q, bins=nBins, normed=True)
  ax.set_xlabel('#cycles')
  ax.set_ylabel('probability density')
  title = DICT[tag] if DICT.has_key(tag) else tag
  ax.set_title(title)
  fig.show()
  return

def hist_4_class(searchclass, dataMax):
  q = interface.Batch.query(
    """
    SELECT entryintervals.end-entryintervals.start AS len
    FROM entryintervals
    LEFT JOIN entries ON entryintervals.entryid = entries.id
    LEFT JOIN modules ON entries.moduleid = modules.id
    WHERE modules.class = ? AND
          len <= ?
    """,
    searchclass, dataMax)
  q = np.array(q)
  if not q.size:
    print >> sys.stderr, 'No histogram data for "%s" searchclass' % searchclass
    return
  nBins = np.max(q)-np.min(q)
  fig = plt.figure()
  ax = fig.gca()
  ax.hist(q, bins=nBins, normed=True)
  ax.set_xlabel('#cycles')
  ax.set_ylabel('probability density')
  title = DICT[searchclass] if DICT.has_key(searchclass) else searchclass
  ax.set_title(title)
  fig.show()
  return

def filter_s1_lates():
  """
  Query to be used for the 'query' analyze command line option in order to
  highlight the intervals where asso latency was detected for an S1 object.
  """

  """
  SELECT DISTINCT ei1.position
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
  WHERE ei1.entryid = ? AND
        lg1.name = "OHY object" AND
        lg2.name = "OHY object" AND
        la1.name = la2.name AND
        mo1.class = "dataevalaebs.search_asso_late.cSearch" AND
        mo2.class = "dataevalaebs.search_cvr3_ohy_pos.cSearch" AND
        mo2.param = "posname=S1" AND
        MAX(ei1.start, ei2.start) < MIN(ei1.end, ei2.end)
  """
  return

def hist_4_s1_lates():
  q = interface.Batch.query(
    """
    SELECT DISTINCT ei1.id, ei1.end-ei1.start intlen
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
          mo1.class = "dataevalaebs.search_asso_late.cSearch" AND
          mo2.class = "dataevalaebs.search_cvr3_ohy_pos.cSearch" AND
          mo2.param = "posname=S1" AND
          MAX(ei1.start, ei2.start) < MIN(ei1.end, ei2.end) AND
          intlen < 30
    """)
  q = [(intlen,) for id, intlen in q]
  q = np.array(q)
  if not q.size:
    print >> sys.stderr, 'No histogram data for S1 lates'
    return
  nBins = np.max(q)-np.min(q)
  fig = plt.figure()
  ax = fig.gca()
  ax.hist(q, bins=nBins, normed=True)
  ax.set_xlabel('#cycles')
  ax.set_ylabel('probability density')
  title = 'S1 late'
  ax.set_title(title)
  fig.show()
  return

class cAnalyze(interface.iAnalyze):
  def analyze(self, param):
    hist_4_s1_lates()
    hist_4_class('dataevalaebs.search_asso_late.cSearch', 30)
    pie_4_labelgroup('asso problem main cause', 'dataevalaebs.search_asso_late.cSearch', True)
    pie_4_labelgroup('asso problem detailed cause', 'dataevalaebs.search_asso_late.cSearch', True)
    pie_4_labelgroup('moving direction', 'dataevalaebs.search_asso_late.cSearch', False)
    count_multilabels('moving direction')
    pie_4_labelgroup('moving state', 'dataevalaebs.search_asso_late.cSearch', False)
    count_multilabels('moving state')

    # entryids = get_entryids_4_label('stationary', 'moving state')
    entryids = get_entryids_4_intlen(9, 11)
    interface.BatchNav.BatchFrame.addEntries(entryids)
    return
