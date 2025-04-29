import sys

from PySide import QtGui, QtCore

from Synchronizer import cNavigator
from Group import iGroup


class ObjectEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(object)

class cGroupList(QtGui.QListWidget):
  def __init__(self, root=None):
    QtGui.QListWidget.__init__(self, parent=root)
    self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    self.Labels = set()
    self.ReturnPressedSignal = ObjectEmittingSignal()
    self.EscapePressedSignal = ObjectEmittingSignal()
    self.KeyPressedSignal = ObjectEmittingSignal()
    self.itemDoubleClicked.connect(self.onDblClick)
    pass
    
  def add(self, Name):
    self.Labels.add(Name)
    self.update()
    return      
    
  def update(self):
    if self.count() != -1:
      self.clear()
    for name in sorted(self.Labels):
      self.addItem(name)
    return
    
  def remove(self, Name):
    self.Labels.remove(Name)
    self.update()
    return      
    
  def keyPressEvent(self, event):
    if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
      self.ReturnPressedSignal.signal.emit(self)
    elif event.key() == QtCore.Qt.Key_Escape:
      self.EscapePressedSignal.signal.emit(self)
    else:
      self.KeyPressedSignal.signal.emit(event)
    return
    
  def onDblClick(self):
    self.ReturnPressedSignal.signal.emit(self)
    return
  
class cGroupNavigator(iGroup, cNavigator):
  SEP = '\t'
  def __init__(self):
    iGroup.__init__(self)
    cNavigator.__init__(self)
    
    self.setWindowTitle( 'GN')
    
    MainFrame = QtGui.QFrame()
    MainLayout =QtGui.QHBoxLayout()
    
    PassFrame = QtGui.QFrame()
    PassFrameLayout = QtGui.QVBoxLayout()
    
    PassLabel = QtGui.QLabel('Passives')
    PassFrameLayout.addWidget(PassLabel)
    
    self.Passives = cGroupList()
    PassFrameLayout.addWidget(self.Passives)
    PassFrame.setLayout(PassFrameLayout)
    
    ActFrame = QtGui.QFrame()
    ActFrameLayout = QtGui.QVBoxLayout()
    
    ActLabel = QtGui.QLabel('Actives')
    ActFrameLayout.addWidget(ActLabel)
    
    self.Actives = cGroupList()
    ActFrameLayout.addWidget(self.Actives)
    ActFrame.setLayout(ActFrameLayout)

    MainLayout.addWidget(PassFrame)
    MainLayout.addWidget(ActFrame)
    MainFrame.setLayout(MainLayout)
    self.setCentralWidget(MainFrame)
    
    self.Actives.ReturnPressedSignal.signal.connect(self.onReturn)
    self.Passives.ReturnPressedSignal.signal.connect(self.onReturn)
    
    self.Actives.EscapePressedSignal.signal.connect(self.onEscape)
    self.Passives.EscapePressedSignal.signal.connect(self.onEscape)
    
    self.Actives.KeyPressedSignal.signal.connect(self.keyPressEvent)
    self.Passives.KeyPressedSignal.signal.connect(self.keyPressEvent)
    pass
    
  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Space:
      if self.playing:
        self.onPause(self.time)
      else:
        self.onPlay(self.time)
    else:
      KeyCode = event.text()
      if KeyCode not in self.KeyCodes:
        KeyCode = KeyCode.upper()
      if KeyCode in self.KeyCodes:
        Group = self.KeyCodes[KeyCode]
        self.onSelectGroup(Group)
    pass
  
  def onReturn(self, widget):
    self.moveAllSelected(widget)
    pass
  
  def onEscape(self, widget):
    widget.clearSelection()
    return
  
  def makeLabel(self, Name, KeyCode):
    return Name + self.SEP + KeyCode
    
  def getNameFromLabel(self, Label):
    Name, Data = Label.split(self.SEP)
    return Name
  
  def move(self, Name, From, To):
    Label = self.makeLabel(Name, self.getKeyCode(Name))
    From.remove(Label)
    To.add(Label)
    pass
  
  def moveAllSelected(self, Widget):
    Names = []
    for item in  Widget.selectedItems():
      Label = item.text()
      Name = self.getNameFromLabel(Label)
      Names.append(Name)
    Widget.clearSelection()
    for Name in Names:
      self.onSelectGroup(Name)
    pass
  
  def _setVisible(self, GroupName, Visible):
    if Visible:
      self.move(GroupName, self.Passives, self.Actives)
    else:
      self.move(GroupName, self.Actives, self.Passives)
    pass
  
  def setGroup(self, GroupName, Visible, KeyCode):
    Label = self.makeLabel(GroupName, KeyCode)
    if Visible:
      self.Passives.add(Label)
    else:
      self.Actives.add(Label)
    pass
  
if __name__ == '__main__':
  import sys
  
  from GroupParam import cGroupParam
  import aebs.par.grouptypes as gtps
  app = QtGui.QApplication([])
  
  Groups = {
             'LRR3_FUS': cGroupParam(gtps, gtps.LRR3_FUS, '1', False, False),
             'CVR3_ATS': cGroupParam(gtps, gtps.CVR3_ATS, 'A', False, False),
             'AC100': cGroupParam(gtps, gtps.AC100, '2', True, False),
           }    
  
  GN = cGroupNavigator()
  GN.addGroups(Groups)
  GN.start()
  GN.show()
  sys.exit(app.exec_())
  pass
