import re

from PySide import QtGui, QtCore

import SectionFrame

class StringEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(str)

class SimpleSignal(QtCore.QObject):
  signal = QtCore.Signal()

class cModuleSection(SectionFrame.cSectionFrame):
  def __init__(self, root, Config, Section, ListBox, SubFromOption=('',''), 
                                                           SubToOption=('','')):
    SectionFrame.cSectionFrame.__init__(self, root, Config, Section, ListBox,
                                     SubFromOption, SubToOption)
    self.itemSelectedSignal = StringEmittingSignal()
    self.Actives.Options.itemClicked.connect(self.emitSelectSignal)
    
    self.clearSelectedItemSignal = SimpleSignal()
    self.Passives.Options.itemClicked.connect(self._emitClearSelectedItemSignal)
    self.Passives.Options.itemSelectionChanged.connect(
                                              self.emitClearSelectedItemSignal)
    self.Actives.Options.itemSelectionChanged.connect(
                                               self.emitClearSelectedItemSignal)
    self.selected = ''
    return

  def emitSelectSignal(self, item):
    if len(self.Actives.Options.selectedItems()) == 1:
      Pattern, Replacement = self.Actives.SubToOption
      newSection = item.text()
      newSection = re.sub(Pattern, Replacement, newSection)
      self.itemSelectedSignal.signal.emit(newSection)
      self.selected = item.text()
    else:
      self.clearSelectedItemSignal.signal.emit()
    return
  
  def emitClearSelectedItemSignal(self):
    if self.selected:
      item = self.Actives.Options.findItems(self.selected, 
                                            QtCore.Qt.MatchExactly)
      if item: return
    self.clearSelectedItemSignal.signal.emit()
    self.selected = ''
    return
    
  def selectActiveModule(self, selected):
    ActOpts = self.Actives.Options
    item = ActOpts.findItems(selected, QtCore.Qt.MatchExactly)
    if item:
        ActOpts.setCurrentIndex(ActOpts.indexFromItem(item[0]))
        self.emitSelectSignal(item[0])
    elif self.selected:
      item = ActOpts.findItems(self.selected, QtCore.Qt.MatchExactly)
      if item:
        ActOpts.setCurrentIndex(ActOpts.indexFromItem(item[0]))
    return
    
  def _emitClearSelectedItemSignal(self, item):
    self.selected = ''
    self.clearSelectedItemSignal.signal.emit()
    return

class cModuleFrame(QtGui.QFrame):
  def __init__(self, root, Config, Section, ListBox, SubFromOption=('',''), 
                                                           SubToOption=('','')):
    QtGui.QFrame.__init__(self)
    self.ModuleSections = cModuleSection(self, Config, Section, ListBox, 
                                         SubFromOption, SubToOption)
    self.ParameterSection = SectionFrame.cSectionFrame(self, Config, '', 
                                                                        ListBox)
    self.ModuleSections.itemSelectedSignal.signal.connect(
                                              self.ParameterSection.editSection)
    self.ModuleSections.clearSelectedItemSignal.signal.connect(
                                                    self.ParameterSection.clear)
    self.ModuleSections.Actives.ItemsMovedSignal.signal.connect(
                                                    self.ParameterSection.clear)
    self.ModuleSections.Passives.ItemsMovedSignal.signal.connect(
                                         self.ModuleSections.selectActiveModule)
    self.ParameterSection.Actives.ItemsMovedSignal.signal.connect(
                                         self.ModuleSections.selectActiveModule)
    self.ParameterSection.Passives.ItemsMovedSignal.signal.connect(
                                         self.ModuleSections.selectActiveModule)
    
    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(self.ModuleSections)
    vbox.addWidget(self.ParameterSection)
    self.setLayout(vbox)   
    return

  def update(self):
    self.ModuleSections.update()
    self.ParameterSection.update()
    return
    
if __name__ == '__main__':
  from datavis import pyglet_workaround  # necessary as early as possible (#164)

  import sys
  from argparse import ArgumentParser  
  
  from config.helper import procConfigFile
  from config.View import cLoad
  
  app = QtGui.QApplication([])
  args = cLoad.addArguments( ArgumentParser() ).parse_args()
  name = procConfigFile('view', args)
  config = cLoad(name)
  config.init(args)

  moduleFrame = cModuleFrame(None, config, 'iView', False, (2, 3))
  moduleFrame.show()
  sys.exit(app.exec_())