# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList

class Search(iSearch):
  optdep = {
    'egospeedstart': 'set_egospeed-start@egoeval', 
    'drivdist': 'set_drivendistance@egoeval',
  }
  
  def check(self):
    sgs = [{
      "tr0_track_selection_status": ("Tracks", "tr0_track_selection_status"),
      "tr0_video_confidence": ("Tracks", "tr0_video_confidence"),
      "tr0_range": ("Tracks", "tr0_range"),
    }]
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def search(self, group):
    # find intervals
    time, value1 = group.get_signal("tr0_track_selection_status")
    value2 = group.get_value("tr0_video_confidence", ScaleTime=time)
    value3 = group.get_value("tr0_range", ScaleTime=time)
    mask = ((value1 & 4).astype(np.bool) & (value2 >= 0.2) & (value3 < 100.0))  # "fused" is approximated as vid_conf >= 0.2
    intervals = cIntervalList.fromMask(time, mask)
    report = Report(intervals, "Most relevant fused object in ego lane")
    # set general quantities
    for qua in 'drivdist', 'egospeedstart':
      if self.optdep[qua] in self.passed_optdep:
        set_qua_for_report = self.modules.get_module(self.optdep[qua])
        set_qua_for_report(report)
      else:
        self.logger.warning("Inactive module: %s" % self.optdep[qua])
    # register results
    self.batch.add_entry(report, result=self.PASSED)
    return
