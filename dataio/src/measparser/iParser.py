"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"


import os
import inspect
import datetime

from filenameparser import FileNameParser

DEVICE_NAME_SEPARATOR = '-'


class CommandError(BaseException):
  pass


class Quit(BaseException):
  pass

class iParser:
  """Interface class for the parser classes."""
  ReSorted = False
  """:type: bool
    Flag to show the measurement file was resorted during the parsing or not."""
  DEVICE_NAME_SEPARATOR = DEVICE_NAME_SEPARATOR

  __version__ = 'unknown'

  @classmethod
  def getVersion(cls):
    return ' '.join([cls.__name__, cls.__version__])

  @classmethod
  def getStartDate(cls, FileName):
    """
    getStartDate try to get the start date from filename, if it fits to:
    `%Y.%m.%d.%H.%M.%S' where dot can be any character and the format patterns
    are the same like in strftime.

    If the name pattern fails, then readStartDate will be called for startdate.
    readStartDate is the measurement file specific method, which gets the
    startdate from the content of the file.

    readStartDate may not implemented for the specific parser, in this case
    creation date will be used as startdate, but AssertionError will be risen if
    the file is not present.

    :Parameters:
      FileName : str

    :Exceptions:
      AssertionError : `FileName` does not exists

    :ReturnType: `datetime.datetime`
    """
    try:
      Date = cls.getStartDateFromFileName(FileName)
    except ValueError:
      assert os.path.exists(FileName), '%s does not exists' % FileName
      try:
        Date = cls.readStartDate(FileName)
      except NotImplementedError:
        Date = os.path.getctime(FileName)
        Date = datetime.datetime.fromtimestamp(Date)
    return Date

  @staticmethod
  def getStartDateFromFileName(FileName):
    fn = FileNameParser(FileName)
    if fn is None:
      raise ValueError('Invalid file name: %s' % os.path.basename(FileName))
    return fn.date_tobj

  @classmethod
  def readStartDate(cls, FileName):
    """
    Read the startdate from the content of the measurement file.
    """
    raise NotImplementedError()

  def __init__(self):
    self.Devices = {}
    """:type: dict
    {DeviceName<str>:{SignalName<str>:Magic}}"""
    self.Times = {}
    """:type: dict
    {TimeKey<str>:Time<`numpy.ndarray`>}"""
    self.FileComment = ''
    """:type: str
    Comment of the measurement file."""
    pass

  def iterDeviceNames(self):
    """
    Iterator over the available device names.

    :ReturnType: str
    """
    return self.Devices.iterkeys()

  def iterTimeKeys(self):
    """
    Iterator over the available time keys.

    :ReturnType: str
    """
    return self.Times.iterkeys()

  def contains(self, DeviceName, SignalName):
    """
    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: bool
    """
    Contains = DeviceName in self.Devices and SignalName in self.Devices[DeviceName]
    if Contains:
      TimeKey  = self.getTimeKey(DeviceName, SignalName)
      Contains = TimeKey in self.Times
    return Contains

  def getPhysicalUnit(self, DeviceName, SignalName):
    """
    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: str
    """
    return ''

  def iterSignalNames(self, DeviceName):
    """
    Iterator over the available signal names of the `DeviceName` in the
    measurement file.

    :Parameters:
      DeviceName : str
    :ReturnType: dictionary-keyiterator
    """
    return self.Devices[DeviceName].iterkeys()

  def getDeviceNames(self, SignalName):
    """
    Get the device names which contain the `SignalName`.

    :Parameters:
      SignalName : str
        Name of the selected signal.
    :ReturnType: list
    """
    DeviceNames = []
    for DeviceName, Signals in self.Devices.iteritems():
      if SignalName in Signals:
        DeviceNames.append(DeviceName)
    return DeviceNames

  def getExtendedDeviceNames(self, DeviceName, FavorMatch=False):
    """
    'AMB'     -> ['AMB-23-78', 'AMB-98-9']
    'AMB-23'  -> ['AMB-23-78',]
    'AMB-*-9' -> ['AMB-98-9',]

    :Parameters:
      DeviceName : str
      FavorMatch : bool, optional
    :ReturnType: list
    """
    DeviceNames = [Name
            for Name in self.iterDeviceNames()
            if Name.startswith(DeviceName)]
    if FavorMatch and DeviceName in DeviceNames:
      DeviceNames = [DeviceName]  # return only the matching device
    return DeviceNames

  def getExtendedSignalInformation(self, DeviceName, SignalName):
    """
    Get the extended information of signal
    """
    raise NotImplementedError()

  def getNames(self, SignalName, Pattern, FavorMatch=False):
    """
    Get the DeviceNames which contain `SignalName` and start with `Pattern`.

    If `FavorMatch` is True, and `Pattern` is an existing device name, return
    only the matching device name, regardless of possible other devices that
    start with `Pattern`. Default is False - returning all device names that
    start with `Pattern`.

    :Parameters:
      SignalName : str
        Name of the selected signal.
      Pattern : str
        Beginning of the name of device which contains the selected signal.
      FavorMatch : bool, optional
        See method description.
    :ReturnType: list
    :Return: [DeviceName<str>]
    """
    DeviceNames = [DeviceName
            for DeviceName in self.iterDeviceNames()
            if    DeviceName.startswith(Pattern)
              and SignalName in self.Devices[DeviceName]]
    if FavorMatch and Pattern in DeviceNames:
      DeviceNames = [Pattern]  # return only the matching device
    return DeviceNames

  def getShortDeviceName(self, DeviceName):
    """
    Get the shortest unique name from `DeviceName`

    :ReturnType: str
    """
    Pos = 0
    for i in xrange(DeviceName.count(DEVICE_NAME_SEPARATOR)):
      Pos = DeviceName.find(DEVICE_NAME_SEPARATOR, Pos)
      Check = DeviceName[:Pos]
      try:
        DeviceName, = self.getExtendedDeviceNames(Check, FavorMatch=False)
      except ValueError:
        pass
      else:
        break
      Pos += 1
    else:
      Check = DeviceName
    return Check

  def getAlias(self, DeviceName, SignalName):
    """
    Get the shortest unique name from `DeviceName` which contains `SignalName`

    :ReturnType: str
    """
    Pos = 0
    for i in xrange(DeviceName.count(DEVICE_NAME_SEPARATOR)):
      Pos = DeviceName.find(DEVICE_NAME_SEPARATOR, Pos)
      Check = DeviceName[:Pos]
      DeviceNames = self.getNames(SignalName, Check, FavorMatch=False)
      if len(DeviceNames) == 1:
        break
      Pos += 1
    else:
      Check = DeviceName
    return Check, SignalName

  def close(self):
    pass

  def getTimeKey(self, DeviceName, SignalName):
    """
    Get the time key of the selected signal

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the selected signal.
    :ReturnType: str
    :Exceptions:
      KeyError : if the `DeviceName` or `SignalName` is incorrect.
    """
    raise KeyError, ('%s.%s' %(DeviceName, SignalName))

  def getSignal(self, DeviceName, SignalName):
    """
    Get a signal from the measurement file.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: `ndarray`, str
    :Return:     Values of the requested signal.
                 Timekey of the requested signal.
    :Exceptions:
      KeyError : if the `DeviceName` or `SignalName` is incorrect.
    """
    raise KeyError, ('%s.%s' %(DeviceName, SignalName))

  def getSignalShape(self, DeviceName, SignalName):
    import logging
    logger = logging.getLogger()
    logger.warning('Parser does not know the shape of the signal, assuming one dimension')
    return [0]

  def getSignalLength(self, DeviceName, SignalName):
    """
    Get the length of the selected signal.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: int
    :Exceptions:
      KeyError : if the `DeviceName` or `SignalName` is incorrect.
    """
    raise KeyError, ('%s.%s' %(DeviceName, SignalName))

  def getConversionRule(self, DeviceName, SignalName):
    """
    Get the conversion rule (lookup table) of the selected signal.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: dict
    """
    return {}

  def isSignalEmpty(self, DeviceName, SignalName):
    """
    Get the length of the selected signal.

    :Parameters:
      DeviceName : str
        Name of device which contains the selected signal.
      SignalName : str
        Name of the requested signal.
    :ReturnType: bool
    :Exceptions:
      KeyError : if the `DeviceName` or `SignalName` is incorrect.
    """
    return self.getSignalLength(DeviceName, SignalName) == 0

  def getTime(self, TimeKey):
    """
    Get a time channel from the measurement file.

    :Parameters:
      TimeKey : str
        Key of the time channel.
    :ReturnType: `ndarray`
    :Exceptions:
      KeyError : if the `TimeKey` is incorrect.
    """
    raise KeyError, TimeKey

  def querySignalNames(self,
                       PosDevTags,
                       NegDevTags,
                       PosSigTags,
                       NegSigTags,
                       MatchCase,
                       DisableEmpty):
    """
    Get the aliases, that contain the input strings.

    :Parameters:
      PosDevTags : list
        Tags that have to be in the device name
      NegDevTags : list
        Tags that doas not have to be in the device name
      PosSigTags : list
        Tags that have to be in the signal name
      NegSigTags : list
        Tags that doas not have to be in the signal name
    :KeyWords:
      MatchCase : bool
      DisableEmpty : bool
        Do not search in signal names which are empty.
    :ReturnType: list
    :Return:     [[ShortDeviceName<str>, Signalame<str>],]
    """
    NameChecks = {}
    Names = []

    if not MatchCase:
      PosSigTags = [Tag.lower() for Tag in PosSigTags]
      NegSigTags = [Tag.lower() for Tag in NegSigTags]
      PosDevTags = [Tag.lower() for Tag in PosDevTags]
      NegDevTags = [Tag.lower() for Tag in NegDevTags]

    for DeviceName in self.iterDeviceNames():
      for SignalName in self.iterSignalNames(DeviceName):
        if DisableEmpty and self.isSignalEmpty(DeviceName, SignalName):
          continue
        if MatchCase:
          CheckName = SignalName
        else:
          CheckName = SignalName.lower()

        if checkName(CheckName, PosSigTags, NegSigTags):
          ShortDevName, SignalName = self.getAlias(DeviceName, SignalName)
          if MatchCase:
            CheckName = ShortDevName
          else:
            CheckName = ShortDevName.lower()
          if CheckName in NameChecks:
            Check = NameChecks[CheckName]
          else:
            Check = checkName(CheckName, PosDevTags, NegDevTags)
            NameChecks[CheckName] = Check
          if Check:
            Names.append((ShortDevName, SignalName))
    Names.sort()
    return Names

  def getSignalNames(self,
                     PosDevTags, NegDevTags,
                     PosSigTags, NegSigTags,
                     MatchCase,
                     DisableEmpty):
    """
    Get the signal names, that contain the input strings.

    :Parameters:
      PosDevTags : list
        Tags that have to be in the device name
      NegDevTags : list
        Tags that doas not have to be in the device name
      PosSigTags : list
        Tags that have to be in the signal name
      NegSigTags : list
        Tags that doas not have to be in the signal name
    :KeyWords:
      MatchCase : bool
      DisableEmpty : bool
        Do not search in signal names which are empty.
    :ReturnType: list
    :Return:     [[DeviceName<str>, Signalame<str>],]
    """
    Names = []
    DeviceNames = self.iterDeviceNames()
    DeviceNames = filterNames(DeviceNames, PosDevTags, NegDevTags, MatchCase)
    for DeviceName in DeviceNames:
      SignalNames = self.iterSignalNames(DeviceName)
      SignalNames = filterNames(SignalNames,PosSigTags,NegSigTags, MatchCase)
      for SignalName in SignalNames:
        if DisableEmpty and self.isSignalEmpty(DeviceName, SignalName):
          continue
        Names.append((DeviceName, SignalName))
    Names.sort()
    return Names

  def save(self):
    return

  def addTime(self, TimeKey, Time):
    return

  def addSignal(self, DeviceName, SignalName, TimeKey, Signal):
    return

  def isMissingSignal(self, DeviceName, SignalName):
    return False

  def addMissingDevice(self, DeviceName):
    pass

  def addMissingSignal(self, DeviceName, SignalName):
    return

  def isMissingDevice(self, DeviceName):
    return False

  def addMissingTime(self, TimeKey):
    pass

  def isMissingTime(self, TimeKey):
    return False

  def getMeasSignalLength(self, DeviceName, SignalName):
    return self.getSignalLength(DeviceName, SignalName)

  def cmd_e(self, dev_name, sig_name):
    """
    export signal
    device-name signal-name
    """
    value, timekey = self.getSignal(dev_name, sig_name)
    time = self.getTime(timekey)
    return [('time',  str(time)),
            ('value', str(value))]

  def cmd_edn(self, dev_name):
    """
    extended device name
    short-device-name
    """
    return [(name,) for name in self.getExtendedDeviceNames(dev_name)]

  def cmd_sdn(self, sig_name, pattern):
    """
    device names of signal where device name starts with pattern
    signal-name device-name-head-pattern
    """
    return [(name,) for name in self.getNames(sig_name, pattern)]

  def cmd_udn(self, dev_name):
    """
    short device name
    device-name
    """
    short = self.getShortDeviceName(dev_name)
    return [(short,)]

  def cmd_f(self, *line):
    """
    find signal name with the following tags
    [pdt positive-device-tag]...
    [ndt negative-device-tag]...
    [pst positive-signal-tag]...
    [nst negative-signal-tag]...
    [all]
    [mc]  matchcase search
    [de]  disable empty signal
    """
    pos_dev_tags,\
    neg_dev_tags,\
    pos_sig_tags,\
    neg_sig_tags,\
    matchcase,\
    dis_empty = get_search_patterns(line)
    return self.getSignalNames(pos_dev_tags, neg_dev_tags,
                               pos_sig_tags, neg_sig_tags,
                               matchcase,
                               dis_empty)

  def cmd_query(self, *line):
    """
    find alias with the following tags
    [pdt positive-device-tag]...
    [ndt negative-device-tag]...
    [pst positive-signal-tag]...
    [nst negative-signal-tag]...
    [all]
    [mc]  matchcase search
    [de]  disable empty signal
    """
    pos_dev_tags,\
    neg_dev_tags,\
    pos_sig_tags,\
    neg_sig_tags,\
    matchcase,\
    dis_empty = get_search_patterns(line)
    return self.querySignalNames(pos_dev_tags, neg_dev_tags,
                                 pos_sig_tags, neg_sig_tags,
                                 matchcase,
                                 dis_empty)

  def cmd_as(self, dev_name, sig_name):
    """
    alias for signal groups value
    device-name signal-name
    """
    return [self.getAlias(dev_name, sig_name)]

  @classmethod
  def cmd_h(cls):
    """
    get the command helps
    """
    return sorted([(name[4:], getattr(cls, name).__doc__)
                   for name in dir(cls)
                   if name.startswith('cmd_')])

  def cmd_q(self):
    """
    quit
    """
    raise Quit()

  def communicate(self, line):
    cmd = []
    ftr = []
    for word in line.split():
      if word.startswith('$'):
        ftr.append(word[1:])
      else:
        cmd.append(word)

    if not cmd:
      return []

    name = 'cmd_%s' %cmd[0]
    if not hasattr(self, name):
      raise CommandError('%s is not a registered command\n' %cmd[0])

    func = getattr(self, name)

    if    inspect.getargspec(func).varargs is None\
      and func.func_code.co_argcount != len(cmd):
      raise CommandError('Invalid call of %s\n' %cmd[0])

    answer = func(*cmd[1:])

    if ftr:
      answerdict = dict(answer)
      answer = [(answerdict[word],)
                for word in ftr
                if word in answerdict]
    return answer


