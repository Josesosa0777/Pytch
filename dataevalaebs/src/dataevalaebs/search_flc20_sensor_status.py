# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals

sgs  = [
  {"SensorStatus": ("Video_Data_General_B", "SensorStatus"),
   "Frame_ID"    : ("Video_Data_General_B", "Frame_ID"),},
]

class Search(iSearch):
  dep = 'calc_flr20_egomotion@aebs.fill',

  rule = { 0: u'Fully Operational',
           1: u'Warming up / Initializing',
           2: u'Partially Blocked',
           3: u'Blocked',
           4: u'Misaligned',
           5: u'Reserved',
           6: u'Reserved',
           7: u'Reserved',
           8: u'Reserved',
           9: u'Reserved',
          10: u'Reserved',
          11: u'Reserved',
          12: u'Reserved',
          13: u'Reserved',
          14: u'Error',
          15: u'NotAvailable',
  }

  def init(self):
    self.title = 'FLC20 sensor status'
    votes = self.batch.get_labelgroups('camera status')
    names = self.batch.get_quanamegroups('mobileye', 'ego vehicle')
    self.kwargs = dict(votes=votes, names=names)
    return

  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def error(self):
    report = Report( cIntervalList(np.array([])), self.title, **self.kwargs )
    self.batch.add_entry(report, result=self.FAILED)
    return

  def search(self, group):
    t,status = group.get_signal("SensorStatus")
    rule = group.get_conversion_rule("SensorStatus")
    # handle BX measurements where conversion rule (value table) is not recorded
    if not rule:
      rule = self.rule
    frames = group.get_value("Frame_ID", ScaleTime=t)
    ego = self.modules.fill('calc_flr20_egomotion@aebs.fill').rescale(t)
    report = Report( cIntervalList(t), self.title, **self.kwargs )
    uniques = np.unique(status)
    for value in uniques:
      mask = status == value
      label = rule[value]
      for st,end in maskToIntervals(mask):
        index = report.addInterval( (st,end) )
        report.vote(index, 'camera status', label)
        report.set( index, 'mobileye', 'frame start', frames[st] )
        report.set( index, 'mobileye', 'frame end',   frames[end-1] )
        report.set( index, 'ego vehicle', 'speed min', np.min(ego.vx[st:end]) )
    report.sort()
    self.batch.add_entry(report, result=self.PASSED)
    return
