from PySide import QtCore, QtGui

from ConfigFrame import cConfigFrame
from SectionFrame import cSectionFrame
from OptionFrames import cFileOption, cDirOption
from ModuleFrame import cModuleFrame
from ParameterFrame import cParameterFrame
from AnalyzeControl import cAnalyzeControl
from ReportFilterEditor import cReportFilterEditor
from section_table import ModuleTableFrame

class cAnalyzeConfigFrame(cConfigFrame):
  Interface = 'iAnalyze'
  def __init__(self, root, Config):
    cConfigFrame.__init__(self, root, Config)

    ListBox  = (25, 7)

    self.TabWidget = QtGui.QTabWidget()
    Control = cAnalyzeControl(Config)
    self.Closes.append(Control.onClose)

    self.MainLayout.addWidget(self.ControlFrame)
    self.MainLayout.addWidget(self.TabWidget)

    StartBtn = QtGui.QPushButton('Start')
    CloseBtn = QtGui.QPushButton('Close')

    StartBtn.clicked.connect(Control.onStart)
    CloseBtn.clicked.connect(Control.onClose)

    main_grid = QtGui.QGridLayout()
    main_grid.addWidget(StartBtn, 0, 0)
    main_grid.addWidget(CloseBtn, 0, 2)

    self.BatchFile = cFileOption(self.ControlFrame, Config, 'General',
                                 'BatchFile')
    main_grid.addWidget(self.BatchFile.Label, 1, 0)
    main_grid.addWidget(self.BatchFile.Value, 1, 1)
    main_grid.addWidget(self.BatchFile.OpenFileBtn, 1, 2)

    self.RepDir = cDirOption(self.ControlFrame, Config, 'General', 'RepDir')
    main_grid.addWidget(self.RepDir.Label, 2, 0)
    main_grid.addWidget(self.RepDir.Value, 2, 1)
    main_grid.addWidget(self.RepDir.OpenFileBtn, 2, 2)

    main_grid.setSizeConstraint(QtGui.QLayout.SetMaximumSize)

    self.ControlFrame.setLayout(main_grid)

    self.Editor = cReportFilterEditor(self.TabWidget, Config, Control)
    self.TabWidget.addTab(self.Editor, 'Refi')
    self.Closes.append(self.Editor.close)
    self.setTabToolTip(self.Editor, cReportFilterEditor.__doc__)

    PF = ModuleTableFrame(Config, self.Interface)
    self.TabWidget.addTab(PF, 'Module parameters')

    self.SectionFrames.append((PF, 'Module parameters'))

    self.TabWidget.currentChanged.connect(self.tabChanged)

    self.Frame = QtGui.QFrame()
    self.Frame.setLayout(self.MainLayout)
    self.setCentralWidget(self.Frame)
    self.Editor.init()
    pass

  def tabChanged(self, TabIndex):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    if TabIndex == self.TabWidget.indexOf(self.Editor):
      self.Editor.init()
    QtGui.QApplication.restoreOverrideCursor()
    return

  def _update(self):
    cConfigFrame._update(self)
    self.RepDir.update()
    self.BatchFile.update()
    return

if __name__ == '__main__':
  from datavis import pyglet_workaround  # necessary as early as possible (#164)

  import sys
  from argparse import ArgumentParser

  from config.Config import Config
  from config.helper import procConfigFile, getConfigPath
  from config.modules import Modules
  from interface.manager import Manager

  interface = 'iAnalyze'
  app = QtGui.QApplication([])
  modules_name = getConfigPath('modules', '.csv')
  modules = Modules()
  modules.read(modules_name)
  args = cLoad.addArguments( ArgumentParser() ).parse_args()
  name = procConfigFile('analyze', args)
  config = Config(name, modules)
  manager = config.createManager(interface)
  config.init(args)

  config_frame = cAnalyzeConfigFrame(config)
  config_frame.show()
  app_status = app.exec_()

  #config.wait(args) TODO: wait app in config
  config.exit(manager)
  modules.protected_write(modules_name)
  sys.exit(app_status)
