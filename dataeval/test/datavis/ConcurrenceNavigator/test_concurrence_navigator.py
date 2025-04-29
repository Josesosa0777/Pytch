import os
import sys
import unittest
import cStringIO

import PIL
from PIL import ImageGrab
import numpy
import matplotlib
from PySide import QtGui, QtCore, QtTest

import matplotlib as mpl

from datavis.Synchronizer import cSynchronizer
from datavis.PlotNavigator import cPlotNavigator
from datavis.ConcurrenceNavigator import cConcurrenceNavigator
import measproc

class Build(unittest.TestCase):
  def setUp(self):
    self.navigator = cConcurrenceNavigator()
    self.syncs = []
    self.sync2plot = {}
    for i in range(2):
      sync = cSynchronizer()
      self.syncs.append(sync)
      plots = set()
      self.sync2plot[sync] = plots
      for i in range(2):
        plot = cPlotNavigator()
        plots.add(plot)

    self.init_navigator()
    return

  def init_navigator(self):
    for sync, plots in self.sync2plot.iteritems():
      for plot in plots:
        t = numpy.arange(0,400,0.01)
        plot.addsignal('sine' ,  [t, numpy.sin(t)])
        sync.addClient(plot)
      sync.start()
      sync.show()
      self.navigator.addConcurrence(sync, str(sync))
    self.navigator.start()
    return

  def tearDown(self):
    self.navigator.close()
    for sync in self.syncs:
      sync.close()
    self.syncs = []
    self.sync2plot = {}
    return

class TestClose(Build):
  def test_close(self):
    self.navigator.close()
    self.assertTrue(self.navigator.isHidden())
    return

  def tearDown(self):
    for sync in self.syncs:
      sync.close()
    self.syncs = []
    self.sync2plot = {}
    return

class TestSetXLim(Build):
  def test_set_axes_limitm(self):
    self.navigator.setAllXlim(0, 400)
    for ax in self.navigator.fig.axes:
      min, max = ax.get_xlim()
      self.assertAlmostEqual(min, 0)
      self.assertAlmostEqual(max, 400)
    return

class TestKeyPress(Build):
  def setUp(self):
    Build.setUp(self)
    renderer = self.navigator.canvas.get_renderer()
    self.navigator.help.draw(renderer)
    return

  def test_f1_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertTrue(self.navigator.help.get_visible())
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_F1)
    self.assertFalse(self.navigator.help.get_visible())
    return

  def test_space_press(self):
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Space)
    for ax in self.navigator.fig.axes:
      con = self.navigator.ax2con[ax]
      self.assertTrue(con.playing)
    QtTest.QTest.keyClick(self.navigator, QtCore.Qt.Key_Space)
    for ax in self.navigator.fig.axes:
      con = self.navigator.ax2con[ax]
      self.assertFalse(con.playing)
    return

  def test_p_press(self):
    for ax in self.navigator.fig.axes:
      ax.set_navigate_mode('ZOOM')
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_P)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_navigate_mode(), 'PAN')
    return

  def test_o_press(self):
    for ax in self.navigator.fig.axes:
      ax.set_navigate_mode('PAN')
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_O)
    for ax in self.navigator.fig.axes:
      self.assertEqual(ax.get_navigate_mode(), 'ZOOM')
    return

  def test_home_press(self):
    self.navigator.toolbar.push_current()
    self.navigator.fig.shared_sp.set_xlim(4.5, 5.0)
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Home)
    left, right = self.navigator.fig.shared_sp.get_xlim()
    self.assertAlmostEqual(0.0, left)
    self.assertAlmostEqual(1.0, right, delta=.01)
    return

  def test_left_press(self):
    self.navigator.toolbar.push_current()
    self.navigator.fig.shared_sp.set_xlim(4.5, 5.0)
    left, right = self.navigator.fig.shared_sp.get_xlim()
    QtTest.QTest.keyPress(self.navigator, QtCore.Qt.Key_Left)
    left, right = self.navigator.fig.shared_sp.get_xlim()
    self.assertAlmostEqual(0.0, left)
    self.assertAlmostEqual(1.0, right, delta=.01)
    return

class TestAddConcurrence(Build):
  def test_add_concurrence(self):
    self.assertEqual(len(self.navigator.fig.axes), len(self.syncs))
    for ax in self.navigator.fig.axes:
      con = self.navigator.ax2con[ax]
      con.onSeek(5.0)
    for sync in self.syncs:
      for plot in self.sync2plot[sync]:
        self.assertAlmostEqual(plot.time, 5)
    return

if  __name__ == '__main__':
  app = QtGui.QApplication([])
  unittest.main()