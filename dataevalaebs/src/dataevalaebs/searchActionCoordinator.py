import interface
import measproc

ACOSignals = {'Optical information'       : 'acoopti.__b_AcoNoFb.__b_Aco.request_B'            ,
              'Acoustic information'      : 'acoacoi.__b_AcoNoFb.__b_Aco.request_B'            ,
              'Brake jerk'                : 'acobraj.__b_AcoCoFb.__b_Aco.request_B'            ,
              'PEB partial deceleration'  : 'acopebp.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B',
              'PEB extended deceleration' : 'acopebe.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B',
              'PEB max deceleration'      : 'acopebm.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B',
              'XBA deceleration'          : 'acoxbad.__b_AcoDece.__b_AcoCoFb.__b_Aco.request_B',
             }
""":type: dict
Dictionary mapping signal descriptions to signal names"""

LRR3shortDeviceName = 'ECU'
CVR3shortDeviceName = 'MRR1plus'
SensorNames = { LRR3shortDeviceName : 'LRR3',
                CVR3shortDeviceName : 'CVR3'}
""":type: dict
Dictionary mapping short device names to sensor names"""

# signal groups list creation
SignalGroups = []
""":type: dict
Dictionary mapping aliases to (short device name, sensor name) pairs"""
for devName, sensorName in SensorNames.iteritems():
  SignalGroup = {}
  for description, signalName in ACOSignals.iteritems():
    signalHead = signalName.split('.')[0]
    Alias = '%s %s (%s)'%(sensorName, description, signalHead)
    SignalGroup[Alias] = (devName, signalName)
  SignalGroups.append(SignalGroup)

# module parameter class creation
REQUEST_TRUE  = 1
REQUEST_FALSE = 0
Param2String = {REQUEST_TRUE : 'requested',
                REQUEST_FALSE: 'not requested'}
class cParameter(interface.iParameter):
  def __init__(self, request):
    self.request     = request
    """:type: int
    Parameter field used for comparsion with signal"""
    self.genKeys()
    self.requestName = Param2String[request]
    """:type: str
    Parameter field used for report generation"""
    pass
# instantiation of module parameters
REQUESTED_Param     = cParameter(REQUEST_TRUE)
NOT_REQUESTED_Param = cParameter(REQUEST_FALSE)

# class implementing the iSearch interface
class cSearchActionCoordinator(interface.iSearch):
  def search(self, Param):
    Source = self.get_source('main')
    Batch = self.get_batch()
    TitlePattern = 'Action coordinator - %s - %s'

    # query the available signals from the source (note that the return signal groups list
    # has the same number and order of signal group dictionaries as the input signal groups list)
    FilteredGroups = Source.filterSignalGroups(SignalGroups, Verbose=True)
    # comparing the original and the filtered signal group lists
    for Original, Filtered in zip(SignalGroups, FilteredGroups):
      for Alias, (DevName, SignalName) in Original.iteritems():
        # if signal was available in source, alias can be found in the filtered signal group
        if Alias in Filtered:
          Time, Value = Source.getSignalFromSignalGroup(Filtered, Alias)
          Intervals = Source.compare(Time, Value, measproc.equal, Param.request)
          # in case no meaningful interval was found, the result is considered to be failed
          if len(Intervals) == 0:
            Result = self.FAILED
          else:
            Result = self.PASSED
          Title = TitlePattern %(Alias, Param.requestName)
          Report = measproc.cIntervalListReport(Intervals, Title)
          Batch.add_entry(Report, Result)
        else:
          # if signal was not available in source, result is considered to be inconsistent
          Result = self.INCONS
          Title = TitlePattern %(Alias, Param.requestName)
          Report = measproc.cEmptyReport(Title)
          Report.ReportAttrs['Comment'] = '%s was inconsistent' %Source.FileName
          Batch.add_entry(Report, Result)
    pass

if __name__ == '__main__':
  print SignalGroups
