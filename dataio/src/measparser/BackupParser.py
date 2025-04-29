"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

import os
import time
import shutil
import sys

import numpy

import iParser
from SignalSource import findParser

TIME_STAMP_SAMPLE = "%Y.%m.%d-%H:%M:%S"
""":type: str
Time stamp pattern for last modification date"""

def getLastModDate(FileName):
  """
  :Parameters:
    FileName : str
      Valid path of a file
  :ReturnType: str
  :Return: 1984.05.08-20:30:05
  """
  LastModDate = os.path.getmtime(FileName)
  LastModDate = time.localtime(LastModDate)
  return time.strftime(TIME_STAMP_SAMPLE, LastModDate)

class BackupParser(iParser.iParser):
  """Interface class for the backup parsers"""
  BaseDirs = ['Devices', 'Reports', 'Times']
  """:type: list
  Main subdirectories that are always contained by the npy backup directpry."""
  BaseFiles = ['FileComment', 'Measurement', 'Version', 'ParserVersion']
  """:type: list
  The necessary files"""

  __version__ = '0.2.0'

  @staticmethod
  def checkParser(DirName):
    """
    :Parameters:
      DirName : str
        Path of the backup directory
    """
    Check = os.path.isdir(DirName)
    if Check:
      for DirName, Dirs, Files in os.walk(DirName):
        for BaseDir in BackupParser.BaseDirs:
          if BaseDir not in Dirs:
            Check = False
        for BaseFile in BackupParser.BaseFiles:
          if BaseFile not in Files:
            Check = False
        break
      Version = BackupParser.getVersion()
      if Check and open(os.path.join(DirName, 'Version')).read() != Version:
        Check = False
    return Check

  def __init__(self, NpyDir, Measurement, ParserVersion, Version, FileComment):
    iParser.iParser.__init__(self)
    self.NpyDir = NpyDir
    """:type: str
    Path of the backup directory"""
    self.Measurement = Measurement
    """:type: str
    Name of the measurement that belongs to the backup directory"""
    self.FileComment = FileComment
    """":type: str
    Comment of the backup directory"""
    self.ParserVersion = ParserVersion
    self.Ext = '.npy'
    """:type: str
    Extension of the backup file"""
    self.MissingSignals = {}
    self.MissingTimes = set()
    self.MissingDevices = set()

    # check the NpyDir
    if os.path.exists(self.NpyDir):
      if    self.checkParser(self.NpyDir)\
        and open(os.path.join(NpyDir, 'ParserVersion')).read() == ParserVersion:
        # load the signals from the
        DevicesDir = os.path.join(self.NpyDir, 'Devices')
        for DeviceName in os.listdir(DevicesDir):
          DevicePath = os.path.join(DevicesDir, DeviceName)
          if os.path.isdir(DevicePath):
            self.Devices[DeviceName] = {}
            self.MissingSignals[DeviceName] = set()
            for TimeKey in os.listdir(DevicePath):
              TimeKeyPath = os.path.join(DevicePath, TimeKey)
              if os.path.isdir(TimeKeyPath):
                for SignalName in os.listdir(TimeKeyPath):
                  SignalNamePath  = os.path.join(TimeKeyPath, SignalName)
                  if SignalName == 'MissingSignals':
                    self.MissingSignals[DeviceName] = self.loadMissingList(SignalNamePath)
                    continue
                  SignalName, Ext = os.path.splitext(SignalName)
                  if Ext == self.Ext and os.path.isfile(SignalNamePath):
                    self.Devices[DeviceName][SignalName] = (SignalNamePath, TimeKey)
          elif DeviceName == 'MissingDevices':
            self.MissingDevices = self.loadMissingList(DevicePath)
        # load the times from the NpyDir
        TimesDir = os.path.join(self.NpyDir, 'Times')
        for TimeKey in os.listdir(TimesDir):
          TimeKeyPath = os.path.join(TimesDir, TimeKey)
          if TimeKey == 'MissingTimes':
            self.MissingTimes = self.loadMissingList(TimeKeyPath)
            continue
          TimeKey, Ext = os.path.splitext(TimeKey)
          if Ext == self.Ext and os.path.isfile(TimeKeyPath):
            self.Times[TimeKey] = TimeKeyPath
        # load the file comment
        self.FileComment = open(os.path.join(self.NpyDir, 'FileComment')).read()
        return
      sys.stderr.write('The backup parser is reinitialized %s!\n' %self.NpyDir)
      shutil.rmtree(self.NpyDir)
    # init the NpyDir
    os.makedirs(self.NpyDir)
    for BaseDir in self.BaseDirs:
      os.mkdir(os.path.join(self.NpyDir, BaseDir))
    # save meta data
    self.Version = self.getVersion()
    for Name in 'Measurement', 'Version', 'ParserVersion':
      open(os.path.join(NpyDir, Name), 'w').write(getattr(self, Name))
    return

  @classmethod
  def fromFile(cls, FileName, NpyHomeDir):
    """
    :Parameters:
      FileName : str
        Path of the measurement file
      NpyHomeDir : str
        Overwrite the generated backupdir path.
    """
    if not NpyHomeDir:
      NpyHomeDir = os.path.dirname(FileName)
      NpyHomeDir = os.path.join(NpyHomeDir, 'Backup')
    NpyDir = os.path.basename(FileName)
    NpyDir = os.path.join(NpyHomeDir, NpyDir)

    Measurement = os.path.basename(FileName)
    ParserVersion = findParser(FileName).getVersion()
    Version = cls.getVersion()

    self = cls(NpyDir, Measurement, ParserVersion, Version, '')
    return self

  @classmethod
  def fromInstance(cls, Parser, NpyDir):
    """
    :Parameters:
      BackupParser : `BackupParser`
      NpyDir : str
        Path of the backup directory.
      LastModeDate : str
        Overwrite the LastModeDate that should be copied from `BackupParser`.
    """
    self = cls(Parser.NpyDir, Parser.Measurement, Parser.ParserVersion,
               Parser.Version, Parser.FileComment)
    return self

  @classmethod
  def fromDir(cls, NpyDir):
    """
    :Parameters:
      NpyDir : str
        Path of the backup directory
    """
    FileComment = open(os.path.join(NpyDir, 'FileComment')).read()
    Measurement = open(os.path.join(NpyDir, 'Measurement')).read()
    ParserVersion = open(os.path.join(NpyDir, 'ParserVersion')).read()
    Version = open(os.path.join(NpyDir, 'Version')).read()
    self = cls(NpyDir, Measurement, ParserVersion, Version, FileComment)
    return self

  def save(self):
    """Save the added signals and times. This method must be called in place of
    the destructor."""
    # save the added signals into npy files
    DeviceMainDir = os.path.join(self.NpyDir, 'Devices')
    Path = os.path.join(DeviceMainDir, 'MissingDevices')
    self.saveMissingList(self.MissingDevices, Path)
    for DeviceName, MissingSignals in self.MissingSignals.iteritems():
      DeviceDir = os.path.join(DeviceMainDir, DeviceName)
      if not os.path.exists(DeviceDir):
        os.mkdir(DeviceDir)
      Path = os.path.join(DeviceDir, 'MissingSignals')
      self.saveMissingList(MissingSignals, Path)
    # save the added times into npy files
    TimeDir = os.path.join(self.NpyDir, 'Times')
    Path = os.path.join(TimeDir, 'MissingTimes')
    self.saveMissingList(self.MissingTimes, Path)
    # save the file comment
    open(os.path.join(self.NpyDir, 'FileComment'), 'w').write(self.FileComment)
    pass

  def getSignal(self, DeviceName, SignalName):
    Device            = self.Devices[DeviceName]
    FilePath, TimeKey = Device[SignalName]
    Signal            = numpy.load(FilePath)
    return Signal, TimeKey

  def getSignalLength(self, DeviceName, SignalName):
    Signal, TimeKey = self.getSignal(DeviceName, SignalName)
    return len(Signal)

  def getTime(self, TimeKey):
    FilePath = self.Times[TimeKey]
    return numpy.load(FilePath)

  def getTimeKey(self, DeviceName, SignalName):
    Device            = self.Devices[DeviceName]
    FilePath, TimeKey = Device[SignalName]
    return TimeKey

  def addMissingTime(self, TimeKey):
    self.MissingTimes.add(TimeKey)
    pass

  def isMissingTime(self, TimeKey):
    return TimeKey in self.MissingTimes

  def addMissingSignal(self, DeviceName, SignalName):
    try:
      Device = self.MissingSignals[DeviceName]
    except KeyError:
      Device = set()
      self.MissingSignals[DeviceName] = Device
    Device.add(SignalName)
    pass

  def isMissingSignal(self, DeviceName, SignalName):
    return     DeviceName in self.MissingSignals\
           and SignalName in self.MissingSignals[DeviceName]

  def addMissingDevice(self, DeviceName):
    self.MissingDevices.add(DeviceName)
    pass

  def isMissingDevice(self, DeviceName):
    return DeviceName in self.MissingDevices

  def saveMissingList(self, List, Path):
    Text = '\n'.join(List)
    File = open(Path, 'w')
    File.write(Text)
    File.close()
    pass

  def loadMissingList(self, Path):
    File = open(Path)
    Text = File.read()
    File.close()
    List = Text.split()
    List = set(List)
    return List

  def getReportDir(self):
    """
    :ReturnType: str
    :Return: Path of the Report directory of the backup parser.
    """
    return os.path.join(self.NpyDir, 'Reports')

  def addSignal(self, DeviceName, SignalName, TimeKey, Signal):
    """
    :Parameters:
      DeviceName : str
      SignalName : str
      TimeKey : str
      Signal : `numpy.ndarray`
    """
    if self.contains(DeviceName, SignalName):
      raise ValueError, ('%(DeviceName)s.%(SignalName)s is a reserved signal name!\n' %locals())
    DeviceMainDir = os.path.join(self.NpyDir, 'Devices')
    DeviceDir = os.path.join(DeviceMainDir, DeviceName)
    if not os.path.exists(DeviceDir):
      os.mkdir(DeviceDir)
    if DeviceName not in self.Devices:
      self.Devices[DeviceName] = {}

    TimeKeyDir     = os.path.join(DeviceDir,  TimeKey)
    SignalPath     = SignalName + self.Ext
    SignalPath     = os.path.join(TimeKeyDir, SignalPath)
    if not os.path.exists(TimeKeyDir):
      os.mkdir(TimeKeyDir)
    numpy.save(SignalPath, Signal)
    self.Devices[DeviceName][SignalName] = SignalPath, TimeKey
    pass

  def addTime(self, TimeKey, Time):
    """
    :Parameters:
      TimeKey : str
      Time : `numpy.ndarray`
    """
    if TimeKey in self.Times:
      raise ValueError, ('%(TimeKey)s is a reserved time channel name!\n' %locals())
    TimeDir = os.path.join(self.NpyDir, 'Times')
    TimePath = TimeKey + self.Ext
    TimePath = os.path.join(TimeDir, TimePath)
    numpy.save(TimePath, Time)
    self.Times[TimeKey] = TimePath
    pass