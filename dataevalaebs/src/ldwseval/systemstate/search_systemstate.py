# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.ldws_state import ldws_state_dict

class Search(iSearch):
  optdep = {
    'egospeedstart': 'set_egospeed-start@egoeval', 
    'egospeedmin': 'set_egospeed-min@egoeval',
    'drivdist': 'set_drivendistance@egoeval',
  }

  sgs = [
    {"LDWSState": ("FLI2_E8", "FLI2_StateOfLDWS")},
    {"LDWSState": ("FLI2", "FLI2_LDWSState")},
  ]

  def check(self):
    group = self.source.selectSignalGroup(self.sgs)
    return group

  def fill(self, group):
    # get signals
    t,status = group.get_signal("LDWSState")
    # init report
    title = "LDWS state"
    votes = self.batch.get_labelgroups('LDWS state')
    report = Report(cIntervalList(t), title, votes=votes)
    # find intervals
    uniques = np.unique(status)
    for value in uniques:
      mask = status == value
      label = ldws_state_dict[value]
      for st,end in maskToIntervals(mask):
        index = report.addInterval( (st,end) )
        report.vote(index, 'LDWS state', label)
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
