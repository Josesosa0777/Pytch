import interface
import aebs.proc
import measproc

DefParam = interface.NullParam

SignalGroups = [
  {
    'Acc': ("ECU", "evi.General_T20.axvRef"),
  },
  {
    'Acc': ("MRR1plus", "evi.General_T20.axvRef"),
  },
]


class cHardBraking(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    Group = Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self, Group):
    return Group

  def search(self, Param, Group):
    Batch = self.get_batch()
    Source = self.get_source('main')

    Time, Acc = Source.getSignalFromSignalGroup(Group, 'Acc')
    AccFilt   = aebs.proc.filters.pt1overSteps(Acc)
    IntervalDict = dict([['HardBraking%d' %Limit,
                          measproc.cEventFinder.compExtSigScal(Time, AccFilt, 
                                                               measproc.less,
                                                               Limit)]
                         for Limit in xrange(-2, -6, -1)])
    for Title, IntervalList in IntervalDict.iteritems():
      Report = measproc.cIntervalListReport(IntervalList,
                                            Title="Report%s" %Title)
      Batch.add_entry(Report, self.NONE)
    pass
