import os
import unittest

import numpy
from PySide import QtGui, QtCore, QtTest

from datavis.ReportNavigator import cReportNavigator, findWidgets, \
                                    changeColor, getWindowColor
import measproc

t = numpy.arange(0.0, 20.0, 0.01)
y = numpy.sin(t)
z = numpy.cos(t)
i = measproc.cEventFinder.compExtSigScal(t, y, measproc.greater, 0.5)
j = measproc.cEventFinder.compExtSigScal(t, z, measproc.greater, 0.5)

title = 'RN'

lower = 17.00
upper = 19.0

class TestFunctions(unittest.TestCase):
  def setUp(self):
    self.main_window = QtGui.QMainWindow()
    self.frame = QtGui.QFrame()

    main_layout = QtGui.QHBoxLayout()
    main_layout.addWidget(self.frame)

    frame_layout = QtGui.QHBoxLayout()

    self.buttons = []

    for i in range(10):
      button = QtGui.QPushButton('Button #%d' %i)
      frame_layout.addWidget(button)
      self.buttons.append(button)

    self.frame.setLayout(frame_layout)
    self.main_window.setLayout(main_layout)
    return

  def tearDown(self):
    self.main_window = None
    self.frame = None

    self.buttons = []
    return

  def test_find_widgets(self):
    frames = findWidgets(self.main_window, QtGui.QFrame)
    for frame in frames:
      self.assertEqual(frame, self.frame)

    buttons = findWidgets(self.frame, QtGui.QPushButton)
    self.assertEqual(len(list(buttons)), len(self.buttons))
    for button in buttons:
      self.assertIn(button, self.buttons)
    return

  def test_change_color(self):
    changeColor(self.frame, QtCore.Qt.red)
    frame_palette = self.frame.palette()
    frame_color = frame_palette.color(self.frame.backgroundRole())
    self.assertEqual(frame_color, QtGui.QColor(QtCore.Qt.red))
    return

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = cReportNavigator(title)
    self.init_navigator()
    return

  def init_navigator(self):
    report1 = measproc.cIntervalListReport(i, 'TestReport1')
    report2 = measproc.cIntervalListReport(j, 'TestReport2')
    self.navigator.addReport('bar', report1)
    self.navigator.addReport('baz', report2)
    self.findPage('foo')
    report_name = '#%3s %s' %(len(report1.IntervalList), 'bar')
    self.navigator.addInterval(report_name, lower, upper)
    self.navigator.start()
    return

  def findPage(self, Name):
    for index in range(self.navigator.NoteBook.count()):
      if self.navigator.NoteBook.tabText(index) == Name:
        ScrolWidget = self.navigator.NoteBook.widget(index)
        return ScrolWidget.widget()
    return None

  def tearDown(self):
    self.navigator.close()

    xmls = [ f for f in os.listdir(".") if f.endswith(".xml") ]
    for xml in xmls:
      os.remove(xml)

    npys = [ f for f in os.listdir(".") if f.endswith(".npy") ]
    for npy in npys:
      os.remove(npy)
    return

class TestAddReports(Build):
  def init_navigator(self):
    return

  def test_add_report(self):
    report1 = measproc.cIntervalListReport(i, 'TestReport1')
    self.navigator.addReport('bar', report1)
    self.navigator.start()
    report_name = '#%3s %s' %(len(report1.IntervalList), 'bar')
    page = self.findPage(report_name)
    self.assertEqual(page.Report, report1)
    for interval in report1.IntervalList:
      self.assertIn(interval, page.Frames)
      self.assertTrue(not page.Frames[interval].isHidden())
    return

  def test_add_interval(self):
    report1 = measproc.cIntervalListReport(i, 'TestReport1')
    self.navigator.addReport('bar', report1)
    report_name = '#%3s %s' %(len(report1.IntervalList), 'bar')
    self.navigator.addInterval(report_name, lower, upper)
    self.navigator.start()
    low    = min(t.searchsorted(lower), t.size-1)
    upp    = min(t.searchsorted(upper), t.size-1) + 1 
    interval = low, upp
    self.assertIn(interval, report1.IntervalList)
    page = self.findPage(report_name)
    self.assertIn(interval, page.IntervalList)
    self.assertIn(interval, page.Frames)
    self.assertTrue(not page.Frames[interval].isHidden())
    with self.assertRaises(ValueError):
      self.navigator.addInterval('foo', lower, upper)
    return

