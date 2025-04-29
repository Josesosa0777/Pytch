#!/usr/bin/python
from datavis import pyglet_workaround  # necessary as early as possible (#164)

import numpy

import measparser
import IntervalList
import relations
import Report
import Statistic

class cEventFinder(measparser.cSignalSource):
  """Event finder for the signals of `cSignalSource`"""
  def compSigSig(self, DeviceName, SignalName, Relation, CompareDeviceName, CompareSignalName):
    """
    Compare two signal of `cSignalSource`.
    
    :Parameters:
      DeviceName : str
        Name of device which contains the first signal of the comparison signal.
      SignalName : str
        Name of the first signal of the comparison.
      Relation : function
        Relation function, that used in comparison. This function must be 
        return with an bool `ndarray`.
      CompareDeviceName : str
        Name of device which contains the second signal of the comparison signal.
      CompareSignalName : str
        Name of the second signal of the comparison.
    :ReturnType: `cIntervalList`
    :Return: List of index interval where the comparison was True.
    """
    Time,        Value        = self.getSignal(DeviceName,        SignalName)
    CompareTime, CompareValue = self.getSignal(CompareDeviceName, CompareSignalName, 
                                               ScaleTime=Time)
    return cEventFinder.compare(Time, Value, Relation, CompareValue)
  
  def compSigExtSig(self, DeviceName, SignalName, Relation, CompareTime, CompareValue):
    """
    Compare a signal of `cSignalSource` with an external signal.
    
    :Parameters:
      DeviceName : str
        Name of device which contains the first signal of the comparison signal.
      SignalName : str
        Name of the `cSignalSource` signal.
      Relation : function
        Relation function, that used in comparison. This function must be 
        return with an bool `ndarray`.
      CompareTime : `ndarray`
        Time of the external signal.
      CompareValue : `ndarray`
        Value of the external signal.
    :ReturnType: `cIntervalList`
    :Return: List of index interval where the comparison was True.
    """
    Time, Value  = self.getSignal(DeviceName, SignalName)
    CompareTime, CompareValue = self.rescale(CompareTime, CompareValue, Time)
    return cEventFinder.compare(Time, Value, Relation, CompareValue)
  
  @staticmethod
  def compExtSigExtSig(Time, Value, Relation, CompareTime, CompareValue):
    """
    Compare two external signal.
    
    :Parameters:
      Time : `ndarray`
        Time of the first external signal in the comparison.
      Value : `ndarray`
        Value of the first external signal in the comparison.
      Relation : function
        Relation function, that used in comparison. This function must be 
        return with an bool `ndarray`.
      CompareTime : `ndarray`
        Time of the second external signal in the comparison.
      CompareValue : `ndarray`
        Value of the second external signal in the comparison.
    :ReturnType: `cIntervalList`
    :Return: List of index interval where the comparison was True.
    """
    CompareTime, CompareValue = measparser.cSignalSource.rescale(CompareTime, CompareValue, Time)
    return cEventFinder.compare(Time, Value, Relation, CompareValue)
  
  def compSigScal(self, DeviceName, SignalName, Relation, Scalar):
    """
    Compare a signal of `cSignalSource` with a scalar.
    
    :Parameters:
      DeviceName : str
        Name of device which contains the first signal of the comparison signal.
      SignalName : str
        Name of the `cSignalSource` signal.
      Relation : function
        Relation function, that used in comparison. This function must be 
        return with an bool `ndarray`.
      Scalar : int or float
        Scalar to compare.
    :ReturnType: `cIntervalList`
    :Return: List of index interval where the comparison was True.
    """
    Time, Value = self.getSignal(DeviceName, SignalName)
    return cEventFinder.compare(Time, Value, Relation, Scalar)
    
  @staticmethod  
  def compExtSigScal(Time, Value, Relation, Scalar):
    """
    Compare an external signal with a scalar.
    
    :Parameters:
      Time : `ndarray`
        Time of the external signal in the comparison.
      Value : `ndarray`
        Value of the external signal.
      Relation : function
        Relation function, that used in comparison. This function must be 
        return with an bool `ndarray`.
      Scalar : int or float
        Scalar to compare.
    :ReturnType: `cIntervalList`
    :Return: List of index interval where the comparison was True.
    """
    return cEventFinder.compare(Time, Value, Relation, Scalar)
  
  @staticmethod
  def compare(Time, Value, Relation, CompareValue):
    """
    Compare the `Value` and `CompareValue` with `Relation`.
    
    :Parameters:
      Time : `ndarray`
        Time of the first signal in the comparison.
      Value : `ndarray`
        First signal in the comparison.
      Relation : function
        Relation function, that used in comparison. This function must be 
        return with a bool `ndarray`.
      CompareValue : `ndarray` or float
        Second signal in the comparison, that can be `ndarray with the same 
        dimension like `Value` or a scalar.
    :ReturnType: `cIntervalList`
    :Return: List of index interval where the comparison was True.
    """
    Indices  = IntervalList.cIntervalList(Time)
    Mask     = Relation(Value, CompareValue)
    MaskList = Mask.tolist()    

    PosL = 0
    PosU = 0    
    while True:
      try:        
        PosL = MaskList.index(True, PosU)
      except ValueError:
        break
      try:
        PosU = MaskList.index(False, PosL)
        Indices.add(PosL, PosU)
      except ValueError:
        Indices.add(PosL, Value.size)
        break
    return Indices
  
  def getSigDomains(self, SignalName):
    """
    Get the intervals of the selected signals domains.
    
    :Parameters:
      SignalName : str
        Name of the selected signal.
    :ReturnType: `cIntervalList`
    """
    Time, Value = self.getSignal(SignalName)
    return cEventFinder.getDomains(Time, Value)
  
  @staticmethod
  def getDomains(Time, Value):
    """
    Get the intervals of the `Value`s domains.
    
    :Parameters:
      Time : `ndarray`
      Value : `ndarray`
    :ReturnType: `cIntervalList`
    """
    Diff      = numpy.ones_like(Value)
    Diff[1:]  = numpy.diff(Value)
    Mask      = Diff != 0
    MaskList  = Mask.tolist()    
    
    Indices   = IntervalList.cIntervalList(Time)
    
    PosL = 0
    PosU = 0    
    while True:
      try:        
        PosL = PosU
        PosU = MaskList.index(True, PosL+1)
        Indices.add(PosL, PosU)
      except ValueError:
        Indices.add(PosL, Value.size)
        break
    return Indices

  def findEvents(self, Events, DistLimitTime):
    """
    :Parameters:
      Events : list
        Container of the selected Events [[ECU<str>, Title<str>, SignalName<str>, CheckValue<int>],]
      DistLimitTime : [s]
        Interval distance limit to merge.
    :ReturnType: list
    :Return:     [<cReport>, ]
    """  
    Reports = []
    for ECU, Title, SignalName, CheckValue in Events:
      Intervals  = self.compSigScal(ECU, SignalName, relations.equal, CheckValue)
      Intervals  = Intervals.merge(DistLimitTime)
      ReportInst = Report.cIntervalListReport(Intervals, Title)
      Reports.append(ReportInst)
    return Reports
  
  @staticmethod
  def splitCoDomain(Time, Value, Start, End, Step):
    Splits = [] 
    for Lower, Upper in zip(numpy.arange(Start, End, Step), numpy.arange(Start+Step, End+Step, Step)):
      Name = '[%s, %s]' %(Lower, Upper)
      Greater = cEventFinder.compare(Time, Value, relations.greater_equal, Lower)
      Less    = cEventFinder.compare(Time, Value, relations.less_equal,    Upper) 
      Split = Greater.intersect(Less)
      Split = Name, Split
      Splits.append(Split)
    return Splits

  @staticmethod
  def convCoDomains(MainTitle, Title, CoDomain, _Title, _CoDomain):
    Names = [[ Title, [Name for Name, Intervals in  CoDomain]],
             [_Title, [Name for Name, Intervals in _CoDomain]]]
    Stat = Statistic.cDinStatistic(MainTitle, Names)   
    for Name, Intervals in CoDomain:
      StatName = Title, Name
      for _Name, _Intervals in _CoDomain:
        _StatName = _Title, _Name
        _Sum = 0.0
        for Lower, Upper in Intervals.iterTime():
          for _Lower, _Upper in _Intervals.iterTime():
            if Upper >= _Lower and Lower <= _Upper:
              _Diff  = min(Upper, _Upper) - max(Lower, _Lower)
              _Sum  += _Diff
        StatNames = StatName, _StatName
        Stat.set(StatNames, _Sum)
    return Stat

