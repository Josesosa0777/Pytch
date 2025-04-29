import os
import sys
import md5
import time
import logging
import ConfigParser
from argparse import ArgumentParser, RawTextHelpFormatter
from traceback import format_exception

from interface.scan import Module as ModuleScan
from interface.module import importModuleAttr
from interface.modules import ModuleName
from measproc.batchsqlite import RESULTS
from measparser.BackupParser import TIME_STAMP_SAMPLE as TIME_FORMAT
from modules import Modules
from helper import getConfigPath, procConfigFile
from logger import Logger
import Fill
import View
import Analyze
import Search
import Compare

class iConfig(ConfigParser.RawConfigParser):
  def __init__(self):
    ConfigParser.RawConfigParser.__init__(self)
    self.optionxform = str
    self.Log = None
    self.BlockedModules = {}
    sys.excepthook = self.excepthook
    pass

  def getActiveOptions(self, Section):
    Options = set()
    if self.has_section(Section):
      for Option in self.options(Section):
        if self.getboolean(Section, Option):
          Options.add(Option)
    return Options

  def getPassiveOptions(self, Section):
    Options = set()
    if self.has_section(Section):
      for Option in self.options(Section):
        if not self.getboolean(Section, Option):
          Options.add(Option)
    return Options

  def blockModule(self, Section, Module):
    if Section not in self.BlockedModules:
      self.BlockedModules[Section] = set()
    self.BlockedModules[Section].add(Module)
    return

  def unBlockModule(self, Section, Module):
    if Section not in self.BlockedModules:
      self.BlockedModules[Section] = set()
    self.BlockedModules[Section].remove(Module)
    return

  def initOptions(self, Section, Options, OptionValue='no'):
    for Option in Options:
      if not Option: continue
      self.set(Section, Option, OptionValue)
    pass

  def likeAlone(self, Section):
    Options = self.options(Section)
    if len(Options) == 1:
      Option, = Options
      self.set(Section, Option, 'yes')
    return Options

  def initModuleByScanModule(self, Module):
    Name = ModuleName.create(Module.name, '', Module.prj)

    self.set(Module.interface, Name, 'no')

    if self.has_section(Name):
      self.remove_section(Name)
    self.add_section(Name)
    self.initOptions(Name, Module.parameters)
    self.likeAlone(Name)
    pass

  def initModuleByName(self, Section, ModName, ParamName, PrjName):
    ExtendedModuleName = ModName + ModuleName.PRJ_SEP + PrjName
    self.set(Section, ExtendedModuleName, 'no')
    if not self.has_section(ExtendedModuleName):
      self.add_section(ExtendedModuleName)
    if ParamName:
      self.set(ExtendedModuleName, ParamName, 'no')
    return

  def removeModule(self, Section, Name):
    if not self.has_section(Name):
      return

    self.remove_option(Section, Name)
    self.remove_section(Name)
    for Section in self.Sections.itervalues():
      Section.removeModule()
    pass

  def removeModuleParam(self, ModuleName, ParamName):
    if not self.has_section(ModuleName): return
    self.remove_option(ModuleName, ParamName)
    return

  def iterModules(self, Section):
    for ModName in self.options(Section):
      ShortModName, _, PrjName = ModuleName.split(ModName)
      ModName_ = ModuleName.create(ShortModName, '', PrjName)
      ParameterNames = self.options(ModName_)
      if ParameterNames:
        for ParameterName in ParameterNames:
          yield ShortModName, ParameterName, PrjName
      else:
        yield ShortModName, '', PrjName
    return

  def scanInterfaceModule(self, FileName, PrjName):
    Module = ModuleScan.from_file(FileName, PrjName)
    return Module

  def scanMemoryModule(self, Name, Prj, Fp):
    Fp.seek(0)
    Module = ModuleScan.from_memory(Name, Prj, Fp)
    return Module

  def _getActiveModules(self, Section):
    Modules = []
    for ModuleName_ in self.getActiveOptions(Section):
      if Section in self.BlockedModules and \
         ModuleName_ in self.BlockedModules[Section]: continue
      ModName, _, PrjName = ModuleName.split(ModuleName_)
      ParameterNames = self.getActiveOptions(ModuleName_)
      if ParameterNames:
        for ParameterName in ParameterNames:
          Name = ModuleName.create(ModName, ParameterName, PrjName)
          Modules.append(Name)
      elif not self.options(ModuleName_):
        Name = ModuleName.create(ModName, '', PrjName)
        Modules.append(Name)
    return Modules

  def hash(self):
    Hash = md5.new()
    for Section in sorted(self.sections()):
      Hash.update(Section)
      for Option in sorted(self.options(Section)):
        Hash.update(Option)
        Hash.update(self.get(Section, Option))
    return Hash.hexdigest()

  def log(self, Msg, Level=logging.INFO):
    if self.Log:
      self.Log.log(Msg, Level)
    return

  def changeStreamLoggerLevel(self, level):
    self.Log.change_stderr_level(level)
    self.set('General', 'StreamLogLevel', level)
    return

  def excepthook(self, excType, excValue, tracebackobj):
    msg = "Unhandled exception\n" + \
      "".join(format_exception(excType, excValue, tracebackobj))
    self.log(msg, logging.CRITICAL)
    print >> sys.stderr, msg  # print even if logger bypasses
    return

