import os
import re
import md5
import time
import xml.dom.minidom
import fnmatch
import sys
import logging

from measparser.BackupParser import TIME_STAMP_SAMPLE as TIME_FORMAT

__version__ = '1.37'
VersionPattern = re.compile('([\\d\.]+)')


ReportAttrNames = ['StartTime',
                   'MeasPath',
                   'MeasLMD',
                   'ReportPath',
                   'SearchClass',
                   'SearchSign',
                   'ReportTitle',
                   'Result',
                   'Type',
                   'ModuleHash']

def getReportAttr(Report, AttrName):
  """
  Get `AttrName` attribute of the `Report` Batch report entry.

  :Parameters:
    Report : tuple
      (StartTime<str>, MeasPath<str>, ReportPath<str>, SearchClass<str>, SearchSign<str>)
    AttrName : str
      'StartTime', 'MeasPath', 'ReportPath', 'SearchClass' or 'SearchSign'
  :ReturnType: str
  """
  Index = ReportAttrNames.index(AttrName)
  Attr  = Report[Index]
  return Attr

def rmReportAttr(Report, AttrName):
  Index = ReportAttrNames.index(AttrName)
  Report = list(Report)
  Report.pop(Index)
  Report = tuple(Report)
  return Report

HeaderAttrNames = ['Version']

def relativePath(Base, Target):
  """
  Create a relative path for `Target` to `Base`.

  :Parameters:
    Base : str
      full path of a directory
    Target : str
      full path of a file or directory under `Base`
      or under the same drive at least.
  :ReturnType: str
  """
  sep = os.path.sep
  BaseNormed = os.path.normcase(Base)
  BasePartsNormed = BaseNormed.split(sep)
  TargetNormed = os.path.normcase(Target)
  TargetPartsNormed = TargetNormed.split(sep)
  TargetParts = Target.split(sep)
  i = 0
  for BasePart, TargetPart in zip(BasePartsNormed, TargetPartsNormed):
    if BasePart != TargetPart:
      break
    i += 1
  up = len(BasePartsNormed)-i
  Relative = ['..' for j in xrange(up)]
  Relative.extend(TargetParts[i:])
  Relative = sep.join(Relative)
  return Relative


