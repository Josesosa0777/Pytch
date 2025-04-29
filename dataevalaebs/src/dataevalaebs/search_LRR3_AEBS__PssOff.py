import interface
import measproc

SignalGroups = [{"sco.PssCoordinationMessage_T20.PSSOff": ("ECU", "sco.PssCoordinationMessage_T20.PSSOff"),},]

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

    Time, Value = Source.getSignalFromSignalGroup(Group, "sco.PssCoordinationMessage_T20.PSSOff")
    Intervals = Source.compare(Time, Value, measproc.equal, 1)
    Report = measproc.cIntervalListReport(Intervals, 'sco.PssCoordinationMessage_T20.PSSOff')
    Batch.add_entry(Report, self.NONE)
    pass
