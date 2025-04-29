# -*- coding: utf-8 -*-

import sys
from operator import itemgetter

from PySide import QtGui, QtCore

from Synchronizer import cNavigator
from ReportNavigator import findWidgets, changeColor, getWindowColor
from IntervalFrame import ObjectEmittingSignal, VoteDelegate
from measproc.batchsqlite import TableQuery, LabelTableQuery,\
                                 CommentTableQuery, get_static_table_ids

START_HEADER = 'start'
END_HEADER = 'end'
COMMENT_HEADER = 'comment'

class OnSeekSignal(QtCore.QObject):
  signal = QtCore.Signal(int, float)

class RefreshSignal(QtCore.QObject):
  signal = QtCore.Signal()

class ReportTable(QtCore.QAbstractTableModel):
  def __init__(self, header, sortby, report):
      QtCore.QAbstractTableModel.__init__(self)
      self.int_labels = {}
      self.quas = {}
      self.selected = None
      self.selectedRowsEmittingSignal = ObjectEmittingSignal()

      self.intervals = []
      self.row_color = QtCore.Qt.gray
      self.sortbys = [sortby]
      self.report = report

      self.ascending_order = True
      self.control_pressed = False
      self.header = []
      self.parse_header(header)
      vg = report.getVoteGroups()
      for gn in vg.keys():
        self.addVoteGroup(gn)
      self.on_seek_signal = OnSeekSignal()
      return

  def parse_header(self, header):
    is_comment_header = False
    self.header = [START_HEADER, END_HEADER]
    for names, query in header:
      query = query.lstrip()
      if query.startswith('LABEL'):
        label, votegroup = query.split(' ', 1)
        votegroup = votegroup.lstrip()
        votegroup = votegroup.rstrip()
        votegroup = votegroup.strip('"\'')
        if not self.report.hasVoteGroup(votegroup):
          self.logger.warning("\n%s doesn't have %s labelgroup. %s are not added to header"
                           %(self.report.getTitle(), votegroup, names))
          continue
        self.header.extend(names)
        for name in names:
          self.int_labels[name] = votegroup
      elif query.startswith('QUANTITY'):
        self.header.extend(names)
        label, quantities = query.split(' ', 1)
        quagroup, qua = quantities.split(',')
        quagroup = quagroup.lstrip()
        quagroup = quagroup.rstrip()
        quagroup = quagroup.strip('"\'')
        qua = qua.lstrip()
        qua = qua.rstrip()
        qua = qua.strip('"\'')
        qua2quagroup = quagroup, qua
        for name in names:
          self.quas[name] = qua2quagroup
    self.header.append(COMMENT_HEADER)
    return

  def addQuantity(self, quagroup, qua, header_name=None):
    header_name = qua if header_name is None else header_name
    quas = [q for _, q in self.quas.itervalues()]
    if qua in quas: return

    ndx = self.header.index(COMMENT_HEADER)
    self.header.insert(ndx, header_name)
    self.quas[header_name] = quagroup, qua
    for interval in self.intervals:
      self.update_interval(interval)
    return

  def addVoteGroup(self, groupname, header_name=None):
    header_name = groupname if header_name is None else header_name

    votegroups = self.int_labels.values()
    if groupname in votegroups: return

    ndx = self.header.index(COMMENT_HEADER)
    self.header.insert(ndx, header_name)
    self.int_labels[header_name] = groupname
    for interval in self.intervals:
      self.update_interval(interval)
    return

  def columnCount(self, parent=QtCore.QModelIndex()):
    return len(self.header)

  def rowCount(self, parent=QtCore.QModelIndex()):
    return len(self.intervals)

  def headerData(self, index, orientation, role=QtCore.Qt.DisplayRole):
    if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole
        and index < len(self.header)):
      header = self.header[index]
      prefix = ""
      if header in self.sortbys:
        if self.ascending_order:
          prefix = '^'
        else:
          prefix = u'^'
        prefix *= self.sortbys.index(header) + 1
      headerLabel = unicode(prefix) + unicode(header)
      return headerLabel
    else:
      return None

  def data(self, index, role=QtCore.Qt.DisplayRole):
    if index.isValid():
      interval = self.intervals[index.row()]
      if role == QtCore.Qt.DisplayRole:
        if isinstance(self.header[index.column()], str):
          headerName = self.header[index.column()]
        else:
          headerName, _ = self.header[index.column()]
        if isinstance(interval[headerName], float):
          return "%.2f" %interval[headerName]
        if isinstance(interval[headerName], (tuple, list)):
          return TableQuery.SEP.join(interval[headerName])
        return str(interval[headerName])

      if role == QtCore.Qt.BackgroundColorRole:
        #set the color of comment column
        if COMMENT_HEADER in self.header \
            and index.column() == self.header.index(COMMENT_HEADER):
          background = QtGui.QBrush(QtCore.Qt.darkGreen)
        else:
          background = QtGui.QBrush(interval['color'])
        return background
    else:
      return None

  def setData(self, index, value, role=QtCore.Qt.EditRole):
    if index.isValid():
      interval = self.intervals[index.row()]
      if role == QtCore.Qt.EditRole:
        if isinstance(self.header[index.column()], str):
          headerName = self.header[index.column()]
        else:
          headerName, query = self.header[index.column()]
        key = headerName
        interval = self.intervals[index.row()]
        i_id = interval["intervalid"]

        if headerName in self.int_labels:
          lg = self.int_labels[headerName]
          exclusive, votes = self.report.getVoteGroup(lg)
          value = value.split(TableQuery.SEP)
          orig_value = index.data().split(TableQuery.SEP)
          diff = set(value) - set(orig_value)

          if not exclusive:
            diff |= set(orig_value) - set(value)

          for v in diff:
            if v != TableQuery.NOT_AVAILABLE:
              self.report.toggle(i_id, lg, v)

        elif headerName in self.quas:
          groupname, qua_name = self.quas[headerName]
          if value != '':
            if groupname not in self.report.getNames():
              self.report.setNames(groupname, set([qua_name]))
            value = float(value)
            self.report.set(i_id, groupname, qua_name, value)

        elif headerName == COMMENT_HEADER:
          self.report.setComment(i_id, value)

        if not key in interval:
          return False

        if isinstance(interval[key], float):
          if value != '':
            interval[key] = float(value)
          else:
            return False

        interval[key] = value
        return True
    else:
      return False

  def toggleColor(self, prevData, data):
    if prevData != data:
      if self.row_color == QtCore.Qt.lightGray:
        self.row_color = QtCore.Qt.gray
      elif self.row_color == QtCore.Qt.gray:
        self.row_color = QtCore.Qt.lightGray
    return self.row_color

  def flags(self, index):
    flag = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
    if isinstance(self.header[index.column()], str):
      name = self.header[index.column()]
    else:
      name, _ = self.header[index.column()]
    if name in self.int_labels or name in self.quas or name == COMMENT_HEADER:
      flag |= QtCore.Qt.ItemIsEditable
    return flag

  def _onSort(self, index):
    # avoid order by commnent
    if COMMENT_HEADER in self.header \
      and self.header.index(COMMENT_HEADER) == index:
      return
    if self.control_pressed:
      self._onHoldSort(index)
    else:
      self._onNormalSort(index)
    self._draw()
    return

  def _onNormalSort(self, index):
    if isinstance(self.header[index], str):
      header = self.header[index]
    else:
      header, _ = self.header[index]
    sortby = header

    if self.sortbys == [sortby]:
      self.ascending_order = not self.ascending_order
    self.sortbys = [sortby]
    return

  def _onHoldSort(self, index):
    if isinstance(self.header[index], str):
      header = self.header[index]
    else:
      header, _ = self.header[index]
    sortby = header
    if sortby not in self.sortbys:
      self.sortbys.append(sortby)
    else:
      self.ascending_order = not self.ascending_order
    self._draw()
    return

  def selectRow(self, row):
    self.selected = self.intervals[row]
    return

  def get_selected(self):
    if self.selected:
      return self.selected['intervalid']
    return None

  def _addInterval(self, intervalid):
    interval = dict(intervalid=intervalid)
    self.update_interval(interval)
    self.intervals.append(interval)
    return

  def addInterval(self, intervalid):
    self._addInterval(intervalid)

    self._draw()
    return

  def _onClick(self, index):
    column = index.column()
    row = index.row()
    interval = self.intervals[row]
    id = interval['intervalid']
    if self.header[column] == START_HEADER:
      time = interval[START_HEADER]
      self.on_seek_signal.signal.emit(id, time)
    elif self.header[column] == END_HEADER:
      time = interval[END_HEADER]
      self.on_seek_signal.signal.emit(id, time)
    return

  def update_interval(self, interval):
    intervalid = interval['intervalid']
    for name in self.header:
      if name == START_HEADER:
        result, _ = self.report.getTimeInterval(intervalid)

      elif name == END_HEADER:
        _, result = self.report.getTimeInterval(intervalid)

      elif name == COMMENT_HEADER:
        result = self.report.getComment(intervalid)
      elif name in self.int_labels:
        exclusive, votes = self.report.getVoteGroup(self.int_labels[name])
        result = [vote for vote in votes
                       if self.report.checkVote(intervalid, name, vote)]
        result = result if result else TableQuery.NOT_AVAILABLE
      elif name in self.quas:
        groupname, qua_name = self.quas[name]
        quantities = self.report.getQuantities(intervalid)
        if quantities:
          result = quantities[groupname][qua_name]
        else:
          result = TableQuery.NOT_AVAILABLE

      else:
        raise KeyError('Cannot handle %s headers'
                                                               %(name))

      interval[name] = result
    if "color" not in interval:
      interval["color"] = QtCore.Qt.gray
    return

  def _findIntervalIds(self, time):
    return self.report.findIntervalIds(time)

  def _draw(self):
    self.layoutAboutToBeChanged.emit()
    sorter = itemgetter(*self.sortbys)
    sortby = self.sortbys[0]

    self.intervals = sorted(self.intervals, key=sorter,
                          reverse=not self.ascending_order)
    if self.intervals:
      prevData = self.intervals[0][sortby]
    for interval in self.intervals:
      if interval['color'] == QtCore.Qt.lightGray \
         or interval['color'] == QtCore.Qt.gray:
        data = interval[sortby]
        interval['color'] = self.toggleColor(prevData, data)
        prevData = data

    self.layoutChanged.emit()

    if not self.selected:
      return

    selected_ndx = self.intervals.index(self.selected)
    self.selectedRowsEmittingSignal.signal.emit(selected_ndx)
    return

  def markInterval(self, intervalid, color):
    for interval in self.intervals:
      if interval['intervalid'] == intervalid:
        interval['color'] = color
    self._draw()
    return

  def remove_interval(self):
    if not self.selected: return
    id = self.selected['intervalid']
    self.report.rmInterval(id)

    self.intervals.remove(self.selected)
    self.selected = None
    self.intervals = []
    for intervalid in self.report.iterIntervalIds():
      self.addInterval(intervalid)
    return

  def addRemoveVotGroup(self, groupname, exclusive, votes):
    ndx = -1
    if groupname in self.int_labels.values():
        removable_headers = [header_name for header_name, g_name in
                            self.int_labels.iteritems() if g_name == groupname]

        for rm_header in removable_headers:
          self.header.remove(rm_header)
          del self.int_labels[rm_header]

    else:
      self.report.addVoteGroup(groupname, exclusive, votes)

      ndx = self.header.index(COMMENT_HEADER)
      self.header.insert(ndx, groupname)
      self.int_labels[groupname] = groupname
    for interval in self.intervals:
      self.update_interval(interval)
    return ndx

  def refresh(self):
    self._draw()
    return

