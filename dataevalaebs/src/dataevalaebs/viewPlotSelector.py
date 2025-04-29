from PySide import QtGui, QtCore

import datavis
import interface

DefParam = interface.NullParam

class cView(interface.iView, datavis.cNavigator):
  def view(self, Param=DefParam):
    datavis.cNavigator.__init__(self, title="Select Plots")
    interface.Sync.addStaticClient(self)
    pass

  def createClientButtons(self):
    self.clientsByName = {}
    self.buttonsByName = {}
    frame = QtGui.QFrame()
    layout = QtGui.QGridLayout()
    for client in interface.Sync.clients.keys():
      if isinstance(client, datavis.cPlotNavigator):
        name = client.title
        if name is not None:
          i = 1
          uniquename = name
          while self.clientsByName.has_key(uniquename):
            uniquename = "%s(%i)"%(name, i)
            i += 1
          if i > 1:
            name = uniquename
          self.clientsByName[name] = client
    if len(self.clientsByName) > 0:
      j = 0
      k = 0
      for name in sorted(self.clientsByName.keys()):
        button = QtGui.QPushButton(name)
        button.clicked.connect(lambda x = name:self.onClientButtonClick(x))
        layout.addWidget(button, j, k)
        self.buttonsByName[name] = button
        j += 1
        if j > 20:
          j = 0
          k += 1
    frame.setLayout(layout)
    self.setCentralWidget(frame)
    pass

  def onClientButtonClick(self, name):
    client = self.clientsByName[name]
    if client.isHidden():
      button = self.buttonsByName[name]
      button.setDisabled(True)
      return
    client.setWindowState(QtCore.Qt.WindowActive)
    client.activateWindow()
    client.setFocus()
    return

  def start(self):
    self.createClientButtons()
    pass

  def getWindowId(self):
    return 'PlotSelector'
