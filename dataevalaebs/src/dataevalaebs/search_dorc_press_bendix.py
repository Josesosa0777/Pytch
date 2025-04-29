# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

sgs  = [
{
  "DFM_red_button": ("DBM", "DFM_red_button"),
},
]

class Search(iSearch):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def search(self, group):
    time, value_00  = group.get_signal("DFM_red_button")
    mask_00 = value_00 == 1
    mask =  mask_00
    intervals = cIntervalList.fromMask(time, mask)
    report = Report(intervals, "DORC Red Button Pressed")
    self.batch.add_entry(report, result=self.PASSED)
    return
