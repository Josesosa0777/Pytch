# -*- coding: utf-8 -*-
import os
from operator import itemgetter

from PySide import QtGui, QtCore

from measproc.batchsqlite import filters as batch_filters

class CommentEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(str, int)

class ObjectEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(object)

class TableModel(QtCore.QAbstractTableModel):
  def __init__(self, root, header, sortby):
    QtCore.QAbstractTableModel.__init__(self, parent=root)
    self.header = []
    self.root = root
    self.headerlabels = {}
    self.headerprefix = u'ˇ'
    self.sortbys = [sortby]
    self.entries = []
    self.selecteds = []
    self.colors = {}
    self.comments = {}
    self.commentid = None
    self.control_pressed = False
    self.ascending_order = True
    self.commentEmittingSignal = CommentEmittingSignal()
    self.selectedRowsEmittingSignal = ObjectEmittingSignal()
    self.row_color = QtCore.Qt.gray

    background = 'lightblue'
    column = -1
    row = 1
    self.query = ''
    for column, name in enumerate(header):
      if name not in self.header:
        self.header.append(name)
        self.headerlabels[name] = name
    if 'query' not in self.header:
      self.header.append('query')
    self.headerlabels['query'] = 'query'
    if 'comment' not in self.header:
      self.header.append('comment')
    self.headerlabels['comment'] = 'comment'
    return

  def columnCount(self, parent):
    return len(self.headerlabels)

  def rowCount(self, parent):
    return len(self.entries)

  def headerData(self, index, orientation, role=QtCore.Qt.DisplayRole):
    if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole):
      return self.headerlabels[self.header[index]]
    else:
      return None

  def toggleColor(self, prevData, data):
    if prevData != data:
      if self.row_color == QtCore.Qt.lightGray:
        self.row_color = QtCore.Qt.gray
      elif self.row_color == QtCore.Qt.gray :
        self.row_color = QtCore.Qt.lightGray
    return self.row_color

  def setHeaderData(self, index, orientation, value, role=QtCore.Qt.EditRole):
    if orientation == QtCore.Qt.Horizontal:
      self.headerlabels[self.header[index]] = unicode(value)
      return True
    else:
      return False

  def data(self, index, role=QtCore.Qt.DisplayRole):
    if index.isValid():
      entry = self.entries[index.row()]
      if role == QtCore.Qt.DisplayRole:
        headerName = self.header[index.column()]
        return entry[headerName]
      if role == QtCore.Qt.BackgroundColorRole:
        #set the color of comment column
        if index.column() == len(self.header) -1:
          background = QtGui.QBrush(QtCore.Qt.darkGreen)
        else:
          background = QtGui.QBrush(entry['color'])
        return background
    else:
      return None

  def setData(self, index, value, role=QtCore.Qt.EditRole):
    if index.isValid():
      if index.column() == len(self.header) - 1:
        entry = self.entries[index.row()]
        entry['comment'] = value
        self.dataChanged.emit(index, index)
      return True
    else:
      return False

  def start(self):
    self._draw()
    return

  def _draw(self):
    self.layoutAboutToBeChanged.emit()
    if self.ascending_order:
      headerPrefix = '^'
    else:
      headerPrefix = u'ˇ'
    for  header, label in self.headerlabels.iteritems():
      i = self.header.index(header)
      if header in self.sortbys:
        prefix = headerPrefix * (self.sortbys.index(header)+1)
        header = unicode(prefix) + unicode(header)
      # avoid to change comment header
      if i < len(self.header):
        self.setHeaderData(i, QtCore.Qt.Horizontal, header)
    sorter = itemgetter(*self.sortbys)
    sortby = self.sortbys[0]
    self.entries = sorted(self.entries, key=sorter,
                          reverse=not self.ascending_order)
    if self.entries:
      prevData = self.entries[0][sortby]
    for entry in self.entries:
      data = entry[sortby]
      entry['color'] = self.toggleColor(prevData, data)
      prevData = data

    self.layoutChanged.emit()
    selecteds = [row for row, entry in enumerate(self.entries)
                 if entry['entryid'] in self.selecteds]
    self.selectedRowsEmittingSignal.signal.emit(selecteds)
    return

  def _onSort(self, index):
    # avoid order by commnent
    if index == len(self.header) -1:
      return
    if self.control_pressed:
      self._onHoldSort(index)
    else:
      self._onNormalSort(index)
    self._draw()
    return

  def _onNormalSort(self, index):
    if self.sortbys == [self.header[index]]:
      self.ascending_order = not self.ascending_order
    self.sortbys = [self.header[index]]
    return

  def _onHoldSort(self, index):
    header = self.header[index]
    if header not in self.sortbys:
      self.sortbys.append(header)
    else:
      self.ascending_order = not self.ascending_order
    self._draw()
    return

  def _getEntryIdOrder(self):
    sorter = itemgetter(*self.sortbys)
    return [entry['entryid']
            for entry in sorted(self.entries, key=sorter)]

  def _getEntryIdInterval(self, first, last):
    if first is None:
      entryids = [last]
    elif last is None:
      entryids = [first]
    else:
      entryids = self._getEntryIdOrder()
      lastindex = entryids.index(last)
      firstindex  = entryids.index(first)
      if lastindex == 0:
        lastid = entryids[lastindex]
        entryids = entryids[firstindex:lastindex:-1]
        entryids.append(lastid)
      elif firstindex < lastindex:
        entryids = entryids[firstindex:lastindex+1]
      else:
        entryids = entryids[firstindex:lastindex-1:-1]
    return entryids

  def selectEntryId(self, entryid):
    if entryid not in self.selecteds:
      self.selecteds.append(entryid)
    return

  def deselectEntryId(self, entryid):
    if entryid in self.selecteds:
      self.selecteds.remove(entryid)
    return

  def toggleEntryId(self, entryid):
    if entryid in self.selecteds:
      self.deselectEntryId(entryid)
    else:
      self.selectEntryId(entryid)
    return

  def _clearSelecteds(self):
    self.selecteds = []
    return

  def _onClick(self, index):
    if index.column() == len(self.header) - 1:
      self._onComment(index)
    return

  def selectRow(self, row):
    entryid = self.entries[row]['entryid']
    self.selectEntryId(entryid)
    return

  def deselectRow(self, row):
    entryid = self.entries[row]['entryid']
    self.deselectEntryId(entryid)
    return

  def _onNormalClick(self, index):
    row = index.row()
    self.selectRow(row)
    return

  def _onControShiftlClick(self, index):
    last =  self.selecteds[-1] if self.selecteds else None
    entryid = self.entries[index.row()]['entryid']
    mark = self.deselectEntryId if entryid in self.selecteds else\
                                                              self.selectEntryId
    for entryid in self._getEntryIdInterval(last, entryid):
      mark(entryid)
    return

  def _onCommentSave(self, comment, row):
    self._setEntryComment(self.commentid, comment)
    self.setData(self.index(row, len(self.header) -1),
                comment)
    return

  def _onComment(self, index):
    entryid = self.entries[index.row()]['entryid']
    comment = self.entries[index.row()]['comment']
    self.commentid = entryid
    self.commentEmittingSignal.signal.emit(comment, index.row())
    return

  def _addEntry(self, entryid):
    entry = dict(entryid=entryid)
    for column in self.header:
      data = self._getEntryData(column, entryid)
      entry[column] = data
    entry['color'] = QtCore.Qt.gray
    self.entries.append(entry)
    comment = self._getEntryComment(entryid)
    return

  def addEntry(self, entryid):
    self._addEntry(entryid)
    self._draw()
    return

  def addEntries(self, entries):
    for entryid in entries:
      self.addEntry(entryid)
    self._draw()
    return

  def refresh(self):
    for entry in self.entries:
      entryid = entry['entryid']
      for column in self.header:
        data = self._getEntryData(column, entryid)
        entry[column] = data
    return

  def _getEntryComment(self, entryid):
    return ''

  def _setEntryComment(self, entryid, comment):
    return

  def _getEntryData(self, column, entryid):
    return 'missing implementation'
  pass


