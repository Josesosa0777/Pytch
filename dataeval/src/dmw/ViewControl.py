import os

from PySide import QtCore, QtGui

from datavis.ConcurrenceNavigator import cConcurrenceNavigator

class StringEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(str)

class cViewControl:
  Channel = 'main'
  Interface = 'iView'
  def __init__(self, root, Config):
    self.Config = Config
    self.Managers = {}
    self.ComboBoxUpdateSignal = StringEmittingSignal()
    self.CNcheck = QtGui.QCheckBox('Use CN')
    self.ConNav = None
    """:type: datavis.cConcurrenceNavigator
    Concurrence Navigator"""
    pass

  def onStart(self):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    BaseName = self.getBaseName()
    self.ComboBoxUpdateSignal.signal.emit(BaseName)
    self.start(BaseName)
    QtGui.QApplication.restoreOverrideCursor()
    return BaseName

  def onStartRecord(self,baseName):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    BaseName = baseName.split("\\")[-1]
    self.ComboBoxUpdateSignal.signal.emit(BaseName)
    list_modules= self.recordingstart(BaseName)
    QtGui.QApplication.restoreOverrideCursor()
    return BaseName,list_modules

  def recordingstart(self, BaseName):
    manager = self._getManager(BaseName)
    if self.CNcheck.isChecked():
      Sync = manager.get_sync()
      if self.ConNav is None:
        self.ConNav = cConcurrenceNavigator()
      Con = self.ConNav.addConcurrence(Sync, BaseName)
      self.addReports(Con, manager)
    module_list = self.Config._recordingbuild(manager, self.Interface)
    return module_list

  def start(self, BaseName):
    manager = self._getManager(BaseName)
    if self.CNcheck.isChecked():
      Sync = manager.get_sync()
      if self.ConNav is None:
        self.ConNav = cConcurrenceNavigator()
      Con = self.ConNav.addConcurrence(Sync, BaseName)
      self.addReports(Con, manager)
    self.Config.build(manager, self.Interface)
    return

  def getManager(self):
    BaseName = self.getBaseName()
    manager = self._getManager(BaseName)
    return manager

  def getBaseName(self):
    Name = self.Config.get('Measurement', 'main')
    BaseName = os.path.basename(Name)
    return BaseName

  def _getManager(self, BaseName):
    if BaseName not in self.Managers:
      Manager = self.Config.createManager(self.Interface)
      Manager.free_interface()
      self.Managers[BaseName] = Manager
    else:
      Manager = self.Managers[BaseName]
    self.Config.load(Manager, self.Interface)
    return Manager

  def addReports(self, Con, manager):
    Source = manager.get_source(self.Channel)
    try:
      Time = Source.getLongestTime()
    except UnboundLocalError:
      pass
    else:
      self.ConNav.setAllXlim(Time[0], Time[-1])
    self.ConNav.addReports(Con, manager.reports)
    return

  def onCloseAll(self):
    if self.ConNav is not None:
      self.ConNav.onClose()
      self.ConNav = None
    BaseNames = self.Managers.keys()
    for BaseName in BaseNames:
      self.close(BaseName)
    pass

  def close(self, BaseName):
    manager = self.Managers.pop(BaseName)
    self.Config.Sections[self.Interface].save(manager)
    manager.close()
    pass

  def getSource(self, Channel):
    BaseName = self.getBaseName()
    Manager = self._getManager(BaseName)
    self.Config.load(Manager, self.Interface)
    Source = Manager.get_source(Channel)
    return Source

class cBatchControl(cViewControl):
  def __init__(self, root, Config, Batch, interval_model=None):
    cViewControl.__init__(self, root, Config)
    self.Batch = Batch
    self.interval_model = interval_model
    return

  def onStart(self, Measurement, BatchResults):
    self.Config.m(Measurement)

    Manager = self.getManager()
    Manager.set_batch( self.Batch )

    Manager.set_batch_results(BatchResults)
    Measurement = cViewControl.onStart(self)
    return Measurement

  def seek(self, time):
    manager = self.getManager()
    manager.seek(time)
    return

  def setROI(self, ROIstart, ROIend):
    manager = self.getManager()
    manager.set_roi(ROIstart, ROIend)
    return

  def close(self, BaseName):
    manager = self.Managers.pop(BaseName)
    self.Config.Sections[self.Interface].save(manager)
    manager.close(close_batch=False)
    pass

  def getROI(self, Manager):
    Sync = Manager.get_sync()
    return Sync.ROIstart, Sync.ROIend

  def getActReport(self, Manager):
    return Manager.report2s or Manager.reports or Manager.statistics

  def addIntervalFromROI(self):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    Managers = self.Managers.values()
    for Manager in Managers:
      Report = self.getActReport(Manager)
      if not Report: continue

      Entries = Report.keys()
      Entry, = Entries
      ROIstart, ROIend = self.getROI(Manager)

      if ROIend <= ROIstart: continue

      IntervalTable = Manager.get_interval_table()
      Ids = Report[Entry]
      Pos, IntervalId, EntryId = Ids[0]

      Manager = self.getManager()

      Interval = Entry.getTimeIndex(ROIstart), Entry.getTimeIndex(ROIend) + 1

      Entry.addInterval(Interval)
      News, Removed = self.Batch.update_entry(Entry, EntryId)
      IntervalTable.addIntervals(News)
    QtGui.QApplication.restoreOverrideCursor()
    return

  def rmInterval(self):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    Manager = self.getManager()
    BaseName = self.getBaseName()
    
    if self.interval_model is None:
      IntervalTable = Manager.get_interval_table()
    else:
      IntervalTable = self.interval_model

    SelectedIntervalID = IntervalTable.get_selected()
    self.Batch.rm_interval(SelectedIntervalID)
    IntervalTable.rmSelectedInterval()

    self.close(BaseName)
    QtGui.QApplication.restoreOverrideCursor()
    return
