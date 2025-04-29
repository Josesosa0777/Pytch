#!/usr/bin/python

import os
import shutil

from PySide import QtGui, QtCore
from PySide.QtGui import QIcon

from config.helper import correctCfgFileExt

IMAGE_DIRECTORY = os.path.join(os.path.dirname(__file__), "images")

class cConfigFrame(QtGui.QMainWindow):
  Interface = ''
  FILE_SEP = ' - '
  def __init__(self, root, Config):
    QtGui.QMainWindow.__init__(self)

    self.setWindowIcon(QIcon(os.path.join(IMAGE_DIRECTORY, 'evaluation_24.png')))

    self.Closes = []
    self.Config = Config
    self.TabWidget = QtGui.QTabWidget()
    self.moveStartPos()
    self.Control = None
    self.SectionFrames = []

    CfgPath = os.path.basename(self.Config.CfgPath)

    self.main_frame = QtGui.QFrame()

    self.MainLayout = QtGui.QVBoxLayout()
    self.MainLayout.setSpacing(0)
    self.MainLayout.setContentsMargins(0,0,0,0)
    self.MainLayout.setContentsMargins(1, 1, 1, 1)

    self.main_frame.setLayout(self.MainLayout)

    self.ControlFrame = QtGui.QFrame()
    pass

  def closeEvent(self, event):
    while self.Closes:
      close = self.Closes.pop()
      close()
    if self.Interface:
      Manager = self.getManager()
      self.Config.close(Manager, self.Interface)
    QtGui.QMainWindow.closeEvent(self, event)
    return

  def exportCfg(self):
    Dir = os.path.dirname(self.Config.CfgPath)
    Path, _ = QtGui.QFileDialog.getSaveFileName(dir=Dir,
                                                filter='config file, *.cfg')
    if Path:
      self.saveConfig()
      shutil.copyfile( self.Config.CfgPath, correctCfgFileExt(Path) )
    return

  def toggle_save_conf(self, save):
    self.Config.NoSave = not save
    self.Config.ForcedSave = save
    return

  def save(self):
    NoSave = self.Config.NoSave
    ForcedSave = self.Config.ForcedSave

    self.Config.NoSave = False
    self.Config.ForcedSave = True

    self.saveConfig()

    self.Config.NoSave = NoSave
    self.Config.ForcedSave = ForcedSave
    return

  def saveConfig(self):
    Manager = self.getManager()
    self.saveLayout()
    self.Config.saveAll(Manager)
    return

  def saveLayout(self):
    return

  def restoreLayout(self):
    return

  def moveStartPos(self):
    central_point = QtGui.QDesktopWidget().availableGeometry().center()
    self.resize(1000, self.height())
    x = central_point.x() - self.width() / 2
    y = QtGui.QDesktopWidget().availableGeometry().top()
    self.move(x, y)
    return

  def setTabToolTip(self, widget, tooltip):
    index = self.TabWidget.indexOf(widget)
    self.TabWidget.setTabToolTip(index, tooltip)
    return

  def getManager(self):
    return self.Control.getManager() if self.Control is not None else None

  def loadCfg(self):
    Dir = os.path.dirname(self.Config.CfgPath)
    Path, _ = QtGui.QFileDialog.getOpenFileName(dir=Dir,
                                                filter='config file, *.cfg')
    if not Path: return

    Manager = self.getManager()
    self.Config.loadCfg(Path, Manager)
    CfgPath = os.path.basename(Path)
    WindowTitle = self.windowTitle()
    Title, _ = WindowTitle.split(self.FILE_SEP, 1)
    NewTitle = Title + self.FILE_SEP + CfgPath
    self.setWindowTitle(CfgPath)
    self._update()
    self.restoreLayout()
    self.save()
    qm = QtGui.QMessageBox
    reply = qm.question(self, '', "Are you sure want load new configuration? Please restart to change the effect", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    if reply == qm.Yes:
      self.close()
    else:
      qm.information(self, '', "Some values may still be unfilled on GUI. Please restart")
    return

  def _update(self):
    for SectionFrame, _ in self.SectionFrames:
      SectionFrame.update()
    return

  def start(self):
    self.setCentralWidget(self.main_frame)
    self.show()
    return
