# -*- coding: utf-8 -*-

__docformat__ = "restructuredtext en"

import csv
import xlwt
import copy
import logging
from operator import itemgetter

from PySide import QtGui, QtCore

from measproc.batchsqlite import TableQuery, LabelTableQuery, QuaTableQuery, \
                                 CommentTableQuery, get_static_table_ids, str_cell
from interval_filter import Filter

format_value = lambda val: ('%.3f' if isinstance(val, float) else '%s') % val

class ObjectEmittingSignal(QtCore.QObject):
  signal = QtCore.Signal(object)

class CommentDelegate(QtGui.QItemDelegate):
  def createEditor(self, parent, option, index):
    editor = QtGui.QLineEdit(parent=parent)
    model = index.model()
    data = str(index.data())
    editor.setText(data)
    return editor

  def setModelData(self, editor, model, index):
    model = index.model()
    model.setData(index, editor.text(), QtCore.Qt.EditRole)
    return

  def setEditorData(self, editor, index):
    data = str(index.data())
    editor.setText(data)
    return

  def updateEditorGeometry(self, editor, option, index):
    editor.setGeometry(option.rect)
    return

class VoteDelegate(QtGui.QItemDelegate):
  def __init__(self, vote_options, exclusive, batch):
    QtGui.QItemDelegate.__init__(self)
    self.select_signal = ObjectEmittingSignal()
    self.vote_options = vote_options
    self.exclusive = exclusive
    self.batch = batch
    return

  def createEditor(self, parent, option, index):
    editor = QtGui.QPushButton(parent=parent)
    editor.setFlat(True)
    menu = QtGui.QMenu()
    votegroup = QtGui.QActionGroup(menu)
    votegroup.setExclusive(self.exclusive)
    model = index.model()
    for option in self.vote_options:
      action = QtGui.QAction(option, editor)
      action.setCheckable(True)
      menu.addAction(action)
      votegroup.addAction(action)
      action.triggered.connect(lambda e=editor, i=index, m=model:
                                      self.setModelData(e, m, i))
    editor.setMenu(menu)

    editor.menu()

    return editor

  def setModelData(self, editor, model, index):
    menu = editor.menu()
    value = []
    for action in menu.actions():
      if action.isChecked():
        value.append(action.text())
    if not value:
      value = [TableQuery.NOT_AVAILABLE]
    model.setData(index, value, QtCore.Qt.EditRole)
    return

  def setEditorData(self, editor, index):
    model = index.model()
    menu = editor.menu()
    interval = model.visible_intervals[index.row()]
    headerName = model.header[index.column()]
    i_id = interval["id"]
    lg = model.int_label[headerName]
    votes = set(self.batch.get_interval_labels(i_id, lg))
    for action in menu.actions():
      action.setChecked(action.text() in votes)
    self.select_signal.signal.emit(index)
    editor.showMenu()
    return

  def updateEditorGeometry(self, editor, option, index):
    editor.setGeometry(option.rect)
    return


