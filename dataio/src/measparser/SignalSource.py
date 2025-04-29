import hashlib
import os
import sys
import inspect

import numpy

import measparser
import signalgroup
import signalproc
from pyutils.functional import cached_attribute

class cStatus(dict):
  def update(self, Status):
    """
    :Parameters:
      Status : dict
    :Exception:
      KeyError : Status contains a booked key.
    """
    Keys = self.keys()
    Keys = set(Keys)
    StatusKeys = Status.keys()
    StatusKeys = set(StatusKeys)
    CommonKeys = Keys.intersection(StatusKeys)
    if CommonKeys:
      Message = ', '.join(CommonKeys)
      Message = 'Status has booked keys: %s\n' %Message
      raise KeyError, Message
    dict.update(self, Status)


def findParser(Measurement):
  if not os.path.exists(Measurement):
    raise IOError("Measurement not found: '%s'" %Measurement)
  for Name in dir(measparser):
    cParser = getattr(measparser, Name)
    if    inspect.isclass(cParser)\
      and issubclass(cParser, measparser.iParser)\
      and hasattr(cParser, 'checkParser')\
      and cParser.checkParser(Measurement):
      return cParser
  raise IOError("Can't open file. File may be corrupted or No parser found for '%s'" % Measurement)


def get_hash(path):
  sha = hashlib.sha256()
  BLOCKSIZE = 65536
  try:
    with open(path, 'rb') as infile:
      file_buffer = infile.read(BLOCKSIZE)
      while len(file_buffer) > 0:
        sha.update(file_buffer)
        file_buffer = infile.read(BLOCKSIZE)
      return sha.hexdigest()
  except:
    print("Exception while finding hash value for {}".format(path))
    return None

