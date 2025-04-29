from datavis import pyglet_workaround  # necessary as early as possible (#164)

from PySide import QtCore

import os
import sys
import inspect
import logging
import traceback

from reportlab.platypus import BaseDocTemplate
from datalab.textilelab.doctemplate import SimpleDocTemplate

import interface
from datavis.Synchronizer import cSynchronizer
from datavis.BatchNavigator import cBatchNavigator, CreateBatchNav
from measproc.batchsqlite import Batch, CreateParams
from modules import Modules
from measparser.SignalSource import cSignalSource
from grouptypes import GroupTypes
from config.parameter import Params, GroupParams, TypeParams
from measproc.mapmanager import MapManager
from datavis.IntervalFrame import TableModel as IntervalTable, \
                                  CreateIntervalTable
import measproc
from measproc.vidcalibs import VidCalibs

class ObjectEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(object)

class Manager:
  LoadSignal = ObjectEmittingSignal()
  def __init__(self):
    self._Source = cSignalSource
    self._measurements = {}
    self._sources = {}
    self._backup = None
    self._sync = None
    self._modules = Modules()
    self._batch_params = None
    self.start_date = None
    self.end_date = None
    self.global_params = {}
    self.meas_path = ''
    self._batch = None
    self._batchnav_params = None
    self._interval_table = None
    self._int_table_params = None
    self._batchnav = None
    self._mapdb = None
    self._osmfile = None
    self._mapman = None
    self.legends = {}
    self._legends = TypeParams()
    self.shape_legends = {}
    self._shape_legends = TypeParams()
    self.groups = {}
    self._groups = GroupParams()
    self.view_angles = {}
    self._view_angles = Params()
    self._vidcalibs = None
    self._vidcalibs_path = None
    self.reports = {}
    self.report2s = {}
    self.statistics = {}
    self.report = None
    self.strong_time_check = True
    self.run_navigator = True
    self.run_batchnav = False
    self.verbose = False
    self.grouptypes = GroupTypes()
    self._doctemplates = {}
    self._docname = None
    self.logger = logging.getLogger()

    self._provide = (
      'vidcalibs', 'legends', 'shape_legends', 'view_angles', 'global_params',)
    return

  def clone(self):
    manager = Manager()
    manager._Source = self._Source
    manager._measurements = self._measurements.copy()
    manager._backup = self._backup
    manager._modules = self._modules.clone()
    manager._batch_params = self._batch_params
    manager.start_date = self.start_date
    manager.end_date = self.end_date
    manager.global_params = self.global_params.copy()
    manager.meas_path = self.meas_path
    manager._batchnav_params = self._batchnav_params
    manager._interval_table = self._interval_table
    manager._int_table_params = self._int_table_params
    manager._legends = self._legends.copy()
    manager._shape_legends = self._shape_legends.copy()
    manager._groups = self._groups.copy()
    manager._view_angles = self._view_angles.copy()
    manager._vidcalibs = self._vidcalibs
    manager._vidcalibs_path = self._vidcalibs_path
    manager.strong_time_check = self.strong_time_check
    manager.run_navigator = self.run_navigator
    manager.run_batchnav = self.run_batchnav
    manager.verbose = self.verbose
    manager.grouptypes = self.grouptypes.copy()
    manager._doctemplates = self._doctemplates.copy()
    manager._docname = self._docname
    return manager

  def close(self, close_batch=True):
    "Clear the class variables."
    for channel in self._sources.keys():
      source = self._sources.pop(channel)
      try:
        source.save()
      except IOError:
        self.logger.warning("IOError while closing %s" % source.FileName)
    if isinstance(self._batchnav, cBatchNavigator):
      #BN can be closed from multiple source. Can be closed by manually or
      #the manager can close too, if ctrl + c pressed from cli. Check the
      #existence of BN before close it from the manager
      if self._batchnav.isVisible():
        self._batchnav.quit()
      self._batchnav = None
    if close_batch and isinstance(self._batch, Batch):
      #self._batch.save()  # save() disabled as a workaround #1133
      self._batch = None
    if isinstance(self._sync, cSynchronizer):
      self._sync.close()
      self._sync = None
    if isinstance(self._mapman, MapManager):
      self._mapman = None
    if isinstance(self._interval_table, IntervalTable):
      #self._interval_table.close()
      pass
    self._modules.close()
    self.legends.clear()
    self.shape_legends.clear()
    self.groups.clear()
    self.view_angles.clear()
    self.reports.clear()
    self.report2s.clear()
    self.statistics.clear()
    self.report = None
    self._mapdb = None
    self._osmfile = None
    self.start_date = None
    self.end_date = None
    self.global_params.clear()
    self.free_interface()
    return

  def free_interface(self):
    interface.Sync = None
    interface.Source = None
    interface.Objects = None
    interface.Batch = None
    interface.BatchNav = None
    interface.Legends = {}
    interface.ShapeLegends = {}
    interface.Groups = {}
    interface.ViewAngles = {}
    interface.Reports = {}
    interface.Statistics = {}
    interface.Report = None
    interface.StrictlyGrowingTimeCheck = True
    return

  def reload_interface(self):
    self.load_main()
    self.load_params()
    return

  def load_main(self):
    "Load the main channel source into interface package"
    self.LoadSignal.signal.emit(self)
    return

  def _load_main(self):
    return

  def select_params(self, status_names):
    names = {
      'view_angles':   self._view_angles,
      'legends':       self._legends,
      'shape_legends': self._shape_legends,
      'groups':        self._groups,
    }
    for name, param in names.iteritems():
      unfiltered = getattr(self, name)
      unfiltered.clear()
      filtered = param.filter(status_names)
      unfiltered.update(filtered)
    return

  def load_params(self):
    interface.ViewAngles = self.view_angles
    interface.Legends = self.legends
    interface.ShapeLegends = self.shape_legends
    interface.Groups = self.groups
    return

  def set_view_angles(self, view_angles):
    self._view_angles.update(view_angles)
    return

  def set_legends(self, prj_name, param):
    activated = param.activate(self.grouptypes, prj_name)
    self._legends.update(activated)
    return

  def set_shape_legends(self, prj_name, param):
    activated = param.activate(self.grouptypes, prj_name)
    self._shape_legends.update(activated)
    return

  def set_groups(self, prj_name, param):
    activated = param.activate(self.grouptypes, prj_name)
    self._groups.update(activated)
    return

  def set_groups_visible(self, visibles):
    for name, param in self.groups.iteritems():
      param.Visible = name in visibles
    return

  def set_vidcalibs(self, vidcalibs_path):
    self._vidcalibs_path = vidcalibs_path
    self._vidcalibs = None
    return

  def get_vidcalibs(self):
    assert self._vidcalibs_path is not None
    if self._vidcalibs is None:
      if os.path.exists(self._vidcalibs_path):
        self._vidcalibs = VidCalibs(self._vidcalibs_path)
      else:
        # default vidcalib.db path
        self._vidcalibs = VidCalibs(os.path.join("\\".join(__file__.split('\\')[:-4]), "aebs\\src\\aebs\\par\\vidcalibs.db"))
    return self._vidcalibs
  vidcalibs = property(get_vidcalibs)

  def get_source(self, channel='main'):
    "Get the `cSignalSource` instance of `channel`."
    assert channel in self._measurements, \
      'No measurement selected for `%s` channel' %channel
    if channel not in self._sources:
      measurement = self._measurements[channel]
      if self.verbose:
        self.logger.info('Loading %s into `%s` channel...' %
                         (measurement, channel))
      else:
        self.logger.info('Loading %s...' % os.path.basename(measurement))
        self.logger.debug('`%s`=%s' % (channel, measurement))
      source = self._Source(measurement, self._backup)
      self._sources[channel] = source
      if self.verbose:
        self.logger.info('Measurement comment:\n\n%s\n\n' %
                         source.getFileComment())
    return self._sources[channel]
  source = property(get_source)

  def set_measurement(self, measurement, channel='main'):
    "Set `measurement` for `channel` to create source from that file."
    self._measurements[channel] = measurement
    return

  def get_backup(self):
    "Get backup directory for source."
    return self._backup
  def set_backup(self, backup):
    "Set backup directory for source."
    self._backup = backup or None
    return
  backup = property(get_backup, set_backup)

  def get_source_class(self):
    return self._Source
  def set_source_class(self, source_class):
    "Set the class of the source"
    self._Source = source_class
    return
  source_class = property(get_source_class, set_source_class)

  def is_source_loaded(self, channel):
    return channel in self._sources

  def get_sync(self):
    "Get the global `cSynchronizer` instance."
    if self._sync is None:
      mediator = CloseMediator(self)
      self._sync = cSynchronizer()
      self._sync.setMediator(mediator)
    return self._sync
  sync = property(get_sync)

  def is_sync_loaded(self):
    return isinstance(self._sync, cSynchronizer)

  def get_modules(self):
    "Get the main `Modules` which is the same like interface.Objects."
    return self._modules
  modules = property(get_modules)

  def get_batch(self):
    "Get the global `cBatch` instance."
    if self._batch is None:
      assert isinstance(self._batch_params, CreateParams),\
             'No batch parameters have been set.'
      if self.verbose:
        db_name_disp = self._batch_params.db_name
      else:
        db_name_disp = os.path.basename(self._batch_params.db_name)
      self.logger.info('Loading %s...' % db_name_disp)
      batch = self._batch_params()
      if self.meas_path:
        batch.repl_meas(self.meas_path)
      self.set_batch(batch)
    return self._batch
  def set_batch(self, batch):
    "Set the global `cBatch` instance."
    self._batch = batch
    self._set_report_dir(batch.dirname)
    return
  batch = property(get_batch, set_batch)

  def _set_report_dir(self, report_dir):
    measproc.Statistic.StatDir = report_dir
    measproc.Report.RepDir = report_dir
    measproc.workspace.WorkSpaceDir = report_dir
    measproc.figentry.FigEntryDir = report_dir
    measproc.textentry.TextEntryDir = report_dir
    return

  def set_batch_params(self, db_file, report_dir, labels, tags, results,
                       quanames, enable_update):
    "Store the parameter of batch constructor"
    self._batch_params = CreateParams(db_file, report_dir, labels, tags,
                                      results, quanames, enable_update)
    return

  def is_batch_loaded(self):
    return isinstance(self._batch, Batch)

  def set_batchnav_params(self, config, header, sortby, query, interval_header,
                          interval_sortby):
    batch = self.get_batch()
    interval_table = self.get_interval_table()
    self._batchnav_params = CreateBatchNav(batch, config, header, sortby, query,
                                           interval_table)
    return

  def set_int_table_params(self, interval_header, interval_sortby):
    self._interval_table = None
    batch = self.get_batch()
    self._int_table_params = CreateIntervalTable(batch, interval_header,
                                                  interval_sortby)
    return

  def get_batchnav(self):
    "Get the global `cBatchNavigator` instance."
    if self._batchnav is None:
      assert isinstance(self._batchnav_params, CreateBatchNav),\
             'No batch navigator parameters have been set'
      self._batchnav = self._batchnav_params()
    return self._batchnav
  batchnav = property(get_batchnav)

  def set_interval_table(self, int_table):
    assert isinstance(int_table, TableModel), 'Invalid table model'
    self._interval_table = int_table
    return
  def get_interval_table(self):
    if self._interval_table is None:
      assert isinstance(self._int_table_params, CreateIntervalTable),\
             'No interval table parameters have been set'
      self._interval_table = self._int_table_params()
    return self._interval_table
  interval_table = property(get_interval_table, set_interval_table)

  def get_mapdb(self):
    return self._mapdb
  def set_mapdb(self, mapdb):
    if isinstance(mapdb, basestring) and mapdb:
      self._mapdb = mapdb
    return
  mapdb = property(get_mapdb, set_mapdb)

  def get_osmfile(self):
    return self._osmfile
  def set_osmfile(self, osmfile):
    if isinstance(osmfile, basestring) and osmfile:
      self._osmfile = osmfile
    return
  osmfile = property(get_osmfile, set_osmfile)

  def get_mapman(self):
    assert self._mapdb is not None, 'No map database has been set'
    if self._mapman is None:
      self._mapman = MapManager(self._mapdb)
      if self._osmfile:
        self._mapman.setOsmFile(self._osmfile)
      else:
        self._mapman.setOsmFile("")
    return self._mapman
  mapman = property(get_mapman)

  def set_doctemplate(self, name, template):
    assert inspect.isclass(template) and issubclass(template, (BaseDocTemplate, SimpleDocTemplate)),\
           'The template is not a BaseDocTemplate descendant'
    self._doctemplates[name] = template
    return

  def get_docname(self):
    return self._docname
  def set_docname(self, docname):
    self._docname = docname
    return
  docname = property(get_docname, set_docname)

  def get_doc(self, template_name, logo='Knorr_logo.png', footer=None,
              header='Strictly confidential', **kwargs):
    """
    :Parameters:
      template_name : str
        Name of the document template.
    :Keywords:
      * : *
        Any keyword for the template initialization.
    """
    assert template_name in self._doctemplates,\
           '%s is not a valid template name, please select from %s'\
           %(template_name, self._doctemplates.keys())
    assert self._docname is not None,\
           'File name for document not set'
    Template = self._doctemplates[template_name]
    Template.set_logo(logo)
    Template.HEADER = header
    if footer is not None:
      Template.FOOTER = footer
    doc = Template(self._docname, **kwargs)
    return doc

  def append_dataeval_path(self, name):
    sys.path.append(name)
    return

  def run(self, name):
    try:
      self._modules.run(name)
    except:
      msg = traceback.format_exc()
    else:
      msg = ''
    return msg

  def _refresh(self, name):
    sync = self.get_sync()
    sync.setModule(name)
    class_sign, param_sign, file_name = self._modules.get_sign(name)
    if self.is_batch_loaded():
      batch = self.get_batch()
      batch.set_module(class_sign, param_sign, file_name)
    return

  def seek(self, time):
    time = float(time)
    sync = self.get_sync()
    sync.seek(time)
    return

  def set_roi(self, start, end, color='g', pre_offset=10.0, post_offset=10.0):
    start = float(start)
    end = float(end)
    sync = self.get_sync()
    sync.onSetROI(None, start, end, color)
    sync.set_xlim_online(start - pre_offset, end + post_offset)
    return

  def set_axes_limits(self, limits):
    limits = [float(limit) if limit else None for limit in limits.split(',')]
    sync = self.get_sync()
    sync.setAxesLimits(limits)
    return

  def select_modules(self, module_names):
    modules = self.get_modules()
    actives = set()
    for module_name in module_names:
      modules.wake(module_name, self)
      self._refresh(module_name)
      if modules.select(module_name):
        self.logger.debug("Active module: %s" % module_name)
        actives.add(module_name)
      else:
        self.logger.warning("Inactive module: %s" % module_name)
        self.logger.info("Reasons:\n%s" % modules.get_error_msg(module_name))
    return actives

  def remove_from_runs(self, module_name):
    """
    Removes a running module from "Runs" list.
    """
    self._modules.remove_from_runs(module_name)
    return

  def build_modules(self, module_names):
    status = 0
    modules = self.get_modules()
    for module_name in module_names:
      self.logger.info("Running module: %s..." % module_name)
      self._refresh(module_name)
      modules.fill(module_name)
      msg = self.run(module_name)
      if msg:
        status += 1
        self.logger.error(msg)
    return status

  def build(self, module_names, status_names=None, visible_group_names=None,
            show_navigators=True):
    status_names = status_names or []
    visible_group_names = visible_group_names or []

    self.load_main()
    active_statuses = self.select_modules(status_names)
    self.select_params(active_statuses)
    self.set_groups_visible(visible_group_names)
    self.load_params()
    activate_modules = self.select_modules(module_names)
    status = self.build_modules(activate_modules)

    self.build_sync(show_navigators)
    return status

  def build_sync(self, show_navigators):
    if not self.is_sync_loaded(): return
    sync = self.get_sync()
    meas = os.path.basename(self._measurements.get('main', ''))
    sync.setWindowTitles(meas)
    sync.start(sync.seektime)
    if show_navigators:
      sync.show()
    return

  def set_batch_results(self, batch_results):
    self.reports = batch_results['measproc.cFileReport']
    self.report2s = batch_results['measproc.Report']
    self.statistics = batch_results['measproc.cFileStatistic']
    return

class CloseMediator(object):
  """
  Unillateral mediator to communicate the Navigator with the Modules
  in order to notify of state changes (To closed state for now)
  """
  def __init__(self, target):
    self.target = target
    return

  def send_close(self, module):
    if isinstance(self.target, Manager):
      self.target.remove_from_runs(module)
    return

class AnalyzeManager(Manager):
  def _load_main(self):
    return

