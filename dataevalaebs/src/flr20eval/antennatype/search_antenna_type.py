# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np

from aebs.par.labels import default as label_groups
from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList,  maskToIntervals

sgs = [
    {
      "antenna_type": ("General_radar_status", "antenna_type"),
    },
]

class Search(iSearch):
  def check(self):
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def search(self, group):
    # get signals
    time, signal  = group.get_signal("antenna_type")
    uniques = np.unique(signal)
    
    # init report
    title = "FLR21 antenna type"
    label_group_name = "FLR21 antenna type"
    votes = self.batch.get_labelgroups(label_group_name)
    report = Report(cIntervalList(time), title, votes=votes)
    label_group = label_groups[label_group_name]
    
    # find intervals
    for value in uniques:
      mask = signal == value
      label = label_group[1][value]
      for st,end in maskToIntervals(mask):
        index = report.addInterval( (st,end) )
        report.vote(index, label_group_name, label)
    
    self.batch.add_entry(report, result=self.PASSED)
    return
