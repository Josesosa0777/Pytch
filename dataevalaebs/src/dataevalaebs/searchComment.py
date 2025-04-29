import measproc
import measparser
import interface

DefParam = interface.NullParam

SignalGroups = [{'Comment': ('', 'Comment'),},]

class cComment(interface.iSearch):
  def check(self):
    Source = self.get_source('main')
    Group = Source.selectSignalGroup(SignalGroups)
    return Group

  def fill(self, Group):
    return Group

  def search(self, Param, Group):
    Source = self.get_source('main')
    Batch = self.get_batch()

    Time, Value = Source.getSignalFromSignalGroup(Group, 'Comment')
    IntervalList = measproc.cIntervalList(Time)
    Report = measproc.cIntervalListReport(IntervalList, 'Comment')
    for i, Comment in enumerate(Value):
      Interval = i, i+1
      Comment = unicode(Comment, 'latin-1')  
      Report.setComment(Interval, Comment)
      Batch.add_entry(Report, self.NONE)
    return
