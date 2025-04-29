# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals

sgs   = [
{
  "CurrentProcessorLoad": ("ACC_S03", "CurrentProcessorLoad"),
},
]

class Search(iSearch):
  def init(self):
    self.title = 'proc load'
    self.names = self.batch.get_quanamegroups('ecu performance',)
    return
  
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def search(self, group):
    time, value_00  = group.get_signal("CurrentProcessorLoad")
    mask_00 = value_00 > 50
    mask =  mask_00
    report = Report( cIntervalList(time), self.title, names=self.names )
    
    for st, end in maskToIntervals(mask):
      index = report.addInterval( (st, end) )
      report.set(index, 'ecu performance', 'processor load max', np.max(value_00[st:end]))
    report.sort()
    self.batch.add_entry(report, result=self.PASSED)
    return
