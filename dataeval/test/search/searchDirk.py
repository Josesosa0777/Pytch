'''
    Driver Feedback Module (DIRK - Driver Interactive Response Key)

    external Device with two push buttons red and green
    
    When driver is pressing a key, this will be reported on CAN
    
    This search script finds the occurences, when a key was pressed
    
'''
import sys

import interface
import measproc

# -----------------------------------------------------------------------------------------
# SignalGroups dictionary mapping aliases to (short device name, sensor name) pairs"""
#                 AliasName              ShortDeviceName   SignalName
SignalGroups = [{"DFM_green_button":     ("DIRK",           "DFM_green_button"),
                 "DFM_red_button":       ("DIRK",           "DFM_red_button"),},]
                 
DefParam = interface.NullParam


class cDirk(interface.iSearch):
  def check(self):
    # query the available signals from the source (note that the return signal groups list 
    # has the same number and order of signal group dictionaries as the input signal groups list)
    Source = self.get_source('main')
    FilteredGroups = Source.filterSignalGroups(SignalGroups, Verbose=True)
    return FilteredGroups

  def fill(self, FilteredGroups):
    return FilteredGroups

  def search(self, Param, FilteredGroups):
    Source = self.get_source('main')
    Batch = self.get_batch()
    
    fileName  = Source.FileName  # Name of the measurement data file
    
    # query the available signals from the source (note that the return signal groups list 
    # has the same number and order of signal group dictionaries as the input signal groups list)
    FilteredGroups = Source.filterSignalGroups(SignalGroups, Verbose=True)

    # comparing the original and the filtered signal group lists
    for Original, Filtered in zip(SignalGroups, FilteredGroups):
      for Alias, (DevName, SignalName) in Original.iteritems():
        print >> sys.stderr, "Alias", Alias
        Alias_without_underscores = Alias.replace("_","")
        print >> sys.stderr, "Alias_without_underscores", Alias_without_underscores
        # if signal was available in source, alias can be found in the filtered signal group
        if Alias in Filtered:
          Time, Value = Source.getSignalFromSignalGroup(Filtered, Alias)  
          Intervals = Source.compare(Time, Value, measproc.equal, 1.0)
          # in case no meaningful interval was found, the result is considered to be failed
          if len(Intervals) == 0:
            Result = self.FAILED
          else:
            Result = self.PASSED
          Title = Alias_without_underscores
          Report = measproc.cIntervalListReport(Intervals, Title)
          Batch.add_entry(Report, Result)
        else:
          # if signal was not available in source, result is considered to be inconsistent
          Result = self.INCONS
          Title = Alias_without_underscores
          Report = measproc.cEmptyReport(Title)
          Report.ReportAttrs['Comment'] = '%s was inconsistent' %fileName
          Batch.add_entry(Report, Result)
    pass