class cConfig(iConfig):
  StatusSection = 'iFill'
  SectionTypes = dict(
    (Section.cSection.Interface.__name__, Section.cSection)
    for Section in (Fill, View, Analyze, Compare, Search)
  )

  def _load(self, Modules):
    self.Modules = Modules
    self.Sections = dict((Name, Section(self))
                         for Name, Section in self.SectionTypes.iteritems())
    return

class cScan(cConfig):
  LOCKED_OPTIONS = {
                     '__doc__' : 'all',
                     'GroupTypes' : 'all',
                     'VidCalibs' : 'all',
                     'DocTemplates' : 'all',
                     'General' : 'MainPth',
                     'Path' : 'all',
                     'Channels' : 'all'
                   }
  EXTRA_FAVORITABLE_OPTIONS = 'GroupNames',
  def __init__(self, Modules, ScanDirs, CfgFiles, MainPth, LogFile='',
              StreamLogLevel=logging.INFO, FileLogLevel=logging.DEBUG,
              colorful_stderr=True):
    cConfig.__init__(self)
    self._load(Modules)
    self.Log = Logger(LogFile, StreamLogLevel, file_logger_level=FileLogLevel,
                      colorful_stderr=colorful_stderr)

    self.add_section('__doc__')
    self.add_section('GroupTypes')
    self.add_section('VidCalibs')
    self.add_section('DocTemplates')
    self.add_section('MASS Layout')

    self.add_section('General')
    self.set('General', 'Report', '')
    self.set('General', 'BatchFile', '')
    self.set('General', 'RepDir', '')
    self.set('General', 'MeasPath', '')
    self.set('General', 'Backup', '')
    self.set('General', 'MapDb', '')
    self.set('General', 'OsmFile')
    self.set('General', 'LogFile', '')
    self.set('General', 'StreamLogLevel', '')

    self.add_section('Measurement')
    for channel in Modules.get_channels():
      self.set('Measurement', channel, '')

    self.add_section('Channels')
    self.read(CfgFiles)
    for Section in self.Sections.itervalues():
      Section.initConfig(Modules)

    self.set('General', 'MainPth', MainPth)

    self.add_section('Path')
    for Name, DirName in ScanDirs.iteritems():
      self.set('Path', Name, DirName)

    self.add_section('Favorites')
    FavoriteOptions = self.Sections.keys()
    FavoriteOptions.extend(self.EXTRA_FAVORITABLE_OPTIONS)
    for Option in FavoriteOptions:
      self.set('Favorites', Option, '')

    self.add_section('PathHistory')
    self.set('PathHistory', 'Measurements', '')
    self.set('PathHistory', 'BatchFileDirectory', '')
    self.set('PathHistory', 'ReportDirectory', '')
    self.set('PathHistory', 'QueryFile', '')
    return

  def save(self, SavePath):
    if os.path.exists(SavePath):
      Other = Config(SavePath, self.Modules)
      self.update(Other)
    File = open(SavePath, 'wb')
    self.write(File)
    File.close()
    pass

  def update(self, Config):
    for Section in self.sections():
      if Config.has_section(Section):
        for Option in self.options(Section):
          if Config.has_option(Section, Option):
            if Section not in self.LOCKED_OPTIONS or \
               ( self.LOCKED_OPTIONS[Section] != 'all' and \
                 Option not in self.LOCKED_OPTIONS[Section] ):
              Value = Config.get(Section, Option)
              self.set(Section, Option, Value)


    for Name, Module in Config.Sections.iteritems():
      for Section in Module.getSessionSections():
        if not Config.has_section(Section) or not Config.options(Section):
          break

      else:
        self.Sections[Name].clearSectionConfig()

        for Section in Module.getSessionSections():
          if not self.has_section(Section):
              self.add_section(Section)

          for Option in Config.options(Section):
            Value = Config.get(Section, Option)
            self.set(Section, Option, Value)
    pass

