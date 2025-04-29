import interface
import measproc
import numpy

from viewIntroObstacleClassif import isSorted

SignalGroups = [{'Counter03' : ('CVR3_Alive_0x03', 'Counter'),
                 'Counter04' : ('CVR3_Alive_0x04', 'Counter')}]
# module parameter class creation
class cParameter(interface.iParameter):
  def __init__(self, behavior, cycletime):
    self.behavior = behavior
    """:type: str
    Parameter field used for checking if either a reset, a plateau (constant-value interval)
    or a time-lapse is present in the signal."""
    self.cycletime = cycletime
    """:type: float
    Parameter for inputting the cycle time of the signal to be checked."""
    self.genKeys()
    pass
  
# instantiation of module parameters
searchReset = cParameter('reset', 0.02)
searchPlateau = cParameter('plateau', 0.02)
searchTimelapse = cParameter('time-lapse', 0.02)

class cSearchCVR3EnduranceTestResult(interface.iSearch):
  def search(self, Param):
    Source = self.get_source('main')
    Batch = self.get_batch()
    TitlePattern = '%s has %s'

    FilteredGroups = Source.filterSignalGroups(SignalGroups, Verbose=True)
    # comparing the original and the filtered signal group lists
    for Original, Filtered in zip(SignalGroups, FilteredGroups):
      for Alias, (DevName, SignalName) in Original.iteritems():
        # if signal was available in source, alias can be found in the filtered signal group
        if Alias in Filtered:
          Time, Value = Source.getSignalFromSignalGroup(Filtered, Alias)
          # convert signal for isSorted function
          if Value.ndim > 1:
            Value.shape = Value.size
          if Time.ndim > 1:
            Time.shape = Time.size
          ConvValue = numpy.float64(Value)
          ConvTime = numpy.float64(Time)
          
          if Param.behavior == 'reset' or Param.behavior == 'plateau':
            # check if signal has reset or plateau
            if Param.behavior == 'reset':
              Value[0] = 2
              Mask = Value <= 1
            elif Param.behavior == 'plateau':
              Diff = numpy.ones_like(ConvValue)
              Diff[:-1] = numpy.diff(ConvValue)
              Mask = Diff == 0
            Intervals = Source.compare(Time, Mask, measproc.not_equal, 0)
            if len(Intervals) != 0:
              Result = self.PASSED
              Title = TitlePattern % (Alias, Param.behavior)
              Report = measproc.cIntervalListReport(Intervals, Title)
            elif isSorted(ConvValue, 'increasing', True):
              Result = self.FAILED
              Title = TitlePattern % (Alias, 'strictly increased the whole time')
              Report = measproc.cEmptyReport(Title)
            elif isSorted(ConvValue, 'decreasing', True):
              Result = self.FAILED
              Title = TitlePattern % (Alias, 'strictly decreased the whole time')
              Report = measproc.cEmptyReport(Title)
          elif Param.behavior == 'time-lapse':
            # check if timestamp intervals have defects (larger than 3 * cycle time) or not
            Diff = numpy.ones_like(ConvTime) * Param.cycletime
            Diff[1:] = numpy.diff(ConvTime)
            Mask = Diff > (Param.cycletime * 3)
            Intervals = Source.compare(Time, Mask, measproc.not_equal, 0)
            if len(Intervals) != 0:
              Result = self.PASSED
              Title = TitlePattern % ('Timestamp of ' + Alias, Param.behavior)
              Report = measproc.cIntervalListReport(Intervals, Title)
            else:
              Result = self.FAILED
              Title = TitlePattern % ('Timestamp of ' + Alias, 'no defects')
              Report = measproc.cEmptyReport(Title)
              
        # if signal was not available in source, result is considered to be inconsistent
        else:
          Result = self.INCONS
          Title = TitlePattern % (Alias, 'inconsistent result because of unavailable signal')
          Report = measproc.cEmptyReport(Title)
          Report.ReportAttrs['Comment'] = '%s was inconsistent' % Source.FileName
        
        # register report in batch
        Batch.add_entry(Report, Result)
    pass
