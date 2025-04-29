# -*- coding: utf-8 -*-

import time
import unittest
from operator import itemgetter

from PySide import QtGui, QtCore, QtTest

from datavis.batchframe import BatchFrame
from measproc.batchsqlite import main, clear, filters as batch_filters,\
                                 InitParams as BatchInitParams ,\
                                 UploadParams as BatchUploadParams, \
                                 CreateParams as BatchCreateParams

class Build(unittest.TestCase):
  def setUp(self):
    labels = {'foo': (False, ['bar', 'baz'])}
    tags = {'spam': ['egg', 'eggegg']}

    self.batch, self.entids = main('batch.db',
                                    'files',
                                   'd:/measurement/2011-02-10_16-50_020.mdf',
                                   True,
                                   labels,
                                   tags,
                                   dict(one=[1, 1], two=[2, 2], three=[3, 3]))

    self.batchframe = BatchFrame(self.batch,
                            ['measurement', 'title', 'intervals'],
                            'measurement')
    self.init_batchframe()
    return

  def init_batchframe(self):
    self.batchframe.start()
    self.batchframe.show()
    self.batchframe.addEntries(self.entids)
    return

  def compare_entries(self):
    model = self.batchframe.batchTable.model()
    for row in range(model.rowCount(self.batchframe.batchTable)):
      for column in range(model.columnCount(self.batchframe.batchTable) - 2 ):
        header = model.headerData(column, QtCore.Qt.Horizontal)
        header = header.replace(u'^', '')
        header = header.replace(unichr(ord('¡')), '')
        index = model.createIndex(row, column)
        id = model.entries[row]['entryid']
        entry_attr = self.batch.get_entry_attr(id, header)
        self.assertEqual(model.data(index), entry_attr)
      column = model.columnCount(self.batchframe.batchTable) - 1
      header = model.headerData(column, QtCore.Qt.Horizontal)
      index = model.createIndex(row, column)
      id = model.entries[row]['entryid']
      entry_comment = self.batch.get_entry_comment(id)
      self.assertEqual(model.data(index), entry_comment)
    return

  def tearDown(self):
    self.batchframe.close()
    self.batch.save()
    clear('batch.db', 'files')
    return

class TestAddEntries(Build):
  def test_add_entries(self):
    self.compare_entries()
    return

