from measproc.batchsqlite import Result
from measproc.Report import cEmptyReport, cIntervalListReport
from measproc.report2 import Report
from measproc.relations import not_equal
from measproc import cIntervalList
from modules import ModuleName

class iInterface(object):
  dep = ()
  ":type: tuple, list, set, dict or basestring"
  optdep = ()
  ":type: tuple, list, set, dict or basestring"
  channels = 'main',

  def __init__(self, manager, prj_name, **kwargs):
    self._manager = manager
    self._prj_name = prj_name
    for name in manager._provide:
      setattr(self, name, getattr(manager, name))
    self.init(**kwargs)
    self._passed_optdep = ()
    ":type: tuple"
    return

  def extend_deps(self, dep):
    return tuple(self.extend_dep(d) for d in self.iterdep(dep))

  def extend_dep(self, single_dep):
    return ModuleName.extend_prj_name(single_dep, self._prj_name)

  @staticmethod
  def iterdep(dep):
    if isinstance(dep, tuple) or isinstance(dep, list) or isinstance(dep, set):
      for d in dep:
        yield d
    elif isinstance(dep, dict):
      for d in dep.itervalues():
        yield d
    elif isinstance(dep, basestring):
      yield dep
    else:
      raise TypeError("Unsupported dep type: '%s'" % type(dep))
    return


  def get_passed_optdep(self):
    return self._passed_optdep
  passed_optdep = property(get_passed_optdep)
  ":type: tuple"

  def init(self, **kwargs):
    return

  def check(self):
    pass

  def fill(self, *args):
    if len(args) == 1:
      args, = args
    return args

  def error(self, *args):
    pass

  @classmethod
  def getSign(cls):
    return '%s.%s' %(cls.__module__, cls.__name__)


  def get_source(self, channel='main'):
    "Get the `cSignalSource` instance of `channel`."
    return self._manager.get_source(channel)
  source = property(get_source)

  def get_sync(self):
    "Get the global `cSynchronizer` instance."
    return self._manager.sync
  sync = property(get_sync)

  def get_modules(self):
    "Get the main `Modules` which is the same like interface.Objects."
    return self._manager.modules
  modules = property(get_modules)

  def get_batch(self):
    "Get the global `cBatch` instance."
    return self._manager.batch
  batch = property(get_batch)

  def get_batchnav(self):
    "Get the global `cBatchNavigator` instance."
    return self._manager.batchnav
  batchnav = property(get_batchnav)

  def get_interval_table(self):
    "Get the global IntervalTable instance."
    return self._manager.interval_table
  interval_table = property(get_interval_table)

  def get_prj_name(self):
    return self._prj_name
  prj_name = property(get_prj_name)

  def get_grouptypes(self):
    "Get the global `GroupTypes` instance."
    return self._manager.grouptypes
  grouptypes = property(get_grouptypes)

  def get_grouptype(self, type_name, prj=None):
    grouptypes = self.get_grouptypes()
    prj = self._prj_name if prj is None else prj
    type_number = grouptypes.get_type(prj, type_name)
    return type_number

  def get_doc(self, template_name, **kwargs):
    return self._manager.get_doc(template_name, **kwargs)

  def get_docname(self):
    return self._manager.get_docname()  # or: self.get_doc(...).filename
  docname = property(get_docname)

  def clone_manager(self):
    return self._manager.clone()

  def get_mapman(self):
    "Get the global `cMapManager` instance"
    return self._manager.mapman
  mapman = property(get_mapman)

  def reload_interface(self):
    self._manager.reload_interface()
    return

  def get_logger(self):
    """
    Get the global logger.

    Use the following methods for logging:
    debug(msg), info(msg), warning(msg), error(msg), critical(msg)

    Example:
      logger = self.get_logger()
      logger.debug("foo")
    """
    return self._manager.logger
  logger = property(get_logger)

  def is_strong_time_check(self):
    return self._manager.strong_time_check
  strong_time_check = property(is_strong_time_check)

  def get_start_date(self):
    return self._manager.start_date
  start_date = property(get_start_date)

  def get_end_date(self):
    return self._manager.end_date
  end_date = property(get_end_date)

class Interface(iInterface):
  def run(self, *args):
    return

  def error(self):
    return

class iFill(Interface):
  """Interface for object source"""

class iCalc(Interface):
  """Interface for object source used for further calculations"""

class iSearch(iInterface, Result):
  """Interface for batch processing"""

  def search(self, *args, **kwargs):
    """
    Register report entry into interface.Batch

    :Exceptions:
      AttributeError
        interface.Batch is not initialized
    """
    pass

  def run(self, *args, **kwargs):
    return self.search(*args, **kwargs)

  def error(self, *args):
    "Register an empty report with ERROR result"
    report = Report(cIntervalList(), "Inactive module")
    self.batch.add_entry(report, result=self.ERROR)
    return