class TestGui(Build):    
  def init_navigator(self):
    self.seek_args = None
    self.set_ROI_args = None
    self.navigator.seekSignal.signal.connect(self.save_seek_args)
    self.navigator.setROISignal.signal.connect(self.save_set_ROI_args)
    Build.init_navigator(self)
    return

  def find_button_on_dock_widget(self, label):
    buttons = self.find_widget_on_dock_widget(QtGui.QPushButton)
    button = [button for button in buttons if button.text() == label]
    self.assertEqual(len(button), 1)
    return button

  def find_widget_on_dock_widget(self, _type):
    dock_widgets =  [child for child in self.navigator.children()
                    if type(child) == QtGui.QDockWidget]
    self.assertEqual(len(dock_widgets), 1)

    widget = dock_widgets[0]
    for child in widget.children():
      if type(child) == QtGui.QFrame:
        for c in child.children():
          if type(c) == _type:
            yield c
    return

  def save_seek_args(self, *args):
    self.seek_args = args
    return

  def save_set_ROI_args(self, *args):
    self.set_ROI_args = args
    return

  def set_current_interval(self):
    time = (lower + upper)/2
    self.navigator.seek(time)
    scroll_widget = self.navigator.NoteBook.currentWidget()
    page = scroll_widget.widget()
    return page

  def test_interval_btn(self):
    page = self.set_current_interval()
    actual_frame = page.Frames[page.ActualFrame]
    button_text = [child.text() for child in actual_frame.children()
                              if type(child) == QtGui.QPushButton]
    self.assertIn('%.2f' %lower, button_text)
    self.assertIn('%.2f' %upper, button_text)
    for child in actual_frame.children():
      if type(child) == QtGui.QPushButton:
        if child.text() == '%.2f' %lower:
          child.click()

          sended_time, = self.seek_args
          self.assertEqual(sended_time, lower)

          client, sended_lower, sended_upper, color = self.set_ROI_args
          self.assertEqual(type(client), cReportNavigator)
          self.assertEqual(sended_lower, lower)
          self.assertEqual(sended_upper, upper)
        elif child.text() == '%.2f' %upper:
          child.click()
          sended_time, = self.seek_args

          self.assertEqual(sended_time, upper)
          client, sended_lower, sended_upper, color = self.set_ROI_args

          self.assertEqual(type(client), cReportNavigator)
          self.assertEqual(sended_lower, lower)
          self.assertEqual(sended_upper, upper)
    return

  def test_seek(self):
    page = self.set_current_interval()

    self.assertEqual(page.ActualFrame, (lower * 100, upper * 100 + 1))

    for child in page.Frames[page.ActualFrame].children():
      if type(child) == QtGui.QPushButton and child.text != 'Comment':
        palette = child.palette()
        color = palette.color(child.backgroundRole())
        self.assertEqual(QtGui.QColor(QtCore.Qt.green), color)

      elif type(child) == QtGui.QPushButton:
        palette = child.palette()
        color = palette.color(child.backgroundRole())
        self.assertNotEqual(QtGui.QColor(QtCore.Qt.green), color)
    return

  def test_arrow_btns(self):
    page = self.set_current_interval()

    for child in page.Frames[page.ActualFrame].children():
      if type(child) == QtGui.QPushButton:
        for offset, arrow in self.navigator.IntervalPostTimes:
            if child.text() == arrow:
              child.click()
              sended_time, = self.seek_args
              self.assertEqual(sended_time, upper + offset)
              client, sended_lower, sended_upper, color = self.set_ROI_args
              self.assertEqual(type(client), cReportNavigator)
              self.assertEqual(sended_lower, lower)
              self.assertEqual(sended_upper, upper)

        for offset, arrow in self.navigator.IntervalPreTimes:
            if child.text() == arrow:
              child.click()
              sended_time, = self.seek_args
              self.assertEqual(sended_time, lower + offset)
              client, sended_lower, sended_upper, color = self.set_ROI_args
              self.assertEqual(type(client), cReportNavigator)
              self.assertEqual(sended_lower, lower)
              self.assertEqual(sended_upper, upper)
    return

  def test_add_remove_interval(self):
    low = lower + 1.5
    scroll_widget = self.navigator.NoteBook.currentWidget()
    page = scroll_widget.widget()
    orig_frames = len(page.Frames)
    self.navigator.setROI(None, low, upper, 'g')
    buttons = self.find_button_on_dock_widget('Add Interval')
    self.assertEqual(len(buttons), 1)
    button = buttons[0]
    button.click()
    self.assertEqual(len(page.Frames), orig_frames + 1)
    self.assertIn((low * 100, upper * 100 + 1), page.Frames)
    #to activate the interval
    actual_frame = page.Frames[page.ActualFrame]

    for child in actual_frame.children():
      for c in child.children():
        if type(c) == QtGui.QPushButton:
          if c.text() == '%.2f' %low:
            c.click()

    buttons = self.find_button_on_dock_widget('Remove Interval')
    self.assertEqual(len(buttons), 1)
    button = buttons[0]
    button.click()

    self.assertNotIn((low * 100, upper * 100 + 1), page.Frames)
    self.assertEqual(len(page.Frames), orig_frames)
    return

  def test_add_remove_vote(self):
    new_vote = 'foo'
    removable_vote = 'missed'

    scroll_widget = self.navigator.NoteBook.currentWidget()
    page = scroll_widget.widget()

    votes = page.Report.getVotes()
    self.assertNotIn(new_vote, votes)

    self.navigator.VoteOption.setText(new_vote)

    buttons = self.find_button_on_dock_widget('add')
    self.assertEqual(len(buttons), 1)
    button = buttons[0]
    button.click()

    votes = page.Report.getVotes()
    self.assertIn(new_vote, votes)
    check_box_label = set()
    for frame in page.children():
      if type(frame) == QtGui.QFrame:
        for check_frame in frame.children():
          if type(check_frame) == QtGui.QFrame:
            for check_box in check_frame.children():
              if type(check_box) == QtGui.QCheckBox:
                check_box_label.add(check_box.text())

    self.assertIn(new_vote, check_box_label)
    self.assertIn(removable_vote, check_box_label)
    
    self.navigator.VoteOption.setText(removable_vote)
    
    buttons = self.find_button_on_dock_widget('rm')
    self.assertEqual(len(buttons), 1)
    button = buttons[0]
    button.click()
    
    votes = page.Report.getVotes()
    self.assertNotIn(removable_vote, votes)
    check_box_label = set()
    for frame in page.children():
      if type(frame) == QtGui.QFrame:
        for check_frame in frame.children():
          if type(check_frame) == QtGui.QFrame:
            for checkbox in check_frame.children():
              if type(checkbox) == QtGui.QCheckBox and not checkbox.isHidden():
                check_box_label.add(checkbox.text())

    self.assertNotIn(removable_vote, check_box_label)
    return

  def test_vote(self):
    scroll_widget = self.navigator.NoteBook.currentWidget()
    page = scroll_widget.widget()

    for interval, frame in page.Frames.iteritems():
      for check_frame in frame.children():
        if type(check_frame) == QtGui.QFrame:
          for check_box in check_frame.children():
            if type(check_box) == QtGui.QCheckBox:
              orig_state = page.Report.checkVote(interval, check_box.text())
              self.assertEqual(orig_state, check_box.isChecked())
              check_box.toggle()
              new_state = page.Report.checkVote(interval, check_box.text())
              self.assertNotEqual(orig_state, new_state)
              self.assertEqual(new_state, check_box.isChecked())
    return

  def test_add_interval_commemt(self):
    scroll_widget = self.navigator.NoteBook.currentWidget()
    page = scroll_widget.widget()

    for interval in page.Frames.iterkeys():          
      if interval != self.navigator.NeutralInterval:
        self.assertNotEqual(page.Report.getComment(interval), 'foo')

    for interval, child in page.Frames.iteritems():
      for frame in child.children():
        if type(frame) == QtGui.QFrame:
          for button in frame.children():
            if type(button) == QtGui.QPushButton and button.text() == 'Comment':
              button.click()

              in_focus = QtGui.QApplication.focusWidget()
              self.assertEqual(in_focus, page.CommentEdit)
              page.CommentEdit.setText('foo')
              QtTest.QTest.keyClick(page.CommentEdit, QtCore.Qt.Key_Enter)

    for interval in page.Frames.iterkeys():          
      if interval != self.navigator.NeutralInterval:
        self.assertEqual(page.Report.getComment(interval), 'foo')

    for interval, child in page.Frames.iteritems():
      for frame in child.children():
        if type(frame) == QtGui.QFrame:
          for button in frame.children():
            if type(button) == QtGui.QPushButton and button.text() == 'Comment':
              button.click()

              in_focus = QtGui.QApplication.focusWidget()
              self.assertEqual(in_focus, page.CommentEdit)
              page.CommentEdit.setText('bar')
              QtTest.QTest.keyClick(page.CommentEdit, QtCore.Qt.Key_Enter)

    for interval in page.Frames.iterkeys():          
      if interval != self.navigator.NeutralInterval:
        self.assertEqual(page.Report.getComment(interval), 'bar')
    return

  def test_add_interval_comment(self):
    scroll_widget = self.navigator.NoteBook.currentWidget()
    page = scroll_widget.widget()

    comment = page.Report.getEntryComment()
    self.assertNotEqual(comment, 'foo')

    self.navigator.ReportCommentEdit.setText('foo')
    QtTest.QTest.keyClick(self.navigator.ReportCommentEdit, QtCore.Qt.Key_Enter)

    comment = page.Report.getEntryComment()
    self.assertEqual(comment, 'foo')

    self.navigator.ReportCommentEdit.setText('bar')
    QtTest.QTest.keyClick(self.navigator.ReportCommentEdit, QtCore.Qt.Key_Enter)

    comment = page.Report.getEntryComment()
    self.assertEqual(comment, 'bar')
    return
    
if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()