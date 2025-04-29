import interface
import measproc

SignalGroups = [{"DFM_red_button": ("DIRK", "DFM_red_button"),
                 "DFM_green_button": ("DIRK", "DFM_green_button"),},]

#class cParameter(interface.iParameter):
#  def __init__(self, SpeedLimit):
#    self.SpeedLimit = SpeedLimit
#    self.genKeys()
#    pass
#
#Parameter = cParameter(65535)
#Parameter2 = cParameter(0)
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
      
    Time, Value = Source.getSignalFromSignalGroup(Group, "DFM_red_button")
    Intervals = Source.compare(Time, Value, measproc.equal, 1)
    Report = measproc.cIntervalListReport(Intervals, 'Red button')
    Batch.add_entry(Report, self.NONE)
    
    Time, Value = Source.getSignalFromSignalGroup(Group, "DFM_green_button")
    Intervals = Source.compare(Time, Value, measproc.equal, 1)
    Report = measproc.cIntervalListReport(Intervals, 'Green button')
    Batch.add_entry(Report, self.NONE)
    pass
