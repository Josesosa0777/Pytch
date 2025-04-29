import collections
import sys

import interface
import analyzeAddLabels

from measproc.Batch import getReportAttr

Param = interface.NullParam

COLUMN_SEP = ':'

class cAnalyze(analyzeAddLabels.cAnalyze):
  def fill(self, Group):
    """
    :ReturnType: dict
    :Return: {Sensor<str>: {Test<str>: {MeasPath<str>: measproc.cIntervalList}}
    """
    Batch = self.get_batch()
    Result = {}
    for Sensor in self.Sensors:
      SensorDict = Result.setdefault(Sensor, {})
      for Test in self.Tests:
        TestDict = SensorDict.setdefault(Test, {})
        Reports = set()
        for Title in analyzeAddLabels.iterTitles(self.ReportTags, 
                                                 self.TitleHead,
                                                 Sensors=(Sensor,),
                                                 Tests=(Test,)):
          Titles = Batch.filter(type='measproc.cFileReport', title=Title)
          Reports = Reports.union(Titles)
        for Entry in Reports:
          Report = Batch.wake_entry(Entry)
          StationaryInts = Report.filter('Stationary')
          MovingInts = Report.filter('Moving')
          RepAttrSet = set(Report.ReportAttrs.keys())
          VoteSet = set(self.Votes)
          # check if there were intervals present and the labels have been added
          # before
          if    Report.ReportAttrs['NoIntervals']\
            and VoteSet.intersection(RepAttrSet): 
            MeasPath = getReportAttr(Entry, 'MeasPath')
            for Vote in self.Votes:
              VoteDict = TestDict.setdefault(Vote, {})
              Intervals = Report.filter(Vote)
              StatInt = Intervals.intersect(StationaryInts)
              MovInt = Intervals.intersect(MovingInts)
              if MeasPath not in VoteDict:
                VoteDict[MeasPath] = {'Stationary': StatInt, 'Moving': MovInt}
              else:
                VoteStatInt = VoteDict[MeasPath]['Stationary']
                ConvStatInt = VoteStatInt.convertIndices(StatInt)
                VoteMovInt = VoteDict[MeasPath]['Moving']
                ConvMovInt = VoteMovInt.convertIndices(MovInt)
                for Lower, Upper in ConvStatInt.Intervals:
                  VoteStatInt.add(Lower, Upper)
                for Lower, Upper in ConvMovInt.Intervals:
                  VoteMovInt.add(Lower, Upper)
    return Result

  def analyze(self, Param, Result):
    DefVote = [(Vote, 0) for Vote in self.Votes]
    Labels = [('sensor', ''), ('test', ''), ('stance', '')]
    Labels.extend(DefVote)
    Labels = collections.OrderedDict(Labels)
    print COLUMN_SEP.join(Labels)

    Sum = {}
    for Sensor, SensorDict in Result.iteritems():
      SumSensorDict = Sum.setdefault(Sensor, {})
      for Stance in ('Moving', 'Stationary'):
        SumStanceDict = SumSensorDict.setdefault(Stance, {})
        for Test, TestDict in SensorDict.iteritems():
          SumTestDict = SumStanceDict.setdefault(Test, dict(DefVote))
          for Vote, VoteDict in TestDict.iteritems():
            for Intervals in VoteDict.itervalues():
              SumTestDict[Vote] += len(Intervals[Stance])
    for Sensor, SensorDict in Sum.iteritems():
      Labels['sensor'] = Sensor
      for Stance, StanceDict in SensorDict.iteritems():
        Labels['stance'] = Stance
        for Test, TestDict in StanceDict.iteritems():
          Labels['test'] = Test
          Labels.update(TestDict)
          print COLUMN_SEP.join([str(e) for e in Labels.itervalues()])
    sys.stdout.flush()
    pass
