# -*- dataeval: method -*-
import interface
import measproc
from measproc.report2 import Report

DefParam = interface.NullParam

signalgroups =   [{'vx_ego': (dev_name, 'evi.General_TC.vxvRef')}
                  for dev_name  in 'ECU', 'MRR1plus', 'RadarFC']

class cSearch(interface.iSearch):
  def check(self):
    source = self.get_source('main')
    group = source.selectSignalGroup(signalgroups)
    return group

  def fill(self, group):
    return group

  def search(self, param, group):
    source = self.get_source('main')
    batch = self.get_batch()

    limit = 5.0
    title = 'vx_ego bigger then %.2f' %limit
    votes = batch.get_labelgroups('standard')

    time, vx_ego = source.getSignalFromSignalGroup(group, 'vx_ego')
    intervals = source.compare(time, vx_ego, measproc.greater, limit)
    report = Report(intervals, title, votes)
    for index, interval in enumerate(intervals):
      report.vote(index, 'standard', 'valid')
    batch.add_entry(report, 'passed', ('radar',))
    return