class TableModel(QtCore.QAbstractTableModel):
  def __init__(self, batch, header, sortbys):
      QtCore.QAbstractTableModel.__init__(self)
      self.int_label = {}
      self.int_comment = set()
      self.selected = {}
      self.selectedRowsEmittingSignal = ObjectEmittingSignal()
      self.quas = {}
      self.intervals = []
      self.visible_intervals = []
      self.row_color = QtCore.Qt.gray
      self.batch = batch


      self.control_pressed = False

      cur = batch.con.cursor()
      self.query = header
      self.queries = [TableQuery.factory(names, query, cur)
                      for names, query in header]
      self.header = []
      for query in self.queries:
        self.header.extend(query.get_names())
        if isinstance(query, LabelTableQuery):
          self.int_label[query.name] = query.labelgroup
        elif isinstance(query, CommentTableQuery):
          self.int_comment.add(query.name)
        elif isinstance(query, QuaTableQuery):
          self.quas[query.qua] = query.quagroup

      self.sortbys = [  [sortby, order]
                         for sortby, order in sortbys
                         if sortby in self.header ]
      self._ids = set()
      self.addIntervals(get_static_table_ids(self.queries))
      return

  def columnCount(self, parent=QtCore.QModelIndex()):
    return len(self.header)

  def rowCount(self, parent=QtCore.QModelIndex()):
    return len(self.visible_intervals)

  def headerData(self, index, orientation, role=QtCore.Qt.DisplayRole):
    if (orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole):
      header = self.header[index]
      prefix = ""
      sortbys = [sby for sby, _ in self.sortbys]
      if header in sortbys:
        ndx = sortbys.index(header)
        if self.sortbys[ndx][1]:
          prefix = '^'
        else:
          prefix = u'ˇ'
        prefix *= ndx + 1
      headerLabel = unicode(prefix) + unicode(header)
      return headerLabel
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
      return True
    else:
      return False

  def data(self, index, role=QtCore.Qt.DisplayRole):
    if index.isValid():
      interval = self.visible_intervals[index.row()]
      headerName = self.header[index.column()]
      if role == QtCore.Qt.DisplayRole:
        result = interval[headerName]
        result = TableQuery.str_result(result)
        return result
      elif role == QtCore.Qt.BackgroundColorRole:
        #set the color of comment column
        if headerName in self.int_comment:
          background = QtGui.QBrush(QtCore.Qt.darkGreen)
        else:
          background = QtGui.QBrush(interval['color'])
        return background
    else:
      return None

  def getHeader(self):
    header = [(query.names, query.query) for query in self.queries]
    return header

  def setViewForQueries(self, viewname):
    for query in self.queries:
      query.query = query.query.replace('entries', viewname)
    return

  def flags(self, index):
    flag = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
    name = self.header[index.column()]
    if name in self.int_label or name in self.int_comment or name in self.quas:
      flag |= QtCore.Qt.ItemIsEditable
    return flag

  def setData(self, index, value, role=QtCore.Qt.EditRole):
    if index.isValid() and role == QtCore.Qt.EditRole:
      interval = self.visible_intervals[index.row()]
      headerName = self.header[index.column()]
      i_id = interval["id"]
      if headerName in self.int_label:
        lg = self.int_label[headerName]
        orig_value = set(self.batch.get_interval_labels(i_id, lg))
        diff = orig_value - set(value)
        for v in value:
          if v != TableQuery.NOT_AVAILABLE:
            self.batch.label_interval(i_id, lg, v)

        for v in diff:
          if v != TableQuery.NOT_AVAILABLE:
            self.batch.unlabel_interval(i_id, lg, v)
      elif headerName in self.int_comment:
        self.batch.add_intervalcomment(i_id, value)
      elif headerName in self.quas:
        self.batch.set_interval_qua(i_id, self.quas[headerName], headerName,
                                    float(value))
      if headerName not in interval:
        return False
      if isinstance(interval[headerName], float):
        interval[headerName] = float(value)
        return True
      interval[headerName] = value
      return True
    else:
      return False

  def _addInterval(self, intervalid, cur):
    if intervalid in self._ids: return

    interval = dict(id=intervalid, color=QtCore.Qt.gray)
    self.update_interval_from_batch(interval, cur)
    if 'DTC in HEX' in interval.keys():
      interval['DTC in HEX'] = hex(int(interval['DTC in DEC']))
    self.intervals.append(interval)
    self.visible_intervals.append(interval)
    self._ids.add(intervalid)
    return

  def rmSelectedInterval(self):
    intervalid = self.selected['id']
    self._ids.remove(intervalid)
    self.intervals.remove(self.selected)
    self.visible_intervals.remove(self.selected)
    self.selected = None
    self._draw()
    return

  def restore_visible_intervals(self):
    self.set_visible_intervals( copy.copy(self.intervals) )
    return

  def set_visible_intervals(self, visible_intervals):
    self.visible_intervals = visible_intervals
    self._draw()
    return

  def addInterval(self, intervalid, cur):
    self._addInterval(intervalid, cur)
    self._draw()
    return

  def addIntervals(self, intervalids):
    cur = self.batch.con.cursor()
    for intervalid in intervalids:
      self._addInterval(intervalid, cur)
    self._draw()
    return

  def addEntry(self, entry):
    ids = self.batch.get_intervalid_by_entryid(entry)
    self.addIntervals(ids)
    return

  def addEntries(self, entries):
    for entry in entries:
      self.addEntry(entry)
    return

  def _draw(self):
    self.layoutAboutToBeChanged.emit()
    if not self.sortbys:
      self.layoutChanged.emit()
      return
    sortby = self.sortbys[0][0]
    for name, asc in self.sortbys[::-1]:
      self.visible_intervals.sort(key=itemgetter(name), reverse=not asc)
    if self.visible_intervals:
      prevData = self.visible_intervals[0][sortby]
      self.row_color = QtCore.Qt.gray
    for interval in self.visible_intervals:
      data = interval[sortby]
      interval['color'] = self.toggleColor(prevData, data)
      prevData = data

    self.layoutChanged.emit()

    if not self.selected:
      return

    #the previously selected ndx maybe filtered out
    try:
      selected_ndx = self.visible_intervals.index(self.selected)
      self.selectedRowsEmittingSignal.signal.emit(selected_ndx)
    except ValueError:
      pass
    return

  def _onSort(self, index):
    # avoid order by commnent
    if self.header[index] in self.int_comment: return

    if self.control_pressed:
      self._onHoldSort(index)
    else:
      self._onNormalSort(index)
    self._draw()
    return

  def _onNormalSort(self, index):
    header = self.header[index]
    sortby = header

    if len(self.sortbys) == 1 and self.sortbys[0][0] == sortby:
      self.sortbys[0][1] = not self.sortbys[0][1]
    else:
      self.sortbys = [[sortby, True]]
    return

  def _onHoldSort(self, index):
    header = self.header[index]
    sortby = header
    sortbys = [sby for sby, _ in self.sortbys]
    if sortby not in sortbys:
      self.sortbys.append([sortby, True])
    else:
      ndx = sortbys.index(sortby)
      self.sortbys[ndx][1] = not self.sortbys[ndx][1]
    self._draw()
    return

  def refresh(self):
    cur = self.batch.con.cursor()
    for interval in self.visible_intervals:
      self.update_interval_from_batch(interval, cur)
    self._draw()
    return

  def selectRow(self, row):
    self.selected = self.visible_intervals[row]
    return

  def get_selected(self):
    if self.selected:
      return self.selected['id']
    return None

  def update_interval_from_batch(self, interval, cur):
    intervalid = interval['id']
    for query in self.queries:
      query.update_row(cur, interval, intervalid)
    return


  def get_selected_int_attr(self, attr_name):
    if not self.selected:
      return None

    i_id = self.selected['id']
    result = self.batch.get_interval_attr(i_id, attr_name)
    return result

  def getStartTime(self):
    return self.get_selected_int_attr('start_time')

  def getEndTime(self):
    return self.get_selected_int_attr('end_time')

  def storePart(self):
    if not self.selected:
      return {}
    i_id = self.selected['id']
    e_id = self.batch.get_entryid_by_interval(i_id)
    try:
      entry = self.batch.wake_entry(e_id)
    except IOError, e:
      logger = logging.getLogger()
      logger.warning(
        "Selected entry could not be waken (Is report directory set properly?)")
      logger.debug("entryid: %s; IOError: %s" % (e_id, str(e)))
      entry = None
    pos = self.batch.get_interval_pos(i_id)
    return {entry : [(pos, i_id, e_id)]}
  
  def export_to_textile_file(self, file_path):
    return self.export_to_csv_file(file_path, "|", wrap_rows=True)

  def export_to_csv_file(self, file_path, delim, wrap_rows=False):
    with open(file_path, 'wb') as csv_output:
      csv_writer = csv.writer(csv_output, delimiter=delim)
      # Write header
      header = self.header
      if wrap_rows:
        header = [""] + header + [""]
      csv_writer.writerow(header)
      # Write all intervals
      for interval in self.visible_intervals:
        row = [str_cell(interval[title]) for title in self.header]
        if wrap_rows:
          row = [""] + row + [""]
        csv_writer.writerow(row)
    return

  def export_to_xls_file(self, file_path):
    xls_file = xlwt.Workbook()
    sheet = xls_file.add_sheet("Intervals")
    # Write header
    for column, title in enumerate(self.header):
      sheet.write(0, column, title)
    # Write all intervals
    for row, interval in enumerate(self.visible_intervals, 1):
      for column, title in enumerate(self.header):
        sheet.write(row, column, str_cell(interval[title]))
    xls_file.save(file_path)
    return

