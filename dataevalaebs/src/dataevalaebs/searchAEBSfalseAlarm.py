import interface
import measparser
import measproc

SignalGroups = [{'Intro':   ('ECU', 'sit.IntroFinder_TC.Intro.i0.Id'),
                 'repprew': ('ECU', 'repprew.__b_Rep.__b_RepBase.status'),
                 'repretg': ('ECU', 'repretg.__b_Rep.__b_RepBase.status')}]

DefParam = interface.NullParam

TitleSAM = 'Acoustical Warning SAM'
TitleSAS = 'Acoustical Warning SAS'
TitleRelevant = 'Acoustical Warning w/o relevant Intro'
TitleBrake = 'Acoustical Warning w/ following brake intervention'
IntervalLists = {TitleSAM: None, TitleSAS: None, TitleRelevant: None, TitleBrake: None}

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

    Time, Value = Source.getSignalFromSignalGroup(Group, 'repprew')
    RepprewEq6 = Source.compare(Time, Value, measproc.equal, 6)
    IntervalLists[TitleRelevant] = RepprewEq6

    Time, Intro = Source.getSignalFromSignalGroup(Group, 'Intro')
    
    for Check, Title in ((3, TitleSAM), (1, TitleSAS)):
      Intervals = Source.compare(Time, Intro, measproc.equal, Check)
      Intervals = Intervals.intersect(RepprewEq6)
      IntervalLists[Title] = Intervals

    Time, Value = Source.getSignalFromSignalGroup(Group, 'repretg')
    Intervals = Source.compare(Time, Value, measproc.equal, 6)
    Intervals = Intervals.intersect(RepprewEq6)
    IntervalLists[TitleBrake] = Intervals

    for Title, Intervals in IntervalLists.iteritems():
      if len(Intervals):
        Result = self.PASSED
      else:
        Result = self.FAILED
      Report = measproc.cIntervalListReport(Intervals, Title)
      Batch.add_entry(Report, Result)
    pass

  def error(self, Param):
    Source = self.get_source('main')
    Batch = self.get_batch()
    for Title in IntervalLists:
      Report = measproc.cEmptyReport(Title)
      Report.ReportAttrs['Comment'] = '%s was inconsistent' %Source.FileName
      Batch.add_entry(Report, self.INCONS)
    return
