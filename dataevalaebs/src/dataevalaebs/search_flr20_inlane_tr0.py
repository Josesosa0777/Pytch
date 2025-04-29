# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

sgs = [{
  "tr0_track_selection_status": ("Tracks", "tr0_track_selection_status"),
}]

class Search(iSearch):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group

  def search(self, group):
    time, value = group.get_signal("tr0_track_selection_status")
    mask = (value & 4).astype(np.bool)
    intervals = cIntervalList.fromMask(time, mask)
    report = Report(intervals, "Most relevant object in ego lane")
    self.batch.add_entry(report, result=self.PASSED)
    return