class Config(cConfig):
  stripSelection = staticmethod(Fill.cSection.stripSelection)

  def __init__(self, CfgPath, Modules):
    self.RunNav = True
    self.SolidTimeCheck = False
    self.ReplMeas = False
    self.Start = ''
    self.StartDate = None
    self.EndDate = None
    self.GlobalParams = {}
    self.Verbose = False
    self.NoSave = False
    self.ForcedSave = False
    self.DocName = ''
    self.EnableBatchUpdate = False
    if not os.path.exists(CfgPath):
      raise IOError("%s doesn't exist" %CfgPath)

    self.Status = 0
    self.CfgPath = CfgPath
    cConfig.__init__(self)
    self._loadCfg(CfgPath, Modules)

    self.UpdateCallbacks = []
    self.TempModules = []
    self._Hash = self.hash()
    return

  def init(self, Args):
    Info = self.procInfoArgs(Args)
    self.procArgs(Args)
    LogFile = self.getLogFile()
    StreamLogLevel = self.getStreamLogLevel()
    self.Log = Logger(LogFile, StreamLogLevel,
                      file_logger_level=self.FileLogLevel,
                      colorful_stderr=not self.NoColor)
    if Info:
      self.log('\n'.join(Info))
      exit(self.Status)
    return self

  def run(self, Manager, Args, Interface):
    if Args.norun: return

    self.load(Manager, Interface)
    self.build(Manager, Interface)
    return

  def wait(self, Args):
    if self.RunNav and not Args.norun:
      raw_input("Press Enter to exit!\n")
      sys.stdout.flush()
    return

  def exit(self, Manager, Interface):
    self.close(Manager, Interface)
    return self.Status

  def load(self, Manager, Interface):
    self._uploadParams(Manager, Interface)
    self.Sections[Interface].uploadParams(Manager)
    return

  def saveAll(self, Manager):
    for Section, Module in self.Sections.iteritems():
      Module.save(Manager)
    self.save()
    return

  def _loadCfg(self, CfgPath, Modules):
    self.read(CfgPath)
    self._load(Modules)
    return

  def loadCfg(self, CfgPath, Manager):
    self.saveAll(Manager)
    for Section in self.Sections.values():
      Section.clearSectionConfig()
    self._loadCfg(CfgPath, self.Modules)
    self.update()
    return

  def changed(self):
    Config = iConfig()
    Config.read(self.CfgPath)
    Changed = self._Hash != Config.hash()
    return Changed

  def loadNameSpace(self, Manager):
    self._loadNameSpace(Manager)
    return

  def _loadNameSpace(self, Manager):
    "Create name space from the selected interface modules"
    Modules = Manager.get_modules()
    for ModuleName, ParamName, PrjName in self.Modules:
      CsvModule = self.Modules.get(ModuleName, ParamName, PrjName)
      Modules.add_csv_module(ModuleName, ParamName, CsvModule)
    return

  def _uploadParams(self, Manager, Interface):
    Manager.strong_time_check = not self.SolidTimeCheck
    Manager.run_navigator = self.RunNav
    Manager.verbose = self.Verbose
    Manager.global_params = self.GlobalParams.copy()

    self._uploadBatchParams(Manager)

    Backup = self.get('General', 'Backup')
    Manager.set_backup(Backup)
    Manager.set_source_class( importModuleAttr(self.get('General', 'cSource')) )
    for Channel in self.options('Measurement'):
      Measurement = self.get('Measurement', Channel)
      if os.path.exists(Measurement):
        Manager.set_measurement(Measurement, channel=Channel)

    MapDb = self.get('General', 'MapDb')
    if os.path.isfile(MapDb):
      Manager.set_mapdb(MapDb)

    OsmFile = self.get('General', 'OsmFile')
    if os.path.isfile(OsmFile):
      Manager.set_osmfile(OsmFile)

    self._uploadDocTemplates(Manager)
    if self.DocName:
      Manager.set_docname(self.DocName)

    self._setGroupTypes(Manager)
    self._uploadParamDicts(Manager)
    return

  def _uploadBatchParams(self, Manager):
    BatchFile = self.get('General', 'BatchFile')
    RepDir = self.get('General', 'RepDir')
    Manager.start_date = self.StartDate
    Manager.end_date = self.EndDate
    if BatchFile and RepDir:
      if not self.Start:
        self.Start = time.strftime(TIME_FORMAT)
      Labels = importModuleAttr( self.get('Params', 'Labels') )
      Tags = importModuleAttr( self.get('Params', 'Tags') )
      QuaNames = importModuleAttr( self.get('Params', 'QuaNames') )
      Manager.set_batch_params(BatchFile, RepDir, Labels, Tags, RESULTS,
                               QuaNames, self.EnableBatchUpdate)
      MeasPath = self.get('General', 'MeasPath')
      if self.ReplMeas and os.path.isdir(MeasPath):
        Manager.meas_path = MeasPath
    return

  def _uploadDocTemplates(self, Manager):
    Section = 'DocTemplates'
    for TemplateName in self.options(Section):
      TemplateClass = importModuleAttr(self.get(Section, TemplateName))
      Manager.set_doctemplate(TemplateName, TemplateClass)
    return

  def _uploadParamDicts(self, Manager):
    for Option in self.options('Groups'):
      Groups = importModuleAttr(self.get('Groups', Option))
      Manager.set_groups(Option, Groups)

    for Option in self.options('ViewAngles'):
      ViewAngles = importModuleAttr(self.get('ViewAngles', Option))
      Manager.set_view_angles(ViewAngles)

    for Option in self.options('Legends'):
      Legends = importModuleAttr(self.get('Legends', Option))
      Manager.set_legends(Option, Legends)

    for Option in self.options('ShapeLegends'):
      ShapeLegends = importModuleAttr(self.get('ShapeLegends', Option))
      Manager.set_shape_legends(Option, ShapeLegends)

    for Option in self.options('VidCalibs'):
      VidCalibs = self.get('VidCalibs', Option)
      Manager.set_vidcalibs(VidCalibs)
    return

  def build(self, Manager, Interface):
    self._printMissingParameterSelection()
    self._loadNameSpace(Manager) # required for new modules from sag
    Section = self.Sections[Interface]
    if not Section.InnerBuild:
      self._build(Manager, Interface)
    Section.build(Manager)
    return

  def _build(self, Manager, Interface):
    ModuleNames = self._getActiveModules(Interface)
    StatusSection = self._getActiveModules(self.StatusSection)
    Statuses = StatusSection if self.Sections[Interface].NeedStatuses else []
    GroupNames = self.getActiveOptions('GroupNames')
    self.Status = Manager.build(ModuleNames, status_names=Statuses,
                                visible_group_names=GroupNames,
                                show_navigators=self.RunNav)
    return

  def _recordingbuild(self, Manager, Interface):
    ModuleNames = self._getActiveModules(Interface)
    StatusSection = self._getActiveModules(self.StatusSection)
    Statuses = StatusSection if self.Sections[Interface].NeedStatuses else []
    result=[]
    result.append((ModuleNames,StatusSection,Statuses))
    return result

  def _uploadManager(self, Manager):
    self._loadNameSpace(Manager)
    self._extendPath(Manager)
    self._setGroupTypes(Manager)
    self._uploadParamDicts(Manager)
    return

  def createManager(self, Interface):
    Manager = self.Sections[Interface].createManager()
    self._uploadManager(Manager)
    return Manager

  def _extendPath(self, Manager):
    for DirName in self.options('Path'):
      Dir = self.get('Path', DirName)
      Manager.append_dataeval_path(Dir)
    return

  def _setGroupTypes(self, Manager):
    Section = 'GroupTypes'
    for Option in self.options(Section):
      GroupTypes = importModuleAttr(self.get(Section, Option))
      Manager.grouptypes.add_types(Option, GroupTypes)
    return

  def _printMissingParameterSelection(self):
    Missing = self.getMissingParameterSelection()
    for ModuleName in sorted(Missing):
      self.log("Missing parameter selection: %s" % ModuleName,
               Level=logging.WARNING)
    return

  def getMissingParameterSelection(self):
    Missing = []
    for Section in self.Sections:
      Missing.extend( self._getMissingParameterSelection(Section) )
    return Missing

  def _getMissingParameterSelection(self, Section):
    Missing = [ModuleName
               for ModuleName in self.getActiveOptions(Section)
               if    self.options(ModuleName)
                 and not self.getActiveOptions(ModuleName)
                 and (Section not in self.BlockedModules
                      or ModuleName not in self.BlockedModules[Section])]
    return Missing

  def getActiveModules(self, Interface):
    Actives = self._getActiveModules(Interface)
    Actives.extend(self._getActiveModules(self.StatusSection))
    return Actives

  def close(self, Manager, Interface):
    self.Sections[Interface].save(Manager)
    self.save()
    if Manager is not None:
      Manager.close()
    self.Log.close()
    return

  def _removeTempModules(self):
    while self.TempModules:
      ModuleName_, ParamName, PrjName = self.TempModules.pop()
      self.Modules.rm(ModuleName_, ParamName, PrjName)
      Module = ModuleName.create(ModuleName_, '', PrjName)
      self.removeModuleParam(Module, ParamName)
    return

  def update(self):
    for update in self.UpdateCallbacks:
      update()
    for Section in self.Sections.values():
      Section.update()
    pass

  def activateModule(self, Interface, ModuleName_, Parameters, Prj,  Channels):
    Params = self._activateModule(Interface, ModuleName_, Parameters, Prj)
    for Channel in Channels:
      if not self.has_option('Measurement', Channel):
        self.set('Measurement', Channel, '')
    Channels = ','.join(Channels)
    for Parameter in Params:
      ExtModuleName = ModuleName.create(ModuleName_, Parameter, Prj)
      self.set('Channels', ExtModuleName, Channels)
    return

  def _activateModule(self, Interface, Name, Parameters, Prj):
    ModName = ModuleName.create(Name, '', Prj)
    self.set(Interface, ModName, 'yes')
    if Parameters:
      for Parameter in Parameters:
        self.set(ModName, Parameter, 'yes')
      return Parameters
    else:
      return self.likeAlone(ModName)
    return

  def initModule(self, Module):
    self.initModuleByScanModule(Module)
    MainPth = self.get('General', 'MainPth')
    self.Modules.add_module(MainPth, Module)
    return

  def removeModule(self, Manager, Interface, Name, Prj):
    ModuleSection = ModuleName.create(Name, '', Prj)
    if not self.has_section(ModuleSection):
      return

    Modules = Manager.get_modules()
    Parametrs = self.options(ModuleSection)
    ParameterNames = Parametrs if Parametrs else ['']
    for ParameterName in ParameterNames:
      ModuleName_ = ModuleName.create(Name, ParameterName, Prj)
      Modules.remove(ModuleName_)
      self.Modules.rm(Name, ParameterName, Prj)
      self.remove_option('Channels', ModuleName_)
    iConfig.removeModule(self, Interface, ModuleSection)
    return

  def cloneModuleParam(self, ModuleName, ParamName, PrjName):
    ParamName, Param = self.Modules.clone_param(ModuleName, ParamName, PrjName)
    return ParamName, Param

  def getMainPath(self):
    return self.get('General', 'MainPth')

  def getMainModuleDir(self, Default=os.curdir):
    MainPth = self.getMainPath()
    if self.has_option('Path', MainPth):
      Name = self.get('Path', MainPth)
    else:
      Name = Default
    return Name

  def addFavorite(self, Option, Module):
    if not self.has_option('Favorites', Option) or \
        self.get('Favorites', Option) == '':
      self.set('Favorites', Option, Module)
      return

    Favorites = self.createFavoriteList(Option)

    if Module in Favorites:
      return

    Favorites.append(Module)
    self.setFavorites(Option, Favorites)
    return

  def removeFavorite(self, Option, Module):
    if not self.has_option('Favorites', Option) or \
        self.get('Favorites', Option) == '':
      return

    Favorites = self.createFavoriteList(Option)

    if Module not in Favorites:
      return

    Favorites.remove(Module)

    self.setFavorites(Option, Favorites)
    return

  def createFavoriteList(self, Option):
    Favorites = self.get('Favorites', Option)
    Favorites = Favorites.split(',')
    for Favorite in Favorites:
      Favorite = Favorite.strip()
      Favorite = Favorite.rstrip()
    return Favorites

  def setFavorites(self, Option, Favorites):
    Value = ','.join(Favorites)
    self.set('Favorites', Option, Value)
    return

  def getLogFile(self):
    LogFile = None
    if self.has_option('General', 'LogFile'):
      LogFile = self.get('General', 'LogFile')
    if not LogFile:
      DataevalDir = os.path.expanduser(
        os.path.join('~', '.'+os.getenv('DATAEVAL_NAME', 'dataeval')))
      LogFile = os.path.join(DataevalDir, 'logs',
        'dataeval_%(Y)s-%(m)s-%(d)s_%(H)s-%(M)s-%(S)s_%(cnt)d.log')
      self.set('General', 'LogFile', LogFile)
    return LogFile

  def getStreamLogLevel(self):
    Level = None
    if self.has_option('General', 'StreamLogLevel'):
      Level = self.get('General', 'StreamLogLevel')
    if not Level:
      Level = Logger.DEFAULT_STREAM_LOG_LEVEL
      self.set('General', 'StreamLogLevel', Level)
    return int(Level)

  def save(self):
    if self.NoSave or (not self.ForcedSave and self.changed()):
      return

    self._removeTempModules()
    Config = open(self.CfgPath, 'wb')
    self.write(Config)
    Config.close()
    return

  def getQtStyleWildCard(self):
    WildCard = self.get('General', 'WildCard')
    if WildCard:
      WildCard = 'foo (' + WildCard + ')'
    return WildCard

  def getQtExtendedStyleWildCard(self):
    QtWildCard = self.getQtStyleWildCard()
    WildCard = '' if not QtWildCard else ' ;;' + str(QtWildCard)
    return 'All ( *.* ) ' + WildCard

  def ls(self):
    "list the sections of the config"
    for Section in sorted(self.sections()):
      yield Section
    return

  def l(self, Section):
    "list the options of SECTION"
    for Option in sorted(self.options(Section)):
      yield '%s = %s' %(Option, self.get(Section, Option) )
    return

  def p(self, Parameter):
    "select (+) or deselect (-) PARAM of MODULE"
    Parameter, Value = self.stripSelection(Parameter)
    Module, Parameter = Parameter.rsplit('.', 1)
    self.set(Module, Parameter, Value)
    return

  def i(self, Module):
    "select the MODULE to run"
    Module, Value = self.stripSelection(Module)

    for Section in self.Sections:
      if self.has_option(Section, Module):
        self.set(Section, Module, Value)
        break
    else:
      raise ValueError('Invalid interface module: %s' %Module)
    return

  def n(self, Section):
    "set all the option of SECTION to no.\n"\
    "All the interface section will be reset in case of Modules"
    if Section == 'Modules':
      Sections = self.Sections.keys()
    else:
      Sections = [Section]
    for Option in self.options(Section):
      self.set(Section, Option, 'no')
    return

  def b(self, BatchFile):
    "set BATCH as batch database"
    if BatchFile is None: return

    BatchFile = os.path.abspath(BatchFile) if BatchFile else BatchFile
    self.set('General', 'BatchFile', BatchFile)
    return

  def repdir(self, RepDir):
    "set REPDIR as report directory for BATCH"
    if RepDir is None: return

    RepDir = os.path.abspath(RepDir) if RepDir else RepDir
    self.set('General', 'RepDir', RepDir)
    return

  def measpath(self, MeasPath):
    "set MEASPATH as searching path to find measurement in case of\n"\
    "inconsistent BATCH"
    if not isinstance(MeasPath, str):
      return
    self.set('General', 'MeasPath', MeasPath)
    return

  def m(self, Measurement):
    "set MEASUREMENT as CHANNEL measurement channel\n\n"\
    "default CHANNEL is main"
    if Measurement.count('=') == 1:
      Channel, Measurement = Measurement.split('=')
    else:
      Channel = 'main'
    Measurement = os.path.abspath(Measurement) if Measurement else Measurement
    self.set('Measurement', Channel, Measurement)
    return

  def u(self, Backup):
    "set BACKUP as backup directory"
    if not Backup: return

    Backup = os.path.abspath(Backup)
    self.set('General', 'Backup', Backup)
    return

  def s(self, cSource):
    "set SOURCE_CLASS as signal source class"
    if not isinstance(cSource, str):
      return
    self.set('General', 'cSource', cSource)
    return

  def param(self, ModuleName, ParamName, PrjName, Value):
    "set PARAM as temporary parameter for MODULE with VALUE\n\n"\
    "--param viewFoo bar spam=42,egg=56"
    Module = self.Modules.clone_module(ModuleName, ParamName, PrjName, Value)
    Interface = Module.interface
    self.TempModules.append( (ModuleName, ParamName, PrjName) )
    self.initModuleByName(Interface, ModuleName, ParamName, PrjName)
    self.activateModule(Interface, ModuleName, {ParamName}, PrjName,
                        Module.channels)
    return

  def mapdb(self, MapDb):
    "Set the name of the map database for map manager"
    if not MapDb: return

    self.set('General', 'MapDb', os.path.abspath(MapDb))
    return

  def osmfile(self, OsmFile):
    "Set the name of the osm file for map manager"
    if not OsmFile: return

    self.set('General', 'OsmFile', os.path.abspath(OsmFile))
    return

  def logfile(self, LogFile):
    "Set the logging file path"
    if not LogFile: return

    self.set('General', 'LogFile', os.path.abspath(LogFile))
    return

  def streamLogLevel(self, StreamLogLevel):
    "Set the logging level of stderr"
    if not StreamLogLevel: return

    self.set('General',  'StreamLogLevel', StreamLogLevel)

    return


  def procInfoArgs(self, Args):
    Info = []
    if Args.ls:
      Info.append('[section names]')
      Info.extend( self.ls() )
    for Section in sorted(Args.l):
      Info.append('[%s]' %Section )
      Info.extend( self.l(Section) )
    return Info

  def procArgs(self, Args):
    # reset sections
    for Section in Args.n:
      self.n(Section)
    # set interface modules
    for InterfaceModule in Args.i:
      self.i(InterfaceModule)
    # set module parameters
    for Parameter in Args.p:
      self.p(Parameter)
    for ModuleName_, ParamName, Value in Args.param:
      ModName, _, Prj = ModuleName.split(ModuleName_)
      self.param(ModName, ParamName, Prj, Value)
    # set global options
    self.RunNav = not Args.nonav
    self.SolidTimeCheck = Args.solidtimecheck
    self.b(Args.batch)
    self.repdir(Args.repdir)
    self.measpath(Args.measpath)
    self.ReplMeas = Args.replmeas
    self.Start = Args.start
    self.StartDate = Args.start_date
    self.EndDate = Args.end_date
    for Param, Value in Args.global_param:
      self.GlobalParams[Param] = Value
    for Measurement in Args.measurement:
      self.m(Measurement)
    self.u(Args.backup)
    self.mapdb(Args.mapdb)
    self.osmfile(Args.osmfile)
    self.s(Args.source_class)
    self.Verbose = Args.verbose
    self.NoSave = Args.nosave
    self.ForcedSave = Args.forced_save
    self.DocName = Args.doc_name
    self.EnableBatchUpdate = Args.batch_update
    if Args.file_log_level:
      self.FileLogLevel = int(Args.file_log_level)
    else:
      self.FileLogLevel = Logger.DEFAULT_FILE_LOG_LEVEL
    self.logfile(Args.log_file)
    self.streamLogLevel(Args.stream_log_level)
    self.NoColor = Args.nocolor

    for Section in self.Sections.itervalues():
      Section.procArgs(Args)
    return

  def toggleVerbose(self):
    self.Verbose = not self.Verbose
    return

  @classmethod
  def addArguments(cls, Parser):
    Group = Parser.add_argument_group(title='config')
    Group.add_argument('--push', metavar='CONFIG',
                       help='use CONFIG as default config')
    Group.add_argument('--export', metavar='CONFIG',
                       help='save the config as CONFIG and exit')
    Group.add_argument('--config', metavar='CONFIG',
                       help='use CONFIG as temporary config')
    Group.add_argument('--nosave',
                       help='do not save the changes into the config file',
                       action='store_true', default=False)
    Group.add_argument('--forced-save',
                       help='save the config even if it was changed by other'
                            'program',
                       action='store_true', default=False)

    Group = Parser.add_argument_group('print')
    Group.add_argument('--ls',
                        help=cls.ls.__doc__+' and exit', action='store_true',
                        default=False)
    Group.add_argument('-l', help=cls.l.__doc__+' and exit', action='append',
                       metavar='SECTION', default=[])

    Group = Parser.add_argument_group('user modules')
    Group.add_argument('-n', help=cls.n.__doc__, action='append', default=[],
                       metavar='SECTION')
    Group.add_argument('-i', help=cls.i.__doc__, action='append', default=[],
                       metavar='+/-MODULE')
    Group.add_argument('-p', help=cls.p.__doc__, action='append', default=[],
                       metavar='+/-MODULE.PARAM')
    Group.add_argument('--param', help=cls.param.__doc__, nargs=3,
                        action='append', default=[],
                        metavar=('MODULE', 'PARAM', 'VALUE'))
    Group.add_argument('--global-param',
                        help='Store parameters (key-value pairs) to be accessible from user modules\n'
                             'Example:\n'
                             '  "--global-param par1 val1 --global-param par2 val2"\n'
                             '  --> self.global_params[par1] = val1\n'
                             '      self.global_params[par2] = val2',
                        nargs=2, action='append', default=[],
                        metavar=('PARAM', 'VALUE'))

    Group = Parser.add_argument_group('control')
    Group.add_argument('--norun',
                        help='set the configuration only and do not run the modules',
                        action='store_true',
                        default=False)
    Group.add_argument('--nonav',
                        help='do not load any navigator and do not wait enter to quit',
                        action='store_true',
                        default=False)
    Group.add_argument('--nodirectsound',  # handled in datavis/pyglet_workaround.py
                        help='do not load DirectSound driver - option might be removed!',
                        action='store_true',
                        default=False)
    Group.add_argument('--solidtimecheck',
                        help='set the global time check choose to not strictly growing',
                        action='store_true',
                        default=False)
    Group.add_argument('-v', '--verbose', action='store_true', default=False)
    Group.add_argument('--log-file',
                        help='Set log file path pattern. Empty string '
                             'disables the logging to file feature.\n'
                             'Possible string specifiers:\n'
                             '  Y,m,d,H,M,S (see time.strftime() for explanation)\n'
                             'Possible integer specifiers:\n'
                             '  cnt (counter, increases until non-existing file found)\n'
                             'Example:\n'
                             '  "mass_%%(Y)s-%%(m)s-%%(d)s_%%(H)s-%%(M)s-%%(S)s_%%(cnt)03d.log"\n'
                             '  --> "mass_2014-03-10_09-35-53_001.log"')
    Group.add_argument('--file-log-level',
                        help='Set the logging level of the file logger, default is DEBUG' \
                              '\nDEBUG=10\nINFO=20\nWARNING=30\nERROR=40\nCRITICAL=50')

    Group.add_argument('--stream-log-level',
                        help='Set the logging level of the stream logger, default is INFO' \
                              '\nDEBUG=10\nINFO=20\nWARNING=30\nERROR=40\nCRITICAL=50',
                      )
    Group.add_argument('--nocolor',
                        help='Disable the stderr coloring function of logger',
                        action='store_true',
                        default=False)

    Group = Parser.add_argument_group('batch')
    Group.add_argument('-b', '--batch', help=cls.b.__doc__,)
    Group.add_argument('--repdir', help=cls.repdir.__doc__,)
    Group.add_argument('--start', default='',
                        help='set the start time for BATCH')
    Group.add_argument('--start-date', default=None,
                        help='Store \'start_date\' attribute to use for filtering query results')
    Group.add_argument('--end-date', default=None,
                        help='Store \'end_date\' attribute to use for filtering query results')
    Group.add_argument('--batch-update', action='store_true',
                       default=False,
                       help='Update obsolete database file to current batch version')

    Group = Parser.add_argument_group('batch measurement replacement')
    Group.add_argument('--measpath', help=cls.measpath.__doc__)
    Group.add_argument('--replmeas',
                        help='replace the non existent measurements from measpath',
                        action='store_true',
                        default=False)

    Group = Parser.add_argument_group('source')
    Group.add_argument('-m', '--measurement', metavar='CHANNEL=MEASUREMENT',
                        help=cls.m.__doc__, action='append', default=[])
    Group.add_argument('-u', '--backup', help=cls.u.__doc__)
    Group.add_argument('-s', '--source-class', help=cls.s.__doc__)

    Group = Parser.add_argument_group('pdf')
    Group.add_argument('--doc-name', help='Name of the generated pdf document')

    Group = Parser.add_argument_group('map navigator')
    Group.add_argument('--mapdb', help=cls.mapdb.__doc__)
    Group.add_argument('--osmfile', help=cls.osmfile.__doc__)

    for Section in cls.SectionTypes.itervalues():
      Section.addArguments(Parser)
    return Parser

def init_dataeval(argv, interface='iView', cfg_name='dataeval',
                  modules_name='modules', modules_ext='.csv'):
  modules_name = getConfigPath(modules_name, modules_ext)
  modules = Modules()
  modules.read(modules_name)

  parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
  args = Config.addArguments( parser ).parse_args(argv)

  name = procConfigFile(cfg_name, args)
  config = Config(name, modules)
  config.init(args)

  manager = config.createManager(interface)
  config.load(manager, interface)
  modules = manager.get_modules()
  return config, manager, modules