class TestGui(Build):
  def _test_sort(self, sortbies, prefix):
    hori_header = self.batchframe.batchTable.horizontalHeader()
    model = hori_header.model()

    orig_entries = model.entries

    if prefix == '¡':
      ndx = model.header.index(sortbies[0])
      ndx = hori_header.logicalIndex(ndx)
      hori_header.sectionClicked.emit(ndx)

    for i, sortby in enumerate(sortbies):
      ndx = model.header.index(sortby)
      ndx = hori_header.logicalIndex(ndx)
      hori_header.sectionClicked.emit(ndx)

      header_data = model.headerData(ndx, QtCore.Qt.Horizontal)
      header  = (i + 1) * prefix + sortby
      self.assertEqual(header_data, header)
      QtTest.QTest.keyPress(self.batchframe, QtCore.Qt.Key_Control)
    QtTest.QTest.keyRelease(self.batchframe, QtCore.Qt.Key_Control)
    self.assertEqual(model.sortbys, sortbies)

    self.assertNotEqual(orig_entries, model.entries)

    sorted_entries = sorted(orig_entries, key=itemgetter(*sortbies))

    self.assertEqual(sorted_entries, model.entries)
    return

  def test_sort(self):
    self._test_sort(['title'], '^')
    return

  def test_sort_by_multiple_criteria(self):
    self._test_sort(['title', 'measurement'], '^')
    return

  def test_sort_reversed(self):
    self._test_sort(['title'], '^')
    return

  def test_sort_by_multiple_criteria_reversed(self):
    self._test_sort(['title', 'measurement'], '^')
    return

  def _test_select(self, selectable_ndxs, expected_ndxs=None):
    expected_ndxs = selectable_ndxs if not expected_ndxs else expected_ndxs

    model = self.batchframe.batchTable.model()
    rows = set()
    selected_entries = set()

    for i in expected_ndxs:
      row, column = i
      ndx = model.index(row, column)
      self.batchframe.batchTable.clicked.emit(ndx)
      self.batchframe.batchTable.setCurrentIndex(ndx)
      rows.add(row)
      id = model.entries[row]['entryid']
      selected_entries.add(id)
    selecteds = self.batchframe.batchTable.selectedIndexes()
    self.assertEqual(len(selecteds) % len(model.header), 0)
    for selected in selecteds:
      self.assertIn(selected.row(), rows)
    return selected_entries

  def test_select_deselect(self):
    selectable_indexes = (3, 4),
    self._test_select(selectable_indexes)
    self.batchframe.batchTable.clearSelection()

    QtTest.QTest.keyPress(self.batchframe, QtCore.Qt.Key_Control)
    selectable_indexes = (1, 1), (2, 2), (4, 2)
    selected_entries = self._test_select(selectable_indexes)
    QtTest.QTest.keyRelease(self.batchframe, QtCore.Qt.Key_Control)

    self._test_sort(['title'], '^')
    selecteds = self.batchframe.batchTable.selectedIndexes()
    model = self.batchframe.batchTable.model()
    rows = set()
    for selected in selecteds:
      row = selected.row()
      if row in rows: continue
      rows.add(row)
      id = model.entries[row]['entryid']
      self.assertIn(id, selected_entries)
      selected_entries.remove(id)
    self.assertEqual(selected_entries, set())

    self.batchframe.batchTable.clearSelection()

    selected_indexes = (2, 2), (5, 2)
    expected_ndxs = (2, 2), (3, 2), (4, 2), (5, 2),
    QtTest.QTest.keyPress(self.batchframe, QtCore.Qt.Key_Shift)
    selected_entries = self._test_select(selectable_indexes, expected_ndxs)
    QtTest.QTest.keyRelease(self.batchframe, QtCore.Qt.Key_Shift)

    self.batchframe.batchTable.clearSelection()
    return

  def test_edit_query(self):
    model = self.batchframe.batchTable.model()
    self.batchframe.queryEdit.setText('foo')
    QtTest.QTest.keyClick(self.batchframe.queryEdit, QtCore.Qt.Key_Enter)
    self.assertEqual(model.query, 'foo')
    self.batchframe.queryEdit.setText('')
    QtTest.QTest.keyClick(self.batchframe.queryEdit, QtCore.Qt.Key_Enter)
    return

  def test_edit_comment(self):
    model = self.batchframe.batchTable.model()
    row = 2
    column = len(model.header) - 1
    selectable_indexes = (row, column),
    self._test_select(selectable_indexes)

    in_focus = QtGui.QApplication.focusWidget()
    self.assertEqual(in_focus, self.batchframe.commentEdit)
    self.batchframe.commentEdit.setText('foo')
    QtTest.QTest.keyClick(self.batchframe.commentEdit, QtCore.Qt.Key_Enter)
    modified_id = None
    for i, entry in  enumerate(model.entries):
      id = entry['entryid']
      comment = self.batch.get_entry_comment(id)
      if i == row:
        self.assertEqual(comment, 'foo')
        modified_id = id
      else:
        self.assertNotEqual(comment, 'foo')
    self.assertIsNotNone(modified_id)
    self._test_sort(['title'], '^')

    for i, entry in  enumerate(model.entries):
      id = entry['entryid']
      comment = self.batch.get_entry_comment(id)
      if id == modified_id:
        self.assertEqual(comment, 'foo')
        self.assertNotEqual(i, row)
      else:
        self.assertNotEqual(comment, 'foo')
    return

if __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()