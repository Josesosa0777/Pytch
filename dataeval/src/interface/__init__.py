import sys
import types

from Interfaces import iSearch
from Interfaces import iView
from Interfaces import iAnalyze
from Interfaces import iCompare
from Interfaces import iFill
from Interfaces import iCalc
from Interfaces import iAreaFill
from Interfaces import iObjectFill
from Interfaces import iTrajectoryFill
from Interfaces import iGPSTrajectoryFill
from Parameter  import iParameter
from manager import Manager
from datavis.IntervalFrame import TableModel

class Interface(types.ModuleType):
  """
  Interface class to provide lazy attribute loading while keeping backward
  compatibility with the old interface module.
  """
  
  NullParam = iParameter()

  def __init__(self, *args, **kwargs):
    types.ModuleType.__init__(self, *args, **kwargs)
    self.Manager = None
    self._IntervalTable = None
    Manager.LoadSignal.signal.connect(self.set_manager)
    return

  def set_manager(self, Manager):
    self.Manager = Manager
    if self._IntervalTable is not None:
      self.Manager.interval_table = self._IntervalTable
    return

  def get_batch(self):
    return None if self.Manager is None else self.Manager.batch
  Batch = property(get_batch)

  def get_source(self):
    return None if self.Manager is None else self.Manager.source
  Source = property(get_source)

  def get_compare(self):
    return None if self.Manager is None else self.Manager.get_source(
                                                              channel='compare')
  Compare = property(get_compare)

  def get_sync(self):
    return None if self.Manager is None else self.Manager.sync
  Sync = property(get_sync)

  def get_batchnav(self):
    return None if self.Manager is None else self.Manager.batchnav
  BatchNav = property(get_batchnav)

  def get_objects(self):
    return None if self.Manager is None else self.Manager.modules
  Objects = property(get_objects)

  def get_legends(self):
    return {} if self.Manager is None else self.Manager.legends
  Legends = property(get_legends)

  def get_shape_legends(self):
    return {} if self.Manager is None else self.Manager.shape_legends
  ShapeLegends = property(get_shape_legends)

  def get_groups(self):
    return {} if self.Manager is None else self.Manager.groups
  Groups = property(get_groups)

  def get_view_angles(self):
    return {} if self.Manager is None else self.Manager.view_angles
  ViewAngles = property(get_view_angles)

  def get_reports(self):
    return {} if self.Manager is None else self.Manager.reports
  Reports = property(get_reports)

  def get_report2s(self):
    return {} if self.Manager is None else self.Manager.report2s
  Report2s = property(get_report2s)

  def get_statistics(self):
    return {} if self.Manager is None else self.Manager.statistics
  Statistics = property(get_statistics)

  def get_report(self):
    return None if self.Manager is None else self.Manager.report
  Report = property(get_report)

  def get_strictly_growing_time_check(self):
    return True if self.Manager is None else self.Manager.strong_time_check
  StrictlyGrowingTimeCheck = property(get_strictly_growing_time_check)

  def get_interval_table_model(self):
    if isinstance(self._IntervalTable, TableModel):
      return self._IntervalTable
    return None if self.Manager is None else self.Manager.interval_table
  IntervalTable = property(get_interval_table_model)

  def overwrite_sys_modules(self):
    if isinstance(sys.modules[__name__], Interface): return

    for attr in dir(sys.modules[__name__]):
      value = getattr(sys.modules[__name__], attr)
      setattr(self, attr, value)

    sys.modules[__name__] = self
    return

int_ = Interface(__name__)
int_.overwrite_sys_modules()
