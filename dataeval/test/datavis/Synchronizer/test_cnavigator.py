import os
import unittest

import numpy
from PySide import QtGui, QtCore, QtTest

from datavis.Synchronizer import cNavigator
from datavis.GroupNavigator import cGroupNavigator
from datavis.ListNavigator import cListNavigator
from datavis.MatplotlibNavigator import MatplotlibNavigator
from datavis.ReportNavigator import cReportNavigator
from datavis.TrackNavigator import cTrackNavigator
from datavis.SituationNavigator import cSituationNavigator
from datavis.GroupNavigator import cGroupNavigator
from datavis.StatisticNavigator import cStatisticNavigator
from datavis.report2navigator import Report2Navigator
from datavis.GroupParam import cGroupParam

import measproc
from measproc.report2 import Report

group_param = cGroupParam((1, 2), 'A', False, False)
group_name = 'FooGroup'

def remove_xmls():
  xmls = [ f for f in os.listdir(".") if f.endswith(".xml") ]
  for xml in xmls:
    os.remove(xml)
  return

def remove_npys():
  npys = [ f for f in os.listdir(".") if f.endswith(".npy") ]
  for npy in npys:
    os.remove(npy)
  return

class BuildBaseNavigator(object):
  Navigator = None
  def setUp(self):
    self.navigator = self.Navigator()
    self.navigator_init()
    self.navigator.start()

    self.args = None

    self.navigator.closeSignal.signal.connect(self.saveArgs)
    self.navigator.playSignal.signal.connect(self.saveArgs)
    self.navigator.pauseSignal.signal.connect(self.saveArgs)
    self.navigator.seekSignal.signal.connect(self.saveArgs)
    self.navigator.setROISignal.signal.connect(self.saveArgs)
    self.navigator.selectGroupSignal.signal.connect(self.saveArgs)
    self.navigator.setXLimOnlineSignal.signal.connect(self.saveArgs)
    return

  def navigator_init(self):
    return

  def saveArgs(self, *args):
    self.args = args
    return

  def tearDown(self):
    self.navigator.closeSignal.signal.disconnect()
    self.navigator.playSignal.signal.disconnect()
    self.navigator.pauseSignal.signal.disconnect()
    self.navigator.seekSignal.signal.disconnect()
    self.navigator.setROISignal.signal.disconnect()
    self.navigator.selectGroupSignal.signal.disconnect()
    self.navigator.setXLimOnlineSignal.signal.disconnect()
    self.navigator.close()
    return