class IntervalFrame(QtGui.QWidget):
  def __init__(self):
    QtGui.QWidget.__init__(self)

    self.batchTable = QtGui.QTableView()
    frame = QtGui.QFrame()
    scroll_area = QtGui.QScrollArea()

    self.batchTableModel = None
    self.selected_column = None
    self.selected_meas_sig = ObjectEmittingSignal()

    splitter = QtGui.QSplitter()
    splitter.setObjectName('IntFrameSplitter')
    splitter.setOrientation(QtCore.Qt.Vertical)

    vbox = QtGui.QVBoxLayout()
    frame_of_intervals = QtGui.QFrame()
    self.add_btn = QtGui.QPushButton('Add')
    self.rm_btn = QtGui.QPushButton('Remove')
    self.export_btn = QtGui.QPushButton('Export')
    self.more_options_btn = QtGui.QPushButton('More Options')
    btn_layout = QtGui.QVBoxLayout()
    dummy = QtGui.QFrame()
    btn_layout.addWidget(dummy)
    btn_layout.addWidget(self.add_btn)
    btn_layout.addWidget(self.rm_btn)
    # btn_layout.insertSpacing(-1, 15)
    btn_layout.addWidget(self.export_btn)
    btn_layout.addWidget(self.more_options_btn)
    dummy = QtGui.QFrame()
    btn_layout.addWidget(dummy)

    self.add_btn.setEnabled(False)
    self.rm_btn.setEnabled(False)
    self.export_btn.setEnabled(False)
    self.more_options_btn.setEnabled(False)

    hbox_layout = QtGui.QHBoxLayout()
    hbox_layout.addWidget(self.batchTable)
    hbox_layout.addLayout(btn_layout)
    frame_of_intervals.setLayout(hbox_layout)
    splitter.addWidget(frame_of_intervals)

    self.filter_vbox = QtGui.QVBoxLayout()
    self.hboxes = []
    self.filters = []
    self.filters_2_buttons = {}
    self.signals_2_filters = {}
    self.add_filter()
    frame.setLayout(self.filter_vbox)
    scroll_area.setWidget(frame)
    scroll_area.setWidgetResizable(True)
    splitter.addWidget(scroll_area)
    vbox.addWidget(splitter)
    self.setLayout(vbox)
    return

  def add_filter(self):
    filter = Filter()
    self.filters.append(filter)
    self.signals_2_filters[filter.sorted_elements] = filter
    hbox = QtGui.QHBoxLayout()
    self.hboxes.append(hbox)
    filter.add_selector_object_signal.signal.connect(hbox.insertWidget)
    self.filter_vbox.addLayout(hbox)
    filter.init()
    ndx = self.filters.index(filter)
    add_btn = QtGui.QPushButton('+')
    dummy = QtGui.QFrame()
    hbox.addWidget(dummy)
    hbox.addWidget(add_btn)
    add_btn.setFixedSize(25, 25)
    add_btn.clicked.connect(self.add_filter)
    rm_btn = QtGui.QPushButton('-')
    hbox.addWidget(rm_btn)
    rm_btn.setFixedSize(25, 25)
    self.filters_2_buttons[filter] = add_btn, rm_btn
    if ndx == 0:
      rm_btn.clicked.connect(filter.disableAll)
    else:
      rm_btn.clicked.connect(lambda f=filter: self.remove_filter(f))

    if self.batchTableModel is not None:
      self.init_filter(filter)

    if len(self.filters) > 1:
      first_filter = self.filters[0]
      _, rm_btn = self.filters_2_buttons[first_filter]
      rm_btn.clicked.disconnect()
      rm_btn.clicked.connect(lambda f=first_filter: self.remove_filter(f))
    return

  def remove_filter(self, filter):
    add_btn, rm_btn = self.filters_2_buttons[filter]
    for btn in  (add_btn, rm_btn):
      btn.close()
      btn.setParent(None)
      btn.deleteLater()
    del self.filters_2_buttons[filter]
    del self.signals_2_filters[filter.sorted_elements]
    self.filters.remove(filter)
    filter.close()
    if filter.is_initalized():
      filter.sorted_elements.signal.disconnect()
      self.filters[0].set_all_elements(self.batchTableModel.intervals)
    if len(self.filters) == 1:
      first_filter, = self.filters
      _, rm_btn = self.filters_2_buttons[first_filter]
      rm_btn.clicked.disconnect()
      rm_btn.clicked.connect(first_filter.disableAll)
    return

  def init_filter(self, filter):
    filter.set_batch(self.batchTableModel.batch)
    filter.set_all_elements(self.batchTableModel.visible_intervals,
                            filtering=False)
    filter.set_int_label(self.batchTableModel.int_label)
    filter.set_quas(self.batchTableModel.quas)
    filter.set_int_comment(self.batchTableModel.int_comment)
    filter.fill_option_selector(self.batchTableModel.header)
    self.make_filter_connections()
    return

  def make_filter_connections(self):
    for ndx, filter in enumerate(self.filters):
      filter.sorted_elements.signal.connect(self.filt)
    return

  def filt(self, elements):
    sender = self.sender()
    filter = self.signals_2_filters[sender]
    ndx = self.filters.index(filter)
    self.batchTableModel.set_visible_intervals(elements)
    if ndx < len(self.filters) - 1:
      self.filters[ndx + 1].set_all_elements(elements)
    return

  def get_table_model(self):
    return self.batchTable.model()

  def set_table_model(self, table_model):
    self.batchTableModel = table_model
    self.batchTable.setModel(self.batchTableModel)

    horizontalHeader = self.batchTable.horizontalHeader()
    horizontalHeader.sectionClicked.connect(self._onSort)
    self.batchTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
    self.batchTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
    selection_model = self.batchTable.selectionModel()
    selection_model.selectionChanged.connect(self.selectionChanged)
    self.batchTableModel.selectedRowsEmittingSignal.signal.connect(
                                                           self.selectSelecteds)

    i = 0
    for _header in self.batchTableModel.query:
      names, query = _header
      Query = TableQuery.get_type(names, query)
      for name in TableQuery.filter_names(names):
        if Query is LabelTableQuery:
          lg = LabelTableQuery.get_lg_from_query(query)
          exclusive, vote_options =  self.batchTableModel.batch.get_labelgroup(
                                                                             lg)

          delegate = VoteDelegate(vote_options, exclusive,
                                                     self.batchTableModel.batch)
          self.batchTable.setItemDelegateForColumn(i, delegate)
          self.batchTable.itemDelegateForColumn(i)
          delegate.select_signal.signal.connect(
            lambda ndx : self.setCurrentIndex(ndx))
        if Query is CommentTableQuery:
          delegate = CommentDelegate()
          self.batchTable.setItemDelegateForColumn(i, delegate)
          self.batchTable.itemDelegateForColumn(i)
        i += 1

    self.batchTable.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)

    self.alignHeader2Content()
    for filter in self.filters:
      self.init_filter(filter)

    return

  def start(self):
    self.batchTableModel.refresh()
    return

  def setCurrentIndex(self, index):
    self.selected_column = index.column()
    self.batchTable.setCurrentIndex(index)
    return

  def _onSort(self, index):
    self.batchTableModel._onSort(index)
    self.alignHeader2Content()
    return

  def selectSelecteds(self, selected):
    self.batchTable.blockSignals(True)
    self.batchTable.clearSelection()
    self.batchTable.selectRow(selected)
    self.batchTable.blockSignals(False)
    return

  def keyPressEvent(self, event):
    if self.batchTableModel is None:
      return QtGui.QWidget.keyPressEvent(self, event)

    if event.key() == QtCore.Qt.Key_Control:
      self.batchTableModel.control_pressed = True
    if event.key() == QtCore.Qt.Key_C and self.batchTableModel.control_pressed:
      selected_ndxs = self.batchTable.selectedIndexes()
      if not selected_ndxs: return

      datas = [unicode(self.batchTableModel.data(ndx))
               for ndx in selected_ndxs]

      txt = '\t'.join(datas)

      clipboard = QtGui.QApplication.clipboard()
      clipboard.clear()

      clipboard.setText(txt)
    return

  def keyReleaseEvent(self, event):
    if self.batchTableModel is None:
      return QtGui.QWidget.keyPressEvent(self, event)
    if event.key() == QtCore.Qt.Key_Control:
      self.batchTableModel.control_pressed = False
    return

  def alignHeader2Content(self):
    for i in range(len(self.batchTableModel.header)):
      self.batchTable.resizeColumnToContents(i)
    return

  def addIntervals(self, intervalids):
    self.batchTableModel.addIntervals(intervalids)
    self.alignHeader2Content()
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
    selecteds = self.batchTable.selectedIndexes()

    if len(selecteds) < len(self.batchTableModel.header): return

    self.select_deselect(selecteds, self.batchTableModel.selectRow)
    entries = self.getEntries()
    measurement, = entries.keys()
    self.selected_meas_sig.signal.emit(measurement)
    return

  def getEntries(self):
    selected = self.batchTableModel.get_selected()
    if not selected:
      return {}
    entry = self.batchTableModel.batch.get_entryid_by_interval(selected)
    measurement_2_entry = self.batchTableModel.batch.pack([entry], 'fullmeas')
    return measurement_2_entry

  def getSelectedTimes(self):
    start = self.batchTableModel.getStartTime()
    end = self.batchTableModel.getEndTime()
    return start, end

  def storePart(self):
    return self.batchTableModel.storePart()

  def getHeaderSortby(self):
    return self.batchTableModel.sortbys

  def sizeHint(self):
    return QtCore.QSize(1000, 1000)

