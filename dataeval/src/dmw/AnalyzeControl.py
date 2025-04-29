from PySide import QtGui, QtCore

from control import SingleControl

class cAnalyzeControl(SingleControl):
  Interface = 'iAnalyze'

  def getBatch(self):
    self.config.load(self.manager, self.Interface)
    return self.manager.get_batch()

  def fillIntervalFrame(self, interval_frame):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    self.manager.close()
    self.config.load(self.manager, self.Interface)
    self.config.Sections[self.Interface].uploadIntervalTable(self.manager)
    interval_table = self.manager.get_interval_table()
    interval_frame.set_table_model(interval_table)
    self.config.build(self.manager, self.Interface)
    QtGui.QApplication.restoreOverrideCursor()
    return

