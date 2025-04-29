# -*- coding: utf-8 -*-
"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright:
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial
  property. We reserve all rights of disposal such as copying and passing on to
  third parties.
"""
__docformat__ = "restructuredtext en"

from operator import itemgetter
import collections

from PySide import QtGui, QtCore

class TreeNode():
  def __init__(self, parent, row, data):
    self.parent = parent
    self.row = row
    self.children = []
    self.data = data

  def addChild(self, child):
    self.children.append(child)

  def __getitem__(self, item):
    return self.data[item]

class cSignalItemModel(QtCore.QAbstractItemModel):
  def __init__(self):
    QtCore.QAbstractItemModel.__init__(self)
    self.signals = []
    self.selecteds = []
    self.sortbys = []
    self.headers = ('DeviceName', 'SignalName', 'Unit')
    self.ascending_order = True
    self.prev_col = None
    return

  def index(self,row, column, parent):
    if not parent.isValid():
      return self.createIndex(row,column,self.signals[row])
    parentNode = parent.internalPointer()
    return self.createIndex(row,column,parentNode.children[row])


  def parent(self, child):
    if not child.isValid():
      return QtCore.QModelIndex()
    node = child.internalPointer()
    try:
      if node.parent is None:
        return QtCore.QModelIndex()
      else:
        return self.createIndex(node.parent.row, 0, node.parent)
    except AttributeError:
      return QtCore.QModelIndex()

  def rowCount(self, parent):
    if not parent.isValid():
      return len(self.signals)
    node = parent.internalPointer()
    return len(node.children)

  def columnCount(self,parent):
    return len(self.headers)

  def headerData(self, section, orientation, role):
    if orientation == QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
      return self.headers[section]

  def flags(self, index):
    flags = QtCore.Qt.ItemIsEnabled
    node = index.internalPointer()
    if len(node.children) == 0:
      flags = flags | QtCore.Qt.ItemIsSelectable
    return flags

  def data(self,index, role=QtCore.Qt.DisplayRole):
    if role == QtCore.Qt.DisplayRole:
      if not index.isValid():
        return None
      node = index.internalPointer()
      signal = node.data
      if index.column() == 0:
        column = 'DeviceName'
      elif index.column() == 1:
        column = 'SignalName'
      else:
        column = 'Unit'
      return signal[column]

  def generateDimensions(self, parent, dimensions, index, text):
    childcount = dimensions[index]
    if childcount == 0:
      if index != 0:
        parent.data['SignalName'] = parent.data['SignalName'][0:-1] + ']'
      return
    for i in range(childcount):
      data = {'DeviceName': '', 'SignalName': '', 'Dimensions': (0, 0), 'Unit': ''}
      owntext = text + str(i) + ','
      data['SignalName'] = owntext[0:-1]+']'
      data['DeviceName'] = parent.data['DeviceName']
      newnode = TreeNode(parent, i, data)
      self.generateDimensions(newnode, dimensions, index+1, owntext)
      parent.addChild(newnode)
    return

  def setData(self, value, role=QtCore.Qt.EditRole):
    if len(value) != 4:  # dirty check for validity of 'value' dict
      return False
    self.layoutAboutToBeChanged.emit()
    start_index = self.createIndex(len(self.signals), 0)
    end_index = self.createIndex(len(self.signals), len(self.headers))
    rootnode = TreeNode(None, len(self.signals), value)
    self.generateDimensions(rootnode, value['Dimensions'], 0, value['SignalName']+'[:,')
    self.signals.append(rootnode)
    self.dataChanged.emit(start_index, end_index)
    self.layoutChanged.emit()
    return True

  def clear(self):
    self.beginResetModel()  # reset is required to prevent python crash
    self.signals = []
    self.endResetModel()
    return

  def sort(self, column, order=QtCore.Qt.AscendingOrder):
    if self.prev_col != column:
      self.ascending_order = True
    self._onNormalSort(column)
    self._onSort()
    self.prev_col = column
    return

  def _onNormalSort(self, index):
    if self.sortbys == [self.headers[index]]:
      self.ascending_order = not self.ascending_order
    self.sortbys = [self.headers[index]]
    return

  def _onSort(self):
    self.layoutAboutToBeChanged.emit()
    sorter = itemgetter(*self.sortbys)
    self.signals = sorted(self.signals, key=sorter,
                          reverse=not self.ascending_order)
    self.layoutChanged.emit()
    return


class cSignalSelector(QtGui.QFrame):
  """Select signal via `setSearcher` and `searchTag`."""
  Channel = 'main'
  SEP = ',\t'
  def __init__(self, root, Control, SingleSelection=False):
    """
    :Parameters:
      root : `tk.Tk`
        Root tk widget
    """
    QtGui.QFrame.__init__(self, parent=root)

    self.Control = Control
    # Listbox of signals
    self.SignalTableModel = cSignalItemModel()

    self.SignalTable = QtGui.QTreeView()
    self.SignalTable.setModel(self.SignalTableModel)
    if SingleSelection:
      self.SignalTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    else:
      self.SignalTable.setSelectionMode(
                                      QtGui.QAbstractItemView.ExtendedSelection)
    self.SignalTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(self.SignalTable)
    #Search Dev
    self.PosDeviceEntry = QtGui.QLineEdit()
    self.PosDeviceEntry.returnPressed.connect(self.filt)
    grid = QtGui.QGridLayout()
    grid.addWidget(self.PosDeviceEntry, 0, 0)
    self.NegDeviceEntry = QtGui.QLineEdit()
    self.NegDeviceEntry.returnPressed.connect(self.filt)
    grid.addWidget(self.NegDeviceEntry, 1, 0)
    # Search Signal
    self.PosSignalEntry = QtGui.QLineEdit()
    self.PosSignalEntry.returnPressed.connect(self.filt)
    grid.addWidget(self.PosSignalEntry, 0, 1)
    self.NegSignalEntry = QtGui.QLineEdit()
    self.NegSignalEntry.returnPressed.connect(self.filt)
    grid.addWidget(self.NegSignalEntry, 1, 1)

    self.MatchCase = QtGui.QCheckBox()
    grid.addWidget(self.MatchCase, 0, 2)
    self.insertHelp()
    vbox.addLayout(grid)
    self.setLayout(vbox)
    pass

  def insertHelp(self):
    self.PosDeviceEntry.setPlaceholderText('Positive Device Filter')
    self.PosDeviceEntry.setToolTip(
                'Filter tags can be added to reduce the number of the signals' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that DEVICE names WILL contain' +
                '\nPress ENTER to run the filtering over the signals.'
                                    )
    self.NegDeviceEntry.setPlaceholderText('Negative Device Filter')
    self.NegDeviceEntry.setToolTip(
                'Filter tags can be added to reduce the number of the signals' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that DEVICE names WONT contain' +
                '\nPress ENTER to run the filtering over the signals.'
                                    )
    self.PosSignalEntry.setPlaceholderText('Positive Signal Filter')
    self.PosSignalEntry.setToolTip(
                'Filter tags can be added to reduce the number of the signals' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that SIGNAL names WILL contain' +
                '\nPress ENTER to run the filtering over the signals.'
                                    )
    self.NegSignalEntry.setPlaceholderText('Negative Signal Filter')
    self.NegSignalEntry.setToolTip(
                'Filter tags can be added to reduce the number of the signals' +
                '\nThe tags have to be separated by SPACE.' +
                '\nThe entry collects the tags that SIGNAL names WONT contain' +
                '\nPress ENTER to run the filtering over the signals.'
                                    )
    self.MatchCase.setToolTip('Match case')
    pass

  def getSignalNames(self,
                     PosDevTags, NegDevTags,
                     PosSigTags, NegSigTags,
                     MatchCase):
    Source = self.Control.getSource(self.Channel)
    return Source.querySignalNames(PosDevTags, NegDevTags,
                                   PosSigTags, NegSigTags,
                                   MatchCase, True)

  def getPhysicalUnit(self, ShortDeviceName, SignalName):
    Source = self.Control.getSource(self.Channel)
    DeviceName=Source.getUniqueName(SignalName,ShortDeviceName,FavorMatch=True)
    return Source.getPhysicalUnit(DeviceName, SignalName)

  def getSignalShape(self, ShortDeviceName, SignalName):
    Source = self.Control.getSource(self.Channel)
    DeviceName=Source.getUniqueName(SignalName,ShortDeviceName,FavorMatch=True)
    return  Source.getSignalShape(DeviceName,SignalName)

  def filt(self):
    """Update the list of the selectable signal names."""
    QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
    PosSignalTag  = self.PosSignalEntry.text()
    PosSignalTags = PosSignalTag.split()
    NegSignalTag  = self.NegSignalEntry.text()
    NegSignalTags = NegSignalTag.split()

    PosDeviceTag  = self.PosDeviceEntry.text()
    PosDeviceTags = PosDeviceTag.split()
    NegDeviceTag  = self.NegDeviceEntry.text()
    NegDeviceTags = NegDeviceTag.split()

    self.SignalTable.setSortingEnabled(False)
    self.SignalTableModel.clear()

    MatchCase = self.MatchCase.isChecked()
    for Signal in self.getSignalNames(PosDeviceTags, NegDeviceTags,
                                      PosSignalTags, NegSignalTags,
                                      MatchCase):
      Sig = {}
      Sig['DeviceName'], Sig['SignalName'] = Signal
      Sig['Unit'] = self.getPhysicalUnit(Sig['DeviceName'],
                                            Sig['SignalName'])
      sizes = self.getSignalShape(Sig['DeviceName'], Sig['SignalName'])
      Sig['Dimensions'] = tuple(sizes[1:]+[0])
      self.SignalTableModel.setData(Sig)
      # it is recommended that sorting is enabled after inserting the items into the tree
      self.SignalTable.setSortingEnabled(True)
    QtGui.QApplication.restoreOverrideCursor()
    pass

  def getRows(self, selectedCells):
    rows = collections.OrderedDict()
    rowData = {'DeviceName' : '', 'SignalName' : '', 'Unit' : ''}
    for cell in selectedCells:
      row = cell.internalPointer()
      column = cell.column()
      if row not in rows:
        rows[row] = rowData.copy()
      if column == 0:
        rows[row]['DeviceName'] = cell.data()
      elif column == 1:
        rows[row]['SignalName'] = cell.data()
      elif column == 2:
        rows[row]['Unit'] = cell.data()
    return rows

  def getCurrentSelection(self, Unit=True):
    Signals = []
    selectionModel = self.SignalTable.selectionModel()
    selectedCells = selectionModel.selectedIndexes()
    rows = self.getRows(selectedCells)
    for row in rows.itervalues():
      if Unit:
        Signals.append((row['DeviceName'], row['SignalName'], row['Unit']))
      else:
        Signals.append((row['DeviceName'], row['SignalName']))
    return Signals

  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.SignalTableModel.controlPressed = True
    QtGui.QFrame.keyPressEvent(self, event)
    return

  def keyReleaseEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.SignalTableModel.controlPressed = False
    QtGui.QFrame.keyReleaseEvent(self, event)
    return

class cCompareSignalSelector(cSignalSelector):
  Channel = 'compare'

