from datavis import pyglet_workaround  # necessary as early as possible (#164)

from PySide import QtGui, QtCore

from SectionFrame import cSectionFrame
from OptionFrames import cFileOption, cDirOption, cCheckDirOption
from ModuleFrame import cModuleFrame
from MeasurementsFrame import cMeasurementsFrame
from ConfigFrame import cConfigFrame
from ParameterFrame import cParameterFrame
from section_table import ModuleTableFrame
from report_creator import SearchEditor
from search_control import SearchControl

INTERFACE = 'iSearch'

class cSearchConfigFrame(cConfigFrame):
  Interface = INTERFACE
  def __init__(self, root, Config, Args, NewTabWidget=True):
    cConfigFrame.__init__(self, root, Config)

    ListBox = (25, 7)

    MainLayout = QtGui.QVBoxLayout()

    self.Control = SearchControl(Config)
    self.Closes.append(self.Control.onClose)

    control_grid = QtGui.QGridLayout()
    self.MainLayout.addWidget(self.ControlFrame)

    StartBtn = QtGui.QPushButton('Start')
    StartBtn.clicked.connect(self.Control.onStart)
    control_grid.addWidget(StartBtn, 0, 0)

    self.BatchFile = cFileOption(self.ControlFrame, Config, 'General',
                                  'BatchFile')
    control_grid.addWidget(self.BatchFile.Label, 1, 1)
    control_grid.addWidget(self.BatchFile.Value, 1, 3)
    control_grid.addWidget(self.BatchFile.OpenFileBtn, 1, 4)

    self.RepDir = cDirOption(self.ControlFrame, Config, 'General', 'RepDir')
    control_grid.addWidget(self.RepDir.Label, 2, 1)
    control_grid.addWidget(self.RepDir.Value, 2, 3)
    control_grid.addWidget(self.RepDir.OpenFileBtn, 2, 4)

    self.Backup = cCheckDirOption(self.ControlFrame, Config, 'General',
                                  'Backup')
    control_grid.addWidget(self.Backup.Label, 3, 1)
    control_grid.addWidget(self.Backup.Check, 3, 2)
    control_grid.addWidget(self.Backup.Value, 3, 3)
    control_grid.addWidget(self.Backup.OpenFileBtn, 3, 4)
    self.Closes.append(self.Backup.save)

    control_grid.setSpacing(5)
    control_grid.setSizeConstraint(QtGui.QLayout.SetMaximumSize)

    self.ControlFrame.setLayout(control_grid)

    self.Meas = cMeasurementsFrame(None, Config, Args.r)

    self.PF = ModuleTableFrame(Config, self.Interface)

    if NewTabWidget:
      TabWidget = QtGui.QTabWidget()
      self.MainLayout.addWidget(TabWidget)
      TabWidget.addTab(self.Meas, 'Measurements')
      TabWidget.addTab(self.PF, 'Module parameters')

    self.SectionFrames.append((self.Meas, 'Measurements'))
    self.SectionFrames.append((self.PF, 'Module parameters'))

    self.Editor = SearchEditor( Config, self.Control)
    self.Closes.append(self.Editor.close)
    self.PF.activate_modules()
    return

  def _update(self):
    cConfigFrame._update(self)
    self.RepDir.update()
    self.Meas.update()
    self.BatchFile.update()
    self.Backup.update()
    return

if __name__ == '__main__':
  import sys
  from argparse import ArgumentParser

  from config.helper import procConfigFile, getConfigPath
  from config.Search import cLoad
  from config.modules import Modules

  app = QtGui.QApplication([])
  modules_name = getConfigPath('modules', '.csv')
  modules = Modules()
  modules.read(modules_name)
  args = cLoad.addArguments( ArgumentParser() ).parse_args()
  name = procConfigFile('search', args)
  config = cLoad(name, modules)
  config.init(args)

  config_frame = cSearchConfigFrame(None, config, args)
  config_frame.show()
  app_status = app.exec_()

  #config.wait(args) TODO: wait app in config
  modules.protected_write(modules_name)
  sys.exit(app_status )