class cBatch:
  TIME_FORMAT = TIME_FORMAT
  """Handle measurement file batch processing."""
  def __init__(self, XmlFile, StartTime, ReplMeas=False, MeasPath=None):
    """
    :Parameters:
      XmlFile : str
        Path of the batch record.
      StartTime : str
        Time stamp to mark common runs
    """
    self.XmlFile = XmlFile
    self.StartTime = StartTime
    self.Reports = set()
    """:type: set
    set(Report<tuple>, )
    """
    self.Groups = {}
    """:type: dict
    {ReportAttrName<str>:{ReportAttrValue<str>:Reports<set>}}"""
    self.Header = {}
    self.ModuleHashes = {}
    """:type: dict
    {ModuleName<str>:ModuleHash<str>"""
    Logger = logging.getLogger()

    self.MaxBackupNr = 5
    self.TimeStampPattern = '%Y%m%d%H%M%S'
    Base = os.path.basename(XmlFile)
    FileName, Ext = os.path.splitext(Base)
    TimeStamp     = time.strftime(self.TimeStampPattern)
    TimeStampLen  = len(TimeStamp)
    BackupPattern = '^%s\\d{%d}%s$' %(FileName, TimeStampLen, Ext)
    BackupPattern = re.compile(BackupPattern)
    self.BackupPattern = BackupPattern

    if not os.path.exists(XmlFile):
      self.Header['Version'] = VersionPattern.search(__version__).group(1)
      self.group()
      return

    Document = xml.dom.minidom.parse(XmlFile)
    Header, = Document.getElementsByTagName('root')
    Version = VersionPattern.search(Header.getAttribute('Version')).group(1)
    Type    = 'measproc.cFileReport'
    Reports = []
    if Version:
      for Name in HeaderAttrNames:
        self.Header[Name] = Header.getAttribute(Name)
      for ReportNode in Header.getElementsByTagName('Report'):
        ReportAttrs = []
        for Name in ReportAttrNames:
          if ReportNode.hasAttribute(Name):
            Attr = ReportNode.getAttribute(Name)
          elif Name == 'Type':
            Attr = Type
          else:
            Attr = 'none'
          ReportAttrs.append(Attr)
        Reports.append(ReportAttrs)
    else:
      self.Header['Version'] = VersionPattern.search(__version__).group(1)
      MeasPathIndex   = ReportAttrNames.index('MeasPath')
      ReportPathIndex = ReportAttrNames.index('ReportPath')
      TypeIndex       = ReportAttrNames.index('Type')
      for Measurement in Header.getElementsByTagName('Measurement'):
        MeasPath = Measurement.getAttribute('Path')
        for ReportNode in Measurement.getElementsByTagName('Measurement'):
          ReportPath = ReportNode.getAttribute('Path')
          ReportAttrs = ['none' for FieldAttr in self.FieldAttrs]
          ReportAttrs[MeasPathIndex]   = MeasPath
          ReportAttrs[ReportPathIndex] = ReportPath
          ReportAttrs[TypeIndex]       = Type
          Reports.append(ReportAttrs)

    ChangePath = Version < '1.37'
    if ChangePath:
      self.Header['Version'] = '1.37'

    Measurements = {}

    for ReportAttrs in Reports:
      if ChangePath:
        i = ReportAttrNames.index('ReportPath')
        ReportPath = self.relativePath(ReportAttrs[i])
        ReportAttrs[i] = ReportPath
      Measurements.setdefault(getReportAttr(ReportAttrs, 'MeasPath'), []).append(ReportAttrs)

    self.Missings = [m for m in Measurements if m[0].isalpha() and not os.path.exists(m)]

    if ReplMeas:
      Targets = dict([(os.path.basename(m), m) for m in self.Missings])
      Replaces = {}
      if not MeasPath:
        MeasPath = re.findall(r"[A-Z]:.+$", os.popen("mountvol /").read(), re.MULTILINE)
      for Dir in MeasPath:
        for Root, Dirs, Files in os.walk(Dir):
          for Hit in set(Files).intersection(Targets):
            Origin = Targets.pop(Hit)
            Replaces[Origin] = os.path.join(Root, Hit)
        if not Targets:
          break
      else:
        Logger.info('Missing measurements')
        Logger.info( '\n'.join(sorted(self.Missings)))
      if not Targets:
        for Origin, Replace in Replaces.iteritems():
          for ReportAttrs in Measurements[Origin]:
            i = ReportAttrNames.index('MeasPath')
            ReportAttrs[i] = Replace
        self.Missings = []

    for ReportAttrs in Reports:
      ReportAttrs = tuple(ReportAttrs)
      self.Reports.add(ReportAttrs)

    self.group()
    pass

  def backup(self, PrettyXml):
    """Creates backup of the results."""
    Dir, FileName = os.path.split(self.XmlFile)
    BaseName, Ext = os.path.splitext(FileName)
    TimeStamp     = time.strftime(self.TimeStampPattern)
    NewBackupPath = os.path.join(Dir, BaseName+TimeStamp+Ext)
    # search for backup files
    Backups = []
    for Name in os.listdir(Dir):
      Path = os.path.join(Dir, Name)
      if self.BackupPattern.match(Name) and os.path.isfile(Path):
        Backups.append(Path)
    # create backup if necessary
    BackupsLen = len(Backups)
    if len(Backups):
      Backups.sort()
      BackupPath = Backups[-1]
      Backup = cBatch(BackupPath, 'DummyStartTime')
      if self.Reports.symmetric_difference(Backup.Reports):
        open(NewBackupPath, 'w').write(PrettyXml)
        Backups.append(NewBackupPath)
    else:
      open(NewBackupPath, 'w').write(PrettyXml)
      Backups.append(NewBackupPath)
    # delete old backups
    if len(Backups) > self.MaxBackupNr:
      for BackupPath in Backups[:-self.MaxBackupNr]:
          os.remove(BackupPath)
    pass

  def save(self):
    """Save the measurement processing results into `XmlFile`."""
    Document = xml.dom.minidom.Document()
    Header   = Document.createElement('root')
    Document.appendChild(Header)

    for Name in HeaderAttrNames:
      Attr = self.Header[Name]
      Header.setAttribute(Name, Attr)

    for ReportAttrs in self.Reports:
      ReportNode = Document.createElement('Report')
      for Name, Attr in zip(ReportAttrNames, ReportAttrs):
        ReportNode.setAttribute(Name, Attr)
      Header.appendChild(ReportNode)

    Dir, Spam = os.path.split(self.XmlFile)
    if Dir and not os.path.exists(Dir):
      os.makedirs(Dir)
    PrettyXml = Document.toprettyxml()
    open(self.XmlFile, 'w').write(PrettyXml)
    self.backup(PrettyXml)
    pass

  def relativePath(self, EntryPath):
    Base = os.path.dirname(self.XmlFile)
    return relativePath(Base, EntryPath)

  def absPath(self, EntryPath):
    Base = os.path.dirname(self.XmlFile)
    Path = os.path.join(Base, EntryPath)
    return os.path.abspath(Path)

  def add(self, Batch):
    """
    :Parameters:
      Batch : cBatch
    """
    self.Reports = self.Reports.union(Batch.Reports)
    pass

  def group(self):
    """Group the `Reports` into `Groups`"""
    for Name in ReportAttrNames:
      self.Groups[Name] = {}
    for ReportAttrs in self.Reports:
      self.addReportAttrsToGroup(ReportAttrs)
    pass

  def addReportAttrsToGroup(self, ReportAttrs):
    for Name, Attr in zip(ReportAttrNames, ReportAttrs):
      ReportAttrsGroup = self.Groups[Name].setdefault(Attr, [])
      ReportAttrsGroup.append(ReportAttrs)
    return

  def wakeEntry(self, Entry):
    Path = getReportAttr(Entry, 'ReportPath')
    Type = getReportAttr(Entry, 'Type')

    Class = importByText(Type)
    Path  = self.absPath(Path)
    Awake = Class(Path)
    return Awake

  def _addEntry(self, StartTime, MeasPath, MeasLMD, ReportPath, SearchClass,
                      SearchSign, ReportTitle, Result, Type, ModuleHash):
    Entry = StartTime, MeasPath, MeasLMD, ReportPath, SearchClass,\
            SearchSign, ReportTitle, Result, Type, ModuleHash
    self.Reports.add(Entry)
    self.addReportAttrsToGroup(Entry)
    return

  def addEntry(self, Entry, ClassName, Signature, Measurement, Result, Type):
    try:
      ModuleHash = self.ModuleHashes[ClassName]
    except KeyError:
      ModuleName, ClsName = ClassName.split('.')
      Module = __import__(ModuleName)
      ModuleHash = get_version(Module)
      self.ModuleHashes[ClassName] = ModuleHash

    RelativePath = self.relativePath(Entry.PathToSave)
    self._addEntry(self.StartTime, Measurement, Entry.ReportAttrs['MeasLMD'], RelativePath,
                   ClassName, Signature, Entry.getTitle(), Result, Type, ModuleHash)
    Entry.save()
    pass

  def addReport(self, Report, ClassName, Signature, Measurement, Result):
    self.addEntry(Report, ClassName, Signature, Measurement, Result, 'measproc.cFileReport')
    pass

  def addReports(self, Reports, ClassName, Signature, Measurement, Result):
    for Report in Reports:
      self.addReport(Report, ClassName, Signature, Measurement, Result)
    pass

  def addStatistic(self, Statistic, ClassName, Signature, Measurement, Result):
    self.addEntry(Statistic, ClassName, Signature, Measurement, Result, 'measproc.cFileStatistic')
    pass

  getReportAttr = staticmethod(getReportAttr)
  rmReportAttr = staticmethod(rmReportAttr)

  def pack(self, Reports, ReportAttr, rename=None):
    """
    Pack the `Reports` via the selected `ReportAttr`. Where the Dummy values
    will be put under the ReportAttrValue to where ReportEntry belongs.

    :Parameters:
      Reports : list
        [[Dummy<void>, ReportEntry<tuple>],]
      ReportAttr : str
        'StartTime', 'MeasPath', 'ReportPath', 'SearchClass' or 'SearchSign'
      rename : function
        Rename the key in the dictionary
    :ReurnType: dict
    :Return: {ReportAttrValue<str>: [Dummy<void>,]}
    """
    Group = self.Groups[ReportAttr]
    Pack  = {}
    for Name, ReportGroup in Group.iteritems():
      DummyPack = []
      Expendables = []
      for Dummy_Report in Reports:
        Dummy, Report = Dummy_Report
        if Report in ReportGroup:
          DummyPack.append(Dummy)
          Expendables.append(Dummy_Report)
      if DummyPack:
        if callable(rename):
          Name = rename(Name)
        Pack[Name] = DummyPack
      for Expendable in Expendables:
        Reports.remove(Expendable)
      if not Reports:
        break
    return Pack

  def pack_itself(self, Reports, ReportAttr, rename=None):
    """
    Pack the `Reports` via the selected `ReportAttr`.
    :Parameters:
      Reports : list
        [ReportEntry<tuple>]
      ReportAttr : str
        'StartTime', 'MeasPath', 'ReportPath', 'SearchClass' or 'SearchSign'
      rename : function
        Rename the key in the dictionary
    :ReurnType: dict
    :Return: {ReportAttrValue<str>: [ReportEntry<tuple>]}
    """
    return self.pack(zip(Reports, Reports), ReportAttr, rename)

  def filter(self, Group, **kwargs):
    """
    The keyword can be any valid report entry name and its value can be any
    valid value of it. The `Group` will be filtered to report report entries
    which have the selected values.

    :Parameters:
      Group : set
        [ReportEntry<tuple>]
    :ReturnType: set
    """
    for Name, Attr in kwargs.iteritems():
      try:
        Filter = self.Groups[Name][Attr]
      except KeyError:
        return set()
      else:
        Group = Group.intersection(Filter)
    return Group

  def ignore(self, Group, Name):
    Ignores = {}
    for Report in Group:
      Ignored = rmReportAttr(Report, Name)
      Ignores[Ignored] = Report
    return set(Ignores.itervalues())

  def getOccurrences(self, Group, Name):
    """
    Get the values of the `Name `report attribute which occur in `Group`.

    :Parameters:
      Group : set
        [ReportEntry<tuple>,]
      Name : str
        Valid report entry attribute name from `ReportAttrs`
    :ReturnType: list
    """
    Table = self.Groups[Name]
    Occurrences = []
    for TableName, TableGroup in Table.iteritems():
      if Group.intersection(TableGroup):
        Occurrences.append(TableName)
    Occurrences.sort()
    return Occurrences

  def getLastStartTime(self, Group):
    """"
    :Parameters:
      Group : set
        [ReportEntry<tuple>]
    """
    Occurrences = self.getOccurrences(Group, 'StartTime')
    LastStartTime = Occurrences[-1]
    return LastStartTime

  def getLastReports(self, SearchClass, SearchSign):
    Group = self.filter(self.Reports, SearchClass=SearchClass, SearchSign=SearchSign)
    LastStartTime = self.getLastStartTime(Group)
    Group = self.filter(Group, StartTime=LastStartTime)
    Pack  = self.pack(zip(Group, Group), 'MeasPath', os.path.basename)
    return Pack

  def getAllReports(self, SearchClass, SearchSign):
    Group = self.filter(self.Reports, SearchClass=SearchClass, SearchSign=SearchSign)
    Pack  = self.pack(zip(Group, Group), 'MeasPath', os.path.basename)
    return Pack

  def getReportAttrs(self, AttrName):
    Index = ReportAttrNames.index(AttrName)
    return [Report[Index] for Report in self.Reports]


