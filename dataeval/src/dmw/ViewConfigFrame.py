#!/usr/bin/python
import os
from PySide import QtGui, QtCore

from NxtSyncAppEditor import cSyncAppEditor
from OptionFrames import cFileOption, cCheckDirOption
from ModuleFrame import cModuleFrame
from ParameterFrame import cParameterFrame
from PySide.QtCore import Qt
from PySide.QtGui import QIcon
from ViewControl import cViewControl
from ConfigFrame import cConfigFrame
from MeasurementFrame import cMeasurementFrame
from dmw.ExecuteScriptRuntime import cExecuteScriptRuntime
from section_table import ModuleTableFrame
from section_table import GroupTableFrame

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

class SimpleSignal(QtCore.QObject):
  signal = QtCore.Signal()

class cViewConfigFrame(cConfigFrame):
  Interface = 'iView'
  def __init__(self, root, Config, need_cn=True):
    cConfigFrame.__init__(self, root, Config)
    Config.UpdateCallbacks.append(self._update)
    self.controlPressed = False
    self.CloseSignal = SimpleSignal()

    Button  = (10, 5)

    self.TabWidget = QtGui.QTabWidget()

    self.MainLayout.addWidget(self.ControlFrame, 0, Qt.AlignTop)
    self.MainLayout.addWidget(self.TabWidget, 0, Qt.AlignTop)

    self.Control = cViewControl(None, Config)
    self.Closes.append(self.Control.onCloseAll)
    StartBtn = QtGui.QPushButton('Start')
    self.CloseAllBtn = QtGui.QPushButton('Close All')
    StartBtn.clicked.connect(self.Control.onStart)
    self.CloseAllBtn.clicked.connect(self.onCloseAll)
    self.Control.ComboBoxUpdateSignal.signal.connect(self.addItemToCombobox)
    self.ComboBox = QtGui.QPushButton()
    menu = QtGui.QMenu()
    self.ComboBox.setMenu(menu)
    self.ComboBox.menu()

    self.ComboBox.setMaximumWidth(20)

    control_panel_grid = QtGui.QGridLayout()
    control_panel_grid.setSpacing(0)
    control_panel_grid.setContentsMargins(1, 1, 1, 1)
    control_panel_grid.addWidget(StartBtn, 0, 0)
    if need_cn:
      control_panel_grid.addWidget(self.Control.CNcheck, 1, 0)

    self.Measurement = cMeasurementFrame(Config, self.Interface, control_panel_grid)
    self.Backup = cCheckDirOption(self.ControlFrame, Config, 'General', 'Backup')
    control_panel_grid.addWidget(self.Backup.Label, 3, 0)
    control_panel_grid.addWidget(self.Backup.Check, 3, 1)
    control_panel_grid.addWidget(self.Backup.Value, 3, 2)
    control_panel_grid.addWidget(self.Backup.OpenFileBtn, 3, 3)
    close_layout = QtGui.QHBoxLayout()
    close_layout.addWidget(self.CloseAllBtn)
    close_layout.addWidget(self.ComboBox)
    control_panel_grid.addLayout(close_layout, 0, 3, columnspan=2)
    close_layout.setSpacing(0)
    self.Closes.append(self.Backup.save)

    self.ControlFrame.setLayout(control_panel_grid)

    control_panel_grid.setSpacing(0)
    control_panel_grid.setSizeConstraint(QtGui.QLayout.SetMaximumSize)

    ModuleTab = ModuleTableFrame(Config, self.Interface)
    self.TabWidget.addTab(ModuleTab, QIcon(os.path.join(IMAGE_DIRECTORY, 'main_module_execution_24.png')),'Main Execution')
    self.TabWidget.setTabToolTip(0, "Add/select modules for execution, Modules can also be added from Standard Templates or Script based Modules")
    self.SectionFrames.append((ModuleTab, 'Main Execution'))

    self.Editor = cSyncAppEditor(self.TabWidget, Config, self.Control, Button)
    ScrollArea = QtGui.QScrollArea()
    ScrollArea.setWidgetResizable(True)
    ScrollArea.setWidget(self.Editor)
    self.TabWidget.addTab(ScrollArea, QIcon(os.path.join(IMAGE_DIRECTORY, 'script_based_24.png')), 'Module Creation')
    self.setTabToolTip(self.Editor, cSyncAppEditor.__doc__)
    self.Closes.append(self.Editor.close)

    self.ExecuteScriptRuntime = cExecuteScriptRuntime(self.TabWidget, Config, self.Control)
    ScrollArea = QtGui.QScrollArea()
    ScrollArea.setWidgetResizable(True)
    ScrollArea.setWidget(self.ExecuteScriptRuntime)
    self.TabWidget.addTab(ScrollArea, QIcon(os.path.join(IMAGE_DIRECTORY, 'standard_templates_24.png')),'Standard Templates')
    self.TabWidget.setTabToolTip(2,
                                 "Create own standard templates/layout or reuse already created one (No need to write scripts)")


    StatusTab = ModuleTableFrame(Config, Config.StatusSection,
                                 sub_from_option='fill')
    self.TabWidget.addTab(StatusTab, QIcon(os.path.join(IMAGE_DIRECTORY, 'status_names_24.png')), 'Status names' )
    self.setTabToolTip(StatusTab, Config.get('__doc__', Config.StatusSection))
    self.SectionFrames.append((StatusTab, 'Status names'))

    GroupTab = GroupTableFrame(Config, 'GroupNames')
    self.TabWidget.addTab(GroupTab, QIcon(os.path.join(IMAGE_DIRECTORY, 'group_names_24.png')), 'Group names' )
    self.setTabToolTip(GroupTab, Config.get('__doc__', 'GroupNames'))
    self.SectionFrames.append((GroupTab, 'GroupNames'))

    for Tab in (ModuleTab, StatusTab, GroupTab):
      Tab.activate_modules()

    pass

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
    return

  def onCloseAll(self):
    menu = self.ComboBox.menu()
    for action in menu.actions():
      menu.removeAction(action)
    self.Control.onCloseAll()
    return

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

  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.controlPressed = True
    if event.key() == QtCore.Qt.Key_Tab and self.controlPressed:
      self.changeTab()
    return

  def keyReleaseEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.controlPressed = False
    return

  def changeTab(self):
    CurrentIndex = self.TabWidget.currentIndex()
    MaxIndex = self.TabWidget.count() - 1
    if CurrentIndex < MaxIndex:
      self.TabWidget.setCurrentIndex(CurrentIndex + 1)
    else:
      self.TabWidget.setCurrentIndex(0)
    return

  def _update(self):
    cConfigFrame._update(self)
    self.Measurement.update()
    self.Backup.update()
    return

if __name__ == '__main__':
  from datavis import pyglet_workaround  # necessary as early as possible (#164)

  import sys
  from argparse import ArgumentParser

  from config.helper import procConfigFile, getConfigPath
  from config.View import cLoad
  from config.modules import Modules
  from interface.manager import Manager

  app = QtGui.QApplication([])
  modules_name = getConfigPath('modules', '.csv')
  modules = Modules()
  modules.read(modules_name)
  args = cLoad.addArguments( ArgumentParser() ).parse_args()
  name = procConfigFile('view', args)
  config = cLoad(name, modules)
  config.init(args)

  config_frame = cViewConfigFrame(None, config)
  config_frame.show()
  app_status = app.exec_()

  #config.wait(args) TODO: wait app in config
  modules.protected_write(modules_name)
  sys.exit(app_status)
