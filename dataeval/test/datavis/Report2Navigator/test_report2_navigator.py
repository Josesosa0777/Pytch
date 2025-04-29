import unittest

import numpy
from PySide import QtGui, QtCore, QtTest

from datavis.ReportNavigator import findWidgets
from datavis.report2navigator import Report2Navigator, START_HEADER, \
                                     END_HEADER, COMMENT_HEADER
from measproc.report2 import Report, CreateQuantity, AddQuantity
from measproc.IntervalList import cIntervalList

votegroups = {'std':  (False, ['valid', 'missed', 'invalid']),
                'road': (True,  ['city', 'rural'])}
time = numpy.arange(0, 10, 1e-2)

intervals_1 = [[0, 7], [23, 56], [76, 90]]
intervals_2 = [[25, 66], [70, 95]]

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = Report2Navigator()
    self.init_navigator()
    return

  def init_navigator(self):
    intervallist = cIntervalList(time)
    self.report = Report(intervallist, 'foo', votegroups)

    for interval in intervals_1:
      self.report.addInterval(interval)

    self.report.vote(0, 'std', 'missed')
    self.report.vote(0, 'std', 'valid')

    self.report.vote(1, 'road', 'city')
    self.report.vote(1, 'road', 'rural')

    intervallist = cIntervalList(time)
    self.report2 = Report(intervallist, 'bar', votegroups)
    for interval in [[25, 66], [70, 95]]:
      self.report2.addInterval(interval)

    self.navigator.addVoteGroup('atomsk', True, ['naota', 'takun'])
    self.navigator.addReport(self.report)
    self.navigator.addReport(self.report2)
    self.navigator.setVoteGroup('std')
    self.navigator.start()
    return

  def findPage(self, Name):
    for index in range(self.navigator.notebook.count()):
      if self.navigator.notebook.tabText(index) == Name:
        ScrolWidget = self.navigator.notebook.widget(index)
        return ScrolWidget.widget()
    return None

  def tearDown(self):
    self.navigator.close()
    return

class TestAddReports(Build):
  def init_navigator(self):
    return

  def test_add_report(self):
    intervallist = cIntervalList(time)
    self.report = Report(intervallist, 'foo', votegroups)

    for interval in intervals_1:
      self.report.addInterval(interval)

    self.navigator.addReport(self.report)

    self.assertEqual(self.report, self.navigator.reports['foo'])
    has_tab = False
    for i in range(self.navigator.notebook.count()):
      has_tab = self.navigator.notebook.tabText(i) == 'foo'
      if has_tab : break
    self.assertTrue(has_tab)

    for id, interval in self.report.iterIntervalsWithId():
      low, up = interval
      report = self.navigator.report_frames[self.report]
      not_finded_bondary = 2
      for row, interval in enumerate(report.table_model.intervals):
        for header, data in zip((START_HEADER, END_HEADER),
                              (low / 100.0, (up - 1)/ 100.0)):
          if interval['intervalid'] == id:
             column = report.table_model.header.index(header)
             qt_index = report.table_model.createIndex(row, column)
             value = float(report.table_model.data(qt_index))
             self.assertEqual(value, data)
    return

  def test_add_votegroups(self):
    intervallist = cIntervalList(time)
    self.report = Report(intervallist, 'foo', votegroups)

    for interval in intervals_1:
      self.report.addInterval(interval)

    self.navigator.addVoteGroup('atomsk', True, ['naota', 'takun'])

    self.navigator.addReport(self.report)

    report = self.navigator.reports['foo']
    vote_options = report.getVoteGroups()
    vote_group_name = vote_options.keys()

    self.assertNotIn('atomsk', vote_group_name)

    scroll = self.navigator.notebook.currentWidget()
    scroll_layout = scroll.layout()
    menu_bar = scroll_layout.menuBar()
    menus = list(findWidgets(menu_bar, QtGui.QMenu))
    self.assertGreater(len(menus), 0)

    vote_group_menu = None
    for menu in menus:
      if menu.title() == 'VoteGroups':
        vote_group_menu = menu

    self.assertIsNotNone(vote_group_menu)

    is_atomsk = False

    for action in vote_group_menu.actions():
      is_atomsk = action.text() == 'atomsk'
      if is_atomsk: break

    self.assertTrue(is_atomsk)
    return

  def test_vote(self):
    intervallist = cIntervalList(time)
    self.report = Report(intervallist, 'foo', votegroups)

    for interval in intervals_1:
      self.report.addInterval(interval)

    self.assertFalse(self.report.checkVote(0, 'std', 'missed'))
    self.report.vote(0, 'std', 'missed')
    self.assertTrue(self.report.checkVote(0, 'std', 'missed'))

    self.assertFalse(self.report.checkVote(0, 'std', 'valid'))
    self.report.vote(0, 'std', 'valid')
    self.assertTrue(self.report.checkVote(0, 'std', 'valid'))

    self.assertFalse(self.report.checkVote(1, 'road', 'city'))
    self.report.vote(1, 'road', 'city')
    self.assertTrue(self.report.checkVote(1, 'road', 'city'))

    self.assertFalse(self.report.checkVote(1, 'road', 'rural'))
    self.report.vote(1, 'road', 'rural')
    self.assertTrue(self.report.checkVote(1, 'road', 'rural'))
    self.assertFalse(self.report.checkVote(1, 'road', 'city'))

    self.navigator.addReport(self.report)

    report_frame = self.navigator.report_frames[self.report]
    intervals = report_frame.table_model.intervals

    self.assertIn('missed', intervals[0]['std'])
    self.assertIn('valid', intervals[0]['std'])

    self.assertIn('rural', intervals[1]['road'])
    self.assertNotIn('city', intervals[1]['road'])
    return

