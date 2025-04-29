from datavis import pyglet_workaround  # necessary as early as possible (#164)

from PySide import QtGui, QtCore

from SectionFrame import cSectionFrame
from OptionFrames import cFileOption, cDirOption, cCheckDirOption
from ModuleFrame import cModuleFrame
from MeasurementsFrame import cMeasurementsFrame
from CompareEditor import cCompareEditor
from CompareControl import cCompareControl
from ConfigFrame import cConfigFrame
from ParameterFrame import cParameterFrame
from section_table import ModuleTableFrame

class cCompareConfigFrame(cConfigFrame):
  Interface = 'iCompare'
  def __init__(self, root, Config, Args):
    cConfigFrame.__init__(self, root, Config)

    ListBox = (25, 7)

    MainLayout = QtGui.QVBoxLayout()

    TabWidget = QtGui.QTabWidget()
    ControlFrame = QtGui.QFrame()

    self.MainLayout.addWidget(ControlFrame)
    self.MainLayout.addWidget(TabWidget)

    control_grid = QtGui.QGridLayout()

    Control = cCompareControl(Config)
    self.Closes.append(Control.onClose)

    StartBtn = QtGui.QPushButton('Start')
    StartBtn.clicked.connect(Control.onStart)
    control_grid.addWidget(StartBtn, 0, 0)


    self.BatchFile = cFileOption(ControlFrame, Config, 'General', 'BatchFile')
    control_grid.addWidget(self.BatchFile.Label, 0, 1)
    control_grid.addWidget(self.BatchFile.Value, 0, 2)
    control_grid.addWidget(self.BatchFile.OpenFileBtn, 0, 3)

    self.Compare = cFileOption(ControlFrame, Config, 'Measurement', 'compare')
    control_grid.addWidget(self.Compare.Label, 1, 0)
    control_grid.addWidget(self.Compare.Value, 1, 2)
    control_grid.addWidget(self.Compare.OpenFileBtn, 1, 3)

    self.RepDir = cDirOption(ControlFrame, Config, 'General', 'RepDir')
    control_grid.addWidget(self.RepDir.Label, 2, 0)
    control_grid.addWidget(self.RepDir.Value, 2, 2)
    control_grid.addWidget(self.RepDir.OpenFileBtn, 2, 3)

    self.Backup = cCheckDirOption(ControlFrame, Config, 'General', 'Backup')
    control_grid.addWidget(self.Backup.Label, 3, 0)
    control_grid.addWidget(self.Backup.Check, 3, 1)
    control_grid.addWidget(self.Backup.Value, 3, 2)
    control_grid.addWidget(self.Backup.OpenFileBtn, 3, 3)
    self.Closes.append(self.Backup.save)

    ControlFrame.setLayout(control_grid)
    control_grid.setSizeConstraint(QtGui.QLayout.SetMaximumSize)

    Meas = cMeasurementsFrame(TabWidget, Config, Args.r)
    TabWidget.addTab(Meas, 'Measurements')

    Comp = cCompareEditor(TabWidget, Config, Control)
    TabWidget.addTab(Comp, 'Editor')
    self.Closes.append(Comp.close)

    self.PF = ModuleTableFrame(Config, self.Interface)
    TabWidget.addTab(self.PF, 'Module parameters')

    self.setLayout(self.MainLayout)
    return

  def _update(self):
    self.PF.update()
    self.RepDir.update()
    self.Compare.update()
    self.BatchFile.update()
    self.Backup.update()
    return

if __name__ == '__main__':
  import sys
  from argparse import ArgumentParser

  from config.Config import procConfigFile, getConfigPath
  from config.Compare import cLoad
  from config.modules import Modules

  app = QtGui.QApplication([])
  modules_name = getConfigPath('modules', '.csv')
  modules = Modules()
  modules.read(modules_name)
  args = cLoad.addArguments( ArgumentParser() ).parse_args()
  name = procConfigFile('compare', args)
  config = cLoad(name, modules)
  config.init(args)

  config_frame = cCompareConfigFrame(config, args)
  config_frame.show()
  app_status = app.exec_()

  modules.protected_write(modules_name)
  sys.exit(app_status  )
