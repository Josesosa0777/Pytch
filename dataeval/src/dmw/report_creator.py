from PySide import QtGui, QtCore

from SyncAppEditor import Editor
from text.SearchText import SearchText
# from SignalSelector import cSignalSelector

from NxtSignalSelector import cSignalSelector
from report_adder_frame import ReportAdderFrame

class SearchEditor(Editor):
  TEMPLATE = 'searchTemplate.py'
  TextClass = SearchText
  def __init__(self, config, control):
    Editor.__init__(self, None, config, control)
    self.setObjectName('ReCre')
    self.Text.update_text_frame = self.TextFrame.update_text
    hbox = QtGui.QHBoxLayout()
    frame = QtGui.QFrame()

    selector = cSignalSelector(self, control, SingleSelection=True)

    adder_frame = ReportAdderFrame(self.Text, selector)
    vbox = QtGui.QVBoxLayout()

    for btn, func in zip([self.OpenBtn, self.SaveBtn, self.UpdateBtn,
                          self.ResetBtn],
                        [self.open, self.save, self.TextFrame.update_parser,
                         self.reset]):
      btn.clicked.connect(func)

    self.dw.setObjectName('ReCreDock')

    vbox.addWidget(selector)
    selector_frame = QtGui.QFrame()
    selector_frame.setLayout(vbox)
    self.value = QtGui.QLineEdit('')
    self.func_selector = QtGui.QPushButton()
    splitter = QtGui.QSplitter()
    splitter.setObjectName('ReCreSplitter')

    splitter.addWidget(selector_frame)
    splitter.addWidget(adder_frame)
    splitter.setSizes([1500, 500])
    hbox.addWidget(splitter)

    frame.setLayout(hbox)
    self.setCentralWidget(frame)
    return

