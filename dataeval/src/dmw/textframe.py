from PySide import QtGui, QtCore
from CodeEditor import QCodeEditor
from syntax_highlighter import PythonSyntaxHighlighter

class TextFrame(QtGui.QFrame):
  TAB_SIZE_IN_SPACE = 2
  def __init__(self, root, parser):
    QtGui.QFrame.__init__(self)

    self.parser = parser
    self.text = QCodeEditor()
    self.text.setStyleSheet(
            """QPlainTextEdit {font-size: 10pt; font-family: Consolas;}""")
    highlighter = PythonSyntaxHighlighter(self.text.document())
    self.text.installEventFilter(self)
    self.text.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
    self.update_text()
    vbox = QtGui.QVBoxLayout()
    vbox.setSpacing(0)
    vbox.setContentsMargins(1, 1, 1, 1)
    vbox.addWidget(self.text)
    self.setLayout(vbox)
    self.text.textChanged.connect(self.textChanged)
    pass

  def eventFilter(self, obj, event):
    if obj == self.text and event.type() == QtCore.QEvent.KeyPress \
       and event.key() == QtCore.Qt.Key_Tab:
        self.text.insertPlainText(' ' * self.TAB_SIZE_IN_SPACE)
        return True
    return QtGui.QFrame.eventFilter(self, obj, event)

  def update_parser(self):
    text = self.text.toPlainText()
    self.parser.update_by_text(text)
    return

  def update_text(self):
    text = self.parser.get_text()
    self.text.clear()
    self.text.setPlainText(text)
    return

  def textChanged(self):
    self.add_star_to_window_title()
    return

  def get_main_window(self):
    parent = self
    while parent.parent():
      parent = parent.parent()
    return parent

  def get_main_window_and_title(self):
    main_window = self.get_main_window()
    window_title = main_window.windowTitle()
    return main_window, window_title

  def remove_star_from_window_title(self):
    main_window, window_title = self.get_main_window_and_title()

    if '*' not in window_title: return

    new_title = window_title.replace('*', '')
    main_window.setWindowTitle(new_title)
    return

  def add_star_to_window_title(self):
    main_window, window_title = self.get_main_window_and_title()
    if '*' in window_title: return

    new_title = window_title + '*'
    main_window.setWindowTitle(new_title)
    return