class BatchTableModel(TableModel):
  def __init__(self, master, batch, header, sortby):
    TableModel.__init__(self, master, header, sortby)
    self.batch = batch
    return

  def _query(self, entryid):
    query = self.query
    if not query:
      return []
    return self.batch.query(query, entryid)

  def _getEntryData(self, column, entryid):
    if column == 'query':
      fetch = self._query(entryid)
      return len(set(fetch))
    if column not in batch_filters and column != 'comment':
      return 'missing header'
    if column == 'comment':
      return self._getEntryComment(entryid)
    return self.batch.get_entry_attr(entryid, column)

  def _getEntryComment(self, entryid):
    return self.batch.get_entry_comment(entryid)

  def _setEntryComment(self, entryid, comment):
    self.batch.set_entry_comment(entryid, comment)
    return

  def getSelected(self, **filters):
    return self._filterEntries(self.selecteds, filters)

  def clearSelection(self, **filters):
    for entryid in self.getSelected(**filters):
      self.deselectEntryId(entryid)
    return

  def _filterEntries(self, entryids, filters):
    filtered = []
    for entryid in entryids:
      for filname, data in filters.iteritems():
        if self.batch.get_entry_attr(entryid, filname) != data:
          break
      else:
        filtered.append(entryid)
    return filtered

  def filterEntries(self, **filters):
    entryids = []
    for entry in self.entries:
      entryids.append(entry['entryid'])
    return self._filterEntries(entryids, filters)

  def _packSelected(self, Type):
    Entries = self.getSelected(type=Type)
    return self.batch.pack(Entries, 'fullmeas')

  def storePart(self, Pack, Key, Entries):
    Part = self._wakePackPart(Pack, Key)
    Entries.update(Part)
    Alives = {}
    for EntryId, Entry in Part.iteritems():
      Alives[Entry] = self._query(EntryId)
    return Alives

  def _wakePackPart(self, Pack, Key):
    return dict([(EntryId, self.batch.wake_entry(EntryId))
                 for EntryId in Pack.get(Key, [])])

