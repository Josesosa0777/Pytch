# -*- coding: utf-8 -*-

import pyglet_workaround  # necessary as early as possible (#164)

import sys
import os

from PySide import QtGui, QtCore

from batchframe import BatchFrame
from IntervalFrame import IntervalFrame
from measproc.Report import getTitle
from dmw.SyncAppEditor import cSyncAppEditor
from dmw.ViewControl import cBatchControl
from dmw.OptionFrames import cCheckDirOption, cFileOption
from dmw.ConfigFrame import cConfigFrame
from dmw.section_table import ModuleTableFrame
from dmw.section_table import GroupTableFrame

class cBatchNavigator(cConfigFrame):
  """Create a tree view from the loaded Batch."""
  Interface = 'iView'
  def __init__(self, Batch, Config, Header, SortBy, IntervalTable):
    cConfigFrame.__init__(self, None, Config)

    self.Batch = Batch
    self.Config = Config
    self.Closes = []
    self.ReportId = None
    self.ReportType = 'measproc.cFileReport'
    self.CheckMeasExist = True
    self.Entries = {}
    self.index2frame = {}
    self._OrigMainMeas = Config.get('Measurement', 'main')

    self.TabWidget = QtGui.QTabWidget()
    MainPanelFrame = QtGui.QFrame()

    self.MainLayout.addWidget(MainPanelFrame)
    self.MainLayout.addWidget(self.TabWidget)

    self.Control = cBatchControl(MainPanelFrame, Config, Batch)

    self.StartBtn = QtGui.QPushButton('&Start')
    self.CloseAllBtn = QtGui.QPushButton('&Close All')

    self.StartBtn.clicked.connect(self.onStart)
    self.CloseAllBtn.clicked.connect(self.onCloseAll)

    self.ComboBox = QtGui.QPushButton()
    menu = QtGui.QMenu()
    self.ComboBox.setMenu(menu)
    self.ComboBox.menu()
    self.ComboBox.setMaximumWidth(20)

    self.Control.ComboBoxUpdateSignal.signal.connect(self.addItemToCombobox)

    control_panel_grid = QtGui.QGridLayout()
    control_panel_grid.addWidget(self.StartBtn, 0, 0)
    control_panel_grid.addWidget(self.Control.CNcheck, 1, 0)
    close_layout = QtGui.QHBoxLayout()
    close_layout.addWidget(self.CloseAllBtn)
    close_layout.addWidget(self.ComboBox)
    control_panel_grid.addLayout(close_layout, 0, 3, columnspan=2)
    close_layout.setSpacing(0)

    self.Backup = cCheckDirOption(MainPanelFrame, self.Config, 'General',
                                  'Backup')
    control_panel_grid.addWidget(self.Backup.Label, 3, 0)
    control_panel_grid.addWidget(self.Backup.Check, 3, 1)
    control_panel_grid.addWidget(self.Backup.Value, 3, 2)
    control_panel_grid.addWidget(self.Backup.OpenFileBtn, 3, 3)
    self.Closes.append(self.Backup.save)

    WildCard = Config.getQtExtendedStyleWildCard()

    Measurement = cFileOption(MainPanelFrame, self.Config, 'Measurement',
                              'main', filter=WildCard)
    control_panel_grid.addWidget(Measurement.Label, 5, 0)
    control_panel_grid.addWidget(Measurement.Value, 5, 2)
    control_panel_grid.addWidget(Measurement.OpenFileBtn, 5, 3)
    self.MeasFileOption = Measurement
    self.Report = cFileOption(MainPanelFrame, self.Config, 'General', 'Report',
                                filter='xml file *.xml')
    control_panel_grid.addWidget(self.Report.Label, 6, 0)
    control_panel_grid.addWidget(self.Report.Value, 6, 2)
    control_panel_grid.addWidget(self.Report.OpenFileBtn, 6, 3)
    self.Config.UpdateCallbacks.append(self.Report.update)

    MainPanelFrame.setLayout(control_panel_grid)

    self.BatchTabWidget = QtGui.QTabWidget()


    BatchPanel = QtGui.QFrame()
    self.BatchFrame = BatchFrame(Batch, Header, SortBy)
    RefreshBtn = QtGui.QPushButton('Refresh')
    RefreshBtn.clicked.connect(self.BatchFrame.batchTableModel.refresh)
    self.SelectReportBtn = QtGui.QPushButton('Select report')
    self.SelectReportBtn.clicked.connect(self.selectReport)
    ClearReportBtn = QtGui.QPushButton('Clear report')
    ClearReportBtn.clicked.connect(self.clearReport)

    BatchLayout = QtGui.QVBoxLayout()
    BatchButtonLayout = QtGui.QHBoxLayout()

    BatchLayout.addWidget(self.BatchFrame)
    BatchButtonLayout.addWidget(self.SelectReportBtn)
    BatchButtonLayout.addWidget(ClearReportBtn)
    BatchButtonLayout.addWidget(RefreshBtn)
    BatchLayout.addLayout(BatchButtonLayout)
    BatchPanel.setLayout(BatchLayout)

    ndx = self.BatchTabWidget.addTab(BatchPanel, 'Entries')
    self.index2frame[ndx] = self.BatchFrame

    self.IntervalFrame = IntervalFrame()
    self.IntervalFrame.set_table_model(IntervalTable)
    IntervalPanel = QtGui.QFrame()
    RefreshBtn = QtGui.QPushButton('Refresh')
    RefreshBtn.clicked.connect(self.IntervalFrame.batchTableModel.refresh)

    layout = QtGui.QVBoxLayout()
    refreshlayout = QtGui.QHBoxLayout()
    refreshlayout.addStretch(1)
    refreshlayout.addWidget(RefreshBtn)
    layout.addWidget(self.IntervalFrame)
    layout.addLayout(refreshlayout)

    IntervalPanel.setLayout(layout)

    ndx = self.BatchTabWidget.addTab(IntervalPanel, "Intervals")
    self.index2frame[ndx] = self.IntervalFrame
    self.TabWidget.addTab(self.BatchTabWidget, 'Batch')
    self.BatchTabWidget.currentChanged.connect(self.changeSubTab)

    Editor = cSyncAppEditor(None, Config, self.Control, None)
    self.TabWidget.addTab(Editor, 'Sag')
    self.setTabToolTip(Editor, cSyncAppEditor.__doc__)
    self.Closes.append(Editor.close)

    self.StatusTab = ModuleTableFrame(Config, Config.StatusSection,
                                 sub_from_option='fill')
    self.TabWidget.addTab(self.StatusTab, 'Status names' )

    self.GroupTab = GroupTableFrame(Config, 'GroupNames')
    self.TabWidget.addTab(self.GroupTab, 'Group names' )

    self.ParamTab = ModuleTableFrame(Config, 'iView')
    self.TabWidget.addTab(self.ParamTab, 'Modules')

    frame = QtGui.QFrame()
    frame.setLayout(self.MainLayout)
    self.setCentralWidget(frame)

    self.setWindowTitle('BN')
    pass

  def selectReport(self):
    try:
      self.ReportId, = self.BatchFrame.batchTableModel.getSelected(
                                                           type=self.ReportType)
    except ValueError:
      self.Config.log('Report selection is supported for one report exactly!\n')
    else:
      # set config and call subwidget update
      Title = self.Batch.select_npyxml_file(self.ReportId)
      self.Config.Sections[self.Interface].report(Title)
      self.Config.update()
      # disable subwidgets
      self.BatchFrame.batchTableModel.deselectEntryId(self.ReportId)
      self.MeasFileOption.disable()
    pass

  def changeSubTab(self, index):
    widget = self.index2frame[index]
    widget.start()
    return

  def clearReport(self):
    self.ReportId = None
    # enable subwidget
    self.MeasFileOption.enable()
    # set config and call subwidget update
    self.Config.report('')
    self.Config.update()
    pass

  def addItemToCombobox(self, itemName):
    menu = self.ComboBox.menu()
    itemName = 'Close ' + itemName
    for action in menu.actions():
      if itemName == action.text():
        return

    action = QtGui.QAction(itemName, menu)
    action.triggered.connect(lambda n=itemName: self.onClose(n))

    menu.addAction(action)
    return

  def start(self):
    """Start the widgets."""
    ndx = self.BatchTabWidget.currentIndex()
    widget = self.index2frame[ndx]
    widget.start()
    # restore last selected report
    Report = self.Config.get('General', 'Report')
    Measurement = self.Config.get('Measurement', 'main')
    if Report and Measurement:
      Measurement = os.path.basename(Measurement)
      Title = getTitle(Report, True)
      try:
        ReportId, = self.BatchFrame.batchTableModel.filterEntries(
                                                 type=self.ReportType,
                                                  measurement=Measurement,
                                                  title=Title)
      except ValueError:
       self.Config.log('Report initialization is ambigous, so it is missed.\n')
      else:
        self.ReportId = ReportId
        self.MeasFileOption.disable()
    self.show()
    pass

  def onStart(self):
    self._OrigMainMeas = self.Config.get('Measurement', 'main')
    ndx = self.BatchTabWidget.currentIndex()
    if self.index2frame[ndx] == self.IntervalFrame:
      self.onStartInterval()
    else:
      self.onStartEntries()
    return

  def onStartEntries(self):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    reports, report2s, statistics = self.BatchFrame.select(
                                                     ReportType=self.ReportType,
                                                     ReportId=self.ReportId
                                                           )
    Types = 'measproc.cFileReport', 'measproc.cFileStatistic', 'measproc.Report'
    Measurements = self.BatchFrame.getMeasurements(Types)
    for Measurement  in Measurements:
      if    self.CheckMeasExist\
        and self.Batch.is_measurement_local(Measurement)\
        and not os.path.exists(Measurement):
        self.Config.log( '%s is missing on the current machine' %Measurement )
        continue

      Entries = {}
      BatchResults = {
      'measproc.cFileReport' : self.BatchFrame.batchTableModel.storePart(
                                                 reports, Measurement, Entries),
      'measproc.Report' : self.BatchFrame.batchTableModel.storePart(report2s,
                                                  Measurement, Entries),
      'measproc.cFileStatistic' : self.BatchFrame.batchTableModel.storePart(
                                               statistics, Measurement, Entries)
                    }

      Measurement = self.Control.onStart(Measurement, BatchResults)

      self.Entries[Measurement] = Entries
    QtGui.QApplication.restoreOverrideCursor()
    return

  def onStartInterval(self):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    Entries = self.IntervalFrame.getEntries()
    if not Entries:
      self.Config.log('No interval was selected')
      QtGui.QApplication.restoreOverrideCursor()
      return
    start, end = self.IntervalFrame.getSelectedTimes()
    for Measurement, Entries in Entries.iteritems():
      if    self.CheckMeasExist\
        and self.Batch.is_measurement_local(Measurement)\
        and not os.path.exists(Measurement):
        self.Config.log('%s is missing on the current machine' %Measurement)
        continue

      BatchResults = {
      'measproc.cFileReport' : {},
      'measproc.Report' : self.IntervalFrame.storePart(),
      'measproc.cFileStatistic' : {}
                    }

      Measurement = self.Control.onStart(Measurement, BatchResults)
      Entry, = Entries
      result, =  BatchResults['measproc.Report' ].keys()
      self.Entries[Measurement] = {Entry : result}
    self.Control.seek(start)
    self.Control.setROI(start, end)
    QtGui.QApplication.restoreOverrideCursor()
    return

  def _closeEntryGroup(self, Measurement):
    if Measurement:
      del self.Entries[Measurement]
    return

  def _closeEntryGroups(self, Measurements):
    for Measurement in Measurements:
      self._closeEntryGroup(Measurement)
    return

  def onClose(self, itemName):
    if not itemName:
      return

    menu = self.ComboBox.menu()
    action = [action for action in menu.actions() if itemName == action.text()]
    if len(action) != 1:
      return
    action, = action

    BaseName = itemName.replace('Close ', '')
    self.Control.close(BaseName)
    menu.removeAction(action)
    action.deleteLater()
    self._closeEntryGroups([BaseName])
    self.refreshTableModel()
    return

  def onCloseAll(self):
    menu = self.ComboBox.menu()
    for action in menu.actions():
      menu.removeAction(action)
      action.deleteLater()
    Measurements = self.Control.onCloseAll()
    if Measurements:
      self._closeEntryGroups(Measurements)
    self.refreshTableModel()
    pass

  def refreshTableModel(self):
    ndx = self.BatchTabWidget.currentIndex()
    tableView = self.index2frame[ndx]
    tableView.batchTableModel.refresh()
    return

  def closeEvent(self, event):
    while self.Closes:
      close = self.Closes.pop()
      close()
    self.onCloseAll()
    self.Config.m(self._OrigMainMeas)
    ndx = self.BatchTabWidget.currentIndex()
    widget = self.index2frame[ndx]
    if widget == self.IntervalFrame:
      IntHeadSbys = self.IntervalFrame.getHeaderSortby()
      self.Config.Sections['iAnalyze'].setIntervalHeaderSortbys(IntHeadSbys)
    self.Config.save()
    self.IntervalFrame.close()
    self.BatchFrame.close()
    QtGui.QFrame.closeEvent(self, event)
    self.Batch.save()
    pass

  def quit(self):
    self.close()
    return

  def _update(self):
    self.ParamTab.update()
    self.StatusTab.update()
    self.GroupTab.update()

    self.Backup.update()
    self.MeasFileOption.update()
    self.Report.update()
    return

