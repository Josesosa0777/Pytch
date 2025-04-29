from PySide import QtGui, QtCore

class SingleControl:
  Interface = ''
  def __init__(self, config):
    self.config = config
    self.manager = self.config.createManager(self.Interface)
    self.basename = ''
    self.module_names = {}
    pass

  def setIntervalFrame(self, interval_frame):
    raise NotImplementedError()

  def onStart(self):
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    basename = self.getBaseName()
    if basename != self.basename:
      self.onClose()
      self.basename = basename
      self.manager.free_interface()
    self.config.load(self.manager, self.Interface)
    self.config.build(self.manager, self.Interface)
    QtGui.QApplication.restoreOverrideCursor()
    return

  def getBaseName(self):
    raise NotImplementedError()

  def getManager(self):
    return self.manager

  def onClose(self):
    self.config.Sections[self.Interface].save(self.manager)
    self.manager.close()
    self.module_names.clear()
    return

