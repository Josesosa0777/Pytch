from PySide import QtGui, QtCore

log_levels = {
               'DEBUG' : 10,
               'INFO' : 20,
               'WARNING' : 30,
               'ERROR' : 40,
               'CRITICAL' : 50,
              }


log_level_2_Gui_Color = {
                         log_levels['DEBUG'] : QtCore.Qt.cyan,
                         log_levels['INFO'] : QtCore.Qt.black,
                         log_levels['WARNING'] : QtCore.Qt.darkYellow,
                         log_levels['ERROR'] : QtCore.Qt.darkRed,
                         log_levels['CRITICAL'] : QtCore.Qt.magenta,
                        }
class LogFrame(QtGui.QPlainTextEdit):
  def __init__(self, config, *args, **kwargs):
    QtGui.QPlainTextEdit.__init__(self, *args, **kwargs)
    self.config = config
    self.config.Log.stderr_form.log_signal.signal.connect(self.add_msg)
    self.setReadOnly(True)
    return

  def create_formatter(self, level):
    format = QtGui.QTextCharFormat()
    color = log_level_2_Gui_Color.get(level, QtCore.Qt.black)
    format.setForeground(color)
    self.setCurrentCharFormat( format )
    return

  def add_msg(self, log):
    msg, level = log
    self.create_formatter(level)
    self.appendPlainText(msg)
    QtCore.QCoreApplication.processEvents()
    return

  def sizeHint(self):
    return QtCore.QSize(50, 50)