class CreateParams:
  def __init__(self, XmlFile, StartTime, ReplMeas, MeasPath):
    self.XmlFile = XmlFile
    self.StartTime = time.strftime(cBatch.TIME_FORMAT, StartTime)
    self.ReplMeas = ReplMeas
    self.MeasPath = MeasPath
    return

  def __call__(self):
    return cBatch(self.XmlFile, self.StartTime, self.ReplMeas, self.MeasPath)


class UploadParams:
  def __init__(self, ClassName, Signature, Measurement, Result, Type):
    self.ClassName = ClassName
    self.Signature = Signature
    self.Measurement = Measurement
    self.Result = Result
    self.Type = Type
    return

  def __call__(self, Batch, Entry):
    Batch.addEntry(Entry,
      self.ClassName, self.Signature, self.Measurement, self.Result, self.Type)
    return


def findMeasurements(Directory, Pattern, Recursively=False, FindDirToo=False):
  """
  :Parameters:
    Directory : str
    Pattern : str
      Wildcard search string
  :Keywords:
    FindDirToo : bool
      Default value is False
    Recursively : bool
      Default value is False
  :ReturnType: generator
  """
  Patterns = Pattern.split(' ')
  for Root, Dirs, Files in os.walk(Directory):
    for Name in Files:
      for Extension in Patterns:
        if fnmatch.fnmatch(Name, Extension):
          Path = os.path.join(Root, Name)
          yield Path
    if FindDirToo:
      for Name in Dirs:
        for Extension in Patterns:
          if fnmatch.fnmatch(Name, Extension):
            Path = os.path.join(Root, Name)
            yield Path
    if not Recursively:
      break
  pass

def importByText(Path):
  Path = Path.split('.')
  Attr = __import__(Path[0])
  for Name in Path[1:]:
    Attr = getattr(Attr, Name)
  return Attr

def get_version(module):
  """Get the __version__ of `module` or its md5 hash. Version can 'unkown' if
  there is no __file__ attribute or it's '__main__'"""
  version = 'unknown'
  if hasattr(module, '__version__'):
    version = module.__version__
  elif hasattr(module, '__file__'):
    name = module.__file__
    if name != '__main__':
      name = module.__file__.replace('.pyc', '.py')
      version = get_text_hash(name)
  return version

def get_text_hash(name):
  "Get the md5 hash of file `name`."
  m = md5.new()
  f = open(name)
  for line in f:
    m.update(line)
  f.close()
  return m.hexdigest()

