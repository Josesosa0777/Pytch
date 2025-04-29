import interface
import measproc
from measproc.Report import cIntervalListReport

DefParam = interface.NullParam

__type__ = 'search-2.0'

signalgroups =   [{'vx_ego': (dev_name, 'evi.General_TC.vxvRef')}
                  for dev_name  in 'ECU', 'MRR1plus', 'RadarFC']

class cSearch(interface.iSearch):
  __type__ = __type__

  def check(self):
    source = self.get_source('main')
    group = source.selectSignalGroup(signalgroups)
    return group

  def fill(self, group):
    return group

  def search(self, param, group):
    batch = self.get_batch()
    source = self.get_source('main')

    limit = 5.0
    title = 'vx_ego bigger then %.2f' %limit
    excluisve, votes = batch.get_labelgroup('standard')

    time, vx_ego = source.getSignalFromSignalGroup(group, 'vx_ego')
    intervals = source.compare(time, vx_ego, measproc.greater, limit)
    report = cIntervalListReport(intervals, title, votes)
    for interval in intervals:
      report.vote(interval, 'valid')
    batch.add_entry(report, 'passed', ('radar',))
    return