class BatchFrame(QtGui.QWidget):
  def __init__(self, batch, header, sortby):
    QtGui.QWidget.__init__(self)
    self.batch = batch

    self.batchTable = QtGui.QTableView()
    self.batchTableModel = BatchTableModel(self, batch, header, sortby)
    commentLabel = QtGui.QLabel('Comment: ')
    self.commentEdit = QtGui.QLineEdit()
    queryLabel = QtGui.QLabel('Query: ')
    self.queryEdit = QtGui.QLineEdit()

    self.batchTable.setModel(self.batchTableModel)
    horizontalHeader = self.batchTable.horizontalHeader()
    horizontalHeader.sectionClicked.connect(self.batchTableModel._onSort)
    self.batchTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    self.batchTable.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    self.batchTable.clicked.connect(self.batchTableModel._onClick)
    selection_model = self.batchTable.selectionModel()
    selection_model.selectionChanged.connect(self.selectionChanged)
    self.batchTableModel.commentEmittingSignal.signal.connect(self.commentClicked)
    self.commentEdit.returnPressed.connect(self.editComment)
    self.queryEdit.returnPressed.connect(self.editQuery)
    self.batchTableModel.selectedRowsEmittingSignal.signal.connect(self.getSelecteds)
    self.queryEdit.setText(self.batchTableModel.query)
    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(self.batchTable)
    grid = QtGui.QGridLayout()
    grid.addWidget(commentLabel, 0, 0)
    grid.addWidget(self.commentEdit, 0, 1)
    grid.addWidget(queryLabel, 1, 0)
    grid.addWidget(self.queryEdit, 1, 1)
    vbox.addLayout(grid)
    self.setLayout(vbox)
    return

  def editComment(self):
    newComment = self.commentEdit.text()
    self.batchTableModel._onCommentSave(newComment, self.currentCommentRow)
    return

  def editQuery(self):
    newQuery = self.queryEdit.text()
    self.batchTableModel.query = newQuery
    return

  def commentClicked(self, comment, row):
    self.commentEdit.setText(comment)
    self.currentCommentRow = row
    self.commentEdit.setFocus()
    return

  def getSelecteds(self, selecteds):
    self.batchTable.blockSignals(True)
    self.batchTable.clearSelection()
    if len(selecteds) > 1:
      self.batchTable.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
    for selected in selecteds:
      self.batchTable.selectRow(selected)
    self.batchTable.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
    self.batchTable.blockSignals(False)
    return

  def setQuery(self, query):
    self.queryEdit.setText(query)
    self.editQuery()
    return

  def addEntries(self, entries):
    self.batchTableModel.addEntries(entries)
    return

  def addEntry(self, entryid):
    self.batchTableModel.addEntry(entryid)
    for i in range(len(self.batchTableModel.header)):
      self.batchTable.resizeColumnToContents(i)
    return

  def start(self):
    self.batchTableModel.start()
    return

  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.batchTableModel.control_pressed = True
    return

  def keyReleaseEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.batchTableModel.control_pressed = False
    return

  def quit(self):
    self.close()
    return

  def select_deselect(self, selections, selectionFunc):
    last_row = -1
    for selection in selections:
      row = selection.row()
      if row == last_row: continue
      selectionFunc(row)
      last_row = row
    return

  def selectionChanged(self, selected, deselected):
    deselecteds = deselected.indexes()
    self.select_deselect(deselecteds, self.batchTableModel.deselectRow)

    selecteds = self.batchTable.selectedIndexes()

    if len(selecteds) < len(self.batchTableModel.header): return

    self.select_deselect(selecteds, self.batchTableModel.selectRow)
    return

  def select(self, **kwargs):
    reportid = kwargs.get('ReportId', None)
    reporttype = kwargs.get('ReportType', None)
    if reportid is None and reporttype is None: return {}, {}, {}
    if reportid is None:
      reports = self.batchTableModel._packSelected(reporttype)
    else:
      measurement = self.batch.get_entry_measname(reportid)
      reports = {measurement: [reportid]}
    statistics = self.batchTableModel._packSelected('measproc.cFileStatistic')
    report2s = self.batchTableModel._packSelected('measproc.Report')
    return reports, report2s, statistics

  def getMeasurements(self, types):
    measurements = set()
    for type in types:
      entries = self.batchTableModel._packSelected(type)
      measurements = measurements or entries.viewkeys()
    return measurements

if __name__ == '__main__':
  import optparse
  import sys
  # report2navigator Report2NavconfigParser
  from measproc.batchsqlite import main, clear, configParser

  def Report2NavconfigParser(parser):
    parser.add_option('-p', '--hold-navigator',
                      help='Hold the navigator, default is %default',
                      default=False,
                      action='store_true')
    return parser

  app = QtGui.QApplication([])
  labels = {'foo': (False, ['bar', 'baz'])}
  tags = {'spam': ['egg', 'eggegg']}

  parser = optparse.OptionParser()
  parser = Report2NavconfigParser(parser)
  parser = configParser(parser)
  opts, args = parser.parse_args()

  batch, entids = main(opts.dbname,
                       opts.dirname,
                       opts.measurement,
                       opts.origmeas,
                       labels,
                       tags, dict(one=[1, 1], two=[2, 2], three=[3, 3]))
  batchframe = BatchFrame(batch,
                            ['measurement', 'title', 'intervals'],
                            'measurement')
  batchframe.start()
  batchframe.show()
  batchframe.addEntries(entids)


  batchframe.batchTableModel.refresh() # test only
  sys.exit(app.exec_())