class TestBaseNavigatorFunction(BuildBaseNavigator):
  def test_close(self):
    self.navigator.show()
    self.assertFalse(self.navigator.isHidden())
    self.navigator.close()
    self.assertTrue(self.navigator.isHidden())
    return

  def test_play(self):
    self.navigator.play(2.0)
    self.assertTrue(self.navigator.playing)
    return

  def test_on_play(self):
    self.navigator.onPlay(2.0)
    self.assertTrue(self.navigator.playing)
    return

  def test_pause(self):
    self.navigator.play(5.0)
    self.navigator.pause(2.0)
    self.assertFalse(self.navigator.playing)
    self.assertAlmostEqual(self.navigator.time, 2.0)
    return

  def test_on_pause(self):
    self.navigator.play(5.0)
    self.navigator.onPause(2.0)
    self.assertFalse(self.navigator.playing)
    self.assertAlmostEqual(self.navigator.time, 2.0)
    return

  def test_seek(self):
    self.navigator.seek(2.0)
    self.assertAlmostEqual(self.navigator.time, 2.0)
    return

  def test_on_seek(self):
    self.navigator.onSeek(2.0)
    self.assertAlmostEqual(self.navigator.time, 2.0)
    return

  def test_set_ROI(self):
    self.navigator.setROI(self.navigator, 2.0, 5.0, 'b')
    self.assertAlmostEqual(self.navigator.ROIstart, 2.0)
    self.assertAlmostEqual(self.navigator.ROIend, 5.0)
    return

  def test_on_set_ROI(self):
    self.navigator.onSetROI(2.0, 5.0, 'b')
    self.assertAlmostEqual(self.navigator.ROIstart, 2.0)
    self.assertAlmostEqual(self.navigator.ROIend, 5.0)
    return

  def test_geometry(self):
    new_geom = '800x600+100+100'
    self.navigator.setWindowGeometry(new_geom)
    self.assertAlmostEqual(new_geom, self.navigator.getWindowGeometry())
    return

  def test_set_window_title(self):
    new_title = 'Foo'
    self.navigator.setWindowTitle(new_title)
    self.assertEqual(new_title, self.navigator.windowTitle())
    return

  def test_close_signal(self):
    layout = self.navigator.getWindowGeometry()
    self.navigator.close()
    self.assertAlmostEqual(self.args, (layout, ))
    return

  def test_play_signal(self):
    self.navigator.onPlay(2.0)
    self.assertAlmostEqual(self.args, (2.0, ))
    return

  def test_pause_signal(self):
    self.navigator.onPause(2.0)
    self.assertAlmostEqual(self.args, (2.0, ))
    return

  def test_seek_signal(self):
    self.navigator.onSeek(2.0)
    self.assertAlmostEqual(self.args, (2.0, ))
    return

  def test_setROI_signal(self):
    self.navigator.onSetROI(1.1, 2.2, 'r')
    self.assertAlmostEqual(self.args, 
                          (self.navigator, 1.1, 2.2, 'r'))
    return

  def test_selectGroup_signal(self):
    self.navigator.onSelectGroup(group_name)
    self.assertAlmostEqual(self.args, (group_name, ))
    return

  def test_set_xlim_online_signal(self):
    self.navigator.on_set_xlim_online(5.0, 10.0)
    self.assertAlmostEqual(self.args, (5.0, 10.0))
    return

  def test_set_xlim_online_signal(self):
    self.navigator.on_set_xlim_online(5.0, 10.0)
    self.assertAlmostEqual(self.args, (5.0, 10.0))
    return

  def test_space_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Space)
    self.assertTrue(self.navigator.playing)
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Space)
    self.assertFalse(self.navigator.playing)
    return

  def test_copy_conter_to_buffer(self):
    #to check its callable to all navigator
    self.navigator.copyContentToBuffer()
    return

  def test_copy_conter_to_clipboard(self):
    #to check its callable to all navigator
    self.navigator.copyContentToClipboard()
    return

class TestGroupNavigator(TestBaseNavigatorFunction, unittest.TestCase):
  Navigator = cGroupNavigator

  def navigator_init(self):
    group_param = cGroupParam((1, 2), 'A', False, False)
    self.navigator.addGroup(group_name, group_param)
    return

class TestListNavigator(TestBaseNavigatorFunction, unittest.TestCase):
  Navigator = cListNavigator

class TestMatplotlibNavigator(TestBaseNavigatorFunction, unittest.TestCase):
  Navigator = MatplotlibNavigator

  def navigator_init(self):
    fig = self.navigator.fig
    ax = fig.add_subplot(111)
    ax.plot((1,2,3), (4,5,6))
    return

class TestReportNavigator(TestBaseNavigatorFunction, unittest.TestCase):
  Navigator = cReportNavigator
  def navigator_init(self):
    t = numpy.arange(0.0, 20.0, 0.01)
    y = numpy.sin(t)
    i = measproc.cEventFinder.compExtSigScal(t, y, measproc.greater, 0.5)
    report = measproc.cIntervalListReport(i, 'TestReport')

    self.navigator.addReport('baz', report)
    return

  @classmethod  
  def tearDownClass(cls):
    remove_xmls()
    remove_npys()
    return

class TestTrackNavigator(TestBaseNavigatorFunction, unittest.TestCase):
  Navigator = cTrackNavigator

  def navigator_init(self):
    self.navigator.addGroup(group_name, group_param)
    return

class TestStatisticNavigator(TestBaseNavigatorFunction, unittest.TestCase):
  Navigator = cStatisticNavigator

if __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()