# -*- dataeval: init -*-

import numpy as np

from interface import iSearch
from measproc.report2 import Report
from measproc.IntervalList import cIntervalList, maskToIntervals
from aebs.par.fcw_state import fcw_state_dict

class Search(iSearch):
  optdep = {
    'egospeedstart': 'set_egospeed-start@egoeval', 
    'egospeedmin': 'set_egospeed-min@egoeval',
    'drivdist': 'set_drivendistance@egoeval',
  }

  sgs = [
    {"AEBSState": ("AEBS1_A0_sA0","AEBS1_AEBSState_A0")},
    {"AEBSState": ("AEBS1_A0_sA0", "AEBS1_AEBSState_2A")},
    {"AEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A")},
    {"AEBSState": ("AEBS1_A0_sA0", "AEBS1_AEBSState_A0_sA0")},
    {"AEBSState": ("AEBS1",    "AEBS_St")},
    {"AEBSState": ("AEBS1_2A", "AEBS1_AEBSState_2A_C1")},
    {"AEBSState": ("AEBS1_A0", "AEBS1_AEBSState_A0")},
  ]
  
  def check(self):
    group = self.source.selectSignalGroup(self.sgs)
    return group

  def fill(self, group):
    # get signals
    t,status = group.get_signal("AEBSState")
    # init report
    title = "FCW state"
    votes = self.batch.get_labelgroups('FCW state')
    report = Report(cIntervalList(t), title, votes=votes)
    # find intervals
    uniques = np.unique(status)
    for value in uniques:
      mask = status == value
      label = fcw_state_dict[value]
      for st,end in maskToIntervals(mask):
        index = report.addInterval( (st,end) )
        report.vote(index, 'FCW state', label)
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
