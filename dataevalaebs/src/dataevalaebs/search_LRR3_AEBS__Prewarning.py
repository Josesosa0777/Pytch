import interface
import measproc

SignalGroups = [{"repprew.__b_Rep.__b_RepBase.status": ("ECU", "repprew.__b_Rep.__b_RepBase.status"),},]

Parameter = interface.NullParam

class cSearch(interface.iSearch):
  def search(self, Param):
    Source = self.get_source('main')
    Batch = self.get_batch()
    Comment = '%s was inconsistent' %Source.FileName

    FilteredGroups = Source.filterSignalGroups(SignalGroups, Verbose=True)
    for Original, Filtered in zip(SignalGroups, FilteredGroups):
      for Alias, (DevName, SignalName) in Original.iteritems():
        if Alias in Filtered:
          Time, Value = Source.getSignalFromSignalGroup(Filtered, Alias)
          Intervals = Source.compare(Time, Value, measproc.equal, 6)
          if len(Intervals) == 0:
            Result = self.FAILED
          else:
            Result = self.PASSED
          Title = Alias
          Report = measproc.cIntervalListReport(Intervals, Title)
          Batch.add_entry(Report, Result)
        else:
          Result = self.INCONS
          Title = Alias
          Report = measproc.cEmptyReport(Title)
          Report.ReportAttrs['Comment'] = Comment
          Batch.add_entry(Report, Result)
    pass
