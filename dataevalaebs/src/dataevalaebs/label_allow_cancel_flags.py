# -*- dataeval: init -*-
from collections import namedtuple

from interface.Interfaces import iCalc
from datavis.PlotNavigator import cPlotNavigator
from aebs.labeling.track import AllowCancelFlags, ContAllowCancelFlags

init_params = {
  'get-cont': dict(dep='get_trw_allow_flags', label='ContAllowCancelFlags'),
  'get-start': dict(dep='get_trw_allow_flags', label='AllowCancelFlags'),
  'sim-cont': dict(dep='sim_allow_flags@trw', label='ContAllowCancelFlags'),
  'sim-start': dict(dep='sim_allow_flags@trw', label='AllowCancelFlags'),
}

class Calc(iCalc):
  def init(self, dep, label):
    Dep = namedtuple('Dep', ['allow'])
    self.dep = Dep(dep)
    self.Label = globals()[label]
    return

  def __call__(self, report, jumps):
    batch = self.get_batch()
    votes = batch.get_labelgroups(*self.Label.LABEL_GROUPS)
    report.addVoteGroups(votes)

    group = self.get_modules().fill(self.dep.allow)
    label = self.Label(group.get_all_values(ScaleTime=report.intervallist.Time))
    for jump, (idx, interval) in zip(jumps, report.iterIntervalsWithId()):
      label(report, idx, interval, jump)
    return