class CreateBatchNav:
  def __init__(self, Batch, Config, Header, SortBy, Query, IntervalTable):
    self.Batch = Batch
    self.Config = Config
    self.Header = Header
    self.SortBy = SortBy
    self.Query = Query
    self.IntervalTable = IntervalTable
    return

  def __call__(self):
    BatchNav = cBatchNavigator(self.Batch, self.Config, self.Header,
                               self.SortBy, self.IntervalTable)
    BatchNav.BatchFrame.query = self.Query
    return BatchNav

if __name__ == '__main__':
  from argparse import ArgumentParser
  import optparse

  from config.Config import Config
  from config.helper import procConfigFile, getConfigPath
  from config.modules import Modules

  def Report2NavconfigParser(parser):
    parser.add_option('-p', '--hold-navigator',
                      help='Hold the navigator, default is %default',
                      default=False,
                      action='store_true')
    return parser

  interface = 'iAnalyze'
  app = QtGui.QApplication([])

  modules = Modules()
  modules.read( getConfigPath('modules', '.csv') )

  args = Config.addArguments( ArgumentParser() ).parse_args()
  config = Config(procConfigFile('dataeval', args), modules)
  config.init(args)

  manager = config.createManager(interface)
  config.load(manager, interface)
  config.build(manager, interface)
  batch = manager.get_batch()

  batchNav = manager.get_batchnav()

  entids = batch.filter(type='measproc.Report')
  batchNav.BatchFrame.addEntries(entids)

  int_ids = [i + 1 for i in range(2000) if i % 3 == 0]

  batchNav.start()
  batchNav.IntervalFrame.addIntervals(int_ids)
  app_status = app.exec_()

  sys.exit(app_status)