if __name__ == '__main__':
  import optparse
  import os
  import sys

  import pylab

  import relations
  
  parser = optparse.OptionParser()
  parser.add_option('-m', '--measurement', 
                    help='measurement file, default is %default',
                    default=r'D:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mdf')
  parser.add_option('-u', '--backup-dir',
                    help='backup directory for SignalSource, default is %default',
                    default=r'D:/measurement/dataeval-test/backup')
  parser.add_option('-p', '--hold-navigator', 
                    help='Hold the navigator, default is %default',
                    default=False,
                    action='store_true')
  Opts, Args = parser.parse_args()
  DevName = 'MRR1plus-0-0'
  SigName = 'evi.General_T20.axvRef'

  status = 0
  if not os.path.isfile(Opts.measurement):
    sys.stderr.write('%s: %s is missing\n' %(__file__, Opts.measurement))
    status += 1
  if not os.path.isdir(Opts.backup_dir):
    sys.stderr.write('%s: %s is missing\n' %(__file__, Opts.backup_dir))
    status += 2
  if status: exit(status)

  myEventFinder = cEventFinder(Opts.measurement, Opts.backup_dir)
  
  IndexIntervals = myEventFinder.compSigScal(DevName, SigName, relations.greater, 0.0)
  
  Time, Value = myEventFinder.getSignal(DevName, SigName)

  if Opts.hold_navigator:
    pylab.figure()
    for Lower, Upper in IndexIntervals:
      pylab.plot(Time[Lower:Upper+1], Value[Lower:Upper+1])    
   
    pylab.show()
  