class CreateIntervalTable:
  def __init__(self, batch, interval_header, sortbys):
    self.batch = batch
    self.interval_header = interval_header
    self.sortbys = sortbys
    return

  def __call__(self):
    return TableModel(self.batch, self.interval_header, self.sortbys)

if __name__ == '__main__':
  import pyglet_workaround  # necessary as early as possible (#164)

  import sys
  from argparse import ArgumentParser
  # report2navigator Report2NavconfigParser

  from config.Config import Config
  from config.helper import procConfigFile, getConfigPath
  from config.modules import Modules
  from interface.manager import Manager
  from measproc.batchsqlite import main, clear, configParser

  def Report2NavconfigParser(parser):
    parser.add_option('-p', '--hold-navigator',
                      help='Hold the navigator, default is %default',
                      default=False,
                      action='store_true')
    return parser

  interface = 'iAnalyze'
  app = QtGui.QApplication([])
  modules = Modules()
  modules.read( getConfigPath('modules', '.csv') )
  args = Config.addArguments( ArgumentParser() ).parse_args()
  name = procConfigFile('dataeval', args)
  config = Config(name, modules)
  manager = config.createManager(interface)
  config.init(args)
  config.load(manager, interface)

  batch = manager.get_batch()

  interval_header = [
            (('title',),
             '''SELECT entries.title FROM entryintervals
                  JOIN entries ON
                       entries.id = entryintervals.entryid
                WHERE entryintervals.id = ?'''),
            (('@', 'start', 'duration'),
             'SELECT id, start_time, end_time-start_time FROM entryintervals'),
            (('meas',),
             '''SELECT measurements.basename FROM entryintervals
                  JOIN entries ON
                       entries.id = entryintervals.entryid
                  JOIN measurements ON
                       measurements.id = entries.measurementid
                WHERE entryintervals.id = ?'''),
            (('Type of vehicle',), "LABEL 'vehicle type'"),
            (('Road Type',), "LABEL 'road type'"),
            (('Sensor',), "LABEL 'sensor'"),
            (('ego speed',),
             '''SELECT quantities.value * 3.6 FROM entryintervals
                  JOIN quantities ON
                       quantities.entry_intervalid = entryintervals.id
                  JOIN quanames ON
                       quanames.id = quantities.nameid
                  JOIN quanamegroups ON
                       quanamegroups.id = quanames.groupid
                WHERE  quanamegroups.name = "ego vehicle"
                  AND  quanames.name = "speed"
                  AND  entryintervals.id = ?'''),
            (('dx at start',),
             '''SELECT quantities.value FROM entryintervals
                  JOIN quantities ON
                       quantities.entry_intervalid = entryintervals.id
                  JOIN quanames ON
                       quanames.id = quantities.nameid
                  JOIN quanamegroups ON
                       quanamegroups.id = quanames.groupid
                WHERE  quanamegroups.name = "target"
                  AND  quanames.name = "dx start"
                  AND  entryintervals.id = ?'''),
            (('aeb duration',),
             '''SELECT quantities.value FROM entryintervals
                  JOIN quantities ON
                       quantities.entry_intervalid = entryintervals.id
                  JOIN quanames ON
                       quanames.id = quantities.nameid
                  JOIN quanamegroups ON
                       quanamegroups.id = quanames.groupid
                WHERE  quanamegroups.name = "target"
                  AND  quanames.name = "pure aeb duration"
                  AND  entryintervals.id = ?'''),
            (('dx at aeb',),
             '''SELECT quantities.value FROM entryintervals
                  JOIN quantities ON
                       quantities.entry_intervalid = entryintervals.id
                  JOIN quanames ON
                       quanames.id = quantities.nameid
                  JOIN quanamegroups ON
                       quanamegroups.id = quanames.groupid
                WHERE  quanamegroups.name = "target"
                  AND  quanames.name = "dx aeb"
                  AND  entryintervals.id = ?'''),
            (('comment',), 'COMMENT'),
          ]

  intervalframe = IntervalFrame(batch, interval_header, ['meas', 'start'])


  intervalframe.start()
  int_ids = [i + 1 for i in range(2000) if i % 3 == 0]
  intervalframe.addIntervals(int_ids)
  intervalframe.show()

  sys.exit(app.exec_())