class TestGui(Build):
  def init_navigator(self):
    self.seek_args = None
    self.set_ROI_args = None
    self.navigator.seekSignal.signal.connect(self.save_seek_args)
    self.navigator.setROISignal.signal.connect(self.save_set_ROI_args)
    Build.init_navigator(self)
    self.navigator.start()
    self.navigator.show()
    return

  def save_seek_args(self, *args):
    self.seek_args = args
    return

  def save_set_ROI_args(self, *args):
    self.set_ROI_args = args
    return

  def test_add_remove_interval(self):
    report = self.navigator.reports['foo']

    lower, upper = 6.0, 6.5
    self.navigator.setROI(None, lower, upper, 'g')

    dockWidgets = list(findWidgets(self.navigator, QtGui.QDockWidget))
    self.assertEqual(len(dockWidgets), 1)

    buttons = list(findWidgets(dockWidgets[0].widget(), QtGui.QPushButton))
    add_btn = [btn for btn in buttons if btn.text() == 'add']
    self.assertEqual(len(add_btn), 1)

    add_btn[0].click()

    interval = int(lower * 100),  int(upper * 100) + 1
    self.assertIn(interval, report.intervallist)

    report_frame = self.navigator.report_frames[report]
    find_button = False
    for row, interval in enumerate(report_frame.table_model.intervals):
      if interval[START_HEADER] == lower:
        column = report_frame.table_model.header.index(START_HEADER)
        report_frame.table.selectRow(row)
        find_button = True

    self.assertTrue(find_button)

    rm_btn = [btn for btn in buttons if btn.text() == 'rm' ]
    self.assertEqual(len(rm_btn), 1)

    rm_btn[0].click()
    self.assertNotIn(interval, report.intervallist)
    return

  def test_select_vote_groups(self):
    report = self.navigator.reports['foo']
    report_frame = self.navigator.report_frames[report]

    scroll = self.navigator.notebook.currentWidget()
    scroll_layout = scroll.layout()
    menu_bar = scroll_layout.menuBar()
    menus = list(findWidgets(menu_bar, QtGui.QMenu))
    self.assertGreater(len(menus), 0)

    vote_group_menu = None
    for menu in menus:
      if menu.title() == 'VoteGroups':
        vote_group_menu = menu

    self.assertIsNotNone(vote_group_menu)

    is_not_selected_vote = False

    for action in vote_group_menu.actions():
      if action.isChecked():
        self.assertIn(action.text(), report_frame.table_model.header)
      else:
        self.assertNotIn(action.text(), report_frame.table_model.header)
        action.trigger()
        is_not_selected_vote = True

    self.assertTrue(is_not_selected_vote)

    is_not_selected_vote = False

    for action in vote_group_menu.actions():
      if action.isChecked():
        self.assertIn(action.text(), report_frame.table_model.header)
      else:
        is_not_selected_vote = True

    self.assertFalse(is_not_selected_vote)
    return

  def test_vote(self):
    report = self.navigator.reports['bar']

    report_frame = self.navigator.report_frames[report]

    row = 0

    test_interval = report_frame.table_model.intervals[row]
    id = test_interval['intervalid']
    vote = report.checkVote(id, 'std', 'missed')

    column = report_frame.table_model.header.index('std')
    qt_index = report_frame.table_model.createIndex(row, column)
    report_frame.table_model.setData(qt_index, 'missed')

    if vote:
      self.assertFalse(report.checkVote(id, 'std', 'missed'))
    else:
      self.assertTrue(report.checkVote(id, 'std', 'missed'))

    return

  def test_comment_btn(self):
    report = self.navigator.reports['foo']
    for id, interval in report.iterIntervalsWithId():
      self.assertNotEqual(report.getComment(id), 'egg')

    commentbtn = []
    report_frame = self.navigator.report_frames[report]
    for row, interval in enumerate(report_frame.table_model.intervals):
      if COMMENT_HEADER in interval:
        commentbtn.append(interval)
        column = report_frame.table_model.header.index(COMMENT_HEADER)
        ndx = report_frame.table_model.createIndex(row, column)
        report_frame.table_model.setData(ndx, 'egg')
    self.assertGreater(len(commentbtn), 0)

    for id, interval in report.iterIntervalsWithId():
      self.assertEqual(report.getComment(id), 'egg')
    return

