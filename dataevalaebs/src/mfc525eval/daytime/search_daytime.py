# -*- dataeval: init -*-

"""
Search for day, night and dusk occurrences
"""

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.daytime import daytime_dict

class Search(iSearch):
  optdep = {
    'egospeedstart': 'set_egospeed-start@egoeval', 
    'egospeedmin': 'set_egospeed-min@egoeval',
    'drivdist': 'set_drivendistance@egoeval',
  }
  
  def check(self):
    sgs = [{
      "daytime": ("Video_Data_General_B", "Day_Time_Indicator"),
    }]
    group = self.source.selectSignalGroup(sgs)
    return group
  
  def fill(self, group):
    # get signals
    t, daytime = group.get_signal("daytime")
    # init report
    title = "Daytime"
    votes = self.batch.get_labelgroups('daytime')
    report = Report(cIntervalList(t), title, votes=votes)
    # find intervals
    uniques = np.unique(daytime)
    for value in uniques:
      mask = daytime == value
      label = daytime_dict[value]
      for st,end in maskToIntervals(mask):
        index = report.addInterval( (st,end) )
        report.vote(index, 'daytime', label)
    report.sort()
    # set general quantities
    for qua in 'drivdist', 'egospeedmin', 'egospeedstart':
      if self.optdep[qua] in self.passed_optdep:
        set_qua_for_report = self.modules.get_module(self.optdep[qua])
        set_qua_for_report(report)
      else:
        self.logger.warning("Inactive module: %s" % self.optdep[qua])
    return report
  
  def search(self, report):
    self.batch.add_entry(report, result=self.PASSED)
    return