class cSignalSource:
  """Parser independent signal handler of measurement files. save method has to
  be called before the python session is terminated."""
  convTime2Cycle = staticmethod(signalproc.convTime2Cycle)
  rescale        = staticmethod(signalproc.rescale)
  mode           = staticmethod(signalproc.mode)

  def __init__(self, Measurement, NpyHomeDir=None, NeedMemoryParser=True):
    """
    :Parameters:
      cParser : class
        The class of the selected parser.
      Measurement : str
        Path of the selected file.
    :Exceptions:
      IOError : if no parser found for `Measurement`
    """
    self.NpyHomeDir = NpyHomeDir
    """:type: : str
    Path of the directory under the npy backup directories will be put.
    Default value is None.
    In case of default value the directory of the mdf file will be used."""
    self.FileName = Measurement
    """:type: str
    Path of the selected measurement."""
    self.MeasHash = ""
    if NeedMemoryParser:
      self.MemoryParser = measparser.cMemoryParser()
    else:
      self.MemoryParser = measparser.iParser()
    """:type: measproc.cMemoryParser or measparser.iParser
    Container of the parsed signals in the dictionary"""
    self.BackupParser = None
    """:type: `measparser.BackupParser`
    Container of the parsed signals in npy files"""
    self.cParser = None
    """:type: `measparser.iParser`
    The class of the selected parser."""
    self.Status = cStatus()
    """:type: cStatus
    {StatusName<str>:[{Alias<str>: [[ShortDeviceName<str>, SignalName<str>],],}]}"""

    # find parser
    cParser = findParser(Measurement)
    if cParser is measparser.BackupParser:
      self.cParser      = lambda Measurement: measparser.iParser()
      self.BackupParser = cParser.fromDir(Measurement)
      if NpyHomeDir is not None:
        self.createNameDump(Parser=self.BackupParser)
      else:
        self.NameDump = measparser.iParser()
    elif NpyHomeDir is None:
      self.cParser      = cParser
      self.BackupParser = measparser.iParser()
      self.NameDump = measparser.iParser()
    else:
      self.cParser      = cParser
      HdfPath = self.getBackupPath(Ext='.h5')
      Version = cParser.getVersion()
      self.BackupParser = measparser.cHdf5Parser(HdfPath, ParserVersion=Version,
                                                 Measurement=Measurement)
      self.createNameDump()
    self.MeasHash = get_hash(Measurement)
    pass

  def getBackupPath(self, Ext=''):
    BaseFileName = self.getBaseName()
    Path = os.path.join(self.NpyHomeDir, BaseFileName + Ext)
    return Path


  def createNameDump(self, Parser=None):
    NameDumpPath = self.getBackupPath(Ext='.db')
    if os.path.exists(NameDumpPath):
      self.NameDump = measparser.NameDump(unicode(NameDumpPath))
    else:
      if Parser is None:
        self.NameDump = measparser.NameDump.fromMeasurement(self.FileName,
                                                 DbName=unicode(NameDumpPath))
      else:
        self.NameDump = measparser.NameDump.fromParser(Parser,
                                                   DbName=unicode(NameDumpPath))
    return

  def contains(self, DeviceName, SignalName):
    if not self.NameDump.contains(DeviceName, SignalName):
      if not self.MemoryParser.contains(DeviceName, SignalName):
        if not self.BackupParser.contains(DeviceName, SignalName):
          if not self.Parser.contains(DeviceName, SignalName):
            return False
    return True

  def save(self):
    self.BackupParser.save()
    self.NameDump.save()
    if self.Parser is not None:
      self.Parser.close()
      self.Parser = None
    pass

  @cached_attribute
  def Parser(self):
    """:type: `iParser`
    Parser for the measurement file"""
    if self.cParser is measparser.MatParser.cMatParser:
      Parser = self.cParser(self.FileName, time_axis_as_devicename=True)
    else:
      Parser = self.cParser(self.FileName)

    if Parser.ReSorted:
      self.BackupParser = measparser.BackupParser.fromFile(self.FileName,
                                                           self.NpyHomeDir)
    return Parser

  def loadParser(self):
    """Load the parser."""
    return self.Parser

  def isSignalLoaded(self, DeviceName, SignalName):
    """
    The signal can get without parsing measurement file or not.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: bool
    """
    return     self.MemoryParser.contains(DeviceName, SignalName)\
            or self.BackupParser.contains(DeviceName, SignalName)

  def getSignals(self, DeviceName, SignalNames, **kwargs):
    """
    Get the requested signals in list of time, value numpy array pairs.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalNames : list of str
        List of the requested signal names.
    :Keywords:
      Keywords are passed to `getSignal`
    :ReturnType: list of `ndarray` pairs
    :Return:
      List of the requested signals in time, value numpy array pairs.
    """
    return [self.getSignal(DeviceName, SignalName, **kwargs) for SignalName in SignalNames]
    pass

  def getTime(self, TimeKey):
    """
    :Parameters:
      TimeKey : str
    :ReturnType: `numpy.ndarray`
    """
    try:
      Time = self.MemoryParser.getTime(TimeKey)
    except KeyError:
      if self.BackupParser.isMissingTime(TimeKey) \
         or self.NameDump.isMissingTime(TimeKey):
        raise KeyError('%s is a missing timekey in %s' %(TimeKey, self.FileName))
      try:
        Time = self.BackupParser.getTime(TimeKey)
      except KeyError:
        try:
          Time = self.Parser.getTime(TimeKey)
        except KeyError, Error:
          self.BackupParser.addMissingTime(TimeKey)
          raise Error
        else:
          self.BackupParser.addTime(TimeKey, Time)
      self.MemoryParser.addTime(TimeKey, Time)
    Time.flags.writeable = False
    return Time

  def getSignal(self, DeviceName, SignalName, Tmin=None, Tmax=None,
                Imin=None, Imax=None, ScaleTime=None, Order='zoh', Mask=None,
                InvalidValue=None, **kwargs):
    """
    Get the requested signal in time, value numpy array pairs.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
      Tmin : float, optional
        The minimum time of the selected time interval.
      Tmax : float, optional
        The maximum time of the selected time interval.
      Imin : int, optional
        `Time[Imin:]`, `Value[Imin:]`.
      Imax : int, optional
        `Time[:Imax]`, `Value[:Imax]`.
      ScaleTime : `ndarray`, optional
        The scale time of the selected time interval.
      Order : str, optional
        See `signalproc.rescale` method's docstring for details.
      Mask : `ndarray`, optional
        See `signalproc.rescale` method's docstring for details.
      InvalidValue : int or float, optional
        See `signalproc.rescale` method's docstring for details.
    :Keywords:
      Every other keyword argument is passed to the fileparser
    :ReturnType: `ndarray`, `ndarray`
    :Return:
      Time of the requested signal.
      Value of the requested signal.
    """
    if kwargs:
      Value, TimeKey = self.Parser.getSignal(DeviceName, SignalName, **kwargs)
      Time = self.getTime(TimeKey)
    else:
      try:
        Value, TimeKey = self.MemoryParser.getSignal(DeviceName, SignalName)
        Time = self.getTime(TimeKey)
      except KeyError:
        if self.BackupParser.isMissingSignal(DeviceName, SignalName) \
            or self.NameDump.isMissingSignal(DeviceName, SignalName):
          raise KeyError('%s %s is a missing signal in %s\n' %(DeviceName, SignalName, self.FileName))
        try:
          Value, TimeKey = self.BackupParser.getSignal(DeviceName, SignalName)
          Time = self.getTime(TimeKey)
        except KeyError:
          try:
            Value, TimeKey = self.Parser.getSignal(DeviceName, SignalName)
            Time = self.getTime(TimeKey)
          except KeyError, Error:
            self.BackupParser.addMissingSignal(DeviceName, SignalName)
            raise Error
          else:
            self.BackupParser.addSignal(DeviceName, SignalName, TimeKey, Value)
        self.MemoryParser.addSignal(DeviceName, SignalName, TimeKey, Value)
    Value.flags.writeable = False

    if Imin is not None and Imax is not None:
      Time  = Time[ Imin:Imax]
      Value = Value[Imin:Imax]
    elif Imin is not None:
      Time  = Time[ Imin:]
      Value = Value[Imin:]
    elif Imax is not None:
      Time  = Time[ :Imax]
      Value = Value[:Imax]
    elif Tmin is not None and Tmax is not None:
      Imin  = min(Time.searchsorted(Tmin), Time.size - 1)
      Imax  = min(Time.searchsorted(Tmax), Time.size - 1)
      Time  = Time[ Imin:Imax]
      Value = Value[Imin:Imax]
    elif Tmin is not None:
      Imin  = min(Time.searchsorted(Tmin), Time.size - 1)
      Time  = Time[ Imin:]
      Value = Value[Imin:]
    elif Tmax is not None:
      Imax  = min(Time.searchsorted(Tmax), Time.size - 1)
      Time  = Time[ :Imax]
      Value = Value[:Imax]

    if ScaleTime is not None:
      RescaleBefore = Imin is None and Tmin is None
      RescaleAfter  = Imax is None and Tmax is None
      if not RescaleBefore or not RescaleAfter:
        ScaleTime = signalproc.trim(Time, ScaleTime, RescaleBefore, RescaleAfter)

      Time, Value = signalproc.rescale(Time, Value, ScaleTime,
                                       Order=Order, Mask=Mask,
                                       InvalidValue=InvalidValue)
    return Time, Value

  def getSignalAtPos(self, DeviceName, SignalName, PosTime, Pos):
    """
    Get the value of the selected signal at the requested index of `PosTime`.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the selected signal.
      PosTime : `ndarray`
        Time where the `Pos` index is valid.
      Pos : int
        The selected time position in `PosTime`.
    :ReturnType: int or float
    """
    Time, Value = self.getSignal(DeviceName, SignalName)
    if PosTime is not Time:
      Pos = min(Time.searchorted(PosTime[Pos]), Time.size-1)
    return Value[Pos]

  def convSigTime2Cycle(self, DeviceName, SignalName, TimeInterval):
    """
    Convert the time interval to the cycle interval of the selected signal.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the selected signal.
      TimeInterval : float
        The requested time interval in secundum.
    :ReturnType: int
    """
    Time, Value = self.getSignal(DeviceName, SignalName)
    return self.convTime2Cycle(Time, TimeInterval)

  def selectScaleTime(self, Signals, StrictlyGrowingCheck):
    """
    Select the scale time based on the given status names.

    :Parameters:
      Signals : list
        [(DeviceName<str>, SignalName<str>)]
      StrictlyGrowingCheck : bool
    :Exceptions:
      IndexError : No valid time signal can be found for any
                   status name in `StatusNames`
    :ReturnType: `ndarray`
    """
    Times = {}
    for DeviceName, SignalName in Signals:
      try:
        TimeKey = self.getTimeKey(DeviceName, SignalName)
      except KeyError:
        pass
      else:
        if TimeKey not in Times:
          Times[TimeKey] = self.getTime(TimeKey)
    ScaleTime = signalproc.selectTimeScale(Times.itervalues(),
                                           StrictlyGrowingCheck)
    return ScaleTime

  def getLongestTime(self):
    """
    :Exceptions:
      UnboundLocalError: MemoryParser.Times is empty
    """
    Diff = 0.0
    for _Time in self.MemoryParser.Times.itervalues():
      _Diff = _Time[-1] - _Time[0]
      if _Diff > Diff:
        Time = _Time
        Diff = _Diff
    return Time

  def checkStatus(self, StatusName):
    """
    :Parameters:
      StatusName : str
    :Exceptions:
      KeyError : `Status` does not contain `StatusName`
    :RetrunType: bool
    """
    SignalGroups = self.Status[StatusName]
    try:
      Group = self.selectSignalGroup(SignalGroups)
    except ValueError:
      return False
    else:
      return True

  def filterByActiveStatus(self, Params):
    """
    Return a list of `Params` values which belongs an active status.

    :Parameters:
      Params : dict
        {StatusName<str> : YouKnowBetter}
    :ReturnType: list
    """
    Result = []
    for Key, Value in Params.iteritems():
      try:
        Flag = self.checkStatus(Key)
      except KeyError:
        pass
      else:
        if Flag:
          Result.append(Value)
    return Result

  def groupStatusNames(self, StatusNames=None):
    """
    Return active (available) and passive status names.

    :Parameters:
      StatusNames : iterable
        Grouping is done only on the given status names
    :ReturnType: set, set
    """
    Actives = set()
    Passives = set()
    if StatusNames is None:
      ActStatusNames = self.Status.iterkeys()
    else:
      ActStatusNames = \
        [StatusName for StatusName in self.Status.iterkeys() if StatusName in StatusNames]
    for StatusName in ActStatusNames:
      if self.checkStatus(StatusName):
        Actives.add(StatusName)
      else:
        Passives.add(StatusName)
    return Actives, Passives

  def activateDeviceNames(self, Signals):
    Actuals = []
    for DeviceName, SignalName in Signals:
      try:
        DeviceName, = self.getExtendedDeviceNames(DeviceName, FavorMatch=True)
      except ValueError:
        raise ValueError('%s is not unique in %s\n' %(DeviceName,self.FileName))
      Signal = DeviceName, SignalName
      Actuals.append(Signal)
    return Actuals

  def checkSignal(self, DeviceName, SignalName):
    try:
      Time, Value = self.getSignal(DeviceName, SignalName)
    except KeyError:
      return False
    else:
      if Time.size == 0:
        return False
    return True

  def getSignalLength(self, DeviceName, SignalName):
    SignalLen = 0
    try:
      SignalLen = self.MemoryParser.getSignalLength(DeviceName, SignalName)
    except KeyError:
      try:
        SignalLen = self.NameDump.getSignalLength(DeviceName, SignalName)
      except KeyError:
        try:
          SignalLen = self.BackupParser.getSignalLength(DeviceName, SignalName)
        except KeyError:
          try:
            SignalLen = self.Parser.getSignalLength(DeviceName, SignalName)
          except KeyError:
            pass
    return SignalLen

  def _filterSignalGroups(self, SignalGroups, StrictTime=False,
                                              TimeMonGapIdx=None,
                                              TimeMonGapEps=1e-8):
    """
    Create a same sized list of dictionaries where only the valid signals are present.
    The shape of the dictionaries are the same like in the input only the short device name
    is replaced with extended device name.

    :Parameters:
      SignalGroups : list
        [{Alias<str>: (ShortDeviceName<str>, SignalName<str>)}]
      StrictTime : bool
        Enable the strictly growing time check.
        default is False
      TimeMonIdx : int
        Time indexes until the monoton time is enabled.
        Available only if in case of `StrictTime`.
        default None means no cheat is enabled
      TimeMonGapEps : float
        Two time stamps between that epsilon will be assumed as equal (monoton)
        Available only if in case of `StrictTime`.
        default is 1e-8
    :ReturnType: list, list
    :Return:
      [{Alias<str>: (ExtendedDeviceName, SignalName<str>)}]
      [{'Missing signals': {ExtendedDeviceName<str>: {SignalName<str>}},
        'Missing devices': {ShortDeviceName<str>},
        'Empty signals': {ExtendedDeviceName<str>: {SignalName<str>}},
        'Invalid times': {ExtendedDeviceName<str>: {SignalName<str>}},
        'Multiple device names': {ShortDeviceName: {ExtendedDeviceName<str>}}}]
    """
    Errors = []
    FilteredGroups = []
    for SignalGroup in SignalGroups:
      FilteredGroup = {}
      Error = {'Missing signals': {},
               'Missing devices': set(),
               'Empty signals': {},
               'Invalid times': {},
               'Multiple device names': {}}
      for Alias, (DeviceName, SignalName) in SignalGroup.iteritems():
        original_signal_name = SignalName
        if len(original_signal_name.split('[:,')) == 2:
          (SignalName, index) = original_signal_name.split('[')

        DeviceNames = list(set(self.getNames(SignalName, DeviceName, FavorMatch=True)))
        if not DeviceNames:
          if not self.getExtendedDeviceNames(DeviceName, FavorMatch=True):
            Error['Missing devices'].add(DeviceName)
          else:
            Missings = Error['Missing signals'].setdefault(DeviceName, set())
            Missings.add(SignalName)
        elif len(DeviceNames) > 1:
          Multiples = Error['Multiple device names'].setdefault(DeviceName, set())
          Error['Multiple device names'][DeviceName] = Multiples.union(DeviceNames)
        else:
          DeviceName, = DeviceNames
          SignalLen = self.getSignalLength(DeviceName, SignalName)
          if SignalLen == 0:
            Missings = Error['Empty signals'].setdefault(DeviceName, set())
            Missings.add(SignalName)
          else:
            try:
              TimeKey = self.getTimeKey(DeviceName, SignalName)
            except KeyError:
              Missings = Error['Missing signals'].setdefault(DeviceName, set())
              Missings.add(SignalName)
            else:
              Time = self.getTime(TimeKey)
              if Time.size == 0:
                Empties = Error['Empty signals'].setdefault(DeviceName, set())
                Empties.add(SignalName)
              elif StrictTime:
                if TimeMonGapIdx is not None:
                  dTime = numpy.diff(Time)
                  if (dTime < -TimeMonGapEps).any():
                    InvalidTimes = Error['Invalid times'].setdefault(DeviceName, set())
                    InvalidTimes.add(SignalName)
                  else:
                    Mask = numpy.abs(dTime) < TimeMonGapEps
                    Mask = numpy.concatenate([Mask, [False]])
                    Mask = Mask.tolist()
                    b = 0
                    Crash = False
                    while True:
                      try:
                        a = Mask.index(True, b)
                      except ValueError:
                        break
                      b = Mask.index(False, a)
                      if b - a > TimeMonGapIdx:
                        InvalidTimes = Error['Invalid times'].setdefault(DeviceName, set())
                        InvalidTimes.add(SignalName)
                        Crash = True
                        break
                    if not Crash:
                      FilteredGroup[Alias] = DeviceName, SignalName
                elif (numpy.diff(Time) <= 0).any():
                  InvalidTimes = Error['Invalid times'].setdefault(DeviceName, set())
                  InvalidTimes.add(SignalName)
              else:
                FilteredGroup[Alias] = DeviceName, original_signal_name
      FilteredGroups.append(FilteredGroup)
      Errors.append(Error)
    return FilteredGroups, Errors

  def strSignalGroupError(self, Errors):
    """
    :Peremeters:
      Errors : list
        [{'Missing signals': {ExtendedDeviceName<str>: {SignalName<str>}},
          'Missing devices': {ShortDeviceName<str>},
          'Empty signals': {ExtendedDeviceName<str>: {SignalName<str>}},
          'Invalid times': {ExtendedDeviceName<str>: {SignalName<str>}},
          'Multiple device names': {ShortDeviceName: {ExtendedDeviceName<str>}}}]
    :ReturnType: str
    """
    Message = signalgroup.str_errors(Errors)
    return Message

  def selectSignalGroup(self, SignalGroups, GetIndex=False, **KwArgs):
    """
    Select the first valid signal group from `SignalGroups`.

    :Parameters:
      SignalGroups : list
        It is assumed that the list contains concurrent singal group dictionaries,
        i.e. with the same alias key set (therefore same size).
        [{Alias<str>: (ShortDeviceName<str>, SignalName<str>)}]
      GetIndex : bool
        Flag to extend the result with the index of the selected signal group.
        Default is False
    :Keywords:
      Any valid optional parameter to _filterSignalGroups()
    :ReturnType: `signalgroup.SignalGroup`
    """
    Group = signalgroup.SignalGroup.from_first_valid(SignalGroups, self,
                                                     **KwArgs)
    if GetIndex:
      Group = Group, Group.winner
    return Group

  def selectLazySignalGroup(self, SignalGroups, Verbose=False,
                            DefResults=None, **KwArgs):
    """
    Select the longest filtered signal group, i.e. the signal group containing
    the most available signals.
    In case of same length after filtering, the first group will win.

    :Parameters:
      SignalGroups : list
        [{Alias<str>: (ShortDeviceName<str>, SignalName<str>)}]
      Verbose : bool
        If true, prints the error message on the standard error.
      DefResults : dict
        Will be passed to `signalgroup.SignalGroup.from_longest()`.
    :Keywords:
      Any valid optional parameter to _filterSignalGroups()
    :ReturnType: `signalgroup.SignalGroup`
    """
    if Verbose:  # for backward compatibility
      FilteredSignalGroups = self.filterSignalGroups(
        SignalGroups, Verbose=Verbose, **KwArgs)
    Group = signalgroup.SignalGroup.from_longest(SignalGroups, self,
      def_results=DefResults, **KwArgs)
    return Group

  def selectSignalGroupOrEmpty(self, SignalGroups, Verbose=False, **KwArgs):
    """
    Wrapper for 'selectLazySignalGroup()'.
    The resulting SignalGroup instance will return empty-like objects
    (e.g. empty array, empty string etc.) in case a signal is missing or
    invalid.
    """
    return self.selectLazySignalGroup(SignalGroups, Verbose=Verbose,
      DefResults=signalgroup.SignalGroup.all_def_results['empty'], **KwArgs)

  def selectSignalGroupOrNone(self, SignalGroups, Verbose=False, **KwArgs):
    """
    Wrapper for 'selectLazySignalGroup()'.
    The resulting SignalGroup instance will return None objects
    in case a signal is missing or invalid.
    """
    return self.selectLazySignalGroup(SignalGroups, Verbose=Verbose,
      DefResults=signalgroup.SignalGroup.all_def_results['None'], **KwArgs)

  def validateSignalGroups(self, SignalGroups, **KwArgs):
    """
    Double or quits test. Checks every signal in each signal group, raising exception if
    any of the signals is not present, otherwise returns the same signal groups list
    as the input parameter with extended device names.

    :Parameters:
      SignalGroups : list
        [{Alias<str>: (ShortDeviceName<str>, SignalName<str>)}]
    :Keywords:
      Any valid optional parameter to _filterSignalGroups()
    :ReturnType: list
    :Return: [{Alias<str>: (ExtendedDeviceName<str>, SignalName<str>)}]
    """
    Groups, Errors = self._filterSignalGroups(SignalGroups, **KwArgs)
    signalgroup.check_by_original(SignalGroups, Groups, Errors)
    return Groups

  def filterSignalGroups(self, SignalGroups, Verbose=False, **KwArgs):
    """
    Create a same sized list of dictionaries where only the valid signals are present.
    The shape of the dictionaries are the same like in the input only the short device name
    is replaced with extended device name.

    :Parameters:
      SignalGroups : list
        [{Alias<str>: (ShortDeviceName<str>, SignalName<str>)}]
      Verbose: bool
        If true, prints the error message on the standard error.
    :Keywords:
      Any valid optional parameter to _filterSignalGroups()
    """
    Groups, Errors = self._filterSignalGroups(SignalGroups, **KwArgs)
    if Verbose:
      Message = signalgroup.str_errors(Errors)
      sys.stderr.write('%s\n'%Message)
    return Groups

  def selectFilteredSignalGroup(self, SignalGroups, DefResults=None, **KwArgs):
    """
    Select the longest filtered signal group.
    In case of same length the first will win.

    :Parameters:
      SignalGroups : list
        [{Alias<str>: (ShortDeviceName<str>, SignalName<str>)}]
      DefResults : dict
        Will be passed to `signalgroup.SignalGroup.from_longest()`.
    :Keywords:
      Any valid optional parameter to _filterSignalGroups()
    """
    Group = signalgroup.SignalGroup.from_longest(SignalGroups, self,
      def_results=DefResults, **KwArgs)
    return Group

  def getSignalFromSignalGroup(self, SignalGroup, Alias, Gains=None, **kwargs):
    DeviceName, SignalName = SignalGroup[Alias]
    Time, Value = self.getSignal(DeviceName, SignalName, **kwargs)
    if Gains and Alias in Gains:
      Value = Gains[Alias] * Value
    return Time, Value

  def getPhysicalUnitFromSignalGroup(self, SignalGroup, Alias):
    DeviceName, SignalName = SignalGroup[Alias]
    Unit = self.getPhysicalUnit(DeviceName, SignalName)
    return Unit


  def getSignalNames(self,
                     PosDeviceTags, NegDeviceTags,
                     PosSignalTags, NegSignalTags,
                     MatchCase=True,
                     DisableEmpty=True):
    """
    Get the signal names, that contain the input strings.

    :Parameters:
      PosDeviceTag : list
        Tags that have to be in the device name
      NegDeviceTag : list
        Tags that doas not have to be in the device name
      PosSignalTag : list
        Tags that have to be in the signal name
      NegSignalTag : list
        Tags that doas not have to be in the signal name
    :KeyWords:
      MatchCase : bool
        Default True
      DisableEmpty : bool
        Do not search in signal names which are empty.
        Default True
    :ReturnType: list
    :Return:     [[DeviceName<str>, Signalame<str>],]
    """
    if isinstance(self.NameDump, measparser.NameDump):
      Parser = self.NameDump
    else:
      Parser = self.Parser
    return Parser.getSignalNames(PosDeviceTags, NegDeviceTags,
                                      PosSignalTags, NegDeviceTags,
                                      MatchCase,
                                      DisableEmpty)

  def getShortDeviceName(self, DeviceName):
    if isinstance(self.NameDump, measparser.NameDump):
      Parser = self.NameDump
    else:
      Parser = self.Parser
    return Parser.getShortDeviceName(DeviceName)

  def getExtendedDeviceNames(self, DeviceName, FavorMatch=False):
    """
    'AMB' -> ['AMB_23_78', 'AMBIENT_98_9']
    
    WARNING:
    This function returns the list of the recently used device names only,
    the measurement might contain additional devices.
    Use
      Source.loadParser()
      Source.getExtendedDeviceNames(DeviceName)
    to get all of them.

    :Parameters:
      DeviceName : str
    :ReturnType: list
    """
    if self.BackupParser.isMissingDevice(DeviceName):
      return []
    DeviceNames = self.NameDump.getExtendedDeviceNames(
      DeviceName, FavorMatch=FavorMatch)
    if DeviceNames == []:
      DeviceNames = self.MemoryParser.getExtendedDeviceNames(
        DeviceName, FavorMatch=FavorMatch)
      if DeviceNames == []:
        DeviceNames = self.BackupParser.getExtendedDeviceNames(
          DeviceName, FavorMatch=FavorMatch)
      if DeviceNames == []:
        DeviceNames = self.Parser.getExtendedDeviceNames(
          DeviceName, FavorMatch=FavorMatch)
        if DeviceNames == []:
          self.BackupParser.addMissingDevice(DeviceName)
    return DeviceNames

  def getAlias(self, DeviceName, SignalName):
    if isinstance(self.NameDump, measparser.NameDump):
      Parser = self.NameDump
    else:
      Parser = self.Parser
    return Parser.getAlias(DeviceName, SignalName)

  def getDeviceNames(self, SignalName):
    """
    'VehSpeed' -> ['CVS-23-78', 'CVS-98-9']
    WARNING this function returns with the list of the recently used device
    names the measurement can contains more than that.

    Source.getAllDeviceNames(`SignalName`) should be used to get all of them.

    :Parameters:
      DeviceName : str
    :ReturnType: list
    """
    DeviceNames = self.NameDump.getDeviceNames(SignalName)
    if DeviceNames == []:
      DeviceNames = self.MemoryParser.getDeviceNames(SignalName)
    if DeviceNames == []:
      DeviceNames = self.BackupParser.getDeviceNames(SignalName)
    if DeviceNames == []:
      DeviceNames = self.Parser.getDeviceNames(SignalName)
    return DeviceNames

  def getAllDeviceNames(self, SignalName):
    """
    Get names all the devices which contains the `SignalName`.
    WARNING this method will parse the measurement file, that take some extra
    time.

    :Parameters:
      SignaName : str
    :ReturnType: list
    """
    if isinstance(self.NameDump, measparser.NameDump):
      Parser = self.NameDump
    else:
      Parser = self.Parser
    return Parser.getDeviceNames(SignalName)

  def getNames(self, SignalName, Pattern, FavorMatch=False):
    DevNames = self.NameDump.getNames(
      SignalName, Pattern, FavorMatch=FavorMatch)
    if not DevNames:
      DevNames = self.MemoryParser.getNames(
        SignalName, Pattern, FavorMatch=FavorMatch)
    if not DevNames:
      DevNames = self.BackupParser.getNames(
        SignalName, Pattern, FavorMatch=FavorMatch)
    if not DevNames:
      DevNames = self.Parser.getNames(
        SignalName, Pattern, FavorMatch=FavorMatch)
    return DevNames

  def getUniqueName(self, SignalName, Pattern, FavorMatch=False):
    DevNames = self.getNames(SignalName, Pattern, FavorMatch=FavorMatch)
    assert DevNames, 'No device name found for %s, %s' %(SignalName, Pattern)
    assert len(DevNames) < 2, 'Multiple device names found for %s, %s'\
                                 %(SignalName, Pattern)
    DevName, = DevNames
    return DevName

  def getPhysicalUnit(self, DeviceName, SignalName):
    """
    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: str
    """
    if isinstance(self.NameDump, measparser.NameDump):
      Parser = self.NameDump
    else:
      Parser = self.Parser
    return Parser.getPhysicalUnit(DeviceName, SignalName)

  def getFileComment(self):
    """
    :ReturnType: str
    """
    if self.BackupParser.FileComment == '':
      self.BackupParser.FileComment = self.Parser.FileComment
    return self.BackupParser.FileComment
  FileComment = property(getFileComment)

  def getBaseName(self):
    """ Get measurement file base name
    :ReturnType: str
    """
    return os.path.basename(self.FileName)
  BaseName = property(getBaseName)

  def getTimeKey(self, DeviceName, SignalName):
    """
    Get the time key of the selected signal

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: str
    """
    try:
      TimeKey = self.NameDump.getTimeKey(DeviceName, SignalName)
    except KeyError:
      try:
        TimeKey = self.MemoryParser.getTimeKey(DeviceName, SignalName)
      except KeyError:
        try:
          TimeKey = self.BackupParser.getTimeKey(DeviceName, SignalName)
        except KeyError:
          TimeKey = self.Parser.getTimeKey(DeviceName, SignalName)
    return TimeKey

  def addSignal(self, DeviceName, SignalName, TimeKey, Value):
    """
    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
      TimeKey : str
        Time key of the selected signal.
      Value : `ndarray`
        The value of the selected signal.
    """
    self.BackupParser.addSignal(DeviceName, SignalName, TimeKey, Value)
    self.MemoryParser.addSignal(DeviceName, SignalName, TimeKey, Value)
    pass

  def addTime(self, TimeKey, Time):
    """
    :Parameters:
      TimeKey : str
        Time key of the selected time.
      Time : `ndarray`
        The value of the selected time.
    """
    self.BackupParser.addTime(self, TimeKey, Time)
    self.MemoryParser.addTime(self, TimeKey, Time)
    pass

  def split(self, Report, **kwargs):
    """
    :Parameters:
      Report : measproc.cReport
      VideoFile : str
    :Keywords:
      VideoFile : str
        Default value is False
    :Exceptions:
      ValueError : if the `Report` created with an another Measurement.
    """
    try:
      VideoFile = kwargs['VideoFile']
    except KeyError:
      VideoFile = False

    if VideoFile:
      MeasTime, VideoTime = self.getSignal('Multimedia_0_0', 'Multimedia_1')

    Report.save()
    ReportFile  = Report.getTitle(WithoutExt=False)
    ReportTime  = self.getTime(Report.ReportAttrs['TimeKey'])
    TimeFormat  = createFormatString(ReportTime)
    PathFormat  = '%s_%s' %(self.BackupParser.NpyDir, ReportFile)
    PathFormat += '_' + TimeFormat + '-' + TimeFormat
    # load all the signals from the backup parser
    for DeviceName in self.BackupParser.iterDeviceNames():
      for SignalName in self.BackupParser.iterSignalNames(DeviceName):
        self.getSignal(DeviceName, SignalName)
    for Lower, Upper in Report.IntervalList:
      Upper  = min(Upper, ReportTime.size - 1)
      Tmin   = ReportTime[Lower]
      Tmax   = ReportTime[Upper]
      Path   = PathFormat %(Tmin, Tmax)
      Backup = measparser.BackupParser.fromInstance(self.BackupParser, Path)
      Backup.FileComment += '\nChunk of report file: %s interval [%d, %d]' %(ReportFile, Lower, Upper)
      for DeviceName in self.MemoryParser.iterDeviceNames():
        for SignalName in self.MemoryParser.iterSignalNames(DeviceName):
          if not Backup.contains(DeviceName, SignalName):
            # find start and end posistion
            Time, Value = self.getSignal(DeviceName, SignalName)
            TimeKey     = self.getTimeKey(DeviceName, SignalName)
            Imin  = max(Time.searchsorted(Tmin)-1, 0)
            Imax  = Time.searchsorted(Tmax)
            Time  = Time[ Imin:Imax]
            Value = Value[Imin:Imax]
            if DeviceName == 'Multimedia_0_0' and SignalName == 'Multimedia_1':
              VideoMin = Value[0]
              VideoMax = Value[-1]
              Value    = Value - VideoMin
            try:
              Backup.addTime(TimeKey, Time)
            except ValueError:
              pass
            Backup.addSignal(DeviceName, SignalName, TimeKey, Value)
      Backup.save()
      Path = Path+'.avi'
      if VideoFile and not os.path.exists(Path):
        Locals = locals()
        if 'VideoMin' not in Locals or 'VideoMax' not in Locals:
          Imin     = max(MeasTime.searchsorted(Tmin)-1, 0)
          Imax     = max(MeasTime.searchsorted(Tmax)-1, 0)
          VideoMin = VideoTime[Imin]
          VideoMax = VideoTime[Imax]
        measparser.splitVideo(VideoFile, Path, VideoMin, VideoMax)
    pass

  def querySignalNames(self,
                       PosDevTags,
                       NegDevTags,
                       PosSigTags,
                       NegSigTags,
                       MatchCase,
                       DisableEmpty):
    if isinstance(self.NameDump, measparser.NameDump):
      return self.NameDump.querySignalNames(PosDevTags, NegDevTags, PosSigTags,
                                            NegSigTags, MatchCase, DisableEmpty)
    else:
      return self.Parser.querySignalNames(PosDevTags, NegDevTags, PosSigTags,
                                          NegSigTags, MatchCase, DisableEmpty)

  def getSignalShape(self, DevName, SigName):
    dims = self.Parser.getSignalShape(DevName, SigName)
    return dims