def checkName(Name, PosTags, NegTags):
  """
  Decide whether `Name` fits to the input tags.

  :Parameters:
    Name : str
      Name to be filtered
    PosTags : list
      Tags that have to be in the name.
    NegTags : list
      Tags that do not have to be in name.
  :ReturnType: bool
  """
  IsSimilar = False
  for Tag in NegTags:
    if Tag in Name:
      break
  else:
    for Tag in PosTags:
      if Tag not in Name:
        break
    else:
      IsSimilar = True
  return IsSimilar

def filterNames(Names, PosTags, NegTags, MatchCase):
  """
  Filter `Names` based on input tags.

  :Parameters:
    Names : iterable
      Names to filter
    PosTags : list
      Tags that have to be in the name.
    NegTags : list
      Tags that do not have to be in name.
    MatchCase : bool
  :ReturnType: list
  """
  if not MatchCase:
    PosTags = [Tag.lower() for Tag in PosTags]
    NegTags = [Tag.lower() for Tag in NegTags]
  Similars = [Name for Name in Names if filterName(Name, PosTags, NegTags, MatchCase)]
  return Similars

def filterName(Name, PosTags, NegTags, MatchCase):
  """
  Decide whether `Name` fits to the input tags.

  :Parameters:
    Name : str
      Name to be filtered
    PosTags : list
      Tags that have to be in the name.
    NegTags : list
      Tags that do not have to be in name.
  :ReturnType: bool
  """
  CheckName = Name if MatchCase else Name.lower()
  IsSimilar = False
  for Tag in NegTags:
    if Tag in CheckName:
      break
  else:
    for Tag in PosTags:
      if Tag not in CheckName:
        break
    else:
      IsSimilar = True
  return IsSimilar

def get_search_patterns(line):
  tags = dict(pdt=[], ndt=[], pst=[], nst=[])

  matchcase = 'mc' in line
  dis_empty = 'de' in line

  if 'all' not in line:
    xline = iter(line)
    for word in xline:
      if word in tags:
        tags[word].append(xline.next())
  return tags['pdt'], tags['ndt'], tags['pst'], tags['nst'], matchcase, dis_empty
