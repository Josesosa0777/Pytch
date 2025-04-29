import interface
import measproc

SignalGroups = [{"CVR2.ats.Po_TC.PO.i0.dxvFilt": ("ECU", "ats.Po_TC.PO.i0.dxvFilt"),
                 "CVR3.ats.Po_TC.PO.i0.dxvFilt": ("MRR1plus", "ats.Po_TC.PO.i0.dxvFilt"),},]

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
      
    Time, ValueCVR2 = Source.getSignalFromSignalGroup(Group, "CVR2.ats.Po_TC.PO.i0.dxvFilt")
    Time, ValueCVR3 = Source.getSignalFromSignalGroup(Group, "CVR3.ats.Po_TC.PO.i0.dxvFilt", ScaleTime=Time)
    dxDiff = abs(ValueCVR2 - ValueCVR3)
    Intervals = Source.compare(Time, dxDiff, measproc.greater, 5)
    #Intervals = Source.compare(Time, ValueCVR3, measproc.greater, 5)
    Report = measproc.cIntervalListReport(Intervals, 'dx difference CVR2 - CVR3')
    Batch.add_entry(Report, self.NONE)
    pass