class ReportFrame(QtGui.QWidget):
  def __init__(self, header, sortby, report):
    QtGui.QWidget.__init__(self)

    self.table = QtGui.QTableView()
    self.report = report
    self.table_model = ReportTable(header, sortby, report)

    self.table.setModel(self.table_model)

    horizontalHeader = self.table.horizontalHeader()
    horizontalHeader.sectionClicked.connect(self.table_model._onSort)
    self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    selection_model = self.table.selectionModel()
    selection_model.selectionChanged.connect(self.selectionChanged)
    self.table_model.selectedRowsEmittingSignal.signal.connect(
                                                           self.selectSelecteds)
    self.table.clicked.connect(self.table_model._onClick)
    self.markedcolor = QtCore.Qt.cyan
    self.actintervals = set()
    self.votegroups = {}

    votemenubar = QtGui.QMenuBar()
    self.votegroupmenu = QtGui.QMenu('VoteGroups', parent=votemenubar)
    votemenubar.addMenu(self.votegroupmenu)

    ndx = self.table_model.header.index(START_HEADER)
    self.default_delegate = self.table.itemDelegateForColumn(ndx)

    self.refresh_delegates(self.table_model.header)

    self.table.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
    vbox = QtGui.QVBoxLayout()
    vbox.addWidget(self.table)
    vbox.setMenuBar(votemenubar)
    vbox.menuBar()
    self.setLayout(vbox)
    self.refresh_signal = RefreshSignal()
    return

  def selectionChanged(self, selected, deselected):
    selecteds = self.table.selectedIndexes()

    if len(selecteds) < len(self.table_model.header): return

    self.select_deselect(selecteds, self.table_model.selectRow)
    return

  def refresh_delegates(self, header):
    for column in range(self.table_model.columnCount()):
      for row in range(self.table_model.rowCount()):
        ndx = self.table_model.createIndex(column, row)
        delegate = self.table.itemDelegate(ndx)
        #delegate.deleteLater()

    for i, h in enumerate(header):
      self.table.setItemDelegateForColumn(i, self.default_delegate)
      self.table.itemDelegateForColumn(i)

    column = self.table_model.header.index(COMMENT_HEADER)

    delegate = self.table.itemDelegate(self.table_model.createIndex(column, 0))
    for i, h in enumerate(header):
      if h not in self.table_model.int_labels : continue
      lg = self.table_model.int_labels[h]

      exclusive, vote_options =  self.report.getVoteGroup(lg)

      delegate = VoteDelegate(vote_options, exclusive)
      self.table.setItemDelegateForColumn(i, delegate)
      self.table.itemDelegateForColumn(i)
      delegate.select_signal.signal.connect(lambda ndx :
                                         self.table.selectRow(ndx.row()))
      self.addVoteGroup(lg, exclusive, vote_options)
    return

  def selectSelecteds(self, selected):
    self.table.blockSignals(True)
    self.table.clearSelection()
    self.table.selectRow(selected)
    self.table.blockSignals(False)
    return

  def addInterval(self, intervalid):
    self.table_model.addInterval(intervalid)
    return

  def keyPressEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.table_model.control_pressed = True
    return

  def keyReleaseEvent(self, event):
    if event.key() == QtCore.Qt.Key_Control:
      self.table_model.control_pressed = False
    return

  def select_deselect(self, selections, selectionFunc):
    last_row = -1
    for selection in selections:
      row = selection.row()
      if row == last_row: continue
      selectionFunc(row)
      last_row = row
    return

  def markInterval(self, intervalid, color=QtCore.Qt.cyan):
    self.table_model.markInterval(intervalid, color)
    return

  def remove_interval(self):
    self.table_model.remove_interval()
    self.table.clearSelection()
    return

  def  setVoteGroup(self, groupname):
    self.table.clearSelection()
    self.table.setCurrentIndex(QtCore.QModelIndex())
    exclusive, votes = self.votegroups[groupname]
    ndx = self.table_model.addRemoveVotGroup(groupname, exclusive, votes)

    if ndx != -1:
      delegate = VoteDelegate(votes, exclusive)
      self.table.setItemDelegateForColumn(ndx, delegate)
      self.table.itemDelegateForColumn(ndx)
      delegate.select_signal.signal.connect(lambda ndx :
                                         self.table.selectRow(ndx.row()))
    else:
      #find the deletable widgets
      for child in self.table.children():
        if isinstance(child, QtGui.QWidget):
          for c in child.children():
            if isinstance(c, QtGui.QPushButton):
              for h in (c.children()):
                if isinstance(h, QtGui.QAction):
                  c.deleteLater()
    self.refresh_delegates(self.table_model.header)
    selected_row = self.table_model.get_selected()
    if selected_row:
      self.table.selectRow(selected_row)
    self.refresh()
    self.refresh_signal.signal.emit()
    for action in self.votegroupmenu.actions():
        if action.text() == groupname:
          action.setChecked(action.isChecked())
    return

  def addVoteGroup(self, groupname, exclusive, votes):
    if groupname in self.votegroups: return

    self.votegroups[groupname] = exclusive, votes
    if self.votegroupmenu.actions():
      self.votegroupmenu.clear()

    for name in sorted(self.votegroups.keys()):
      action = QtGui.QAction(name, self)
      action.setCheckable(True)
      action.triggered.connect(lambda n=name: self.setVoteGroup(n))
      self.votegroupmenu.addAction(action)
    self.refresh()
    return

  def refresh(self):
    self.table_model.refresh()
    for action in self.votegroupmenu.actions():
      lgs = self.table_model.int_labels.values()
      name = action.text()
      action.setChecked(name in lgs)
    self.alignHeader2Content()
    return

  def alignHeader2Content(self):
    for i in range(len(self.table_model.header)):
      self.table.resizeColumnToContents(i)
    return

