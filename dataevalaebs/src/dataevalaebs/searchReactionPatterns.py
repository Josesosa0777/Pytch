import interface
import measproc

LRR3shortDeviceName = 'ECU'
CVR3shortDeviceName = 'MRR1plus'
SensorNames = { LRR3shortDeviceName : 'LRR3',
                CVR3shortDeviceName : 'CVR3'}
REPSignals = {'Prewarning'           : 'repprew.__b_Rep.__b_RepBase.status',
              'Acute Warning'        : 'repacuw.__b_Rep.__b_RepBase.status',
              'Reaction Time Gain'   : 'repretg.__b_Rep.__b_RepBase.status',
              'Deceleration Support' : 'repdesu.__b_Rep.__b_RepBase.status',
             }

SignalGroups = []
for DevName, SensorName in SensorNames.iteritems():
  SignalGroup = {}
  for Description, SignalName in REPSignals.iteritems():
    SignalHead = SignalName.split('.')[0]
    Alias = '%s %s (%s)'%(SensorName, Description, SignalHead)
    SignalGroup[Alias] = (DevName, SignalName)
  SignalGroups.append(SignalGroup)

STATUS_LOCKED = 6
Status2String = {STATUS_LOCKED : 'locked'}
class cParameter(interface.iParameter):
  def __init__(self, status):
    self.status     = status
    self.genKeys()
    self.statusName = Status2String[status]
    pass

STATUS_LOCKED_Param = cParameter(STATUS_LOCKED)

class cSearchReactionPatterns(interface.iSearch):
  def search(self, Param):
    Batch = self.get_batch()
    Source = self.get_source('main')
    TitlePattern = 'Reaction pattern - %s - %s'
    Comment = '%s was inconsistent' %Source.FileName
    FilteredGroups = Source.filterSignalGroups(SignalGroups, Verbose=True)
    for Original, Filtered in zip(SignalGroups, FilteredGroups):
      for Alias, (DevName, SignalName) in Original.iteritems():
        if Alias in Filtered:
          Time, Value = Source.getSignalFromSignalGroup(Filtered, Alias)
          Intervals = Source.compare(Time, Value, measproc.equal, Param.status)
          if len(Intervals) == 0:
            Result = self.FAILED
          else:
            Result = self.PASSED
          Title = TitlePattern %(Alias, Param.statusName)
          Report = measproc.cIntervalListReport(Intervals, Title)
          Batch.add_entry(Report, Result)
        else:
          Result = self.INCONS
          Title = TitlePattern %(Alias, Param.statusName)
          Report = measproc.cEmptyReport(Title)
          Report.ReportAttrs['Comment'] = Comment
          Batch.add_entry(Report, Result)
    pass

if __name__ == '__main__':
  print SignalGroups
