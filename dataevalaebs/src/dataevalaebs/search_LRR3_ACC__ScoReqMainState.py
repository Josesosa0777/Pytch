import interface
import measproc

SignalGroups = [{"ScoRequestedMainState": ("ECU", "sco.AccCoordinationMessage_T20.ACCRequestedMainState"),},]

Parameter = interface.NullParam

class cSearch(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    Group = Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self, Group):
    return Group

  def search(self, Param, Group):
    Source = self.get_source('main')
    Batch = self.get_batch()
      
    Time, Value = Source.getSignalFromSignalGroup(Group, "ScoRequestedMainState")
    Intervals = Source.compare(Time, Value, measproc.not_equal, 2)
    Report = measproc.cIntervalListReport(Intervals, 'ScoRequestedMainState')
    Batch.add_entry(Report, self.NONE)
    pass