def createFormatString(Time):
  """
  :Parameters:
    Time : `numpy.ndarray`
  :ReturnType: str
  :Return: %0D.2f
  """
  Format = '%.2f'
  Digit  = len(Format % Time[-1])
  Format = '%0' + str(Digit) + '.2f'
  return Format

if __name__ == '__main__':
  import pylab
  import optparse

  parser = optparse.OptionParser()
  parser.add_option('-m', '--measurement',
                    help='measurement file, default is %default',
                    default='d:/measurement/dataeval-test/CVR3_B1_2011-02-10_16-53_020.mdf')
  parser.add_option('-u', '--backup-dir',
                    help='backup directory for SignalSource, default is %default',
                    default='D:/measurement/dataeval-test/backup')
  parser.add_option('-p', '--plot',
                    help='Plot the signals, default is %default',
                    default=False,
                    action='store_true')
  Opts, Args = parser.parse_args()

  Tag = 'nMot'

  mySignalSource = cSignalSource(Opts.measurement, Opts.backup_dir)

  Names = mySignalSource.getSignalNames([], [], [Tag], [])
  print '\n'.join(['%-20s %s' %Name for Name in Names])
  assert len(Names) == 2
  Empty = mySignalSource.getSignalNames([], [], [Tag.lower()], [], MatchCase=True)
  print Empty
  assert not Empty

  DevName, SigName = Names[0]
  Time, Value = mySignalSource.getSignal(DevName, SigName)

  SigNames = [SigName for _DevName, SigName in Names if _DevName == DevName]
  Signals = mySignalSource.getSignals(DevName, SigNames)

  if Opts.plot:
    pylab.figure()
    for Time, Value in Signals:
      pylab.plot(Time, Value)
    pylab.show()

  mySignalSource.save()