class TestQuantity(Build):
  def init_navigator(self):
    time = numpy.arange(0, 10, 1e-2)

    intervallist = cIntervalList(time)
    param = CreateQuantity(time, 'foo', {'vehicle': {'speed': 100, 'accel': 42 }})
    self.report = param()

    for interval in [[0,7], [23, 56], [76, 90]]:
      add = AddQuantity(interval, 'vehicle', 'speed', 100)
      id = add(self.report)
      self.report.set(id, 'vehicle', 'accel', 42)

    self.navigator.addReport(self.report)
    self.navigator.start()
    self.navigator.show()
    return

  def test_edit_quantity(self):
    frame = self.navigator.report_frames[self.report]
    new_value = 69

    for id in self.report.iterIntervalIds():
      orig_quantity = self.report.getQuantities(id)
      for alias, (quagroup, quas) in frame.table_model.quas.iteritems():
        self.assertIn(quagroup, orig_quantity)
        column = frame.table_model.header.index(alias)
        row = -1
        for i, interval in enumerate(frame.table_model.intervals):
          if interval['intervalid'] == id:
            row = id
            break

        qt_index = frame.table_model.createIndex(row, column)
        frame.table_model.setData(qt_index, new_value)
        row += 1

    for id in self.report.iterIntervalIds():
      quantity = self.report.getQuantities(id)
      for name, qua in quantity.iteritems():
        for name, value in qua.iteritems():
          self.assertEqual(value, new_value)

    return

  def test_add_interval(self):
    report = self.navigator.reports['foo']

    lower, upper = 6.0, 6.5
    self.navigator.setROI(None, lower, upper, 'g')

    dockWidgets = list(findWidgets(self.navigator, QtGui.QDockWidget))
    self.assertEqual(len(dockWidgets), 1)

    buttons = list(findWidgets(dockWidgets[0].widget(), QtGui.QPushButton))
    add_btn = [btn for btn in buttons if btn.text() == 'add']
    self.assertEqual(len(add_btn), 1)

    add_btn[0].click()
    last_id = len(self.report.iterIntervalIds()) - 1
    for id in self.report.iterIntervalIds():

      quantity = self.report.getQuantities(id)
      names = self.report.getNames()
      qua_groups = names.keys()
      self.assertGreater(len(buttons), 0)

      if id == last_id:
        self.assertEqual(quantity, {})
      else:
        self.assertNotEqual(quantity, {})
    return

if  __name__ == '__main__':
  app = QtGui.QApplication([])
#   unittest.main()  <-- Deactivated. Test is not needed.