class Report2Navigator(cNavigator):
  SEP = '\t'
  def __init__(self, header=[], color='m'):
    cNavigator.__init__(self)

    self.notebook = QtGui.QTabWidget()
    self.setCentralWidget(self.notebook)

    addbtn = QtGui.QPushButton('add')
    rmbtn = QtGui.QPushButton('rm')

    addbtn.clicked.connect(self._onAddInterval)
    rmbtn.clicked.connect(self._onRmInterval)

    frame = QtGui.QFrame()
    layout = QtGui.QHBoxLayout()
    layout.addStretch(1)
    layout.addWidget(addbtn)
    layout.addWidget(rmbtn)
    frame.setLayout(layout)

    dw = QtGui.QDockWidget()
    dw.setWidget(frame)
    self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dw)

    self.votegroups = {}
    self.reports = {}
    self.report_frames = {}

    self.color = color
    self.time = None

    self.header = header

    self.marked = {}
    self.seekedintervals  = {}
    self.neutral_color = QtCore.Qt.gray
    return

  def seekWindow(self):
    index = self.notebook.currentIndex()
    title = self.notebook.tabText(index)

    report = self.reports[title]
    report_frame = self.report_frames[report]
    old_marked = self.seekedintervals[report]
    intervalids = self._findIntervalIds(title)

    if intervalids == old_marked:
      return

    self._unmarkIntervals(title, old_marked)

    self.seekedintervals[report] = intervalids
    self._markIntervals(title, intervalids)

    forever_marked = list(self.marked[report])
    self._markIntervals(title, forever_marked, color=QtCore.Qt.cyan)
    self.refresh()
    return

  def setVoteGroup(self, groupname):
    index = self.notebook.currentIndex()
    title = self.notebook.tabText(index)

    report = self.reports[title]
    report_frame = self.report_frames[report]

    report_frame.setVoteGroup(groupname)
    return

  def _storeReport(self, report):
    postfix = 1
    title = report.getTitle()
    while title in self.reports:
      title = title.rsplit('-', 1)[0]
      title = '%s-%d' %(title, postfix)
      postfix += 1
    self.reports[title] = report
    return title

  def addReport(self, report, visible_header=None, sortby=None, header=[]):
    title = self._storeReport(report)

    votegroups = report.getVoteGroups()
    names = report.getNames()
    sortby = START_HEADER if sortby is None else sortby

    header = header if header else self.header
    report_frame = ReportFrame(header, sortby, report)
    self.report_frames[report] = report_frame
    self.marked[report] = set()
    self.seekedintervals[report] = []
    for intervalid in report.iterIntervalIds():
      report_frame.addInterval(intervalid)

    report_frame.table_model.on_seek_signal.signal.connect(self._onSeek)
    report_frame.refresh_signal.signal.connect(self.refresh)

    self.notebook.addTab(report_frame, title)
    for name, (exclusive, votes) in self.votegroups.iteritems():
      self.addVoteGroup(name, exclusive, votes)

    names = report.getNames()
    votegroups = report.getVoteGroups()

    for groupname, (exclusive, votes) in votegroups.iteritems():
      self.addVoteGroup(groupname, exclusive, votes)

    for quagroup, quas in names.iteritems():
      for qua in quas.iterkeys():
        self.report_frames[report].table_model.addQuantity(quagroup, qua)
    return title

  def refresh(self):
    for report_frame in self.report_frames.itervalues():
      report_frame.refresh()
    if self.time:
      self.seek(self.time)
    return

  def addVoteGroup(self, groupname, exclusive, votes):
    self.votegroups[groupname] = exclusive, votes
    for name, (exclusive, votes) in self.votegroups.iteritems():
      for reportframe in self.report_frames.itervalues():
        reportframe.addVoteGroup(name, exclusive, votes)
    if self.time:
      self.seek(self.time)
    return

  def _onSeek(self, intervalid, time):
    index = self.notebook.currentIndex()
    title = self.notebook.tabText(index)
    report = self.reports[title]

    self.time = time

    self.seekSignal.signal.emit(self.time)
    report = self.reports[title]
    lower, upper = report.getTimeInterval(intervalid)
    self.setROISignal.signal.emit(self, lower, upper, self.color)
    self.seek(time)
    return

  def _findIntervalIds(self, title):
    if self.time is None:
      return []
    report = self.reports[title]
    return report.findIntervalIds(self.time)

  def markIntervalForever(self, title, intervalid):
    report = self.reports[title]
    marked = self.marked[report]
    marked.add(intervalid)
    report_frame = self.report_frames[report]
    report_frame.markInterval(intervalid)
    return

  def _markIntervals(self, title, intervalids, color=QtCore.Qt.green):
    report = self.reports[title]
    report_frame = self.report_frames[report]

    for intervalid in intervalids:
      report_frame.markInterval(intervalid, color=color)
    return

  def _unmarkIntervals(self, title, intervalids):
    self._markIntervals(title, intervalids, color=self.neutral_color)
    return

  def _rmInterval(self, title):
    report = self.reports[title]
    report_frame = self.report_frames[report]

    report_frame.remove_interval()
    if self.time:
      self.seek(self.time)
    return

  def _onAddInterval(self):
    index = self.notebook.currentIndex()
    title = self.notebook.tabText(index)
    report = self.reports[title]

    interval = report.getTimeIndex(self.ROIstart), \
              report.getTimeIndex(self.ROIend)+1

    intervalid = report.addInterval(interval)

    report_frame = self.report_frames[report]
    report_frame.addInterval(intervalid)
    return

  def _onRmInterval(self):
    index = self.notebook.currentIndex()
    title = self.notebook.tabText(index)
    self._rmInterval(title)
    return

