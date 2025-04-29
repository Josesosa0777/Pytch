import re

from PySide import QtGui, QtCore

class StringEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(str)

class cSectionTab(QtGui.QFrame):
  VALUE = ''
  def __init__(self, root, Config, Section, ListBox, SubFromOption, SubToOption):
    QtGui.QFrame.__init__(self)
    
    self.Config  = Config
    self.Section = Section
    self.SubFromOption = SubFromOption
    self.SubToOption   = SubToOption
    Config.UpdateCallbacks.append(self.update)
    self.Options = QtGui.QListWidget(parent=self)
    self.Options.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    self.Options.resize(*ListBox)
    self.ItemsMovedSignal = StringEmittingSignal()
    self.selected = ''
    self.Options.itemDoubleClicked.connect(self.onReturn)
    self.update()
    pass
  
  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Escape:
      self.onEscape(event)
    if  (event.key() == QtCore.Qt.Key_Return 
      or event.key() == QtCore.Qt.Key_Enter):
      self.onReturn(event)
    return
  
  def onClick(self, item):
    self.Options.setCurrentItem(item)
    pass
    
  def onReturn(self, event):
    Pattern, Replacement = self.SubToOption
    for Index in self.Options.selectedItems():
      Text = Index.text()
      Option = re.sub(Pattern, Replacement, Text)
      self.Config.set(self.Section, Option, self.VALUE)
    self.Config.update()
    self.ItemsMovedSignal.signal.emit(Text)
    pass
  
  def onEscape(self, event):
    self.Options.clearSelection()
    pass
  
  def update(self):
    Pattern, Replacement = self.SubFromOption
    Options = [re.sub(Pattern, Replacement, Option)
               for Option in self.list()
               if re.search(Pattern, Option)]
    Options = list(Options)
    Options.sort()
    if self.Options.count():
      self.Options.clear()
    self.Options.insertItems(0, Options)
    pass
  
  def list(self):
    pass
  
  def forget(self):
    self.Config.UpdateCallbacks.remove(self.update)
    pass
    
  def editSection(self, newSection):
    self.Section = newSection
    self.update()
    return
  
class cActives(cSectionTab):
  VALUE = 'no'
  def list(self):
    if self.Section:
      return self.Config.getActiveOptions(self.Section)
    else: 
      return ''
  
class cPassives(cSectionTab):
  VALUE = 'yes'
  def list(self):
    if self.Section:
      return self.Config.getPassiveOptions(self.Section)
    else:
      return ''

class cSectionFrame(QtGui.QFrame):
  def __init__(self, root, Config, Section, ListBox, SubFromOption=('',''), 
                                                          SubToOption=('','')):
    QtGui.QFrame.__init__(self)
    
    self.Config = Config
    self.Section = Section
    listbox_grid = QtGui.QGridLayout()
    ActivesLabel = QtGui.QLabel('Actives', parent=self)
    PassivesLabel = QtGui.QLabel('Passives', parent=self)
    listbox_grid.addWidget(ActivesLabel, 0, 1)
    listbox_grid.addWidget(PassivesLabel, 0, 0)
    
    self.Passives = cPassives(self, Config, Section, ListBox, SubFromOption, 
                                                                    SubToOption)
    listbox_grid.addWidget(self.Passives.Options, 1, 0)

    self.Actives = cActives(self, Config, Section, ListBox, SubFromOption,
                                                                    SubToOption)
    listbox_grid.addWidget(self.Actives.Options, 1, 1)
    
    self.setLayout(listbox_grid)
    pass
    
  def keyPressEvent(self, event):
    if self.Passives.Options.selectedItems():
      self.Passives.keyPressEvent(event)
    elif self.Actives.Options.selectedItems():
      self.Actives.keyPressEvent(event)
    return

  def forget(self):
    self.Actives.forget()
    self.Passives.forget()
    
  def editSection(self, newSection):
    self.Actives.editSection(newSection)
    self.Passives.editSection(newSection)
    return
    
  def clear(self):
    self.editSection('')
    if self.Actives.Options.count():
      self.Actives.Options.clear()
    if self.Passives.Options.count():
      self.Passives.Options.clear()
    return

  def update(self):
    self.Actives.update()
    self.Passives.update()
    return
