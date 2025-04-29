import glob
import logging
import os

from NxtListNavigatorFrame import cListNavigatorFrame
from NxtPlotNavigatorFrame import cPlotNavigatorFrame
from NxtSignalSelector import cSignalSelector
from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QGroupBox, QIcon, QSizePolicy, QSpacerItem
# from SignalSelector import cSignalSelector
from config.Config import cScan
from config.helper import getConfigPath, getScanDirs
from config.modules import Modules
from text.ViewText import ViewText
from textframe import TextFrame

logger = logging.getLogger("NxtSyncAppEditor")

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

class LargeFrame(QtGui.QFrame):
  def sizeHint(self):
    height = self.height()
    return QtCore.QSize(500, height)

class Editor(QtGui.QMainWindow):
  TEMPLATE_DIR = 'text\\templates'
  TEMPLATE = 'foo.py'
  def __init__(self, root, Config, Control):
    QtGui.QMainWindow.__init__(self)
    self.SaveName = '*.py'
    ParentDir = os.path.dirname(os.path.dirname(__file__))
    DirName = os.path.join(ParentDir, self.TEMPLATE_DIR)
    self.FileName = os.path.join(DirName, self.TEMPLATE)
    self.active_modules_table = root.widget(0) # Get main module execution tab widget
    vboxlayout_editor = QtGui.QVBoxLayout()
    vboxlayout_editor.setSpacing(0)
    vboxlayout_editor.setContentsMargins(1, 1, 1, 1)

    # <editor-fold desc="Treeview operations">
    gbox_editor_operations = QGroupBox('')
    hboxlayout_editor_operations = QtGui.QHBoxLayout()
    hboxlayout_editor_operations.setSpacing(0)
    hboxlayout_editor_operations.setContentsMargins(1, 1, 1, 1)

    self.Text = self.TextClass(self.FileName, Config, Control)
    self.TextFrame = TextFrame(None, self.Text)
    self.OpenBtn = QtGui.QPushButton('Open')
    self.OpenBtn.setToolTip('Open Script')
    self.OpenBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'open_folder_24.png')))
    hboxlayout_editor_operations.addWidget(self.OpenBtn, 0, Qt.AlignVCenter)

    self.SaveBtn = QtGui.QPushButton('Save')
    self.SaveBtn.setToolTip('Save Script')
    self.SaveBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'save_24.png')))
    hboxlayout_editor_operations.addWidget(self.SaveBtn, 0, Qt.AlignVCenter)

    self.UpdateBtn = QtGui.QPushButton('Update')
    self.UpdateBtn.setToolTip('Update Script')
    self.UpdateBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'update_file_24.png')))
    hboxlayout_editor_operations.addWidget(self.UpdateBtn, 0, Qt.AlignVCenter)

    self.ResetBtn = QtGui.QPushButton('Reset')
    self.ResetBtn.setToolTip('Reset Script')
    self.ResetBtn.setIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'reset_24.png')))
    hboxlayout_editor_operations.addWidget(self.ResetBtn, 0, Qt.AlignVCenter)

    horizontal_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding)
    hboxlayout_editor_operations.addItem(horizontal_spacer)

    gbox_editor_operations.setLayout(hboxlayout_editor_operations)
    vboxlayout_editor.addWidget(gbox_editor_operations)
    vboxlayout_editor.addWidget(self.TextFrame)

    Frame = LargeFrame()
    Frame.setLayout(vboxlayout_editor)
    Frame.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                        QtGui.QSizePolicy.Expanding)
    self.dw = QtGui.QDockWidget("Script Editor")
    self.dw.setWidget(Frame)
    dw_features = QtGui.QDockWidget.DockWidgetMovable | \
                  QtGui.QDockWidget.DockWidgetFloatable
    self.dw.setFeatures(dw_features)
    self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dw)
    return

  def close(self):
    self.Text.close()
    return

  def save(self):
    InitDir = self.Text.get_init_dir()
    Name =  QtGui.QFileDialog.getSaveFileName(filter='python *.py',
                                          caption=self.SaveName,
                                          dir=InitDir)[0]
    if Name:
      self.SaveName = Name
      self.Text.save(Name)
      self.TextFrame.remove_star_from_window_title()
      self.active_modules_table.act_module_frame.refresh_elemnents()
      logger.info("Module is saved at: {}".format(Name))
    return

  def open(self):
    InitDir = self.Text.get_init_dir()
    Name = QtGui.QFileDialog.getOpenFileName(filter='python *.py',
                                        dir=InitDir)[0]
    if Name:
      self.Text.open(Name)
      self.TextFrame.remove_star_from_window_title()
    return

  def reset(self):
    self.Text.open(self.FileName)
    return

class cSyncAppEditor(Editor):
  """Script editor for `datavis.cSynchronizer` application"""
  TEMPLATE = 'viewTemplate.py'
  TextClass = ViewText
  def __init__(self, root, Config, Control, Button):
    """
    :Parameters:
      root : `tk.Tk`
        Root tk widget
      Config : foo
    """

    Editor.__init__(self, root, Config, Control)
    self.dw.setObjectName('SAGDock')
    self.setObjectName('SAG')

    self.Selector = cSignalSelector(self, Control)
    vboxlayout_script_editor = QtGui.QVBoxLayout()
    vboxlayout_script_editor.setSpacing(0)
    vboxlayout_script_editor.setContentsMargins(1, 1, 1, 1)

    frame = QtGui.QFrame()

    self.Text.update_text_frame = self.TextFrame.update_text
    self.Text.update_nav_metadata = self.update_navigator_metadata

    self.PlotNav = cPlotNavigatorFrame(None, '', self.Text, self.Selector)
    self.ListNav = cListNavigatorFrame(None, '', self.Text, self.Selector)

    self.OpenBtn.clicked.connect(self.open)
    self.SaveBtn.clicked.connect(self.save)
    self.UpdateBtn.clicked.connect(self.TextFrame.update_parser)
    self.ResetBtn.clicked.connect(self.reset)

    self.PlotNav.ValueNrIncreasedSignal.signal.connect(
                                            self.ListNav.incrementValueCounter)
    self.ListNav.ValueNrIncreasedSignal.signal.connect(
                                            self.PlotNav.incrementValueCounter)

    self.PlotNav.ClientNrIncreasedSignal.signal.connect(
                                            self.ListNav.incrementClientCounter)
    self.ListNav.ClientNrIncreasedSignal.signal.connect(
                                            self.PlotNav.incrementClientCounter)

    self.ResetBtn.clicked.connect(self.PlotNav.resetCounters)
    self.ResetBtn.clicked.connect(self.ListNav.resetCounters)

    # gbox_navigator_operations = QGroupBox('')
    # button_hbox = QtGui.QHBoxLayout()
    # button_hbox.setSpacing(0)
    # button_hbox.setContentsMargins(1, 1, 1, 1)
    # button_hbox.addWidget(self.PlotNav)
    # button_hbox.addWidget(self.ListNav)
		#
    # horizontal_spacer = QSpacerItem(0, 0, QSizePolicy.Expanding)
    # button_hbox.addItem(horizontal_spacer)

    # gbox_navigator_operations.setLayout(button_hbox)
    # vboxlayout_script_editor.addWidget(gbox_navigator_operations)
    vboxlayout_script_editor.addWidget(self.Selector)

    frame.setLayout(vboxlayout_script_editor)
    self.setCentralWidget(frame)
    pass
  
  def update_navigator_metadata(self):
    self.PlotNav.update_from_metadata()
    self.ListNav.update_from_metadata()
    return