def _markSubButtons(frame, color, isComment):
  for subframe in frame.children():
    Buttons = findWidgets(subframe, QtGui.QPushButton)
    for button in Buttons:
      if (button.text() == 'comment') == isComment:
        changeColor(button, color)
  return


def configParser(parser):
  parser.add_option('-p', '--hold-navigator',
                    help='Hold the navigator, default is %default',
                    default=False,
                    action='store_true')
  return parser

if __name__ == '__main__':
  import sys
  import optparse

  import numpy

  from measproc.report2 import Report, CreateQuantity, AddQuantity
  from measproc.IntervalList import cIntervalList
  app = QtGui.QApplication([])
  parser = optparse.OptionParser()
  parser = configParser(parser)
  opts, args = parser.parse_args()

  votegroups = {'std':  (False, ['valid', 'missed', 'invalid']),
                'road': (True,  ['city', 'rural', 'highway']),
                'AEBS event rating scale': (True, ['foo', 'bar'])}
  time = numpy.arange(0, 100.0, 1e-2)

  intervallist = cIntervalList(time)
  param = CreateQuantity(time, 'foo', {'ego vehicle': {'speed': 100, 'accel': 42 }})
  report = param()
  quaintity = param()

  intervals = [[6 * i, 6 * i + 5] for i in range(200)]
  intervals.append([0.1, 99])

  for interval in intervals:
    add = AddQuantity(interval, 'ego vehicle', 'speed', 100)
    id = add(report)
    report.set(id, 'ego vehicle', 'accel', 42)

  intervallist = cIntervalList(time)
  report2 = Report(intervallist, 'bar', votegroups)
  for interval in intervals:
    report2.addInterval(interval)

  navigator = Report2Navigator()
  navigator.addVoteGroup('atomsk', True, ['naota', 'takun'])
  navigator.addReport(report)
  navigator.addReport(report2,
       header=[(('measurement',), '''SELECT measurements.basename FROM
              entryintervals JOIN entries ON entries.id = entryintervals.entryid
              JOIN measurements ON measurements.id = entries.measurementid WHERE
              entryintervals.id = ?'''), (('title',), '''SELECT entries.title
              FROM entryintervals JOIN entries ON entries.id =
              entryintervals.entryid WHERE entryintervals.id = ?'''),
              (('start    ',), '''SELECT start_time FROM entryintervals WHERE
              id = ?'''), (('duration',), '''SELECT end_time - start_time FROM
              entryintervals WHERE id = ?'''), (('moving state',), '''SELECT
              labels.name FROM entryintervals JOIN interval2label ON
              interval2label.entry_intervalid = entryintervals.id JOIN labels ON
              labels.id = interval2label.labelid JOIN labelgroups ON
              labelgroups.id = labels.groupid WHERE labelgroups.name =
              "moving state" AND entryintervals.id = ?'''), (('asso state',),
              '''SELECT labels.name FROM entryintervals JOIN interval2label ON
              interval2label.entry_intervalid = entryintervals.id JOIN labels ON
              labels.id = interval2label.labelid JOIN labelgroups ON
              labelgroups.id = labels.groupid WHERE labelgroups.name =
              "asso state" AND entryintervals.id = ?'''), (('algo state',),
              '''SELECT labels.name FROM entryintervals JOIN interval2label ON
              interval2label.entry_intervalid = entryintervals.id JOIN labels ON
              labels.id = interval2label.labelid JOIN labelgroups ON
              labelgroups.id = labels.groupid WHERE labelgroups.name =
              "AEBS algo" AND entryintervals.id = ?'''), (('ego speed',),
              '''SELECT quantities.value * 3.6 FROM entryintervals JOIN quantities
              ON quantities.entry_intervalid = entryintervals.id JOIN quanames
              ON quanames.id = quantities.nameid JOIN quanamegroups ON
              quanamegroups.id = quanames.groupid WHERE quanamegroups.name =
              "ego vehicle" AND quanames.name = "speed" AND entryintervals.id =
              ?'''), (('dx at start',), '''SELECT quantities.value FROM
              entryintervals JOIN quantities ON quantities.entry_intervalid =
              entryintervals.id JOIN quanames ON quanames.id = quantities.nameid
              JOIN quanamegroups ON quanamegroups.id = quanames.groupid WHERE
              quanamegroups.name = "target" AND quanames.name = "dx start" AND
              entryintervals.id = ?'''), (('aeb period before start',),
              '''SELECT quantities.value FROM entryintervals JOIN quantities ON
              quantities.entry_intervalid = entryintervals.id JOIN quanames ON
              quanames.id = quantities.nameid JOIN quanamegroups ON
              quanamegroups.id = quanames.groupid WHERE quanamegroups.name =
              "target" AND quanames.name = "pure aeb duration" AND
              entryintervals.id = ?'''), (('dx at aeb selection',), '''SELECT
              quantities.value FROM entryintervals JOIN quantities ON
              quantities.entry_intervalid = entryintervals.id JOIN quanames ON
              quanames.id = quantities.nameid JOIN quanamegroups ON
              quanamegroups.id = quanames.groupid WHERE quanamegroups.name =
              "target" AND quanames.name = "dx aeb" AND entryintervals.id =
              ?'''), (('warning rating scale',), '''LABEL
              "AEBS event rating scale"'''), (('comment',), 'COMMENT'),
              (('speed',), 'QUANTITY "ego vehicle", "speed"'),
              (('std',), 'LABEL "std"'), (('road',), 'LABEL "road"'),])

  navigator.setVoteGroup('std')
  navigator.setROI(navigator, 4.2, 5.6, QtCore.Qt.magenta) # cheet for add interval
  #navigator.seek(0.3)
  navigator.seek(0.1)
  navigator.markIntervalForever('bar', 1)
  navigator.start()
  navigator.show()
  sys.exit(app.exec_())
