import os
from PySide import QtGui, QtCore


# from SignalSelector import cSignalSelector

from NxtSignalSelector import cSignalSelector
from textframe import TextFrame
from text.ViewText import ViewText
from NxtPlotNavigatorFrame import cPlotNavigatorFrame
from NxtListNavigatorFrame import cListNavigatorFrame

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
    self.Text = self.TextClass(self.FileName, Config, Control)
    self.TextFrame = TextFrame(None, self.Text)
    self.OpenBtn = QtGui.QPushButton('Open')
    self.SaveBtn = QtGui.QPushButton('Save')
    self.UpdateBtn = QtGui.QPushButton('Update')
    self.ResetBtn = QtGui.QPushButton('Reset')
    ButtonLayout = QtGui.QVBoxLayout()
    ButtonLayout.addStretch(1)
    ButtonLayout.addWidget(self.OpenBtn)
    ButtonLayout.addWidget(self.SaveBtn)
    ButtonLayout.addWidget(self.UpdateBtn)
    ButtonLayout.addWidget(self.ResetBtn)
    ButtonLayout.addStretch(1)
    Hbox = QtGui.QHBoxLayout()
    Hbox.addWidget(self.TextFrame)
    Hbox.addLayout(ButtonLayout)
    Frame = LargeFrame()
    Frame.setLayout(Hbox)
    Frame.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
                        QtGui.QSizePolicy.Expanding)
    self.dw = QtGui.QDockWidget()
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

    Selector = cSignalSelector(None, Control)
    hbox = QtGui.QHBoxLayout()
    frame = QtGui.QFrame()

    self.Text.update_text_frame = self.TextFrame.update_text
    self.Text.update_nav_metadata = self.update_navigator_metadata

    self.PlotNav = cPlotNavigatorFrame(None, 'PlotNavigator', self.Text, Selector)
    self.ListNav = cListNavigatorFrame(None, 'ListNavigator', self.Text, Selector)

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


    ButtonFrame = QtGui.QFrame()
    button_vbox = QtGui.QVBoxLayout()
    button_vbox.addStretch()
    button_vbox.addWidget(self.PlotNav)
    button_vbox.addWidget(self.ListNav)
    button_vbox.addStretch()
    ButtonFrame.setLayout(button_vbox)

    splitter = QtGui.QSplitter()

    splitter.addWidget(Selector)
    splitter.addWidget(ButtonFrame)
    splitter.setObjectName('SAGSplitter')
    splitter.setSizes([1500, 250])
    hbox.addWidget(splitter)

    frame.setLayout(hbox)
    self.setCentralWidget(frame)
    pass
  
  def update_navigator_metadata(self):
    self.PlotNav.update_from_metadata()
    self.ListNav.update_from_metadata()
    return