class iCompare(iInterface):
  channels = 'main', 'compare'
  """Interface to compare signal in two measurement."""
  SignalGroups = [{}]
  """:type: list
  Signal group list for comparition."""
  TitlePattern = '%s not equal'
  """:type: str
  Title pattern string"""

  def check(self):
    Compare = self.get_source('compare')
    Source = self.get_source('main')
    CompareGroup = Compare.selectSignalGroup(self.SignalGroups)
    SourceGroup = Source.selectSignalGroup(self.SignalGroups)
    return CompareGroup, SourceGroup

  def fill(self, CompareGroup, SourceGroup):
    return CompareGroup, SourceGroup

  def compare(self, Param, CompareGroup, SourceGroup):
    """
    Register reports into interface.Batch

    :Exceptions:
      AttributeError
        interface.Batch is not initialized
        interface.Compare is not initialized
        interface.Source is not initialized
    """
    ClassSign = self.getSign()
    ParSign = Param.getSign()
    Compare = self.get_source('compare')
    Source = self.get_source('main')
    Batch = self.get_batch()

    Measurement, Local = Batch.get_measurement()

    for Alias in CompareGroup:
      CompareTime,\
      CompareValue = Compare.getSignalFromSignalGroup(CompareGroup, Alias)
      SourceTime,\
      SourceValue  = Source.getSignalFromSignalGroup(SourceGroup, Alias)
      Intervals = Source.compExtSigExtSig(CompareTime, CompareValue,
                                          not_equal,
                                          SourceTime,  SourceValue)
      Title = self.TitlePattern %Alias
      Report = cIntervalListReport(Intervals, Title)
      Result = 'passed' if len(Intervals) == 0 else 'failed'
      for FileName in Compare.FileName, Source.FileName:
        Batch.set_measurement(FileName, Local)
        Batch.add_entry(Report, result=Result)
    Batch.set_measurement(Measurement, Local)
    pass

  def run(self, *args, **kwargs):
    return self.compare(*args, **kwargs)

  def error(self, Param):
    ClassSign = self.getSign()
    ParSign = Param.getSign()
    Compare = self.get_source('compare')
    Source = self.get_source('main')
    Comment = '%s or %s was inconsistent' %(Compare.FileName, Source.FileName)
    self.addInconcReports(ClassSign, ParSign, Comment)
    return

  def addInconcReports(self, ClassSign, ParSign, Comment):
    Result = 'inconc'
    Compare = self.get_source('compare')
    Source = self.get_source('main')
    Batch = self.get_batch()

    Measurement, Local = Batch.get_measurement()

    for Alias in self.SignalGroups[0]:
      Title = self.TitlePattern %Alias
      Report = cEmptyReport(Title)
      Report.ReportAttrs['Comment'] = Comment
      for FileName in Compare.FileName, Source.FileName:
        Batch.set_measurement(FileName, Local)
        Batch.add_entry(Report, result=Result)
    Batch.set_measurement(Measurement, Local)
    return

class iAnalyze(iInterface):
  """Interface for BatchNavigator initialization"""
  def analyze(self, *args, **kwargs):
    """
    Add new frame to `datavis.BatchNav`

    :Exceptions:
      AttributeError
        interface.BatchNav is not initialized
        interface.Batch is not initialized
    """
    pass

  def run(self, *args, **kwargs):
    return self.analyze(*args, **kwargs)

  def addLastReports(self, SearchClass, SearchSign):
    Batch = self.get_batch()
    Pack = Batch.get_last_entries(SearchClass, SearchSign,
                                  type='measproc.Report')
    BatchNav = self.get_batchnav()
    BatchNav.BatchFrame.addEntries(Pack)
    pass

  def addAllReports(self, SearchClass, SearchSign):
    Batch = self.get_batch()
    Pack  = Batch.filter(class_name=SearchClass, param=SearchSign,
                         type='measproc.Report')
    BatchNav = self.get_batchnav()
    BatchNav.BatchFrame.addEntries(Pack)
    pass

class iView(iInterface):
  """Interface for navigator initialization"""
  def view(self, *args, **kwargs):
    """
    Add new navigator to `datavis.Sync`

    :Exceptions:
      AttributeError
        interface.Sync is not initialized
    :ReturnType: list
    :Return: Selected group of the initialized navigators, it can be anempty list.
    """
    pass

  def run(self, *args, **kwargs):
    return self.view(*args, **kwargs)

class iObjectFill(iFill):
  """Interface for object source in TrackNavigator and VideoNavigator"""

class iAreaFill(iFill):
  """Interface for areas in TrackNavigator"""

class iGPSTrajectoryFill(iFill):
  """Interface for trajectories in MapNavigator"""

class iTrajectoryFill(iFill):
  """Interface for trajectories in TrackNavigator"""
