import os
from collections import OrderedDict

from PySide import QtGui, QtCore

from OptionFrames import cNameOption
from measproc.Batch import findMeasurements

class cMeasurementsFrame(QtGui.QFrame):
  def __init__(self, root, Config, Recursively):
    QtGui.QFrame.__init__(self, parent=root)
    self.Config = Config

    grid = QtGui.QGridLayout()

    ScanBtn = QtGui.QPushButton('Scan', parent=self)
    ScanBtn.clicked.connect(self.scan)

    grid.addWidget(ScanBtn, 0, 0)

    self.Recursively = QtGui.QCheckBox('Recursively')
    self.Recursively.setChecked(Recursively)


    self.WildCardOption = cNameOption(self, Config, 'General', 'WildCard')

    grid.addWidget(self.WildCardOption, 0, 2)
    grid.addWidget(self.WildCardOption.Label, 0, 2)
    grid.addWidget(self.Recursively , 0, 1)
    grid.addWidget(self.WildCardOption.Value, 0, 3)

    AddBtn = QtGui.QPushButton('Add')
    RemoveBtn = QtGui.QPushButton('Remove')
    ClearBtn = QtGui.QPushButton('Remove All')

    AddBtn.clicked.connect(self.add)
    RemoveBtn.clicked.connect(self.remove)
    ClearBtn.clicked.connect(self.clear)

    grid.addWidget(AddBtn, 2, 0)
    grid.addWidget(RemoveBtn, 2, 1)
    grid.addWidget(ClearBtn, 2, 2)

    main_vbox = QtGui.QVBoxLayout()
    main_vbox.addLayout(grid)

    self.Tree = QtGui.QTreeWidget()
    self.Tree.setHeaderHidden(True)
    self.Tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    self.Tree.setIconSize(QtCore.QSize(100, 100))
    main_vbox.addWidget(self.Tree)
    self.Tree.itemExpanded.connect(self._exp)
    self.Tree.itemCollapsed.connect(self._coll)
    self.ExpandedItem = set()
    self.ScanDirs = []

    self.setLayout(main_vbox)
    self.update()
    return

  def update(self):
    if self.Tree.columnCount():
      self.Tree.clear()
    Measurements = groupMeasurements(self.Config.Sections['iSearch'].Measurements)
    self.Tree.setColumnCount(1)
    for DirName, BaseNames in Measurements.iteritems():
      DirItem = QtGui.QTreeWidgetItem(self.Tree)
      DirItem.setIcon(0, QtGui.QIcon.fromTheme('folder'))
      DirItem.setText(0, DirName)
      for BaseName in BaseNames:
        FileItem = QtGui.QTreeWidgetItem(DirItem)
        FileItem.setText(0, BaseName)
        FileItem.setIcon(0,  QtGui.QIcon('x-office-document'))

    self.WildCardOption.update()

    if not self.ExpandedItem: return

    its = QtGui.QTreeWidgetItemIterator(self.Tree,
                                  QtGui.QTreeWidgetItemIterator.HasChildren)
    for it in its:
        item = it.value()
        text = item.text(self.Tree.indexFromItem(item).column())
        if text in self.ExpandedItem:
            self.Tree.expandItem(item)
    return

  def setScanDirs(self, Dirs):
    self.ScanDirs = Dirs
    return

  def scan(self):
    Root = getMeasurementsRoot(self.Config.Sections['iSearch'].Measurements)
    Dirs = []
    Dialog = QtGui.QFileDialog()
    Dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
    Dialog.filesSelected.connect(self.setScanDirs)
    Dialog.setDirectory(Root)
    Lists = Dialog.findChildren(QtGui.QListView)
    for List in Lists:
      List.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    Tree = Dialog.findChild(QtGui.QTreeView)
    if Tree:
      Tree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    Directory = Dialog.exec_()
    for Directory in self.ScanDirs:
      WildCard = self.Config.get('General', 'WildCard')
      Recursively = self.Recursively.isChecked()
      Measurements = findMeasurements(Directory, WildCard, Recursively)
      self.Config.Sections['iSearch'].Measurements.update(Measurements)
      self.update()
    return

  def clear(self):
    self.Config.Sections['iSearch'].Measurements = set()
    self.update()
    return

  def add(self):
    WildCard = self.Config.get('General', 'WildCard')
    FileTypes = self.Config.getQtExtendedStyleWildCard()
    Root = getMeasurementsRoot(self.Config.Sections['iSearch'].Measurements)
    FileName = QtGui.QFileDialog.getOpenFileName(filter=FileTypes, dir=Root)[0]
    if FileName:
      FileName = os.path.abspath(FileName)
      self.Config.Sections['iSearch'].Measurements.add(FileName)
      self.update()
    return

  def remove(self):
    for MeasurementItem in self.Tree.selectedItems():
      column = self.Tree.indexFromItem(MeasurementItem).column()
      Measurement = MeasurementItem.text(column)
      Measurements = groupMeasurements(self.Config.Sections['iSearch'].Measurements)
      if Measurement in Measurements:
        for BaseName in Measurements[Measurement]:
          Name = os.path.join(Measurement, BaseName)
          self.Config.Sections['iSearch'].Measurements.remove(Name)
          if Measurement in self.ExpandedItem:
            self.ExpandedItem.remove(Measurement)
      else:
        DirectoryItem = MeasurementItem.parent()
        Directory = DirectoryItem.text(column)
        Meas = os.path.join(Directory, Measurement)
        self.Config.Sections['iSearch'].Measurements.remove(Meas)
      directory = MeasurementItem.parent()

    self.update()
    return

  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Delete:
      self.remove()
    QtGui.QFrame.keyPressEvent(self, event)
    return

  def _exp(self, item):
    dir = item.text(self.Tree.indexFromItem(item).column())
    self.ExpandedItem.add(dir)
    return

  def _coll(self, item):
    dir = item.text(self.Tree.indexFromItem(item).column())
    self.ExpandedItem.remove(dir)
    return

def groupMeasurements(Measurements):
  Groups = OrderedDict()
  for Measurement in sorted(Measurements):
    DirName, BaseName = os.path.split(Measurement)
    Group = Groups.setdefault(DirName, [])
    Group.append(BaseName)
  return Groups

def getMeasurementsRoot(Measurements):
  Measurements = dict([(Measurement.count(os.path.sep), Measurement)
                       for Measurement in Measurements])
  if Measurements:
    Measurement = Measurements[min(Measurements)]
    Root = os.path.basename(Measurement)
  else:
    Root = ''
  return Root

