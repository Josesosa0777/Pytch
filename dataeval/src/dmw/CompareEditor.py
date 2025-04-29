from PySide import QtGui, QtCore

from SignalSelector import cCompareSignalSelector
from textframe import TextFrame
from text.CompareText import CompareText
from SyncAppEditor import Editor

class cCompareEditor(Editor):
  TEMPLATE = 'compareTemplate.py'
  TextClass = CompareText
  def __init__(self, root, Config, Control):
    Editor.__init__(self, root, Config, Control)
    
    self.Selector = cCompareSignalSelector(self, Control)
    hbox_main = QtGui.QHBoxLayout()
    hbox_main.addWidget(self.Selector)
    
    self.TextFrame = TextFrame(self, self.Text)
    self.Text.update_text_frame = self.TextFrame.update_text
    hbox_main.addWidget(self.TextFrame)
    
    vbox_button = QtGui.QVBoxLayout()
    
    OpenBtn = QtGui.QPushButton('Open', parent=self)
    SaveBtn = QtGui.QPushButton('Save', parent=self)
    UpdateBtn = QtGui.QPushButton('Update', parent=self)
    AddBtn = QtGui.QPushButton('Add', parent=self)
    ResetBtn = QtGui.QPushButton('Reset', parent=self)
    
    OpenBtn.clicked.connect(self.open)
    SaveBtn.clicked.connect(self.save)
    UpdateBtn.clicked.connect(self.Text.update)
    AddBtn.clicked.connect(self.add)
    ResetBtn.clicked.connect(self.reset)
    
    vbox_button.addWidget(OpenBtn)
    vbox_button.addWidget(SaveBtn)
    vbox_button.addWidget(UpdateBtn)
    vbox_button.addWidget(AddBtn)
    vbox_button.addWidget(ResetBtn)
    
    hbox_main.addLayout(vbox_button)
    self.setLayout(hbox_main)
    
    pass
  
  def add(self):
    for DevName, SigName in self.Selector.getCurrentSelection(Unit=False):
      self.Text.add_signal(DevName, SigName)
    pass

